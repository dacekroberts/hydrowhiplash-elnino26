"""Build the private sample dashboard (session 12, sample visuals).

A storyboard in five scenes for a first-time reader: the question, the
record, the result, what survived, what comes next. Reads only committed
tables under results/tables/ (the registered run, the fire table through
the pinned loader, the site settings and the rollout calendar), puts them
into scripts/dashboard/template.html as JSON with the design tokens from
theme/tokens.json as its CSS variables, and writes one HTML file. No
polygon is opened and no number is typed by hand. The seasons drawn are
the ones the registered tests use (fire_figures.test_seasons), so no
held-back season can appear.

Usage, from the repo root:
    python scripts/build_dashboard.py --out <path to .html>

TEXT holds every sentence the page shows. Lines marked "site" repeat
wording the owner approved for the site; lines once marked "draft" were drafts
for the owner to word.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import diagrams, figures, fire_figures, pin_inputs, theme  # noqa: E402  (needs ROOT on the path)
from src.config import REGIONS  # noqa: E402

TEMPLATE = ROOT / "scripts" / "dashboard" / "template.html"
TABLES = ROOT / "results" / "tables"
RUN = "run1"
SIG_DIGITS = 6
# Registered tests that set El Nino itself against burned area; the count
# of significant ones among them is the page's third headline figure.
ENSO_BURN_TESTS = ("H2", "H3a", "H3b", "H4", "C2")
LEDGER_TEST = "H3a"
# Calendar items shown in the last scene, in this order after the next one due.
NEXT_ITEMS = ("djf_index", "swe_april1", "verify_north")
REGION_NAMES = {"PNW": "Pacific Northwest", "BC": "British Columbia", "AB": "Alberta",
                "AK": "Alaska", "YT": "Yukon", "NorCal": "Northern California",
                "SoCal": "Southern California"}
# A significant test's label, what its figure measures and an optional note.
# A test missing here stops the build, so a rerun cannot show an unworded row.
SURVIVED = {
    "H1": ("H1 (winter precipitation, El Niño winters against the rest)",
           "December to February precipitation in El Niño winters, minus the rest",
           "A check, not a finding: I had seen these values before the freeze."),  # site
    "H5_lag0": ("H5 (wet winters and burned area, same year)",
                "burned area that year, when the winter is wetter by one standard deviation "
                "(a typical year-to-year swing)", ""),  # approved 2026-10-13
    "H5_lag1": ("H5 (wet winters and burned area, the year after)",
                "burned area the year after a winter that much wetter", ""),  # approved 2026-10-13
    "H6_swe": ("H6 (1 April snowpack and burned area)",
               "burned area that year, when the 1 April snowpack is deeper by the same kind "
               "of swing", ""),  # approved 2026-10-13
}
# The address the opening flow ends at (owner, 2026-10-12; D84).
SITE_URL = "https://hydrowhiplash.dacekroberts.dev"
TEXT = {
    # Owner, 2026-10-13: "yes but we need to include el nino somehow"; the
    # flow's label below: "looks good".
    "title": "Does an El Niño winter say how much the next fire season will burn?",  # approved 2026-10-13
    "scene1": "I asked whether the winter before a fire season says how much will burn, and "
              "whether El Niño is the useful part of that winter. I fixed the tests in writing "
              "before opening any fire data, then ran them once.",  # site
    "flow": "From four sources to the live site",  # approved 2026-10-13
    "scene2": "Every fire season since {first}, as a multiple of the region's typical season. "
              "A shaded year follows an El Niño winter; a darker tick marks a strong one.",  # site
    "scene3": "The change in burned area per 1 °C of the winter index, with a year trend. "
              "Every interval crosses zero.",  # site, joined from a caption and its alt text
    "scene4": "What does show up is the step after El Niño. These are associations over "
              "about {n} seasons, not causes.",  # site
    "scene5": "A forecast for {year} goes up before the season and is checked against it "
              "afterwards.",  # site
}


def _clean(value):
    """JSON-safe cell: NaN to None, floats to SIG_DIGITS significant digits."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, float):
        return float(f"{value:.{SIG_DIGITS}g}")
    if hasattr(value, "item"):
        return _clean(value.item())
    return value


def _rows(frame: pd.DataFrame, columns: list[str]) -> list[dict]:
    return [{k: _clean(v) for k, v in row.items()} for row in frame[columns].to_dict("records")]


