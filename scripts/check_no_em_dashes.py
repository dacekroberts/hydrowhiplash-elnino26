"""Fail if any em dash appears in Python source (comments, docstrings, code).

Scans .py files and the code cells of notebooks (.ipynb). Visible prose in
Markdown, Quarto pages and notebook Markdown cells is exempt.

Run:  python scripts/check_no_em_dashes.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)
SCANNED = ["src", "tests", "scripts", "notebooks"]


def find_hits(root: Path = ROOT) -> list[str]:
    """One "path:line: text" entry per line holding an em dash; notebook
    entries read "path:cell N:line: text" (cells and lines counted from 1)."""
    hits = []
    for folder in SCANNED:
        for path in sorted((root / folder).rglob("*.py")):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if EM_DASH in line:
                    hits.append(f"{path.relative_to(root).as_posix()}:{n}: {line.strip()}")
        for path in sorted((root / folder).rglob("*.ipynb")):
            if ".ipynb_checkpoints" in path.parts:
                continue
            cells = json.loads(path.read_text(encoding="utf-8")).get("cells", [])
            for c, cell in enumerate(cells, 1):
                if cell.get("cell_type") != "code":
                    continue
                source = cell.get("source", "")
                text = "".join(source) if isinstance(source, list) else source
                for n, line in enumerate(text.splitlines(), 1):
                    if EM_DASH in line:
                        hits.append(f"{path.relative_to(root).as_posix()}:cell {c}:{n}: "
                                    f"{line.strip()}")
    return hits


def main() -> int:
    hits = find_hits()
    for hit in hits:
        print(hit)
    print(f"{len(hits)} em dash(es) found" if hits else "no em dashes")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
