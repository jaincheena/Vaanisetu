"""
VaaniSetu — SQLite Database Layer
Creates all 4 tables and seeds impact_config on first run.
"""

import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime

from backend.config import DB_PATH, LANG_CODES, DEFAULT_FARMERS_PER_HOUR, DEFAULT_RATE_PER_MIN


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    username        TEXT PRIMARY KEY,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'user',
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id                   TEXT PRIMARY KEY,
    mode                 TEXT NOT NULL DEFAULT 'translate',
    submitter_id         TEXT,
    filename             TEXT,
    file_hash            TEXT,
    file_size            INTEGER,
    input_type           TEXT,
    source_lang          TEXT,
    target_langs         TEXT,           -- JSON array of lang names
    status               TEXT NOT NULL DEFAULT 'queued',
    confidence_level     TEXT,           -- green / amber / red
    avg_confidence       REAL,
    queued_at            TEXT,
    started_at           TEXT,
    completed_at         TEXT,
    output_path          TEXT,
    error_log            TEXT,
    farmer_context       TEXT,
    distribution_clearance TEXT
);

CREATE TABLE IF NOT EXISTS translation_memory (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source_hash    TEXT UNIQUE NOT NULL,
    source_text    TEXT NOT NULL,
    source_lang    TEXT NOT NULL,
    target_lang    TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    confidence     REAL NOT NULL,
    times_used     INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL,
    last_used_at   TEXT NOT NULL,
    flagged        INTEGER NOT NULL DEFAULT 0,
    domain         TEXT DEFAULT 'agriculture'
);

CREATE TABLE IF NOT EXISTS review_queue (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id),
    segment_index       INTEGER NOT NULL,
    source_text         TEXT NOT NULL,
    translated_text     TEXT NOT NULL,
    source_lang         TEXT NOT NULL,
    target_lang         TEXT NOT NULL,
    confidence          REAL NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    reviewer            TEXT,
    edited_translation  TEXT,
    created_at          TEXT NOT NULL,
    reviewed_at         TEXT
);

CREATE TABLE IF NOT EXISTS impact_config (
    language                TEXT PRIMARY KEY,
    farmers_per_hour        INTEGER NOT NULL DEFAULT 120,
    translation_rate_per_min INTEGER NOT NULL DEFAULT 850,
    updated_at              TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_status        ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_file_hash     ON jobs(file_hash);
CREATE INDEX IF NOT EXISTS idx_tm_source_hash     ON translation_memory(source_hash);
CREATE INDEX IF NOT EXISTS idx_rq_job_id          ON review_queue(job_id);
CREATE INDEX IF NOT EXISTS idx_rq_status          ON review_queue(status);
"""


def init_db() -> None:
    """Create tables and seed impact_config."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.executescript(SCHEMA_SQL)
        _seed_impact_config(conn)
        # Safe column migrations — no-op if column already exists
        _safe_add_column(conn, "jobs", "submitter_id",            "TEXT")
        _safe_add_column(conn, "jobs", "distribution_clearance",  "TEXT")
        _safe_add_column(conn, "jobs", "confidence_level",        "TEXT")
        _safe_add_column(conn, "jobs", "farmer_context",          "TEXT")
        _safe_add_column(conn, "jobs", "quality_mode",            "TEXT DEFAULT 'full'")
        _safe_add_column(conn, "translation_memory", "domain",   "TEXT DEFAULT 'agriculture'")
        conn.commit()
    finally:
        conn.close()


def _safe_add_column(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    """Add a column to an existing table only if it doesn't already exist."""
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except sqlite3.OperationalError:
        pass  # Column already exists — expected for fresh schemas


def _seed_impact_config(conn: sqlite3.Connection) -> None:
    now = datetime.utcnow().isoformat()
    for lang_name in LANG_CODES.keys():
        conn.execute(
            """
            INSERT OR IGNORE INTO impact_config
            (language, farmers_per_hour, translation_rate_per_min, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (lang_name, DEFAULT_FARMERS_PER_HOUR, DEFAULT_RATE_PER_MIN, now),
        )


@contextmanager
def get_db():
    """Context manager yielding a sqlite3 connection with row_factory."""
    # timeout: concurrent jobs and their generation pools all write here
    # (status updates, TM stores, review-queue inserts). WAL lets readers run
    # during a write, but writers still serialize — 30s of patience beats
    # sqlite3's 5s default raising "database is locked" under a full pool.
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to plain dict."""
    return dict(row)


def rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]
