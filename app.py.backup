from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import secrets
import sqlite3
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFError, CSRFProtect, generate_csrf
from werkzeug.security import check_password_hash, generate_password_hash

from database import close_db, get_db, init_db, rows_as_dicts

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
ADMIN_EMAIL = "banupriyamani96@gmail.com"
DAY1_EVENTS = (
    "WebCraft Challenge",
    "Construct2Conquer",
    "Jigsaw Jam",
    "Logo Rang",
)
DAY2_EVENTS = ("Prompt Battle", "Meme Battle", "Password Challenge")
DAY2_ROUNDS = {
    "Prompt Battle": ("AI Image Generation", "Movie Poster"),
    "Meme Battle": ("Theme-Based Meme", "Picture Meme"),
    "Password Challenge": ("Dataset-Based Password Challenge", "Family Tree Logic"),
}
EVENT_DETAILS = {
    "WebCraft Challenge": {
        "day": 1,
        "description": "Design and build a website that turns an idea into a polished digital experience.",
        "rules": "Create your own work during the event. Judges evaluate creativity, usability, and technical execution.",
    },
    "Construct2Conquer": {
        "day": 1,
        "description": "A two-person jigsaw and puzzle-solving challenge built around logic, teamwork, and speed.",
        "rules": "Register exactly two members as one team. Both members must participate together.",
    },
    "Jigsaw Jam": {
        "day": 1,
        "description": "A jigsaw puzzle competition rewarding focus, patience, and pattern recognition.",
        "rules": "Complete the assigned puzzle during the event. Follow the organizer's time and material instructions.",
    },
    "Logo Rang": {
        "day": 1,
        "description": "A creative logo and rangoli challenge blending artistic flair with visual storytelling.",
        "rules": "Create an original design that follows the theme announced by the organizer.",
    },
    "Prompt Battle": {
        "day": 2,
        "description": "A team creativity challenge with AI Image Generation and Movie Poster rounds.",
        "rules": "Teams complete both rounds. Each round is scored separately; the event total is their sum.",
    },
    "Meme Battle": {
        "day": 2,
        "description": "A team competition in Theme-Based Meme and Picture Meme creation.",
        "rules": "Teams complete both rounds. Keep content original, respectful, and suitable for college.",
    },
    "Password Challenge": {
        "day": 2,
        "description": "A team reasoning contest with Dataset-Based Password Challenge and Family Tree Logic rounds.",
        "rules": "Teams complete both rounds. Each round is scored separately; the event total is their sum.",
    },
}
MAX_LOGIN_FAILURES = 5
LOGIN_WINDOW_SECONDS = 15 * 60


