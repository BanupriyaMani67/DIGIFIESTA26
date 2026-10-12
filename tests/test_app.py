from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import ADMIN_EMAIL, DAY1_EVENTS, DAY2_EVENTS, create_app


class DigifiestaAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "test.db"
        self.admin_config = self.root / "admin.json"
        self.admin_config.write_text(
            json.dumps({
                "email": ADMIN_EMAIL,
                "password_hash": generate_password_hash("a-very-long-test-password"),
            }),
            encoding="utf-8",
        )
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "DATABASE": str(self.database),
            "ADMIN_CONFIG": str(self.admin_config),
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _login_admin(self) -> None:
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_email"] = ADMIN_EMAIL

    def _db(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _fetchone(self, query: str, parameters: tuple[object, ...] = ()) -> sqlite3.Row:
        with closing(self._db()) as connection:
            return connection.execute(query, parameters).fetchone()

    @staticmethod
    def _day1_form(student_id: str = "MVJ-001", events: tuple[str, ...] = (DAY1_EVENTS[0],)) -> dict[str, object]:
        return {
            "participant_name": "Asha Rao",
            "participant_class": "BCA II",
            "participant_id": student_id,
            "events": list(events),
        }

    @staticmethod
    def _team_form(name: str, prefix: str, events: tuple[str, ...] = DAY2_EVENTS) -> dict[str, object]:
        return {
            "team_name": name,
            "submitter_name": f"{prefix} One",
            "events": list(events),
            "member_name": [f"{prefix} One", f"{prefix} Two"],
            "member_class": ["BCA II", "BCA III"],
            "member_id": [f"{prefix}-ID-1", f"{prefix}-ID-2"],
        }

    def test_welcome_and_public_pages_render_branding(self) -> None:
        for path in ("/", "/day1", "/day2", "/results", "/admin/login"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"MVJ DEGREE COLLEGE", response.data)
                self.assertIn(b"DIGIFIESTA", response.data)
        self.assertIn(b"Results have not been published yet.", self.client.get("/results").data)

    def test_day1_registration_persists_after_database_reconnection(self) -> None:
        response = self.client.post("/register/day1", data=self._day1_form())
        self.assertEqual(response.status_code, 302)
        with closing(self._db()) as connection:
            registration = connection.execute(
                "SELECT registration_ref FROM day1_registrations"
            ).fetchone()
            self.assertRegex(registration["registration_ref"], r"^D1-[A-F0-9]{10}$")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_members").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_registration_events").fetchone()[0], 1)

        restarted = create_app({
            "TESTING": True,
            "SECRET_KEY": "another-test-secret",
            "DATABASE": str(self.database),
            "ADMIN_CONFIG": str(self.admin_config),
            "WTF_CSRF_ENABLED": False,
        })
        self.assertEqual(restarted.test_client().get("/").status_code, 200)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_registrations").fetchone()[0], 1)

    def test_day1_invalid_construct_team_and_duplicate_entries_are_rejected(self) -> None:
        response = self.client.post(
            "/register/day1",
            data=self._day1_form(events=("Construct2Conquer",)),
            follow_redirects=True,
        )
        self.assertIn(b"Member name is required", response.data)
        self.assertEqual(self._fetchone("SELECT COUNT(*) FROM day1_registrations")[0], 0)

        self.client.post("/register/day1", data=self._day1_form(student_id="dup-1"))
        duplicate = self.client.post(
            "/register/day1",
            data=self._day1_form(student_id=" DUP-1 ", events=(DAY1_EVENTS[0],)),
            follow_redirects=True,
        )
        self.assertIn(b"already registered", duplicate.data)
        self.assertEqual(self._fetchone("SELECT COUNT(*) FROM day1_registrations")[0], 1)

    def test_construct2conquer_saves_exactly_two_members(self) -> None:
        response = self.client.post(
            "/register/day1",
            data={
                **self._day1_form("C2C-1", ("Construct2Conquer",)),
                "member2_name": "Kiran Das",
                "member2_class": "BCA II",
                "member2_id": "C2C-2",
            },
        )
        self.assertEqual(response.status_code, 302)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT kind FROM day1_registrations").fetchone()[0], "team")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_members").fetchone()[0], 2)

    def test_day2_team_and_every_member_are_saved_transactionally(self) -> None:
        form = self._team_form("Code Comets", "CC")
        form["member_name"].append("CC Three")
        form["member_class"].append("BCA I")
        form["member_id"].append("CC-ID-3")
        response = self.client.post("/register/day2", data=form, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Team registration saved successfully.", response.data)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_teams").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_team_members").fetchone()[0], 3)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_team_events").fetchone()[0], 3)
            team = connection.execute(
                "SELECT team_name, submitter_name FROM day2_teams"
            ).fetchone()
            self.assertEqual(tuple(team), ("Code Comets", "CC One"))
            member_details = connection.execute(
                """SELECT full_name, class_year, college_id FROM day2_team_members
                   ORDER BY member_order"""
            ).fetchall()
            self.assertEqual(
                [tuple(member) for member in member_details],
                [
                    ("CC One", "BCA II", "CC-ID-1"),
                    ("CC Two", "BCA III", "CC-ID-2"),
                    ("CC Three", "BCA I", "CC-ID-3"),
                ],
            )
            selected_events = [
                row["event"] for row in connection.execute(
                    "SELECT event FROM day2_team_events ORDER BY event"
                ).fetchall()
            ]
            self.assertEqual(selected_events, sorted(DAY2_EVENTS))

        self._login_admin()
        dashboard = self.client.get("/admin")
        for expected in (
            b"Code Comets",
            b"Submitted by CC One",
            b"CC Three",
            b"BCA I",
            b"CC-ID-3",
            *(event.encode() for event in DAY2_EVENTS),
        ):
            self.assertIn(expected, dashboard.data)

    def test_day2_event_links_have_matching_event_checkboxes(self) -> None:
        response = self.client.get("/day2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="team_name"', response.data)
        self.assertIn(b'name="submitter_name"', response.data)
        for event in DAY2_EVENTS:
            with self.subTest(event=event):
                self.assertIn(
                    f'name="events" value="{event}" data-event-choice="{event}"'.encode(),
                    response.data,
                )

    def test_day2_database_failure_shows_error_and_does_not_claim_success(self) -> None:
        with closing(self._db()) as connection:
            connection.execute(
                """CREATE TRIGGER reject_day2_registration
                   BEFORE INSERT ON day2_teams
                   BEGIN SELECT RAISE(ABORT, 'simulated database failure'); END"""
            )
            connection.commit()

        response = self.client.post(
            "/register/day2",
            data=self._team_form("Rejected Team", "RJ"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"could not be saved because of a database error", response.data)
        self.assertNotIn(b"Team registration saved successfully.", response.data)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_teams").fetchone()[0], 0)

    def test_day2_rejects_single_member_invalid_submitter_and_duplicate_member(self) -> None:
        response = self.client.post(
            "/register/day2",
            data={
                "team_name": "Solo Team",
                "submitter_name": "Solo",
                "events": [DAY2_EVENTS[0]],
                "member_name": ["Solo"],
                "member_class": ["BCA"],
                "member_id": ["SOLO-1"],
            },
            follow_redirects=True,
        )
        self.assertIn(b"at least two team members", response.data)
        form = self._team_form("Duplicate Members", "DM")
        form["member_id"][1] = form["member_id"][0]
        response = self.client.post("/register/day2", data=form, follow_redirects=True)
        self.assertIn(b"different College ID", response.data)
        self.assertEqual(self._fetchone("SELECT COUNT(*) FROM day2_teams")[0], 0)

    def test_admin_login_correct_password_and_wrong_password(self) -> None:
        wrong = self.client.post("/admin/login", data={"password": "wrong"}, follow_redirects=True)
        self.assertIn(b"password is incorrect", wrong.data)
        self.assertEqual(wrong.status_code, 200)
        with self.client.session_transaction() as session:
            self.assertNotIn("admin_authenticated", session)
        correct = self.client.post("/admin/login", data={"password": "a-very-long-test-password"})
        self.assertEqual(correct.status_code, 302)
        self.assertTrue(correct.headers["Location"].endswith("/admin"))

    def test_login_is_rate_limited(self) -> None:
        for _ in range(5):
            self.client.post("/admin/login", data={"password": "incorrect"})
        limited = self.client.post("/admin/login", data={"password": "incorrect"})
        self.assertEqual(limited.status_code, 429)
        self.assertIn(b"Too many unsuccessful attempts", limited.data)

    def test_unauthenticated_users_cannot_view_admin_or_change_scores(self) -> None:
        self.assertEqual(self.client.get("/admin").status_code, 302)
        self.assertEqual(self.client.post("/admin/results/publish").status_code, 401)
        self.assertEqual(self.client.get("/admin/export/day1.csv").status_code, 302)

    def test_admin_can_add_edit_delete_and_export_registration(self) -> None:
        self._login_admin()
        add = self.client.post(
            "/admin/day1/add",
            data=self._day1_form("ADMIN-1", (DAY1_EVENTS[0], DAY1_EVENTS[2])),
        )
        self.assertEqual(add.status_code, 302)
        with closing(self._db()) as connection:
            row = connection.execute("SELECT id FROM day1_registrations").fetchone()
            registration_id = row["id"]
        self.client.post(f"/admin/scores/day1/{registration_id}/0", data={"score": "8"})
        self.client.post(f"/admin/scores/day1/{registration_id}/2", data={"score": "6"})
        edit = self.client.post(
            f"/admin/day1/{registration_id}/edit",
            data={
                "participant_name": "Asha Updated",
                "participant_class": "BCA III",
                "participant_id": "ADMIN-1",
                "events": [DAY1_EVENTS[2]],
            },
        )
        self.assertEqual(edit.status_code, 302)
        with closing(self._db()) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM day1_scores WHERE registration_id = ?",
                    (registration_id,),
                ).fetchone()[0],
                0,
            )
        exported = self.client.get("/admin/export/day1.csv")
        self.assertIn(b"Asha Updated", exported.data)
        self.assertIn(b"ADMIN-1", exported.data)
        deleted = self.client.post(f"/admin/day1/{registration_id}/delete")
        self.assertEqual(deleted.status_code, 302)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_registrations").fetchone()[0], 0)

    def test_admin_can_add_edit_and_delete_day2_team(self) -> None:
        self._login_admin()
        form_page = self.client.get("/admin")
        self.assertEqual(form_page.status_code, 200)
        self.assertIn(b'action="/admin/day2/add"', form_page.data)
        self.assertIn(b'name="team_name"', form_page.data)
        self.assertIn(b'name="submitter_name"', form_page.data)
        add = self.client.post(
            "/admin/day2/add",
            data=self._team_form("Test Team", "TT"),
            follow_redirects=True,
        )
        self.assertEqual(add.status_code, 200)
        self.assertIn(b"Day 2 team added. Reference:", add.data)
        for expected in (
            b"Test Team",
            b"TT One",
            b"BCA II",
            b"TT-ID-1",
            b"TT Two",
            b"BCA III",
            b"TT-ID-2",
            *(event.encode() for event in DAY2_EVENTS),
        ):
            self.assertIn(expected, add.data)
        with closing(self._db()) as connection:
            team_id = connection.execute("SELECT id FROM day2_teams").fetchone()["id"]
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM day2_team_members WHERE team_id = ?", (team_id,)
                ).fetchone()[0],
                2,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM day2_team_events WHERE team_id = ?", (team_id,)
                ).fetchone()[0],
                len(DAY2_EVENTS),
            )
        form = self._team_form("Updated Team", "TT")
        edit = self.client.post(f"/admin/day2/{team_id}/edit", data=form)
        self.assertEqual(edit.status_code, 302)
        self.assertIn(b"Updated Team", self.client.get("/admin/export/day2.csv").data)
        deleted = self.client.post(f"/admin/day2/{team_id}/delete")
        self.assertEqual(deleted.status_code, 302)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_teams").fetchone()[0], 0)

    def test_admin_day2_database_error_is_logged_and_reported(self) -> None:
        self._login_admin()
        with (
            patch(
                "app._save_day2_team",
                side_effect=sqlite3.IntegrityError(
                    "NOT NULL constraint failed: day2_registrations.team_name"
                ),
            ),
            self.assertLogs("app", level="ERROR") as captured,
        ):
            response = self.client.post(
                "/admin/day2/add",
                data=self._team_form("Database Error Team", "DE"),
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NOT NULL constraint failed: day2_registrations.team_name", response.data)
        self.assertNotIn(b"already registered", response.data)
        self.assertTrue(any("SQLite rejected an admin-created Day 2 team" in line for line in captured.output))
        self.assertTrue(any(str(self.database.resolve()) in line for line in captured.output))
        self.assertEqual(self._fetchone("SELECT COUNT(*) FROM day2_teams")[0], 0)

    def test_day2_edits_invalidate_scores_for_changed_members_and_removed_events(self) -> None:
        self._login_admin()
        self.client.post("/admin/day2/add", data=self._team_form("Scored Team", "SC"))
        with closing(self._db()) as connection:
            team_id = connection.execute("SELECT id FROM day2_teams").fetchone()["id"]
        for index in range(len(DAY2_EVENTS)):
            self.client.post(
                f"/admin/scores/day2/{team_id}/{index}",
                data={"round1": "2", "round2": "3"},
            )

        changed_members = self._team_form("Scored Team", "SC2")
        self.client.post(f"/admin/day2/{team_id}/edit", data=changed_members)
        with closing(self._db()) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM day2_scores WHERE team_id = ?", (team_id,)
                ).fetchone()[0],
                0,
            )

        for index in range(len(DAY2_EVENTS)):
            self.client.post(
                f"/admin/scores/day2/{team_id}/{index}",
                data={"round1": "4", "round2": "5"},
            )
        retained_event_form = self._team_form(
            "Scored Team", "SC2", events=(DAY2_EVENTS[0],)
        )
        self.client.post(f"/admin/day2/{team_id}/edit", data=retained_event_form)
        with closing(self._db()) as connection:
            scores = connection.execute(
                "SELECT event FROM day2_scores WHERE team_id = ?", (team_id,)
            ).fetchall()
            self.assertEqual([row["event"] for row in scores], [DAY2_EVENTS[0]])

    def test_scores_validate_non_negative_complete_rounds_and_allow_correction(self) -> None:
        self._login_admin()
        self.client.post("/register/day1", data=self._day1_form("SCORE-D1", (DAY1_EVENTS[0],)))
        self.client.post("/register/day2", data=self._team_form("Scoring Team", "ST"))
        with closing(self._db()) as connection:
            registration_id = connection.execute("SELECT id FROM day1_registrations").fetchone()["id"]
            team_id = connection.execute("SELECT id FROM day2_teams").fetchone()["id"]
        invalid = self.client.post(
            f"/admin/scores/day1/{registration_id}/0", data={"score": "-1"}, follow_redirects=True
        )
        self.assertIn(b"non-negative", invalid.data)
        partial = self.client.post(
            f"/admin/scores/day2/{team_id}/0", data={"round1": "2", "round2": ""}
        )
        self.assertEqual(partial.status_code, 302)
        with closing(self._db()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day2_scores").fetchone()[0], 0)
        saved = self.client.post(
            f"/admin/scores/day2/{team_id}/0", data={"round1": "2.5", "round2": "3"}
        )
        self.assertEqual(saved.status_code, 302)
        corrected = self.client.post(
            f"/admin/scores/day2/{team_id}/0", data={"round1": "4", "round2": "5"}
        )
        self.assertEqual(corrected.status_code, 302)
        with closing(self._db()) as connection:
            score = connection.execute(
                "SELECT round1, round2 FROM day2_scores WHERE team_id = ? AND event = ?",
                (team_id, DAY2_EVENTS[0]),
            ).fetchone()
            self.assertEqual(tuple(score), (4.0, 5.0))

    def test_results_require_complete_scores_tie_and_exclude_day1_from_championship(self) -> None:
        self._login_admin()
        self.client.post("/register/day1", data=self._day1_form("CHAMP-D1", (DAY1_EVENTS[0],)))
        for team_name, prefix in (("Tie Alpha", "TA"), ("Tie Beta", "TB")):
            self.client.post("/register/day2", data=self._team_form(team_name, prefix))
        with closing(self._db()) as connection:
            day1_id = connection.execute("SELECT id FROM day1_registrations").fetchone()["id"]
            teams = connection.execute("SELECT id FROM day2_teams ORDER BY id").fetchall()
        for team in teams:
            for event_index, _event in enumerate(DAY2_EVENTS):
                self.client.post(
                    f"/admin/scores/day2/{team['id']}/{event_index}",
                    data={"round1": "5", "round2": "5"},
                )
        incomplete = self.client.post("/admin/results/publish", follow_redirects=True)
        self.assertIn(b"WebCraft Challenge has 1 entrant(s) without scores", incomplete.data)
        self.client.post(f"/admin/scores/day1/{day1_id}/0", data={"score": "900"})
        self.client.post("/admin/results/publish")
        public = self.client.get("/results")
        self.assertIn(b"Tie Alpha", public.data)
        self.assertIn(b"Tie Beta", public.data)
        self.assertIn(b"Overall DIGIFIESTA Champion", public.data)
        self.assertNotIn(b"CHAMP-D1", public.data)
        self.assertIn(b"10 pts", public.data)
        with closing(self._db()) as connection:
            snapshot = json.loads(connection.execute(
                "SELECT value FROM app_state WHERE key = 'published_results'"
            ).fetchone()["value"])
        self.assertEqual(snapshot["championship"]["standings"][0]["place"], 1)
        self.assertEqual(snapshot["championship"]["standings"][1]["place"], 1)
        self.assertEqual(snapshot["championship"]["standings"][0]["score"], 30.0)

    def test_admin_preview_hides_incomplete_championship_standings(self) -> None:
        self._login_admin()
        self.client.post("/register/day2", data=self._team_form("Incomplete Team", "INC"))
        with closing(self._db()) as connection:
            team_id = connection.execute("SELECT id FROM day2_teams").fetchone()["id"]
        self.client.post(
            f"/admin/scores/day2/{team_id}/0",
            data={"round1": "3", "round2": "4"},
        )
        dashboard = self.client.get("/admin")
        self.assertIn(b"No team is registered for all three Day 2 events with complete scores.", dashboard.data)

    def test_admin_sees_full_ranking_but_public_results_show_only_top_three(self) -> None:
        self._login_admin()
        registration_ids = []
        for index in range(4):
            form = self._day1_form(f"RANK-{index}")
            form["participant_name"] = f"Entrant {index + 1}"
            self.client.post("/register/day1", data=form)
            registration_ids.append(index + 1)
        for registration_id in registration_ids:
            self.client.post(
                f"/admin/scores/day1/{registration_id}/0",
                data={"score": str(10 - registration_id)},
            )
        dashboard = self.client.get("/admin")
        self.assertIn(b"#4 Entrant 4", dashboard.data)
        self.assertEqual(self.client.post("/admin/results/publish").status_code, 302)
        public = self.client.get("/results")
        self.assertNotIn(b"Entrant 4", public.data)
        self.assertIn(b"Entrant 3", public.data)

    def test_public_results_hide_private_data_until_published_and_can_be_unpublished(self) -> None:
        self.client.post("/register/day1", data=self._day1_form("PRIVATE-COLLEGE-ID"))
        response = self.client.get("/results")
        self.assertIn(b"Results have not been published yet.", response.data)
        self.assertNotIn(b"PRIVATE-COLLEGE-ID", response.data)
        self._login_admin()
        self.client.post("/admin/scores/day1/1/0", data={"score": "1"})
        self.assertEqual(self.client.post("/admin/results/publish").status_code, 302)
        public = self.client.get("/results")
        self.assertNotIn(b"PRIVATE-COLLEGE-ID", public.data)
        self.client.post("/admin/results/unpublish")
        self.assertIn(b"Results have not been published yet.", self.client.get("/results").data)

    def test_csrf_rejects_state_change_without_a_valid_token(self) -> None:
        csrf_app = create_app({
            "TESTING": True,
            "SECRET_KEY": "csrf-test-secret",
            "DATABASE": str(self.root / "csrf.db"),
            "ADMIN_CONFIG": str(self.admin_config),
            "WTF_CSRF_ENABLED": True,
        })
        response = csrf_app.test_client().post("/register/day1", data=self._day1_form())
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"could not be verified", response.data)
        with closing(sqlite3.connect(self.root / "csrf.db")) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM day1_registrations").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
