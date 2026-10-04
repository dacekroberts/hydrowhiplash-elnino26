"""Tests for scripts/log.py: create, parse and export daily logs."""
import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("log", ROOT / "scripts" / "log.py")
log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log)


@pytest.fixture
def logdir(tmp_path, monkeypatch):
    d = tmp_path / "logs"
    d.mkdir()
    (d / "_TEMPLATE.md").write_text((ROOT / "logs" / "_TEMPLATE.md").read_text(encoding="utf-8"),
                                    encoding="utf-8")
    monkeypatch.setattr(log, "ROOT", tmp_path)
    monkeypatch.setattr(log, "LOGS", d)
    monkeypatch.setattr(log, "TEMPLATE", d / "_TEMPLATE.md")
    monkeypatch.setattr(log, "EXPORT", d / "export")
    return d


def test_new_fills_date_and_is_idempotent(logdir):
    log.cmd_new("2026-10-05")
    text = (logdir / "2026-10-05.md").read_text(encoding="utf-8")
    assert "date: 2026-10-05" in text and "YYYY-MM-DD" not in text
    (logdir / "2026-10-05.md").write_text(text + "\nkept\n", encoding="utf-8")
    log.cmd_new("2026-10-05")
    assert (logdir / "2026-10-05.md").read_text(encoding="utf-8").endswith("kept\n")


def test_parse_rejects_mismatched_date(logdir):
    (logdir / "2026-10-06.md").write_text("---\ndate: 2026-10-07\n---\n# x\n", encoding="utf-8")
    with pytest.raises(ValueError):
        log.parse(logdir / "2026-10-06.md")


def test_export_writes_index_in_date_order(logdir):
    for day, hrs in [("2026-10-07", 2), ("2026-10-05", 1.5)]:
        (logdir / f"{day}.md").write_text(
            f"---\ndate: {day}\nphase: Phase 1\nhours: {hrs}\nsessions: [a, b]\n"
            f"tags: [era5]\nsummary: did {day}\n---\n# {day}\n", encoding="utf-8")
    log.cmd_export(None)
    with open(logdir / "export" / "index.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["date"] for r in rows] == ["2026-10-05", "2026-10-07"]
    assert rows[0]["sessions"] == "a; b" and rows[0]["tags"] == "era5"
    log.cmd_export("2026-10-06")
    with open(logdir / "export" / "index.csv", encoding="utf-8") as f:
        assert [r["date"] for r in csv.DictReader(f)] == ["2026-10-07"]


def test_repo_logs_all_parse():
    for path in log.log_files():
        log.parse(path)
