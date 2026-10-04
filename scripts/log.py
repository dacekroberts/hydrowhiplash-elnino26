"""Daily log helper: create today's log, list logs, and export them.

Logs live in logs/YYYY-MM-DD.md, one file per local calendar day, each with
YAML frontmatter (date, phase, hours, sessions, tags, summary) so they can be
pulled into an external catalogue.

Usage (from the repo root):
  python scripts/log.py new            create today's log from the template (no-op if it exists)
  python scripts/log.py new 2026-10-05 create the log for a given date
  python scripts/log.py list           one line per log: date, phase, hours, summary
  python scripts/log.py export         write logs/export/index.csv and logs/export/all_logs.md
  python scripts/log.py export --since 2026-11-01
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
TEMPLATE = LOGS / "_TEMPLATE.md"
EXPORT = LOGS / "export"
DATE_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
FIELDS = ["date", "phase", "hours", "sessions", "tags", "summary"]


def log_files(since: str | None = None) -> list[Path]:
    """Daily log files in date order, optionally from a start date on."""
    files = sorted(p for p in LOGS.glob("*.md") if DATE_FILE.match(p.name))
    if since:
        files = [p for p in files if p.stem >= since]
    return files


def parse(path: Path) -> tuple[dict, str]:
    """Split a log into its frontmatter dict and its Markdown body."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: missing frontmatter")
    _, front, body = text.split("---", 2)
    meta = yaml.safe_load(front) or {}
    meta["date"] = str(meta.get("date", path.stem))
    if meta["date"] != path.stem:
        raise ValueError(f"{path.name}: frontmatter date {meta['date']} does not match file name")
    return meta, body.strip()


def cmd_new(day: str | None) -> int:
    day = day or date.today().isoformat()
    target = LOGS / f"{day}.md"
    if target.exists():
        print(f"{target.relative_to(ROOT)} already exists; append a new session to it")
        return 0
    text = TEMPLATE.read_text(encoding="utf-8").replace("YYYY-MM-DD", day)
    target.write_text(text, encoding="utf-8")
    print(f"created {target.relative_to(ROOT)}")
    return 0


def cmd_list() -> int:
    for path in log_files():
        meta, _ = parse(path)
        print(f"{meta['date']}  {str(meta.get('phase', '')):<28} "
              f"{meta.get('hours', 0):>4}h  {meta.get('summary', '')}")
    return 0


def cmd_export(since: str | None) -> int:
    EXPORT.mkdir(parents=True, exist_ok=True)
    files = log_files(since)
    rows, combined = [], []
    for path in files:
        meta, body = parse(path)
        row = {k: meta.get(k, "") for k in FIELDS}
        row["sessions"] = "; ".join(meta.get("sessions") or [])
        row["tags"] = ", ".join(meta.get("tags") or [])
        row["file"] = f"logs/{path.name}"
        rows.append(row)
        combined.append(body)
    with open(EXPORT / "index.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ["file"])
        writer.writeheader()
        writer.writerows(rows)
    (EXPORT / "all_logs.md").write_text("\n\n---\n\n".join(combined) + "\n", encoding="utf-8")
    total = sum(float(r["hours"] or 0) for r in rows)
    print(f"exported {len(rows)} log(s), {total:g} hours, to {EXPORT.relative_to(ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_new = sub.add_parser("new")
    p_new.add_argument("day", nargs="?")
    sub.add_parser("list")
    p_exp = sub.add_parser("export")
    p_exp.add_argument("--since")
    args = parser.parse_args(argv)
    if args.cmd == "new":
        return cmd_new(args.day)
    if args.cmd == "list":
        return cmd_list()
    return cmd_export(args.since)


if __name__ == "__main__":
    sys.exit(main())
