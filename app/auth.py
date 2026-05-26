"""
auth.py
SQLite database setup and authentication helpers.
Handles user registration, login, and saving / loading analysis history.
"""

import sqlite3
import hashlib
import json
import os

# ── Database file path ────────────────────────────────────────────────────────
# Stored in the project's data/ folder.
# os.path.dirname(__file__) points to app/, so we go up one level.
DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'tiktok_intelligence.db'
)


def _conn():
    """Return an open SQLite connection with dict-style row access."""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    """
    Create the users and analyses tables if they do not already exist.
    Called once at app start-up.
    """
    conn = _conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password      TEXT    NOT NULL,
            tiktok_handle TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id              INTEGER NOT NULL,
            analysis_date        TEXT    DEFAULT (datetime('now')),
            total_comments       INTEGER,
            positive_pct         REAL,
            negative_pct         REAL,
            neutral_pct          REAL,
            top_keywords         TEXT,
            content_health_score TEXT,
            account_niche        TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)
    conn.commit()
    conn.close()


def _hash(password: str) -> str:
    """One-way SHA-256 hash of a password string."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, tiktok_handle: str) -> tuple:
    """
    Register a new user.
    Returns (True, success_message) or (False, error_message).
    """
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password, tiktok_handle) VALUES (?, ?, ?)",
            (username.strip(), _hash(password), tiktok_handle.strip())
        )
        conn.commit()
        return True, "Account created! You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username is already taken — please choose another."
    finally:
        conn.close()


def login_user(username: str, password: str):
    """
    Check credentials.
    Returns a user dict on success, or None if credentials are wrong.
    """
    conn = _conn()
    row  = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username.strip(), _hash(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def save_analysis(user_id: int, summary: dict, keywords: list,
                  health_score: str, niche: str):
    """
    Persist one analysis result for a logged-in user.
    keywords is a list of (word, score) tuples — only the words are stored.
    """
    conn = _conn()
    conn.execute(
        """INSERT INTO analyses
           (user_id, total_comments, positive_pct, negative_pct, neutral_pct,
            top_keywords, content_health_score, account_niche)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            summary.get('total', 0),
            summary.get('positive', 0.0),
            summary.get('negative', 0.0),
            summary.get('neutral', 0.0),
            json.dumps([kw[0] for kw in keywords[:10]]),
            health_score,
            niche,
        )
    )
    conn.commit()
    conn.close()


def get_user_analyses(user_id: int) -> list:
    """Return all past analyses for a user, oldest first."""
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY analysis_date ASC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
