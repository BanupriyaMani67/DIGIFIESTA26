# DIGIFIESTA 2026 — MVJ Degree College

A local-first fest website with Flask, SQLite, participant registration, a protected organizer dashboard, manual scoring, automatic rankings, and explicitly published public results.

## What it uses

- HTML templates, CSS, and vanilla JavaScript.
- Python Flask server and SQLite database at `instance/digifiesta.db`.
- Flask sessions, CSRF-protected forms, password hashing, and rate-limited admin login.
- Fixed administrator email: `banupriyamani96@gmail.com`.
- No Firebase, Firestore, cloud database, paid API, participant accounts, announcements, or approval queue.

SQLite lives on the computer that runs Flask. It is persistent across server restarts, but it does not synchronize with another computer and does not make the website publicly available on the internet. Do not put the private database, local admin configuration, or `.env` file in source control or share them.

## Windows PowerShell setup

Open PowerShell and run these commands from the project directory:

```powershell
cd C:\Users\mpriy\Desktop\DIGIFIESTA26
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, allow scripts only for this PowerShell process and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Configure a local Flask session secret. The app generates and keeps a random secret in the ignored `instance\session_secret` file if `FLASK_SECRET_KEY` is not set. If you prefer a `.env` file, copy the example and replace its placeholder:

```powershell
Copy-Item .\.env.example .\.env
notepad .\.env
```

Set the admin password without putting it into a command, `.env`, or source file:

```powershell
python app.py setup-admin
```

Enter a new password twice at the hidden prompts. Use at least 12 characters. The app stores only a salted password hash in the ignored file `instance\admin.json`. To change the local admin password later, run the same setup command again. This is a local password for the standalone Flask site; it is not a Firebase password and does not sync to another machine.

Initialize the database without deleting existing records, then start the site:

```powershell
python app.py init-db
python app.py
```

Open <http://127.0.0.1:5000> in a browser. Stop the server with **Ctrl+C**.

## Registration

- **Day 1:** Open **Day 1**, select one or more events, and enter full name, class/year, and College ID/UUCMS ID. Selecting Construct2Conquer reveals the second member fields; that event requires exactly two members.
- **Day 2:** Open **Day 2**, enter a team name and submitting member, select one or more Day 2 events, and enter all team members. A team needs at least two members. Use **Add team member** to add more. The submitting member must also be in the team member list.
- A successful form submission is written to SQLite and displays a unique registration reference. Duplicate member/event entries are rejected. There are no participant accounts, email addresses, phone numbers, or approval steps.

Day 1 event list: WebCraft Challenge, Construct2Conquer, Jigsaw Jam, and Logo Rang.

Day 2 event rounds:

- Prompt Battle: AI Image Generation + Movie Poster.
- Meme Battle: Theme-Based Meme + Picture Meme.
- Password Challenge: Dataset-Based Password Challenge + Family Tree Logic.

## Organizer workflow

1. Open **Admin** in the site navigation and sign in with `banupriyamani96@gmail.com` and the local password configured above.
2. Search registration data by name, event, class/year, ID, or reference. Expand a registration/team to edit it, or use the add/delete controls. Changing registered members clears that entrant's old scores; removing an event clears only that event's score. CSV downloads are restricted to the signed-in admin.
3. In **Scores**, enter non-negative Day 1 scores or both Day 2 round scores. A missing score stays missing; it is never treated as zero. Clearing a Day 1 score or both Day 2 fields removes the saved score.
4. Review the full calculated rankings. An event with any registered entrant/team missing required scores is not ranked and blocks publishing. Tied scores remain tied.
5. Select **Review and publish results** to save a snapshot for the public Results page. Later score or registration edits do not change the already-published snapshot; review and publish again to update it. **Unpublish results** hides the snapshot.

Day 1 events are ranked independently. An overall championship entrant must be registered for all three Day 2 events and have both round scores for each. The championship adds only those three Day 2 totals; it never includes Day 1 scores. Equal totals share a place; the application does not invent tie-breaks.

The public Results page shows only the published snapshot, displays the top three places, and never returns registration IDs or member details. Before the first publication, it says “Results have not been published yet.”

## Database and backup

The database is created automatically and kept at `instance\digifiesta.db`. Running `python app.py init-db` is safe: it creates any missing tables and does not reset existing data.

Make a backup while the server is stopped:

```powershell
Copy-Item .\instance\digifiesta.db "$env:USERPROFILE\Desktop\digifiesta-backup-$(Get-Date -Format yyyyMMdd-HHmmss).db"
```

Keep backups private because registrations contain student names and College IDs. The SQLite file belongs to this local application; copying the source code alone does not copy the database.

## Tests

With the virtual environment active:

```powershell
python -m unittest discover -s tests -p "test_app.py" -v
```

The tests use temporary databases and do not edit the live event database. They cover page rendering, registration, team members, database persistence, admin authentication/rate limiting, authorization, CSRF, registration management, score validation/correction and invalidation after edits, full admin versus top-three public rankings, incomplete championship visibility, ties, Day 2 championship totals, Day 1 exclusion, and public-result privacy.

## Project layout

```text
app.py
database.py
schema.sql
requirements.txt
.env.example
instance/                 local database and private admin/session configuration
templates/                Flask-rendered pages
static/css/style.css
static/js/                progressive enhancement for forms and navigation
tests/test_app.py
```

`instance/`, `.env`, virtual environments, Python caches, and local credentials are ignored by `.gitignore`. Do not run this local Flask/SQLite setup as a public production service: a single local SQLite file is intended for local use and does not provide multi-host synchronization or managed hosting.