def _read_or_create_secret(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    value = secrets.token_urlsafe(48)
    path.write_text(value, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return value


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    load_dotenv(BASE_DIR / ".env")
    app = Flask(__name__, instance_path=str(INSTANCE_DIR), instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    supplied_secret = (test_config or {}).get("SECRET_KEY")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or supplied_secret or _read_or_create_secret(
            Path(app.instance_path) / "session_secret"
        ),
        DATABASE=os.environ.get("DIGIFIESTA_DATABASE")
        or str(Path(app.instance_path) / "digifiesta.db"),
        ADMIN_CONFIG=os.environ.get("DIGIFIESTA_ADMIN_CONFIG")
        or str(Path(app.instance_path) / "admin.json"),
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=3600,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=8 * 60 * 60,
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "").lower()
        in ("1", "true", "yes"),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    csrf = CSRFProtect()
    csrf.init_app(app)
    app.teardown_appcontext(close_db)
    init_db(app.config["DATABASE"])

    @app.template_filter("score_number")
    def score_number(value: float) -> str:
        return f"{value:g}"

    app.jinja_env.globals.update(
        day1_events=DAY1_EVENTS,
        day2_events=DAY2_EVENTS,
        event_details=EVENT_DETAILS,
        day2_rounds=DAY2_ROUNDS,
        csrf_token=generate_csrf,
    )

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/day1")
    def day1_page() -> str:
        return render_template("day1.html")

    @app.post("/register/day1")
    def register_day1() -> Response:
        try:
            events = _selected_events(request.form.getlist("events"), DAY1_EVENTS)
            first = _member(
                request.form.get("participant_name"),
                request.form.get("participant_class"),
                request.form.get("participant_id"),
            )
            is_team = "Construct2Conquer" in events
            members = [first]
            if is_team:
                members.append(
                    _member(
                        request.form.get("member2_name"),
                        request.form.get("member2_class"),
                        request.form.get("member2_id"),
                    )
                )
            _assert_unique_member_ids(members)
            reference = _save_day1_registration(get_db(), members, events, is_team)
        except (ValueError, sqlite3.IntegrityError) as error:
            flash(str(error) or "That registration could not be saved.", "error")
            return redirect(url_for("day1_page") + "#registration")
        flash(f"Registration saved successfully. Your reference is {reference}.", "success")
        return redirect(url_for("day1_page") + "#registration")

    @app.get("/day2")
    def day2_page() -> str:
        return render_template("day2.html")

    @app.post("/register/day2")
    def register_day2() -> Response:
        try:
            events = _selected_events(request.form.getlist("events"), DAY2_EVENTS)
            names = request.form.getlist("member_name")
            classes = request.form.getlist("member_class")
            college_ids = request.form.getlist("member_id")
            if not names or len(names) != len(classes) or len(names) != len(college_ids):
                raise ValueError("Enter complete details for every team member.")
            members = [
                _member(name, class_year, college_id)
                for name, class_year, college_id in zip(names, classes, college_ids)
            ]
            if len(members) < 2:
                raise ValueError("Day 2 registration requires at least two team members.")
            _assert_unique_member_ids(members)
            team_name = _clean_text(request.form.get("team_name"), "Team name", 120)
            submitter = _clean_text(request.form.get("submitter_name"), "Submitting member", 120)
            if not any(member["name"].casefold() == submitter.casefold() for member in members):
                raise ValueError("The submitting member must be included in the team member list.")
            reference = _save_day2_team(get_db(), team_name, submitter, members, events)
        except ValueError as error:
            current_app.logger.warning("Day 2 participant registration rejected: %s", error)
            flash(str(error), "error")
            return redirect(url_for("day2_page") + "#registration")
        except sqlite3.Error:
            current_app.logger.exception(
                "Failed to save a Day 2 registration (database=%s).",
                Path(current_app.config["DATABASE"]).expanduser().resolve(),
            )
            flash(
                "The Day 2 registration could not be saved because of a database error. "
                "Please try again; if it continues, contact the organizer.",
                "error",
            )
            return redirect(url_for("day2_page") + "#registration")
        flash(f"Team registration saved successfully. Your reference is {reference}.", "success")
        return redirect(url_for("day2_page") + "#registration")

    @app.get("/results")
    def results() -> str:
        state = _get_state(get_db(), "published_results")
        snapshot = json.loads(state["value"]) if state and state["value"] else None
        published_state = _get_state(get_db(), "results_published")
        is_published = bool(published_state and published_state["value"] == "1" and snapshot)
        return render_template("results.html", published=is_published, results=snapshot)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login() -> str | Response:
        if session.get("admin_authenticated") is True:
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            connection = get_db()
            ip_hash = _ip_hash(request.remote_addr or "unknown")
            now = int(time.time())
            connection.execute(
                "DELETE FROM admin_login_failures WHERE failed_at < ?",
                (now - LOGIN_WINDOW_SECONDS,),
            )
            failures = connection.execute(
                "SELECT COUNT(*) FROM admin_login_failures WHERE ip_hash = ? AND failed_at >= ?",
                (ip_hash, now - LOGIN_WINDOW_SECONDS),
            ).fetchone()[0]
            if failures >= MAX_LOGIN_FAILURES:
                flash("Too many unsuccessful attempts. Wait 15 minutes before trying again.", "error")
                return render_template("admin-login.html"), 429

            admin_config = _load_admin_config(app.config["ADMIN_CONFIG"])
            password = request.form.get("password", "")
            if not admin_config:
                flash(
                    "Admin access is not configured on this computer. Run `python app.py setup-admin` in PowerShell.",
                    "error",
                )
            elif check_password_hash(admin_config.get("password_hash", ""), password):
                connection.execute("DELETE FROM admin_login_failures WHERE ip_hash = ?", (ip_hash,))
                connection.commit()
                session.clear()
                session["admin_authenticated"] = True
                session["admin_email"] = ADMIN_EMAIL
                session.permanent = True
                return redirect(url_for("admin_dashboard"))
            else:
                connection.execute(
                    "INSERT INTO admin_login_failures (ip_hash, failed_at) VALUES (?, ?)",
                    (ip_hash, now),
                )
                connection.commit()
                flash("The administrator password is incorrect.", "error")
        return render_template("admin-login.html")

    @app.post("/admin/logout")
    @admin_required
    def admin_logout() -> Response:
        session.clear()
        flash("You have been signed out.", "success")
        return redirect(url_for("admin_login"))

    @app.get("/admin")
    @admin_required
    def admin_dashboard() -> str:
        connection = get_db()
        day1 = _load_day1_registrations(connection)
        day2 = _load_day2_teams(connection)
        search = request.args.get("q", "").strip().casefold()
        if search:
            day1 = [
                record for record in day1
                if search in " ".join([
                    record["registration_ref"], record["kind"], *record["events"],
                    *[
                        " ".join((member["full_name"], member["class_year"], member["college_id"]))
                        for member in record["members"]
                    ],
                ]).casefold()
            ]
            day2 = [
                record for record in day2
                if search in " ".join([
                    record["registration_ref"], record["team_name"], record["submitter_name"],
                    *record["events"],
                    *[
                        " ".join((member["full_name"], member["class_year"], member["college_id"]))
                        for member in record["members"]
                    ],
                ]).casefold()
            ]
        day1_score_rows = _load_day1_score_rows(connection)
        day2_score_rows = _load_day2_score_rows(connection)
        preview = _calculate_results(connection)
        published_state = _get_state(connection, "results_published")
        published = bool(published_state and published_state["value"] == "1")
        return render_template(
            "admin.html",
            day1=day1,
            day2=day2,
            day1_score_rows=day1_score_rows,
            day2_score_rows=day2_score_rows,
            preview=preview,
            published=published,
            search=request.args.get("q", "").strip(),
        )

    @app.post("/admin/day1/add")
    @admin_required
    def admin_add_day1() -> Response:
        try:
            events = _selected_events(request.form.getlist("events"), DAY1_EVENTS)
            first = _member(
                request.form.get("participant_name"),
                request.form.get("participant_class"),
                request.form.get("participant_id"),
            )
            members = [first]
            is_team = "Construct2Conquer" in events
            if is_team:
                members.append(
                    _member(
                        request.form.get("member2_name"),
                        request.form.get("member2_class"),
                        request.form.get("member2_id"),
                    )
                )
            _assert_unique_member_ids(members)
            reference = _save_day1_registration(get_db(), members, events, is_team)
            flash(f"Day 1 registration added. Reference: {reference}.", "success")
        except (ValueError, sqlite3.IntegrityError) as error:
            flash(str(error) or "Could not add that registration.", "error")
        return redirect(url_for("admin_dashboard") + "#day1")

    @app.post("/admin/day1/<int:registration_id>/edit")
    @admin_required
    def admin_edit_day1(registration_id: int) -> Response:
        connection = get_db()
        if not connection.execute(
            "SELECT 1 FROM day1_registrations WHERE id = ?", (registration_id,)
        ).fetchone():
            abort(404)
        try:
            events = _selected_events(request.form.getlist("events"), DAY1_EVENTS)
            first = _member(
                request.form.get("participant_name"),
                request.form.get("participant_class"),
                request.form.get("participant_id"),
            )
            members = [first]
            is_team = "Construct2Conquer" in events
            if is_team:
                members.append(
                    _member(
                        request.form.get("member2_name"),
                        request.form.get("member2_class"),
                        request.form.get("member2_id"),
                    )
                )
            _assert_unique_member_ids(members)
            _check_day1_duplicates(connection, members, events, exclude_id=registration_id)
            old_members = connection.execute(
                """SELECT full_name, class_year, normalized_id FROM day1_members
                   WHERE registration_id = ? ORDER BY member_order""",
                (registration_id,),
            ).fetchall()
            new_members = [
                (member["name"], member["class_year"], member["normalized_id"])
                for member in members
            ]
            if [tuple(member) for member in old_members] != new_members:
                connection.execute(
                    "DELETE FROM day1_scores WHERE registration_id = ?",
                    (registration_id,),
                )
            placeholders = ",".join("?" for _ in events)
            connection.execute(
                f"DELETE FROM day1_scores WHERE registration_id = ? AND event NOT IN ({placeholders})",
                (registration_id, *events),
            )
            connection.execute(
                "UPDATE day1_registrations SET kind = ? WHERE id = ?",
                ("team" if is_team else "individual", registration_id),
            )
            connection.execute("DELETE FROM day1_members WHERE registration_id = ?", (registration_id,))
            connection.execute("DELETE FROM day1_registration_events WHERE registration_id = ?", (registration_id,))
            _insert_day1_members(connection, registration_id, members)
            _insert_events(connection, "day1_registration_events", "registration_id", registration_id, events)
            connection.commit()
            flash("Day 1 registration updated.", "success")
        except (ValueError, sqlite3.IntegrityError) as error:
            connection.rollback()
            flash(str(error) or "Could not update that registration.", "error")
        return redirect(url_for("admin_dashboard") + "#day1")

    @app.post("/admin/day1/<int:registration_id>/delete")
    @admin_required
    def admin_delete_day1(registration_id: int) -> Response:
        cursor = get_db().execute(
            "DELETE FROM day1_registrations WHERE id = ?", (registration_id,)
        )
        get_db().commit()
        if cursor.rowcount == 0:
            abort(404)
        flash("Day 1 registration deleted.", "success")
        return redirect(url_for("admin_dashboard") + "#day1")

    @app.post("/admin/day2/add")
    @admin_required
    def admin_add_day2() -> Response:
        connection: sqlite3.Connection | None = None
        try:
            team_name, submitter, members, events = _team_from_form(DAY2_EVENTS)
            connection = get_db()
            reference = _save_day2_team(connection, team_name, submitter, members, events)
            flash(f"Day 2 team added. Reference: {reference}.", "success")
        except ValueError as error:
            current_app.logger.warning("Admin-created Day 2 team rejected: %s", error)
            flash(_team_error(error), "error")
        except sqlite3.IntegrityError as error:
            if connection is not None:
                connection.rollback()
            current_app.logger.exception(
                "SQLite rejected an admin-created Day 2 team (database=%s).",
                Path(current_app.config["DATABASE"]).expanduser().resolve(),
            )
            flash(_team_error(error), "error")
        except sqlite3.Error:
            if connection is not None:
                connection.rollback()
            current_app.logger.exception(
                "Failed to save an admin-created Day 2 team (database=%s).",
                Path(current_app.config["DATABASE"]).expanduser().resolve(),
            )
            flash(
                "The Day 2 team could not be saved because of a database error. "
                "Please try again; if it continues, contact the organizer.",
                "error",
            )
        return redirect(url_for("admin_dashboard") + "#day2")

    @app.post("/admin/day2/<int:team_id>/edit")
    @admin_required
    def admin_edit_day2(team_id: int) -> Response:
        connection = get_db()
        if not connection.execute("SELECT 1 FROM day2_teams WHERE id = ?", (team_id,)).fetchone():
            abort(404)
        try:
            team_name, submitter, members, events = _team_from_form(DAY2_EVENTS)
            _check_day2_duplicates(connection, members, events, exclude_id=team_id)
            old_members = connection.execute(
                """SELECT full_name, class_year, normalized_id FROM day2_team_members
                   WHERE team_id = ? ORDER BY member_order""",
                (team_id,),
            ).fetchall()
            new_members = [
                (member["name"], member["class_year"], member["normalized_id"])
                for member in members
            ]
            if [tuple(member) for member in old_members] != new_members:
                connection.execute("DELETE FROM day2_scores WHERE team_id = ?", (team_id,))
            placeholders = ",".join("?" for _ in events)
            connection.execute(
                f"DELETE FROM day2_scores WHERE team_id = ? AND event NOT IN ({placeholders})",
                (team_id, *events),
            )
            connection.execute(
                "UPDATE day2_teams SET team_name = ?, normalized_name = ?, submitter_name = ? WHERE id = ?",
                (team_name, team_name.casefold(), submitter, team_id),
            )
            connection.execute("DELETE FROM day2_team_members WHERE team_id = ?", (team_id,))
            connection.execute("DELETE FROM day2_team_events WHERE team_id = ?", (team_id,))
            _insert_day2_members(connection, team_id, members)
            _insert_events(connection, "day2_team_events", "team_id", team_id, events)
            connection.commit()
            flash("Day 2 team updated.", "success")
        except (ValueError, sqlite3.IntegrityError) as error:
            connection.rollback()
            flash(_team_error(error), "error")
        return redirect(url_for("admin_dashboard") + "#day2")

    @app.post("/admin/day2/<int:team_id>/delete")
    @admin_required
    def admin_delete_day2(team_id: int) -> Response:
        cursor = get_db().execute("DELETE FROM day2_teams WHERE id = ?", (team_id,))
        get_db().commit()
        if cursor.rowcount == 0:
            abort(404)
        flash("Day 2 team deleted.", "success")
        return redirect(url_for("admin_dashboard") + "#day2")

    @app.get("/admin/export/<kind>.csv")
    @admin_required
    def export_csv(kind: str) -> Response:
        connection = get_db()
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        if kind == "day1":
            writer.writerow(["Registration reference", "Name", "Class/year", "College ID", "Events", "Registered at"])
            for registration in _load_day1_registrations(connection):
                for member in registration["members"]:
                    writer.writerow([
                        _csv_safe(registration["registration_ref"]), _csv_safe(member["full_name"]),
                        _csv_safe(member["class_year"]), _csv_safe(member["college_id"]),
                        ", ".join(_csv_safe(event) for event in registration["events"]),
                        registration["created_at"],
                    ])
        elif kind == "day2":
            writer.writerow(["Registration reference", "Team", "Submitting member", "Member", "Class/year", "College ID", "Events", "Registered at"])
            for team in _load_day2_teams(connection):
                for member in team["members"]:
                    writer.writerow([
                        _csv_safe(team["registration_ref"]), _csv_safe(team["team_name"]),
                        _csv_safe(team["submitter_name"]), _csv_safe(member["full_name"]),
                        _csv_safe(member["class_year"]), _csv_safe(member["college_id"]),
                        ", ".join(_csv_safe(event) for event in team["events"]),
                        team["created_at"],
                    ])
        else:
            abort(404)
        return Response(
            "\ufeff" + output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=digifiesta-{kind}-registrations.csv"},
        )

    @app.post("/admin/scores/day1/<int:registration_id>/<int:event_index>")
    @admin_required
    def save_day1_score(registration_id: int, event_index: int) -> Response:
        if event_index < 0 or event_index >= len(DAY1_EVENTS):
            abort(404)
        event = DAY1_EVENTS[event_index]
        connection = get_db()
        if not connection.execute(
            "SELECT 1 FROM day1_registration_events WHERE registration_id = ? AND event = ?",
            (registration_id, event),
        ).fetchone():
            abort(404)
        raw_score = request.form.get("score", "").strip()
        if not raw_score:
            connection.execute(
                "DELETE FROM day1_scores WHERE registration_id = ? AND event = ?",
                (registration_id, event),
            )
            connection.commit()
            flash("Day 1 score cleared; this entry is no longer ranked.", "success")
        else:
            try:
                score = _score(raw_score, "Score")
            except ValueError as error:
                flash(str(error), "error")
                return redirect(url_for("admin_dashboard") + "#scores")
            connection.execute(
                """INSERT INTO day1_scores (registration_id, event, score, updated_at)
                   VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                   ON CONFLICT(registration_id, event) DO UPDATE SET
                     score = excluded.score, updated_at = excluded.updated_at""",
                (registration_id, event, score),
            )
            connection.commit()
            flash(f"{event} score saved.", "success")
        return redirect(url_for("admin_dashboard") + "#scores")

    @app.post("/admin/scores/day2/<int:team_id>/<int:event_index>")
    @admin_required
    def save_day2_score(team_id: int, event_index: int) -> Response:
        if event_index < 0 or event_index >= len(DAY2_EVENTS):
            abort(404)
        event = DAY2_EVENTS[event_index]
        connection = get_db()
        if not connection.execute(
            "SELECT 1 FROM day2_team_events WHERE team_id = ? AND event = ?", (team_id, event)
        ).fetchone():
            abort(404)
        round1_raw = request.form.get("round1", "").strip()
        round2_raw = request.form.get("round2", "").strip()
        if not round1_raw and not round2_raw:
            connection.execute("DELETE FROM day2_scores WHERE team_id = ? AND event = ?", (team_id, event))
            connection.commit()
            flash(f"{event} scores cleared; the team is no longer ranked for it.", "success")
            return redirect(url_for("admin_dashboard") + "#scores")
        if not round1_raw or not round2_raw:
            flash("Enter both round scores, or clear both fields to remove the score.", "error")
            return redirect(url_for("admin_dashboard") + "#scores")
        try:
            round1 = _score(round1_raw, "Round 1 score")
            round2 = _score(round2_raw, "Round 2 score")
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("admin_dashboard") + "#scores")
        connection.execute(
            """INSERT INTO day2_scores (team_id, event, round1, round2, updated_at)
               VALUES (?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
               ON CONFLICT(team_id, event) DO UPDATE SET
                 round1 = excluded.round1, round2 = excluded.round2, updated_at = excluded.updated_at""",
            (team_id, event, round1, round2),
        )
        connection.commit()
        flash(f"{event} round scores saved. Total: {round1 + round2:g}.", "success")
        return redirect(url_for("admin_dashboard") + "#scores")

    @app.post("/admin/results/publish")
    @admin_required
    def publish_results() -> Response:
        connection = get_db()
        calculated = _calculate_results(connection)
        if not calculated["ready"]:
            flash("Results cannot be published yet: " + "; ".join(calculated["issues"]), "error")
            return redirect(url_for("admin_dashboard") + "#results")
        snapshot = {
            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "day1": calculated["day1"],
            "day2": calculated["day2"],
            "championship": calculated["championship"],
        }
        _set_state(connection, "published_results", json.dumps(snapshot, ensure_ascii=False))
        _set_state(connection, "results_published", "1")
        connection.commit()
        flash("Calculated results are now published publicly.", "success")
        return redirect(url_for("admin_dashboard") + "#results")

    @app.post("/admin/results/unpublish")
    @admin_required
    def unpublish_results() -> Response:
        connection = get_db()
        _set_state(connection, "results_published", "0")
        connection.commit()
        flash("Public results have been unpublished.", "success")
        return redirect(url_for("admin_dashboard") + "#results")

    @app.errorhandler(CSRFError)
    def csrf_error(_error: CSRFError) -> tuple[str, int]:
        return render_template(
            "error.html",
            title="Form expired",
            message="This form could not be verified. Reload the page and submit it again.",
        ), 400

    @app.errorhandler(404)
    def not_found(_error: Any) -> tuple[str, int]:
        return render_template("error.html", title="Page not found", message="That page or record does not exist."), 404

    @app.errorhandler(413)
    def request_too_large(_error: Any) -> tuple[str, int]:
        return render_template("error.html", title="Form too large", message="The submitted form is too large. Remove unnecessary fields and try again."), 413

    return app


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if session.get("admin_authenticated") is not True or session.get("admin_email") != ADMIN_EMAIL:
            if request.method == "GET":
                flash("Sign in with the configured administrator account to continue.", "error")
                return redirect(url_for("admin_login", next=request.path))
            abort(401)
        return view(*args, **kwargs)
    return wrapped


def _clean_text(value: str | None, label: str, maximum: int = 160) -> str:
    text = " ".join((value or "").split())
    if not text:
        raise ValueError(f"{label} is required.")
    if len(text) > maximum:
        raise ValueError(f"{label} must be {maximum} characters or fewer.")
    return text


def _member(name: str | None, class_year: str | None, college_id: str | None) -> dict[str, str]:
    full_name = _clean_text(name, "Member name", 120)
    class_value = _clean_text(class_year, "Class/year", 80)
    student_id = _clean_text(college_id, "College ID/UUCMS ID", 80)
    normalized = "".join(student_id.casefold().split())
    return {
        "name": full_name,
        "class_year": class_value,
        "college_id": student_id,
        "normalized_id": normalized,
    }


def _assert_unique_member_ids(members: list[dict[str, str]]) -> None:
    if len({member["normalized_id"] for member in members}) != len(members):
        raise ValueError("Each team member must have a different College ID/UUCMS ID.")


def _selected_events(values: list[str], allowed: tuple[str, ...]) -> list[str]:
    selected = list(dict.fromkeys(values))
    if not selected:
        raise ValueError("Select at least one event.")
    if any(event not in allowed for event in selected):
        raise ValueError("The form included an invalid event.")
    return selected


def _insert_day1_members(
    connection: sqlite3.Connection, registration_id: int, members: list[dict[str, str]]
) -> None:
    connection.executemany(
        """INSERT INTO day1_members
           (registration_id, full_name, class_year, college_id, normalized_id, member_order)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (
                registration_id, item["name"], item["class_year"], item["college_id"],
                item["normalized_id"], index,
            )
            for index, item in enumerate(members)
        ],
    )


def _insert_day2_members(
    connection: sqlite3.Connection, team_id: int, members: list[dict[str, str]]
) -> None:
    connection.executemany(
        """INSERT INTO day2_team_members
           (team_id, full_name, class_year, college_id, normalized_id, member_order)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (
                team_id, item["name"], item["class_year"], item["college_id"],
                item["normalized_id"], index,
            )
            for index, item in enumerate(members)
        ],
    )


