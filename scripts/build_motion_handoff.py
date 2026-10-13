"""Gather the reference material for a Claude Motion film into one folder.

The Motion session runs in another account and starts with nothing, so
everything it needs travels in one upload (the global skill
claude-motion-handoff). This script builds that folder from committed
files only: a numbers file and two CSVs written from results/tables/, the
colour tokens, the typefaces with their licences, the site's figures, the
banners, the sample dashboard as a storyboard draft and, with --capture,
pictures of the live site's pages (in the theme the machine is set to). The folder is flat (subfolders were
dropped on upload) and its names hold no @ or brackets.

It writes a brief (the owner's decisions of 2026-10-13, the rules a film
keeps, the scene skeleton the owner approved, a suggested card line per
scene that the owner has not approved) and a draft of the prompt to
paste; the card wording is the owner's and is settled before a film is
built. No polygon is opened: the
map shapes are cut from the committed map page, which already holds the
region outlines and the coast as paths in the map's own projection.
Nothing under data/ is read except through the pinned loader's check of
the committed tables, and no held-back season leaves: the seasons are the
ones the registered tests use.

Usage, from the repo root:
    python scripts/build_motion_handoff.py [--out motion_handoff] [--capture]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_dashboard  # noqa: E402  (needs scripts/ on the path)
from src import diagrams, theme  # noqa: E402

FIGURES = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"
# Figures the site or the README shows, copied as reference images.
REFERENCE_FIGURES = (
    "mechanism.png", "mechanism_dark.png", "methods_flow.png", "methods_flow_dark.png",
    "project_flow.png", "project_flow_dark.png",
    "headline1_el_nino_vs_rest.png", "headline1_el_nino_vs_rest_dark.png",
    "headline2_enso_strength.png", "headline2_enso_strength_dark.png",
    "headline3_north_vs_socal.png", "headline3_north_vs_socal_dark.png",
    "headline4_interval_coverage.png", "headline4_interval_coverage_dark.png",
    "banner_social_dark.png", "banner_readme_light.png", "banner_readme_dark.png",
)
# Live pages pictured with --capture: (page, window width, window height),
# once per theme. Edge's preferredColorScheme setting: 0 dark, 1 light.
SITE_PAGES = (("index", 1280, 4200), ("map", 1280, 3000), ("tracker", 1280, 2200),
              ("flowchart", 1500, 2400))
SITE_THEMES = (("dark", 0), ("light", 1))
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
SEASON_COLUMNS = ["region", "year", "burn_ha", "anomaly", "phase", "strong", "enso_djf"]
WINTER_TABLE = "climate_controls_region_year.csv"
WINTER_COLUMNS = ["region", "year", "winter", "precip_djf_mm", "pct_of_average", "phase",
                  "strong", "enso_djf"]
MAP_PAGE = FIGURES / "region_map.html"
METHODS = ROOT / "site" / "methods.qmd"
NOTICES_HEADING = "### Required notices"
# The owner's decisions before any scene (2026-10-13). One film first; a
# shorter cut or a longer one is decided after it is seen.
FILM = {"ratio": "16:9", "width": 1920, "height": 1080, "fps": 30, "max_seconds": 150,
        "themes": ["dark", "light"], "first_theme": "dark"}
# Scene skeleton, approved by the owner 2026-10-13: (share of the film, what
# is on screen, the files it draws from). Shares sum to 1.
SCENES = (
    (0.10, "The question, over the season strips of all seven regions.",
     "seasons.csv, ref_banner_social_dark.png"),
    (0.12, "Where: the seven regions on the map, north to south, named once.",
     "map_shapes.json"),
    (0.14, "The idea being tested: the two pathways, north and south, built step by step. "
           "Only the diagram's two top boxes and three steps a side; no footnotes.",
     "numbers.json (mechanism), ref_mechanism.png for the look"),
    (0.10, "How it was tested: four sources into one table, the plan frozen before any fire "
           "data was read, the tests run once.", "numbers.json (flow), ref_project_flow.png"),
    (0.18, "The record: winters, then the fire seasons that followed, El Ni\u00f1o years "
           "highlighted on the full record.", "winters.csv, seasons.csv"),
    (0.16, "The main result: El Ni\u00f1o against burned area, region by region, every "
           "interval crossing zero.", "numbers.json (ledger, counts), tests.csv"),
    (0.12, "What did pass: the four results, each with its estimate and interval.",
     "numbers.json (survived)"),
    (0.08, "What comes next: the dates up to the 2027 season, and the site's address.",
     "timetable.csv, numbers.json (next)"),
)
# One suggested card line per scene, in SCENES' order: drafts for the owner,
# cut from wording the site already carries where there is some. Filled
# from the run's counts, so no figure is typed here.
CARDS = (
    "{title}",
    "Seven regions, from Alaska to Southern California.",
    "The idea: after an El Ni\u00f1o winter the north runs milder and often drier, the "
    "south wetter.",
    "I fixed {tests} tests in writing before opening any fire data, then ran them once.",
    "Every fire season since {first_year}. A shaded year follows an El Ni\u00f1o winter.",
    "{enso_burn} of the {enso_burn_tests} tests that set El Ni\u00f1o against burned area "
    "are significant. Every interval crosses zero.",
    "{significant} of {tests} tests are significant after correcting for the number of "
    "tests. These are associations, not causes.",
    "A forecast for {forecast_year} goes up before the season and is checked against it "
    "afterwards.",
)
# The prompt to paste into the Motion session with the folder: a draft.
PROMPT = (
    "I have uploaded one flat folder. Read 00_MANIFEST.md and brief_draft.md first, then "
    "tell me in a few lines what you will build and anything in the brief you cannot do.",
    "Before building, tell me your current limits: film length, pixel size, frame rates, "
    "the number and size of code and data modules, the number of uploaded assets. If any "
    "file here breaks one, say which.",
    "Build one film: {ratio}, {width} x {height} px, {fps} fps, {max_seconds} s at most, "
    "eight scenes at the starts and lengths in the brief's table.",
    "Build the dark theme only for now. Order of work: first one theme module that reads "
    "tokens.json, written so a light set can be switched in later, and one pace constant for every cut and camera move. Then the map from "
    "map_shapes.json with its region labels. Then the scenes, each as its own module so "
    "one can be dropped or stretched later.",
    "Take every number from numbers.json, tests.csv, seasons.csv or winters.csv. Do not "
    "type, estimate or re-round a figure. If a scene needs a number that is not in those "
    "files, stop and ask.",
    "Keep every rule under 'Rules the film keeps'. Where a rule and a nicer picture "
    "disagree, the rule wins.",
    "On-screen wording: use the brief's card lines exactly. Do not add a headline, a "
    "caption or an adjective of your own; if a scene seems to need more words, ask.",
    "Use the typefaces in the folder. The ref_ pictures show how the site draws the same "
    "data: match their colours and marks, not their layout.",
    "Credits: a scene that shows burned area or climate values carries its sources' "
    "short credit, and the closing card carries every notice in credits.md.",
    "When the film is built, send back what the brief lists under 'What comes back'. I "
    "export the MP4s myself from the film's page.",
)
RETURNS = (
    "The dark film at the size above, exported from the film's page; light follows later.",
    "A scene table with each scene's start time and length.",
    "Every figure and every credit on screen, per scene.",
    "Any on-screen wording added or changed since this brief.",
    "The value of the pace constant and where it is set.",
)
TIMETABLE_COLUMNS = ["when", "title", "site_change", "done"]
SAFE = {
    "numbers": "counts, the H3a ledger, the results that pass Holm and the next dates, from "
               "results/tables/run1/ and rollout_calendar.json; public in the repository",
    "seasons": "the seasons the registered tests use, from results/tables/fire_region_year.csv; "
               "public in the repository; no 2026 or 2027, and no 2025 for BC, AB or YT",
    "timetable": "the reader's rows of results/tables/rollout_calendar.json; on the tracker page",
    "tokens": "theme/tokens.json; public in the repository",
    "font": "SIL Open Font License 1.1, its text beside it; the licence allows copies",
    "figure": "results/figures/, drawn by code from committed tables; public on the site or "
              "in the repository; (c) Dace Roberts",
    "page": "a picture of a public page of the live site",
    "storyboard": "the private sample dashboard, a draft: its wording is not all approved",
    "winters": "December to February precipitation per region and winter with the winter's "
               "ENSO class, from results/tables/climate_controls_region_year.csv; public in "
               "the repository and drawn on the site's Overview page",
    "tests": "results/tables/run1/registered_tests.csv as committed: all 52 registered "
             "tests; public in the repository",
    "map": "the region outlines and the coast as paths, cut from the committed "
           "results/figures/region_map.html (public on the site's map page); made from "
           "Natural Earth, public domain, no credit required; display only",
    "credits": "the 'Required notices' of site/methods.qmd, as published",
    "brief": "the owner's decisions of 2026-10-13, the rules, the approved scene skeleton, "
             "and a suggested card line per scene that is not approved",
    "prompt": "a draft of the prompt to paste into the Motion session; not approved",
}
MISSING = (
    "The owner's approval of the card lines in brief_draft.md and of prompt_draft.md.",
    "Pictures of the site at phone width.",
)


def winters() -> list[dict]:
    """Each region's December to February precipitation per winter, in mm
    and as a percent of the region's average over the winters in the
    table (as on the Overview chart), with the winter's ENSO class."""
    from src import pin_inputs

    table = pin_inputs.load_input(WINTER_TABLE).dropna(subset=["precip_djf_mm"])
    table = table.sort_values(["region", "year"])
    mean = table.groupby("region")["precip_djf_mm"].transform("mean")
    table = table.assign(pct_of_average=(100 * table["precip_djf_mm"] / mean).round(1),
                         precip_djf_mm=table["precip_djf_mm"].round(1))
    return table[WINTER_COLUMNS].to_dict("records")


