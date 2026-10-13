"""Gather the reference material for a Claude Motion film into one folder.

The Motion session runs in another account and starts with nothing, so
everything it needs travels in one upload (the global skill
claude-motion-handoff). This script builds that folder from committed
files only: a numbers file and two CSVs written from results/tables/, the
colour tokens, the typefaces with their licences, the site's figures, the
banners, the sample dashboard as a storyboard draft and, with --capture,
pictures of the live site's pages (in the theme the machine is set to). The folder is flat (subfolders were
dropped on upload) and its names hold no @ or brackets.

It writes no brief and no storyboard: the scene list and its wording are
the owner's, and the storyboard is approved before a film is built. No
polygon is opened; map shapes are not in the folder (00_MANIFEST.md says
what is missing). Nothing under data/ is read except through the pinned
loader's check of the committed fire table, and no held-back season
leaves: the seasons are the ones the registered tests use.

Usage, from the repo root:
    python scripts/build_motion_handoff.py [--out motion_handoff] [--capture]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_dashboard  # noqa: E402  (needs scripts/ on the path)
from src import theme  # noqa: E402

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
# Live pages pictured with --capture: (page, window width, window height).
SITE_PAGES = (("index", 1280, 4200), ("map", 1280, 3000), ("tracker", 1280, 2200),
              ("flowchart", 1500, 2400))
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
SEASON_COLUMNS = ["region", "year", "burn_ha", "anomaly", "phase", "strong", "enso_djf"]
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
}
MISSING = (
    "An approved storyboard and the brief (scene table, card wording, rules, the prompt). "
    "The owner words these.",
    "Map shapes as vector data. The region outlines come from Natural Earth (public domain, "
    "terms read 2026-10-04); writing them out reads the region polygons, which waits for the "
    "owner's yes.",
    "The decisions the skill asks for before any scene: every aspect ratio, one pace "
    "constant, light or dark, export sizes in pixels, what the Motion session returns.",
    "The sources' credit lines for any scene that shows burned area or climate values: "
    "site/methods.qmd, 'Required notices'.",
)


def _csv(rows: list[dict], columns: list[str]) -> str:
    import pandas as pd
    return pd.DataFrame(rows)[columns].to_csv(index=False, lineterminator="\n")


def capture(out: Path) -> list[tuple[str, str]]:
    """Pictures of the live site's pages by headless Edge, in the machine's theme."""
    made = []
    for page, width, height in SITE_PAGES:
        name = f"ref_site_{page}.png"
        url = f"{build_dashboard.SITE_URL}/{'' if page == 'index' else page + '.html'}"
        subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
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

    numbers = {key: data[key] for key in ("meta", "counts", "ledger", "survived", "next")}
    write("numbers.json", json.dumps(numbers, ensure_ascii=False, indent=1), SAFE["numbers"])
    seasons = [{"region": r["region"], **s} for r in data["regions"] for s in r["seasons"]]
    write("seasons.csv", _csv(seasons, SEASON_COLUMNS), SAFE["seasons"])
    calendar = json.loads((TABLES / "rollout_calendar.json").read_text("utf-8"))["items"]
    write("timetable.csv", _csv([row for row in calendar if row["reader"]], TIMETABLE_COLUMNS),
          SAFE["timetable"])
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