def _insert_events(
    connection: sqlite3.Connection,
    table: str,
    owner_column: str,
    owner_id: int,
    events: list[str],
) -> None:
    if (table, owner_column) not in (
        ("day1_registration_events", "registration_id"),
        ("day2_team_events", "team_id"),
    ):
        raise ValueError("Invalid event selection table.")
    connection.executemany(
        f"INSERT INTO {table} ({owner_column}, event) VALUES (?, ?)",
        [(owner_id, event) for event in events],
    )


def _check_day1_duplicates(
    connection: sqlite3.Connection,
    members: list[dict[str, str]],
    events: list[str],
    exclude_id: int | None = None,
) -> None:
    for member in members:
        for event in events:
            parameters: list[Any] = [member["normalized_id"], event]
            exclusion = ""
            if exclude_id is not None:
                exclusion = " AND r.id != ?"
                parameters.append(exclude_id)
            existing = connection.execute(
                """SELECT 1 FROM day1_members m
                   JOIN day1_registrations r ON r.id = m.registration_id
                   JOIN day1_registration_events e ON e.registration_id = r.id
                   WHERE m.normalized_id = ? AND e.event = ?""" + exclusion + " LIMIT 1",
                parameters,
            ).fetchone()
            if existing:
                raise ValueError(f"That College ID/UUCMS ID is already registered for {event}.")


