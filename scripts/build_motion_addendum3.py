"""Build addendum 3 to the Motion handoff: the finer coast and a whiplash scene.

Writes a small flat folder to upload into the same Motion chat:

  addendum3.md                     what changes, the rules, the line, the prompt
  card_map_shapes.json             the finer outlines (results/figures/, D107)
  addendum3_whiplash_tests.json    the two H5 rows, read from run1
  addendum3_whiplash_series.csv    the whiplash index per region and year
  addendum3_ref_whiplash.png       the index as a static chart, for the look

No polygon is opened and nothing under results/ is written.

Usage, from the repo root:
    python scripts/build_motion_addendum3.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "motion_handoff_addendum3"
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
# The scene's rows: (test, region, the line beside it, as on the site).
ROWS = (("H5_lag1", "NorCal", "Northern California", "burned area the year after a wet winter"),
        ("H5_lag0", "AB", "Alberta", "burned area the same year as a wet winter"))
# A draft: the owner has not approved it.
CARD_LINE = ("A wet winter changes what burns in only some places: more the next year in "
             "Northern California, less the same year in Alberta.")
BRIEF = """# Addendum 3: the finer coast and a whiplash scene

For the film already in this chat. Both changes land in one re-export, dark and light.
Change nothing else: the pace constant, the other scenes' timings and the credits layout stay.

## Finer coast (Scene 2)

`card_map_shapes.json` replaces the outlines in `map_shapes.json`. Same frame: SVG path data,
x to the right, y down, in a {width} by {height} box. Per region: `d` (closed rings to fill),
`border` and `coast` (open lines), `label` (the same label point as the map page). The top-level
`coast` is land outside the regions. The file is about 205 KB; report if that breaks a limit or
slows the scene. A boundary is `border` only where another region shares it, or on a long inland
run of a region's largest part; islands and lakes are always `coast`. Compare the two files and
report what changes before swapping. Keep the existing rule for BC: the bright line on its
mainland only, drawn as already approved.

## Whiplash scene (new, between Scenes 7 and 8, about 12 to 15 s)

Card line (DRAFT, the owner may reword it; show as written and list it in the return notes):

> {line}

Show the two rows in `addendum3_whiplash_tests.json`, the way Scene 7 shows a result. The percent
is the plain reading; the estimate is in log points per 1 SD. You may draw the index from
`addendum3_whiplash_series.csv` behind or before them; `addendum3_ref_whiplash.png` shows the look.

## Rules for the scene

- The two rows are H5, a test of wet winters (October to March precipitation) against burned area.
  Both pass the Holm correction, and they are already in Scene 7. 'Significant' may be used for
  these two rows and nothing else in the scene.
- The series is the whiplash index: summer SPEI-3 minus winter SPEI-3. It is description only and
  was not tested. Never show a p-value, 'significant', or a link to burned area for it.
- Never say the index predicts a fire season: summer falls inside the season.
- A bar below zero swings from wet to dry. In the north a bar above zero can be a dry winter and a
  wetter summer, so don't call every large bar 'wet to dry'.
- Associations, not causes. No 'drives', 'causes' or 'leads to'. This is apart from El Niño: don't
  imply El Niño produces these two results.
- Every figure comes from these files. Reading time at least 3 s, as elsewhere. If the film passes
  3:00, flag it; don't shorten other scenes.
- Credits: ERA5-Land and burned area, as Scene 7 carries them (credits.md in the first bundle).

## What comes back

- Both MP4s at 1920 x 1080, 30 fps.
- Every scene's new start time and length.
- What the finer coast changed in Scene 2: label or pill moves, and draw speed.
- Every new on-screen line, word for word, for the site's transcript.

## Files and why each may leave the repository

| File | Why |
|---|---|
| `addendum3.md` | this note |
| `card_map_shapes.json` | committed in the public repository; display only; land from Natural Earth (public domain) |
| `addendum3_whiplash_tests.json` | rows of results/tables/run1/registered_tests.csv, public |
| `addendum3_whiplash_series.csv` | columns of results/tables/whiplash_swe_region_year.csv, public; no fire data |
| `addendum3_ref_whiplash.png` | results/figures/, drawn by code; (c) Dace Roberts |
"""


def tests() -> list[dict]:
    reg = pd.read_csv(TABLES / "run1" / "registered_tests.csv")
    rows = []
    for test, region, name, what in ROWS:
        r = reg[(reg["test"] == test) & (reg["region"] == region)].iloc[0]
        if r["significant"] is not True and r["significant"] != True:  # noqa: E712
            raise ValueError(f"{test} {region} does not pass Holm.")
        rows.append({"test": test, "region": region, "name": name, "what": what,
                     "unit": "log points per 1 SD", **{k: round(float(r[k]), 3) for k in
                     ("estimate", "ci_low", "ci_high", "pct_change", "pct_low", "pct_high",
                      "p_holm")}})
    return rows


def build(out: Path = OUT) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shapes = FIGURES / "card_map_shapes.json"
    shutil.copyfile(shapes, out / shapes.name)
    meta = json.loads(shapes.read_text("utf-8"))
    (out / "addendum3_whiplash_tests.json").write_bytes(
        json.dumps({"run": "run1", "rows": tests()}, ensure_ascii=False, indent=1).encode("utf-8"))
    series = pd.read_csv(TABLES / "whiplash_swe_region_year.csv")
    series[["region", "year", "whiplash", "spei3_djf", "spei3_jja", "phase", "strong",
            "enso_djf"]].dropna(subset=["whiplash"]).round(3).to_csv(
        out / "addendum3_whiplash_series.csv", index=False, lineterminator="\n")
    shutil.copyfile(FIGURES / "whiplash_series_roni.png", out / "addendum3_ref_whiplash.png")
    (out / "addendum3.md").write_bytes(BRIEF.format(
        width=meta["width"], height=meta["height"], line=CARD_LINE).encode("utf-8"))
    return sorted(path.name for path in out.iterdir())


if __name__ == "__main__":
    for name in build():
        print(f"wrote {OUT / name}")
