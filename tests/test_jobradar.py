from pathlib import Path

import yaml

from jobradar.filters import extract_technologies
from jobradar.main import process_source
from jobradar.notify import format_message
from jobradar.parsers import parse_listing
from jobradar.storage import Storage
from jobradar.textutil import contains_term, parse_date

ROOT = Path(__file__).parent.parent
HTML = (Path(__file__).parent / "fixtures" / "careers.html").read_text(encoding="utf-8")
CFG = yaml.safe_load((ROOT / "config" / "config.yaml").read_text(encoding="utf-8"))
SRC = CFG["sources"]["example_radio"]


def test_parse_dates():
    assert str(parse_date("11.11.2026")) == "2026-11-11"
    assert str(parse_date("2026-11-11")) == "2026-11-11"
    assert str(parse_date("11 noiembrie 2026")) == "2026-11-11"
    assert parse_date("azi") is None


def test_term_matching():
    assert not contains_term("JavaScript dev", "Java")
    assert contains_term("C# and .NET", "C#")
    assert contains_term("Dezvoltator Șef", "dezvoltator")


def test_parse_listing():
    jobs = parse_listing(HTML, "example_radio", SRC)
    assert len(jobs) == 4
    assert jobs[0].url == "https://example.ro/cariere/java-dev"


def test_message_format():
    job = parse_listing(HTML, "example_radio", SRC)[0]
    techs = extract_technologies(job, CFG["technologies"])
    assert techs == ["Java", "JavaScript", "Spring Boot", "PostgreSQL", "Docker"]
    msg = format_message(job, ["Software Development"], techs)
    assert "<b>Java Software Developer</b>" in msg
    assert "Exemplu Radio · București" in msg
    assert "• Publicat: 11 noiembrie 2026" in msg
    assert "Potrivire: Software Development" in msg


def test_only_relevant_notified_once(tmp_path, monkeypatch):
    sent = []
    monkeypatch.setattr("jobradar.main.send_telegram", sent.append)
    storage = Storage(tmp_path / "t.db")
    assert process_source("example_radio", SRC, CFG, storage, False, HTML) == 1
    assert process_source("example_radio", SRC, CFG, storage, False, HTML) == 0  # dedup
    assert len(sent) == 1 and "Java Software Developer" in sent[0]
