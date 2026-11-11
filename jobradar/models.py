from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date


@dataclass
class Job:
    source: str  # source key from config
    company: str
    title: str
    url: str
    location: str = ""
    department: str = ""
    job_type: str = ""
    published: date | None = None
    description: str = ""

    @property
    def id(self) -> str:
        return hashlib.sha1(f"{self.source}|{self.url}".encode()).hexdigest()[:16]
