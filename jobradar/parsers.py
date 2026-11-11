from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .models import Job
from .textutil import parse_date


def _extract(node: Tag, spec: str | None) -> str:
    """spec is a CSS selector, optionally 'selector@attr' (e.g. 'a@href')."""
    if not spec:
        return ""
    selector, _, attr = spec.partition("@")
    selector = selector.strip()
    target = node if selector in ("", ".") else node.select_one(selector)
    if target is None:
        return ""
    if attr:
        return (target.get(attr.strip()) or "").strip()
    return target.get_text(" ", strip=True)


def parse_listing(html: str, source_key: str, source: dict) -> list[Job]:
    sel = source["selectors"]
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[Job] = []
    for node in soup.select(sel["item"]):
        title = _extract(node, sel.get("title"))
        href = _extract(node, sel.get("link", "a@href"))
        if not title or not href:
            continue
        jobs.append(
            Job(
                source=source_key,
                company=source["company"],
                title=title,
                url=urljoin(source["url"], href),
                location=_extract(node, sel.get("location")) or source.get("default_location", ""),
                department=_extract(node, sel.get("department")),
                job_type=_extract(node, sel.get("job_type")),
                published=parse_date(_extract(node, sel.get("date"))),
                description=_extract(node, sel.get("description")),
            )
        )
    return jobs
