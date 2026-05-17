"""SQLite database layer with secure queries and legacy migration."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "students.db"
_db_mtime: float | None = None
LEGACY_DB_PATH = Path(__file__).resolve().parent.parent / "somedata.db"

STUDENT_COLUMNS = (
    "student_id",
    "first_name",
    "last_name",
    "gender",
    "course",
    "branch",
    "mail",
    "contact",
    "state",
    "address",
    "areapincode",
)


def get_db_mtime() -> float:
    """Last modified time of the database file (for external-edit detection)."""
    if not DB_PATH.exists():
        return 0.0
    return DB_PATH.stat().st_mtime


def database_changed_since(last_mtime: float | None) -> bool:
    """True when the DB file was modified after last_mtime."""
    current = get_db_mtime()
    if last_mtime is None:
        return False
    return current != last_mtime


def get_connection() -> sqlite3.Connection:
    """Fresh connection per operation — reads always see latest committed data."""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                course TEXT NOT NULL,
                branch TEXT NOT NULL,
                mail TEXT NOT NULL,
                contact TEXT NOT NULL,
                state TEXT NOT NULL,
                address TEXT NOT NULL,
                areapincode TEXT NOT NULL
            )
            """
        )
        conn.commit()
    _migrate_legacy_data()
    global _db_mtime
    _db_mtime = get_db_mtime()


def touch_database() -> None:
    """Call after writes so sync helpers can detect in-app changes."""
    global _db_mtime
    _db_mtime = get_db_mtime()


def _migrate_legacy_data() -> None:
    """Import records from legacy somedata.db / cloud table if present."""
    if not LEGACY_DB_PATH.exists():
        return

    with sqlite3.connect(LEGACY_DB_PATH) as legacy_conn:
        legacy_conn.row_factory = sqlite3.Row
        try:
            rows = legacy_conn.execute("SELECT * FROM cloud").fetchall()
        except sqlite3.OperationalError:
            return

    if not rows:
        return

    with get_connection() as conn:
        for row in rows:
            conn.execute(
                """
                INSERT OR IGNORE INTO students (
                    student_id, first_name, last_name, gender, course,
                    branch, mail, contact, state, address, areapincode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    str(row[7]),
                    row[8],
                    row[9],
                    row[10],
                ),
            )
        conn.commit()
