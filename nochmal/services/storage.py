"""SQLite persistence for local lesson attempts and learning events."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProgressStore:
    """Small SQLite repository used by the Streamlit prototype."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    initial_answer TEXT NOT NULL DEFAULT '',
                    final_answer TEXT NOT NULL DEFAULT '',
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attempt_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    item_id TEXT,
                    occurred_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (attempt_id) REFERENCES attempts(id)
                );

                CREATE INDEX IF NOT EXISTS idx_attempts_lesson
                ON attempts(learner_id, lesson_id, started_at DESC);

                CREATE INDEX IF NOT EXISTS idx_events_attempt
                ON events(attempt_id, occurred_at);
                """
            )

    def start_attempt(
        self,
        lesson_id: str,
        initial_answer: str,
        *,
        learner_id: str = "local",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        attempt_id = str(uuid4())
        timestamp = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attempts (
                    id, learner_id, lesson_id, stage, initial_answer, started_at
                ) VALUES (?, ?, ?, 'study', ?, ?)
                """,
                (attempt_id, learner_id, lesson_id, initial_answer, timestamp),
            )
            connection.execute(
                """
                INSERT INTO events (
                    attempt_id, event_type, occurred_at, metadata_json
                ) VALUES (?, 'initial_answer_submitted', ?, ?)
                """,
                (attempt_id, timestamp, json.dumps(metadata or {}, sort_keys=True)),
            )
        return attempt_id

    def set_stage(
        self,
        attempt_id: str,
        stage: str,
        *,
        event_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        timestamp = utc_now()
        with self._connect() as connection:
            connection.execute(
                "UPDATE attempts SET stage = ? WHERE id = ?",
                (stage, attempt_id),
            )
            connection.execute(
                """
                INSERT INTO events (
                    attempt_id, event_type, occurred_at, metadata_json
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    attempt_id,
                    event_type,
                    timestamp,
                    json.dumps(metadata or {}, sort_keys=True),
                ),
            )

    def complete_attempt(
        self,
        attempt_id: str,
        final_answer: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        timestamp = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE attempts
                SET stage = 'complete', final_answer = ?, completed_at = ?
                WHERE id = ?
                """,
                (final_answer, timestamp, attempt_id),
            )
            connection.execute(
                """
                INSERT INTO events (
                    attempt_id, event_type, occurred_at, metadata_json
                ) VALUES (?, 'attempt_completed', ?, ?)
                """,
                (attempt_id, timestamp, json.dumps(metadata or {}, sort_keys=True)),
            )

    def mark_lesson_complete(
        self,
        lesson_id: str,
        *,
        learner_id: str = "local",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Save a completion for the direct-study lesson flow."""
        attempt_id = str(uuid4())
        timestamp = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attempts (
                    id, learner_id, lesson_id, stage, started_at, completed_at
                ) VALUES (?, ?, ?, 'complete', ?, ?)
                """,
                (attempt_id, learner_id, lesson_id, timestamp, timestamp),
            )
            connection.execute(
                """
                INSERT INTO events (
                    attempt_id, event_type, occurred_at, metadata_json
                ) VALUES (?, 'lesson_completed', ?, ?)
                """,
                (attempt_id, timestamp, json.dumps(metadata or {}, sort_keys=True)),
            )
        return attempt_id

    def clear_all_progress(self) -> None:
        """Permanently remove every locally stored attempt and event."""
        with self._connect() as connection:
            connection.execute("DELETE FROM events")
            connection.execute("DELETE FROM attempts")

    def abandon_attempt(self, attempt_id: str) -> None:
        self.set_stage(
            attempt_id,
            "abandoned",
            event_type="attempt_abandoned",
        )

    def latest_incomplete_attempt(
        self,
        lesson_id: str,
        *,
        learner_id: str = "local",
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM attempts
                WHERE learner_id = ? AND lesson_id = ?
                  AND stage IN ('study', 'final')
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (learner_id, lesson_id),
            ).fetchone()
        return dict(row) if row else None

    def recent_attempts(
        self,
        *,
        learner_id: str = "local",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM attempts
                WHERE learner_id = ?
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (learner_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def completed_lesson_ids(
        self,
        *,
        learner_id: str = "local",
    ) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT lesson_id FROM attempts
                WHERE learner_id = ? AND stage = 'complete'
                """,
                (learner_id,),
            ).fetchall()
        return {row["lesson_id"] for row in rows}

    def events_for_attempt(self, attempt_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM events
                WHERE attempt_id = ?
                ORDER BY id
                """,
                (attempt_id,),
            ).fetchall()
        return [dict(row) for row in rows]