def map_shapes() -> dict:
    """The seven region outlines and the coast behind them, as SVG path
    data in one box, read from the committed map page. Display only."""
    from src.config import MAP_DISPLAY_CRS, MAP_SIMPLIFY_KM

    page = MAP_PAGE.read_text("utf-8")
    payload = json.loads(re.search(r'<script type="application/json">(.*?)</script>',
                                   page, re.S).group(1))
    shape, coast = payload["shapes"], re.search(r'<path class="land" d="([^"]*)"', page)
    if coast is None:
        raise ValueError(f"{MAP_PAGE.name} holds no coast path.")
    return {"width": shape["width"], "height": shape["height"], "projection": MAP_DISPLAY_CRS,
            "simplified_km": MAP_SIMPLIFY_KM,
            "note": "SVG path data; x to the right, y down, in a width by height box. "
                    "label is a point inside the region's largest part.",
            "regions": {code: {"name": payload["names"][code], **shape["regions"][code]}
                        for code in shape["regions"]},
            "coast": coast.group(1)}


def notices() -> str:
    """The published 'Required notices' section of the methods page."""
    text = METHODS.read_text("utf-8")
    start = text.index(NOTICES_HEADING)
    return text[start:text.index("\n## ", start)].rstrip() + "\n"


def brief(data: dict) -> str:
    """The brief as a draft: the decisions, the rules and a scene skeleton
    with times cut from FILM. Counts come from the run, not from here."""
    counts, meta = data["counts"], data["meta"]
    fill = {**counts, **meta, "title": data["text"]["title"]}
    lines = ["# Brief", "",
             "The decisions and the scene skeleton are approved (owner, 2026-10-13). The "
             "card lines are suggestions and are not approved.",
             "", "## Decided by the owner, 2026-10-13", "",
             f"- One film, {FILM['ratio']}, {FILM['width']} x {FILM['height']} px, "
             f"{FILM['fps']} fps, {FILM['max_seconds']} s at most.",
             "- A shorter cut or a longer one is decided after this film is seen. Build "
             "each scene as its own module so one can be dropped or stretched.",
             "- Dark first. The light film waits until the dark one is refined: keep every "
             "colour in one theme module, read from tokens.json, so light is a switch.",
             "- The seven regions are shown on a real map in one scene (map_shapes.json).",
             "- One pace constant for every cut and camera move, set in one place. Start "
             "slow: the last film's cuts were judged too fast.",
             "- Typefaces from the files here: National Park for display, Public Sans for "
             "text, JetBrains Mono for figures.",
             "", "## Rules the film keeps", "",
             "- Every figure on screen comes from numbers.json, tests.csv, seasons.csv or "
             "winters.csv. None is typed or rounded differently from the site.",
             "- Every year is drawn. El Ni\u00f1o years are highlighted on the full record, "
             "never shown alone.",
             "- Associations, not causes: no 'drives', 'causes' or 'leads to' for a result.",
             f"- 'Significant' is used only for the {counts['significant']} of "
             f"{counts['tests']} tests that pass the Holm correction. "
             f"{counts['enso_burn']} of the {counts['enso_burn_tests']} tests that set "
             "El Ni\u00f1o against burned area pass it; the film says so plainly.",
             "- Effect size and interval before any p-value. A null result is shown as a "
             "result.",
             f"- No season after the ones in seasons.csv is drawn. {meta['forecast_year']} "
             "appears only as an empty slot or a date.",
             f"- Burned area counts fires of {meta['min_fire_ha']} ha or more, by ignition "
             "date, in each region's fire season.",
             "- The map is a picture: nothing is measured from its shapes, and one shade "
             "covers a whole region.",
             "- A scene that shows burned area or climate values carries its sources' "
             "credit (credits.md). The closing card carries all of them.",
             "- Nothing flashes more than three times a second.",
             "", "## Scene skeleton (approved 2026-10-13)", "",
             "| # | Start | Length | On screen | Draws from |", "|---|---|---|---|---|"]
    start = 0
    for number, (share, what, source) in enumerate(SCENES, start=1):
        length = round(share * FILM["max_seconds"])
        lines.append(f"| {number} | {start} s | {length} s | {what} | {source} |")
        start += length
    lines += ["", f"Total {start} s.", "", "## Card lines (suggestions, not approved)", "",
              "One line per scene. The site's address closes scene 8: "
              f"{build_dashboard.SITE_URL.split('//')[1]}", ""]
    lines += [f"{number}. {card.format(**fill)}" for number, card in enumerate(CARDS, start=1)]
    lines += ["", "## What comes back", ""]
    lines += [f"- {item}" for item in RETURNS]
    return "\n".join(lines) + "\n"


