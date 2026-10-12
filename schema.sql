PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS day1_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_ref TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('individual', 'team')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS day1_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL REFERENCES day1_registrations(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    class_year TEXT NOT NULL,
    college_id TEXT NOT NULL,
    normalized_id TEXT NOT NULL,
    member_order INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_day1_members_normalized_id ON day1_members(normalized_id);

CREATE TABLE IF NOT EXISTS day1_registration_events (
    registration_id INTEGER NOT NULL REFERENCES day1_registrations(id) ON DELETE CASCADE,
    event TEXT NOT NULL CHECK (event IN (
        'WebCraft Challenge', 'Construct2Conquer', 'Jigsaw Jam', 'Logo Rang'
    )),
    PRIMARY KEY (registration_id, event)
);

CREATE TABLE IF NOT EXISTS day2_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE,
    submitter_name TEXT NOT NULL,
    registration_ref TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS day2_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL REFERENCES day2_teams(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    class_year TEXT NOT NULL,
    college_id TEXT NOT NULL,
    normalized_id TEXT NOT NULL,
    member_order INTEGER NOT NULL,
    UNIQUE (team_id, normalized_id)
);
CREATE INDEX IF NOT EXISTS idx_day2_members_normalized_id ON day2_team_members(normalized_id);

CREATE TABLE IF NOT EXISTS day2_team_events (
    team_id INTEGER NOT NULL REFERENCES day2_teams(id) ON DELETE CASCADE,
    event TEXT NOT NULL CHECK (event IN ('Prompt Battle', 'Meme Battle', 'Password Challenge')),
    PRIMARY KEY (team_id, event)
);

CREATE TABLE IF NOT EXISTS day1_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL REFERENCES day1_registrations(id) ON DELETE CASCADE,
    event TEXT NOT NULL CHECK (event IN (
        'WebCraft Challenge', 'Construct2Conquer', 'Jigsaw Jam', 'Logo Rang'
    )),
    score REAL NOT NULL CHECK (score >= 0),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (registration_id, event)
);

CREATE TABLE IF NOT EXISTS day2_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL REFERENCES day2_teams(id) ON DELETE CASCADE,
    event TEXT NOT NULL CHECK (event IN ('Prompt Battle', 'Meme Battle', 'Password Challenge')),
    round1 REAL CHECK (round1 IS NULL OR round1 >= 0),
    round2 REAL CHECK (round2 IS NULL OR round2 >= 0),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (team_id, event),
    CHECK (round1 IS NOT NULL OR round2 IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_login_failures (
    ip_hash TEXT NOT NULL,
    failed_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_admin_login_failures_ip_time ON admin_login_failures(ip_hash, failed_at);
