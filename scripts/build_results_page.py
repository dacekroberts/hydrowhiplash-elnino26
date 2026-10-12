"""Build the private results page for one run folder.

Reads results/tables/<run>/ (the three result tables and one provenance
file), puts the rows into scripts/results_page/template.html as JSON, with
the design tokens from theme/tokens.json as its CSS variables, and writes
one HTML file. The page holds no number typed by hand; a rerun gets
its own page from its own folder.

Usage, from the repo root:
    python scripts/build_results_page.py --run run1 --out <path to .html>

NOTES holds the owner's own reading per hypothesis section (H1 ... C2);
empty until the owner writes it. Nothing here writes interpretation.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import theme  # noqa: E402  (the design tokens; needs ROOT on the path)

TEMPLATE = ROOT / "scripts" / "results_page" / "template.html"
TAGS = {"run1": "registered-run1"}
NOTES: dict[str, str] = {}
SIG_DIGITS = 6


def _clean(value):
    """JSON-safe cell: NaN to None, floats to SIG_DIGITS significant digits."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, float):
        return float(f"{value:.{SIG_DIGITS}g}")
    if hasattr(value, "item"):
        return _clean(value.item())
    return value


def _records(path: Path) -> list[dict]:
    frame = pd.read_csv(path)
    return [{k: _clean(v) for k, v in row.items()} for row in frame.to_dict("records")]


def build(run: str) -> str:
    folder = ROOT / "results" / "tables" / run
    provenance = json.loads((folder / "registered_tests.csv.provenance.json").read_text("utf-8"))
    data = {
        "meta": {
            "run": run,
            "tag": TAGS.get(run, ""),
            "commit": provenance["commit"],
            "run_utc": provenance["run_utc"],
            "seed": provenance["seed"],
            "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        },
        "notes": NOTES,
        "registered": _records(folder / "registered_tests.csv"),
        "beside": _records(folder / "reported_beside.csv"),
        "validation": _records(folder / "validation.csv"),
    }
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace("</", "<\\/")
    page = TEMPLATE.read_text("utf-8")
    for marker, text in (("__FONT_URL__", theme.font_url()),
                         ("__THEME__", theme.css_variables()), ("__DATA__", payload)):
        if page.count(marker) != 1:
            raise ValueError(f"{TEMPLATE.name} must hold {marker} exactly once.")
        page = page.replace(marker, text)
    return page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.write_bytes(build(args.run).encode("utf-8"))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