def _csv(rows: list[dict], columns: list[str]) -> str:
    import pandas as pd
    return pd.DataFrame(rows)[columns].to_csv(index=False, lineterminator="\n")


def capture(out: Path) -> list[tuple[str, str]]:
    """Pictures of the live site's pages by headless Edge, in the machine's theme."""
    made = []
    for page, width, height in SITE_PAGES:
        for scheme, setting in SITE_THEMES:
            name = f"ref_site_{page}_{scheme}.png"
            url = f"{build_dashboard.SITE_URL}/{'' if page == 'index' else page + '.html'}"
            subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            f"--blink-settings=preferredColorScheme={setting}",
                            f"--window-size={width},{height}", "--virtual-time-budget=8000",
                            f"--screenshot={out / name}", url], check=True, timeout=120,
                           capture_output=True)
            if not (out / name).exists():
                raise RuntimeError(f"No picture was written for {url}.")
            made.append((name, SAFE["page"]))
    return made


def build(out: Path, with_capture: bool) -> list[tuple[str, str]]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    data = build_dashboard.payload()
    files: list[tuple[str, str]] = []

    def write(name: str, text: str, why: str) -> None:
        (out / name).write_bytes(text.encode("utf-8"))
        files.append((name, why))

    numbers = {key: data[key] for key in ("meta", "counts", "flow", "ledger", "survived",
                                          "next")}
    numbers["film"] = FILM
    numbers["mechanism"] = {"top": list(diagrams.MECHANISM_TOP),
                            "north": {"regions": list(diagrams.NORTH_REGIONS),
                                      "steps": list(diagrams.MECHANISM_STEPS["North"])},
                            "south": {"regions": list(diagrams.SOUTH_REGIONS),
                                      "steps": list(diagrams.MECHANISM_STEPS["South"])}}
    write("numbers.json", json.dumps(numbers, ensure_ascii=False, indent=1), SAFE["numbers"])
    seasons = [{"region": r["region"], **s} for r in data["regions"] for s in r["seasons"]]
    write("seasons.csv", _csv(seasons, SEASON_COLUMNS), SAFE["seasons"])
    calendar = json.loads((TABLES / "rollout_calendar.json").read_text("utf-8"))["items"]
    write("timetable.csv", _csv([row for row in calendar if row["reader"]], TIMETABLE_COLUMNS),
          SAFE["timetable"])
    write("winters.csv", _csv(winters(), WINTER_COLUMNS), SAFE["winters"])
    write("tests.csv", (TABLES / data["meta"]["run"] / "registered_tests.csv").read_text("utf-8"),
          SAFE["tests"])
    write("map_shapes.json", json.dumps(map_shapes(), ensure_ascii=False, separators=(",", ":")),
          SAFE["map"])
    write("credits.md", notices(), SAFE["credits"])
    write("brief_draft.md", brief(data), SAFE["brief"])
    write("prompt_draft.md", "# Prompt to paste, a draft\n\n" + "\n\n".join(
        line.format(**FILM) for line in PROMPT) + "\n", SAFE["prompt"])
    write("tokens.json", theme.TOKENS.read_text("utf-8"), SAFE["tokens"])
    write("storyboard_draft.html", build_dashboard.build(), SAFE["storyboard"])
    for path in sorted(theme.SITE_FONTS_DIR.iterdir()):
        shutil.copyfile(path, out / path.name)
        files.append((path.name, SAFE["font"]))
    for name in REFERENCE_FIGURES:
        shutil.copyfile(FIGURES / name, out / f"ref_{name}")
        files.append((f"ref_{name}", SAFE["figure"]))
    if with_capture:
        files += capture(out)
    lines = ["# Motion handoff: what is in this folder", "",
             f"Built by scripts/build_motion_handoff.py from run {data['meta']['run']} "
             f"(commit {data['meta']['commit'][:7]}) on {data['meta']['built_utc']}.", "",
             "| File | Why it may leave the repository |", "|---|---|"]
    lines += [f"| `{name}` | {why} |" for name, why in files]
    lines += ["", "## Not here yet", ""] + [f"- {item}" for item in MISSING]
    (out / "00_MANIFEST.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    for path in out.iterdir():
        if path.is_dir() or any(mark in path.name for mark in "@[]()"):
            raise ValueError(f"{path.name} would not survive the upload.")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "motion_handoff")
    parser.add_argument("--capture", action="store_true",
                        help="also picture the live site's pages (needs Edge and a connection)")
    args = parser.parse_args()
    files = build(args.out, args.capture)
    print(f"wrote {len(files) + 1} files to {args.out}")


if __name__ == "__main__":
    main()