def seasons(settings: dict) -> list[dict]:
    """One entry per region: its typical season and every season the tests
    use, each as its log departure from the region's mean (None where no
    fire of counted size burned)."""
    table = figures.season_anomaly(fire_figures.test_seasons(
        pin_inputs.load_input(TABLES / "fire_region_year.csv")))
    out = []
    for region in REGIONS:
        g = table[table["region"] == region].sort_values("year")
        last = settings["fire_last_year_by_region"][region]
        if g["year"].max() > last:
            raise ValueError(f"{region} holds a season after {last}.")
        burned = g[g["anomaly"].notna()]
        out.append({"region": region, "name": REGION_NAMES[region], "last": last,
                    "typical": _clean(float(np.expm1(burned["log_burn"].mean()))),
                    "seasons": _rows(g, ["year", "anomaly", "burn_ha", "phase", "strong",
                                         "enso_djf"])})
    return out


def flow() -> dict:
    """The project flowchart cut to its spine for the opening scene: the four
    sources, the table they meet in, and the steps down to the site. Every
    label is the site flowchart's own (src.diagrams), so the two cannot
    drift apart. Each label is its first line and the rest."""
    def one_line(text: str) -> list[str]:
        head, _, rest = text.partition("\n")
        return [head, rest.replace("\n", " ")]

    return {"sources": [{"token": token, "text": one_line(stream[0])}
                        for token, stream in zip(diagrams.PROJECT_STREAM_TOKENS,
                                                 diagrams.PROJECT_STREAMS)],
            "table": one_line(diagrams.PROJECT_TABLE), "plan": one_line(diagrams.PROJECT_PLAN),
            "spine": [one_line(text) for _, text in diagrams.PROJECT_SPINE[:-1]],
            "pages": diagrams.PROJECT_SPINE[-1][1].replace("\n", " "),
            "site": SITE_URL}


def payload() -> dict:
    """Everything the page shows, read from the committed tables."""
    settings =json.loads((TABLES / "site_settings.json").read_text("utf-8"))
    calendar = {row["id"]: row for row in json.loads(
        (TABLES / "rollout_calendar.json").read_text("utf-8"))["items"]}
    reg = pd.read_csv(TABLES / RUN / "registered_tests.csv")
    provenance = json.loads(
        (TABLES / RUN / "registered_tests.csv.provenance.json").read_text("utf-8"))
    sig = reg[reg["significant"] == True]  # noqa: E712  (the column holds booleans and blanks)
    unworded = sorted(set(sig["test"]) - set(SURVIVED))
    if unworded:
        raise ValueError(f"No wording in SURVIVED for {unworded}.")
    n_fire_years = int(reg[(reg["test"] == LEDGER_TEST) & (reg["region"] == "PNW")]["n"].iloc[0])
    columns = ["test", "region", "estimate", "ci_low", "ci_high", "pct_change", "pct_low",
               "pct_high", "p_holm", "significant"]
    survived = _rows(sig, columns)
    for row in survived:
        row["label"], row["what"], row["note"] = SURVIVED[row["test"]]
        row["name"] = REGION_NAMES[row["region"]]
    ledger = _rows(reg[reg["test"] == LEDGER_TEST], columns)
    for row in ledger:
        row["name"] = REGION_NAMES[row["region"]]
    upcoming = next(row for row in calendar.values() if row["reader"] and not row["done"])
    later = [calendar[i] for i in NEXT_ITEMS if i != upcoming["id"]]
    text = dict(TEXT)
    text["scene2"] = text["scene2"].format(first=settings["fire_first_year"])
    text["scene4"] = text["scene4"].format(n=n_fire_years)
    text["scene5"] = text["scene5"].format(year=settings["forecast_year"])
    return {
        "meta": {"run": RUN, "commit": provenance["commit"], "run_utc": provenance["run_utc"],
                 "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                 "enso_index": settings["enso_index"], "min_fire_ha": settings["min_fire_ha"],
                 "first_year": settings["fire_first_year"],
                 "forecast_year": settings["forecast_year"],
                 "plan_frozen": calendar["plan_frozen"]["when"]},
        "counts": {"tests": len(reg), "significant": len(sig),
                   "enso_burn": int(sig["test"].isin(ENSO_BURN_TESTS).sum()),
                   "enso_burn_tests": int(reg["test"].isin(ENSO_BURN_TESTS).sum()),
                   "regions": len(settings["regions"]), "fire_years": n_fire_years},
        "text": text,
        "flow": flow(),
        "regions": seasons(settings),
        "ledger": ledger,
        "survived": survived,
        "next": [{"when": row["when"], "title": row["title"]} for row in [upcoming, *later]],
    }


def build() -> str:
    data = json.dumps(payload(), ensure_ascii=False, allow_nan=False).replace("</", "<\\/")
    page = TEMPLATE.read_text("utf-8")
    for marker, value in (("__FONT_URL__", theme.font_url()),
                          ("__THEME__", theme.css_variables()), ("__DATA__", data)):
        if page.count(marker) != 1:
            raise ValueError(f"{TEMPLATE.name} must hold {marker} exactly once.")
        page = page.replace(marker, value)
    return page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.write_bytes(build().encode("utf-8"))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
