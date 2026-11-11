from __future__ import annotations

import html
import os

import requests

from .models import Job
from .textutil import format_date_ro


def format_message(job: Job, matches: list[str], technologies: list[str]) -> str:
    e = html.escape
    header = " · ".join(p for p in (job.company, job.location) if p)
    lines = [f"<b>{e(job.title)}</b>", e(header), ""]
    if job.department:
        lines.append(f"• Departament: {e(job.department)}")
    if technologies:
        lines.append(f"• Tehnologii: {e(', '.join(technologies))}")
    if job.published:
        lines.append(f"• Publicat: {format_date_ro(job.published)}")
    lines.append("")
    if matches:
        lines.append(f"Potrivire: {e(', '.join(matches))}")
    lines.append(f'<a href="{e(job.url, quote=True)}">Link către anunțul original</a>')
    return "\n".join(lines)


def send_telegram(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=20,
    )
    resp.raise_for_status()