def _save_day1_registration(
    connection: sqlite3.Connection,
    members: list[dict[str, str]],
    events: list[str],
    is_team: bool,
) -> str:
    _assert_unique_member_ids(members)
    if is_team != (len(members) == 2):
        raise ValueError("Construct2Conquer registrations must contain exactly two team members.")
    if not is_team and len(members) != 1:
        raise ValueError("Individual event registrations require one participant.")
    try:
        connection.execute("BEGIN IMMEDIATE")
        _check_day1_duplicates(connection, members, events)
        reference = "D1-" + secrets.token_hex(5).upper()
        cursor = connection.execute(
            "INSERT INTO day1_registrations (registration_ref, kind) VALUES (?, ?)",
            (reference, "team" if is_team else "individual"),
        )
        registration_id = int(cursor.lastrowid)
        _insert_day1_members(connection, registration_id, members)
        _insert_events(connection, "day1_registration_events", "registration_id", registration_id, events)
        connection.commit()
        return reference
    except Exception:
        connection.rollback()
        raise


def _team_from_form(
    allowed_events: tuple[str, ...],
) -> tuple[str, str, list[dict[str, str]], list[str]]:
    events = _selected_events(request.form.getlist("events"), allowed_events)
    names = request.form.getlist("member_name")
    classes = request.form.getlist("member_class")
    ids = request.form.getlist("member_id")
    if not names or len(names) != len(classes) or len(names) != len(ids):
        raise ValueError("Enter complete details for every team member.")
    members = [_member(name, class_year, college_id) for name, class_year, college_id in zip(names, classes, ids)]
    if len(members) < 2:
        raise ValueError("Day 2 registration requires at least two team members.")
    _assert_unique_member_ids(members)
    team_name = _clean_text(request.form.get("team_name"), "Team name", 120)
    submitter = _clean_text(request.form.get("submitter_name"), "Submitting member", 120)
    if not any(member["name"].casefold() == submitter.casefold() for member in members):
        raise ValueError("The submitting member must be included in the team member list.")
    return team_name, submitter, members, events


