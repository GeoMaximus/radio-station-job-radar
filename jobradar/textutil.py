from __future__ import annotations

import re
import unicodedata
from datetime import date

RO_MONTHS = [
    "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
    "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie",
]


def norm(text: str) -> str:
    """Lowercase and strip diacritics (ș/ş/ț/ţ/ă/â/î) for robust matching."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_term(haystack: str, term: str) -> bool:
    """Whole-word match on normalized text; handles terms like 'c#' or 'c++'."""
    pattern = r"(?<![\w+#])" + re.escape(norm(term)) + r"(?![\w+#])"
    return re.search(pattern, norm(haystack)) is not None


_NUMERIC = re.compile(r"(\d{1,4})[./-](\d{1,2})[./-](\d{1,4})")
_TEXTUAL = re.compile(r"(\d{1,2})\s+([a-z]+)\.?\s+(\d{4})")


def parse_date(text: str) -> date | None:
    """Parse ISO (2026-11-11), 11.11.2026 or '11 noiembrie 2026'."""
    t = norm(text)
    try:
        m = _NUMERIC.search(t)
        if m:
            a, b, c = (int(x) for x in m.groups())
            if a > 31:  # yyyy-mm-dd
                return date(a, b, c)
            return date(c, b, a)  # dd.mm.yyyy
        m = _TEXTUAL.search(t)
        if m:
            day, month, year = m.groups()
            for i, name in enumerate(RO_MONTHS, 1):
                if name.startswith(month[:3]) and month[:3] == name[:3]:
                    return date(int(year), i, int(day))
    except ValueError:
        pass
    return None


def format_date_ro(d: date) -> str:
    return f"{d.day} {RO_MONTHS[d.month - 1]} {d.year}"
