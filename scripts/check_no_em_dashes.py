"""Fail if any em dash appears in Python source (comments, docstrings, code).

Visible prose in Markdown and Quarto pages is exempt.

Run:  python scripts/check_no_em_dashes.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)
SCANNED = ["src", "tests", "scripts", "notebooks"]


def main() -> int:
    hits = []
    for folder in SCANNED:
        for path in (ROOT / folder).rglob("*.py"):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if EM_DASH in line:
                    hits.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()}")
    for hit in hits:
        print(hit)
    print(f"{len(hits)} em dash(es) found" if hits else "no em dashes")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