def _check_day2_duplicates(
    connection: sqlite3.Connection,
    members: list[dict[str, str]],
    events: list[str],
    exclude_id: int | None = None,
) -> None:
    for member in members:
        for event in events:
            parameters: list[Any] = [member["normalized_id"], event]
            exclusion = ""
            if exclude_id is not None:
                exclusion = " AND t.id != ?"
                parameters.append(exclude_id)
            existing = connection.execute(
                """SELECT 1 FROM day2_team_members m
                   JOIN day2_teams t ON t.id = m.team_id
                   JOIN day2_team_events e ON e.team_id = t.id
                   WHERE m.normalized_id = ? AND e.event = ?""" + exclusion + " LIMIT 1",
                parameters,
            ).fetchone()
            if existing:
                raise ValueError(f"That College ID/UUCMS ID is already registered for {event}.")


def _save_day2_team(
    connection: sqlite3.Connection,
    team_name: str,
    submitter: str,
    members: list[dict[str, str]],
    events: list[str],
) -> str:
    _assert_unique_member_ids(members)
    if len(members) < 2:
        raise ValueError("Day 2 registration requires at least two team members.")
    if not any(member["name"].casefold() == submitter.casefold() for member in members):
        raise ValueError("The submitting member must be included in the team member list.")
    try:
        connection.execute("BEGIN IMMEDIATE")
        _check_day2_duplicates(connection, members, events)
        reference = "D2-" + secrets.token_hex(5).upper()
        cursor = connection.execute(
            """INSERT INTO day2_teams
               (team_name, normalized_name, submitter_name, registration_ref)
               VALUES (?, ?, ?, ?)""",
            (team_name, team_name.casefold(), submitter, reference),
        )
        team_id = int(cursor.lastrowid)
        _insert_day2_members(connection, team_id, members)
        _insert_events(connection, "day2_team_events", "team_id", team_id, events)
        connection.commit()
        return reference
    except Exception:
        connection.rollback()
        raise


