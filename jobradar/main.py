from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

from .fetch import fetch
from .filters import extract_technologies, job_type_ok, location_ok, match_interests
from .notify import format_message, send_telegram
from .parsers import parse_listing
from .storage import Storage

log = logging.getLogger("jobradar")


def process_source(key: str, source: dict, cfg: dict, storage: Storage, dry_run: bool, html: str | None = None) -> int:
    html = html if html is not None else fetch(source)
    jobs = parse_listing(html, key, source)
    if not jobs:
        log.warning("[%s] 0 jobs parsed - selectors may be outdated", key)
        return 0

    sent = 0
    for job in jobs:
        if storage.is_seen(job):
            continue
        ok = location_ok(job, cfg["locations"]) and job_type_ok(job, cfg["job_type"])
        matches = match_interests(job, cfg["interests"]) if ok else []
        relevant = ok and (matches or not cfg["interests"])
        if relevant:
            text = format_message(job, matches, extract_technologies(job, cfg["technologies"]))
            if dry_run:
                print(text, "\n" + "-" * 40)
            else:
                send_telegram(text)
            sent += 1
        # Irrelevant jobs are stored too, so they are not re-evaluated every run.
        # In dry-run nothing is stored, so you can iterate on selectors/filters.
        if not dry_run:
            storage.save(job, notified=bool(relevant))
    log.info("[%s] %d listings, %d notifications", key, len(jobs), sent)
    return sent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Monitor radio careers pages")
    ap.add_argument("--config", default="config/config.yaml")
    ap.add_argument("--dry-run", action="store_true", help="print messages, do not send or store")
    ap.add_argument("--html-file", help="parse this local file instead of fetching (use with --only)")
    ap.add_argument("--only", help="run a single source key")
    args = ap.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")  # Romanian diacritics on Windows consoles
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    storage = Storage(cfg.get("database", "data/jobs.db"))

    failures = attempted = 0
    for key, source in cfg["sources"].items():
        if args.only and key != args.only:
            continue
        if not args.only and not source.get("enabled", True):
            continue
        attempted += 1
        try:
            html = Path(args.html_file).read_text(encoding="utf-8") if args.html_file else None
            process_source(key, source, cfg, storage, args.dry_run, html)
        except Exception:
            failures += 1
            log.exception("[%s] failed", key)
    storage.close()

    if attempted and failures == attempted:
        return 1  # everything failed: make the GitHub Actions run red
    return 0


if __name__ == "__main__":
    sys.exit(main())
