"""
core/database.py

Low-level connection + schema only. Nobody outside this module should call
sqlite3.connect() directly — go through get_connection().
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wisely.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    class_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- class_number lives here, not on subjects: the same subject (e.g. Алгебра)
-- can have topics in different grades.
CREATE TABLE IF NOT EXISTS topics (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id   INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    class_number INTEGER NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT,
    order_index  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id    INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    question    TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'text',      -- 'text' | 'number' | 'choice'
    kind        TEXT NOT NULL DEFAULT 'practice',  -- 'practice' | 'diagnostic'
    answer      TEXT NOT NULL,
    difficulty  INTEGER NOT NULL DEFAULT 1,         -- 1..3
    explanation TEXT,                                -- short one-line hint on wrong answer
    solution_steps TEXT NOT NULL DEFAULT '[]',       -- JSON array of strings: full step-by-step
                                                      -- solution for the "Правильное решение" screen
    order_index INTEGER NOT NULL DEFAULT 0
);

-- Every attempt a student makes. Source of truth; `progress` is a cached
-- aggregate over this, recomputed by core/progress.py.
CREATE TABLE IF NOT EXISTS attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id      INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    answer_given TEXT,
    correct      INTEGER NOT NULL,               -- 0/1
    score        INTEGER NOT NULL DEFAULT 0,      -- 0..100
    mistake_type TEXT,                            -- 'calculation'|'formula'|'concept'|'formatting'|NULL
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS progress (
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id   INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    score      INTEGER NOT NULL DEFAULT 0,
    completed  INTEGER NOT NULL DEFAULT 0,
    mistakes   INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_tasks_topic ON tasks(topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user_task ON attempts(user_id, task_id);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Creates tables if they don't exist. Safe to call every startup."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


def reset_db() -> None:
    """Wipes the db file and recreates schema. Dev-only convenience."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
