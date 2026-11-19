"""Database layer for flet-pomodoro."""

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Self

from py_flet_pomodoro.models import Session


class Database:
    """SQLite storage for pomodoro sessions."""

    def __init__(self: Self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self: Self) -> None:
        """Create tables if they don't exist."""
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 25,
                completed_minutes INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'planned',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_created
            ON sessions(created_at);
        """
        )
        self.conn.commit()

    def _now(self: Self) -> str:
        return datetime.now().isoformat()

    # --- Sessions ---

    def add_session(self: Self, session: Session) -> int:
        """Insert a session and return its new id."""
        cur = self.conn.execute(
            """
            INSERT INTO sessions (task, duration_minutes, completed_minutes,
                                  status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session.task,
                session.duration_minutes,
                session.completed_minutes,
                session.status,
                session.created_at or self._now(),
            ),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def get_session(self: Self, session_id: int) -> Session | None:
        """Return a session by id, or None if not found."""
        row = self.conn.execute(
            """
            SELECT id, task, duration_minutes, completed_minutes, status, created_at
            FROM sessions WHERE id = ?
            """,
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return Session(
            id=row["id"],
            task=row["task"],
            duration_minutes=row["duration_minutes"],
            completed_minutes=row["completed_minutes"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def get_sessions(self: Self) -> list[Session]:
        """Return all sessions ordered by created_at desc."""
        rows = self.conn.execute(
            """
            SELECT id, task, duration_minutes, completed_minutes, status, created_at
            FROM sessions
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [
            Session(
                id=r["id"],
                task=r["task"],
                duration_minutes=r["duration_minutes"],
                completed_minutes=r["completed_minutes"],
                status=r["status"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def get_sessions_by_date(self: Self, day: str) -> list[Session]:
        """Return sessions for a given day (ISO date)."""
        rows = self.conn.execute(
            """
            SELECT id, task, duration_minutes, completed_minutes, status, created_at
            FROM sessions
            WHERE date(created_at) = ?
            ORDER BY created_at DESC
            """,
            (day,),
        ).fetchall()
        return [
            Session(
                id=r["id"],
                task=r["task"],
                duration_minutes=r["duration_minutes"],
                completed_minutes=r["completed_minutes"],
                status=r["status"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def update_session(self: Self, session: Session) -> bool:
        """Update a session. Returns True if a row was updated."""
        assert session.id is not None
        cur = self.conn.execute(
            """
            UPDATE sessions
            SET task = ?, duration_minutes = ?, completed_minutes = ?, status = ?
            WHERE id = ?
            """,
            (
                session.task,
                session.duration_minutes,
                session.completed_minutes,
                session.status,
                session.id,
            ),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete_session(self: Self, session_id: int) -> bool:
        """Delete a session. Returns True if a row was deleted."""
        cur = self.conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self.conn.commit()
        return cur.rowcount > 0

    # --- Statistics ---

    def total_focus_minutes(self: Self, days: int = 7) -> int:
        """Return total completed focus minutes in the last N days."""
        start_date = (date.today() - timedelta(days=days - 1)).isoformat()
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(completed_minutes), 0) as total
            FROM sessions
            WHERE status = 'completed' AND date(created_at) >= ?
            """,
            (start_date,),
        ).fetchone()
        return int(row["total"])

    def sessions_count(self: Self, days: int = 7) -> int:
        """Return completed sessions count in the last N days."""
        start_date = (date.today() - timedelta(days=days - 1)).isoformat()
        row = self.conn.execute(
            """
            SELECT COUNT(*) as cnt
            FROM sessions
            WHERE status = 'completed' AND date(created_at) >= ?
            """,
            (start_date,),
        ).fetchone()
        return int(row["cnt"])

    def daily_stats(self: Self, days: int = 7) -> list[tuple[str, int]]:
        """Return per-day completed minutes for the last N days."""
        start_date = (date.today() - timedelta(days=days - 1)).isoformat()
        rows = self.conn.execute(
            """
            SELECT date(created_at) as day, SUM(completed_minutes) as total
            FROM sessions
            WHERE status = 'completed' AND date(created_at) >= ?
            GROUP BY date(created_at)
            ORDER BY day
            """,
            (start_date,),
        ).fetchall()
        return [(r["day"], int(r["total"])) for r in rows]

    def close(self: Self) -> None:
        """Close the database connection."""
        self.conn.close()
