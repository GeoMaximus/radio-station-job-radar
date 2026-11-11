from __future__ import annotations

from .models import Job
from .textutil import contains_term, norm


def location_ok(job: Job, allowed: list[str]) -> bool:
    loc = norm(job.location)
    return bool(loc) and any(norm(a) in loc for a in allowed)


def job_type_ok(job: Job, cfg: dict) -> bool:
    """Reject explicit non-full-time; accept unknown type (most postings are full-time)."""
    text = norm(f"{job.job_type} {job.title}")
    if any(norm(t) in text for t in cfg["exclude"]):
        return False
    declared = norm(job.job_type)
    if declared:
        return any(norm(t) in declared for t in cfg["accept"])
    return True


def match_interests(job: Job, interests: dict[str, list[str]]) -> list[str]:
    """Categories whose keywords appear in title or department."""
    text = f"{job.title} {job.department}"
    return [
        category
        for category, keywords in interests.items()
        if any(contains_term(text, k) for k in keywords)
    ]


def extract_technologies(job: Job, technologies: list[str]) -> list[str]:
    text = f"{job.title} {job.description}"
    return [t for t in technologies if contains_term(text, t)]
