from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Job

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    notified INTEGER NOT NULL DEFAULT 0
)
"""


class Storage:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(SCHEMA)

    def is_seen(self, job: Job) -> bool:
        return self.db.execute("SELECT 1 FROM jobs WHERE id = ?", (job.id,)).fetchone() is not None

    def save(self, job: Job, notified: bool) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO jobs (id, source, title, url, first_seen, notified) VALUES (?,?,?,?,?,?)",
            (job.id, job.source, job.title, job.url, datetime.now(timezone.utc).isoformat(), int(notified)),
        )
        self.db.commit()

    def close(self) -> None:
        self.db.close()