def _load_day1_registrations(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    registrations = rows_as_dicts(
        connection.execute("SELECT * FROM day1_registrations ORDER BY created_at DESC, id DESC").fetchall()
    )
    for registration in registrations:
        registration["members"] = rows_as_dicts(
            connection.execute(
                "SELECT * FROM day1_members WHERE registration_id = ? ORDER BY member_order",
                (registration["id"],),
            ).fetchall()
        )
        registration["events"] = [
            row["event"] for row in connection.execute(
                "SELECT event FROM day1_registration_events WHERE registration_id = ? ORDER BY event",
                (registration["id"],),
            ).fetchall()
        ]
    return registrations


def _load_day2_teams(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    teams = rows_as_dicts(connection.execute("SELECT * FROM day2_teams ORDER BY created_at DESC, id DESC").fetchall())
    for team in teams:
        team["members"] = rows_as_dicts(
            connection.execute(
                "SELECT * FROM day2_team_members WHERE team_id = ? ORDER BY member_order",
                (team["id"],),
            ).fetchall()
        )
        team["events"] = [
            row["event"] for row in connection.execute(
                "SELECT event FROM day2_team_events WHERE team_id = ? ORDER BY event",
                (team["id"],),
            ).fetchall()
        ]
    return teams


def _load_day1_score_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """SELECT r.id AS registration_id, r.registration_ref, r.kind, e.event, s.score,
                  GROUP_CONCAT(m.full_name, ' / ') AS participant_name
           FROM day1_registration_events e
           JOIN day1_registrations r ON r.id = e.registration_id
           JOIN day1_members m ON m.registration_id = r.id
           LEFT JOIN day1_scores s ON s.registration_id = r.id AND s.event = e.event
           GROUP BY r.id, e.event ORDER BY e.event, participant_name"""
    ).fetchall()
    return rows_as_dicts(rows)


def _load_day2_score_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    return rows_as_dicts(
        connection.execute(
            """SELECT t.id AS team_id, t.team_name, t.registration_ref, e.event,
                      s.round1, s.round2
               FROM day2_team_events e
               JOIN day2_teams t ON t.id = e.team_id
               LEFT JOIN day2_scores s ON s.team_id = t.id AND s.event = e.event
               ORDER BY e.event, t.team_name"""
        ).fetchall()
    )


def _rank(entrants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(entrants, key=lambda item: (-item["score"], item["name"].casefold()))
    previous_score: float | None = None
    place = 0
    for index, entrant in enumerate(ordered, start=1):
        if previous_score is None or entrant["score"] != previous_score:
            place = index
            previous_score = entrant["score"]
        entrant["place"] = place
    return ordered


def _calculate_results(connection: sqlite3.Connection) -> dict[str, Any]:
    issues: list[str] = []
    day1_results: list[dict[str, Any]] = []
    day2_results: list[dict[str, Any]] = []
    for event in DAY1_EVENTS:
        entrants = connection.execute(
            """SELECT r.id, r.registration_ref, GROUP_CONCAT(m.full_name, ' / ') AS name, s.score
               FROM day1_registration_events e
               JOIN day1_registrations r ON r.id = e.registration_id
               JOIN day1_members m ON m.registration_id = r.id
               LEFT JOIN day1_scores s ON s.registration_id = r.id AND s.event = e.event
               WHERE e.event = ? GROUP BY r.id ORDER BY name""",
            (event,),
        ).fetchall()
        incomplete = [row for row in entrants if row["score"] is None]
        if incomplete:
            issues.append(f"{event} has {len(incomplete)} entrant(s) without scores")
        day1_results.append({
            "event": event,
            "complete": not incomplete,
            "entrant_count": len(entrants),
            "standings": _rank([
                {"name": row["name"], "score": float(row["score"])}
                for row in entrants if row["score"] is not None
            ]) if entrants and not incomplete else [],
        })

    complete_teams: list[dict[str, Any]] = []
    for event in DAY2_EVENTS:
        entrants = connection.execute(
            """SELECT t.id, t.team_name, s.round1, s.round2
               FROM day2_team_events e
               JOIN day2_teams t ON t.id = e.team_id
               LEFT JOIN day2_scores s ON s.team_id = t.id AND s.event = e.event
               WHERE e.event = ? ORDER BY t.team_name""",
            (event,),
        ).fetchall()
        incomplete = [
            row for row in entrants
            if row["round1"] is None or row["round2"] is None
        ]
        if incomplete:
            issues.append(f"{event} has {len(incomplete)} team(s) without both round scores")
        day2_results.append({
            "event": event,
            "rounds": list(DAY2_ROUNDS[event]),
            "complete": not incomplete,
            "entrant_count": len(entrants),
            "standings": _rank([
                {
                    "name": row["team_name"],
                    "score": float(row["round1"]) + float(row["round2"]),
                }
                for row in entrants
                if row["round1"] is not None and row["round2"] is not None
            ]) if entrants and not incomplete else [],
        })

    eligible = connection.execute(
        """SELECT t.id, t.team_name
           FROM day2_teams t
           WHERE (SELECT COUNT(DISTINCT event) FROM day2_team_events e WHERE e.team_id = t.id) = ?
           AND NOT EXISTS (
             SELECT 1 FROM day2_team_events e
             LEFT JOIN day2_scores s ON s.team_id = e.team_id AND s.event = e.event
             WHERE e.team_id = t.id AND e.event IN (?, ?, ?)
               AND (s.round1 IS NULL OR s.round2 IS NULL)
           )
           ORDER BY t.team_name""",
        (len(DAY2_EVENTS), *DAY2_EVENTS),
    ).fetchall()
    eligible_without_scores = connection.execute(
        """SELECT COUNT(*) FROM day2_teams t
           WHERE (SELECT COUNT(DISTINCT event) FROM day2_team_events e WHERE e.team_id = t.id) = ?
           AND EXISTS (
             SELECT 1 FROM day2_team_events e
             LEFT JOIN day2_scores s ON s.team_id = e.team_id AND s.event = e.event
             WHERE e.team_id = t.id AND e.event IN (?, ?, ?)
               AND (s.round1 IS NULL OR s.round2 IS NULL)
           )""",
        (len(DAY2_EVENTS), *DAY2_EVENTS),
    ).fetchone()[0]
    if eligible_without_scores:
        issues.append(f"{eligible_without_scores} championship-eligible team(s) have incomplete event scores")
    for team in eligible:
        totals = connection.execute(
            "SELECT SUM(round1 + round2) FROM day2_scores WHERE team_id = ? AND event IN (?, ?, ?)",
            (team["id"], *DAY2_EVENTS),
        ).fetchone()[0]
        complete_teams.append({"name": team["team_name"], "score": float(totals)})
    championship = {
        "event": "Overall Day 2 Championship",
        "note": "Only the three Day 2 event totals are included. Day 1 scores are excluded.",
        "entrant_count": len(complete_teams),
        "standings": _rank(complete_teams) if not eligible_without_scores else [],
        "complete": eligible_without_scores == 0,
    }
    return {
        "ready": not issues,
        "issues": issues,
        "day1": day1_results,
        "day2": day2_results,
        "championship": championship,
    }


def _get_state(connection: sqlite3.Connection, key: str) -> dict[str, str] | None:
    row = connection.execute("SELECT key, value FROM app_state WHERE key = ?", (key,)).fetchone()
    return dict(row) if row else None


def _set_state(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT INTO app_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def _score(raw: str, label: str) -> float:
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(f"{label} must be a non-negative number.") from error
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be a non-negative number.")
    return value


def _load_admin_config(path: str | Path) -> dict[str, str] | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("email") != ADMIN_EMAIL or not data.get("password_hash"):
        return None
    return data


def _ip_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _csv_safe(value: str) -> str:
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "-", "@")) else text


def _team_error(error: Exception) -> str:
    if isinstance(error, sqlite3.IntegrityError) and "UNIQUE constraint failed" in str(error):
        return "That team name or member/event combination is already registered."
    if isinstance(error, sqlite3.IntegrityError):
        return f"The database rejected that team registration: {error}"
    return str(error) or "Could not save that team."


def set_admin_password(config_path: str | Path) -> None:
    print(f"Configure the local admin password for {ADMIN_EMAIL}.")
    password = __import__("getpass").getpass("New admin password (minimum 12 characters): ")
    confirmation = __import__("getpass").getpass("Confirm admin password: ")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")
    if password != confirmation:
        raise SystemExit("Passwords did not match. No changes were made.")
    target = Path(config_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({"email": ADMIN_EMAIL, "password_hash": generate_password_hash(password)}, indent=2),
        encoding="utf-8",
    )
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    temporary.replace(target)
    print(f"Password hash saved to the private instance folder for {ADMIN_EMAIL}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DIGIFIESTA 2026 locally.")
    parser.add_argument("command", nargs="?", choices=("run", "setup-admin", "init-db"), default="run")
    args = parser.parse_args()
    if args.command == "setup-admin":
        set_admin_password(app.config["ADMIN_CONFIG"])
    elif args.command == "init-db":
        init_db(app.config["DATABASE"])
        print(f"Database is ready at {app.config['DATABASE']}. Existing records were retained.")
    else:
        print(f"Using SQLite database at {Path(app.config['DATABASE']).expanduser().resolve()}.")
        app.run(
            host=os.environ.get("FLASK_HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes"),
        )


app = create_app()

if __name__ == "__main__":
    main()
