"""
database.py

SQLite database connection helper for the
Face Recognition Attendance System.
"""

import sqlite3
from pathlib import Path


# ==================================================
# DATABASE PATH
# ==================================================

DATABASE_FOLDER = Path("database")
DATABASE_PATH = DATABASE_FOLDER / "attendance.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection() -> sqlite3.Connection:
    """
    Return a new SQLite database connection.
    """
    DATABASE_FOLDER.mkdir(exist_ok=True)
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


# ==================================================
# INITIALISE DATABASE
# ==================================================

def initialize_database():
    """
    Create all required tables if they do not
    already exist.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # ATTENDANCE TABLE
    # --------------------------------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            date    TEXT    NOT NULL,
            time    TEXT    NOT NULL
        )
        """
    )

    # --------------------------------------------------
    # ADMIN TABLE
    # --------------------------------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        )
        """
    )

    # --------------------------------------------------
    # SETTINGS TABLE
    # --------------------------------------------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    # --------------------------------------------------
    # DEFAULT SETTINGS
    # --------------------------------------------------
    default_settings = [
        ("recognition_threshold", "0.45"),
        ("confirmation_frames",   "5"),
        ("camera_index",          "0"),
        ("theme",                 "dark"),
        ("registration_images",   "5"),
    ]

    for key, value in default_settings:
        cursor.execute(
            """
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

    connection.commit()
    connection.close()


# ==================================================
# SETTINGS HELPERS
# ==================================================

def get_setting(key: str, default=None):
    """Return a single setting value by key."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,)
    )
    row = cursor.fetchone()
    connection.close()
    if row:
        return row["value"]
    return default


def set_setting(key: str, value: str):
    """Upsert a setting value."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, str(value))
    )
    connection.commit()
    connection.close()
