"""Build addendum 2 to the Motion handoff: pictures of the region map.

The first bundle carried the map as coarse vector shapes (map.json, 6 km).
The site's link card later got a finer map with islands kept (D107), and
the owner asked for pictures of it at different zooms, for the film's map
illustrations to follow, in place of new shapes. This writes a small flat
folder to upload into the same Motion chat:

  addendum2.md                 what the pictures are for, the rules, the prompt
  addendum2_map_<view>_dark.png  the card's map, whole and in closer views

The map is drawn by src.banner.draw_map from the committed
results/figures/card_map_shapes.json. The whole map is the card's drawing
enlarged; a closer view has the same shapes with thinner lines. No polygon is
opened and nothing under results/ is written.

Usage, from the repo root:
    python scripts/build_motion_addendum2.py
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_motion_handoff as handoff  # noqa: E402
from src import banner, theme  # noqa: E402

OUT = ROOT / "motion_handoff_addendum2"
FILM_THEME = "dark"  # the film is built dark first (owner, 2026-10-13)
ZOOM = 4  # shapes, times their size on the card
# Lines and labels in a closer view, times their size on the card: less than
# ZOOM, so a narrow channel is wider than the line beside it.
CLOSE_LINES = 2
# Each view as fractions of the whole map picture: left, top, right, bottom.
# Chosen by eye on the card (2026-10-13); re-check if the card's map box or
# the shapes file changes.
VIEWS = {
    "whole": ((0.0, 0.0, 1.0, 1.0), "all seven regions, as on the link card"),
    "alaska": ((0.0, 0.0, 0.54, 0.44), "Alaska with the Aleutians and Kodiak"),
    "panhandle": ((0.36, 0.26, 0.64, 0.54),
                  "the Alaska panhandle and the north coast of British Columbia"),
    "bc_coast": ((0.44, 0.30, 0.80, 0.68),
                 "British Columbia's coast with Haida Gwaii and Vancouver Island"),
    "california": ((0.52, 0.72, 1.0, 1.0), "the Pacific Northwest coast, NorCal and SoCal"),
}
RULES = (
    "These pictures are a guide to the look of the film's map: the shape of the coast, which "
    "islands are drawn and how the lines are weighted. map.json in the first bundle stays the "
    "source for where things sit; nothing is traced from a picture into a position.",
    "Islands stay islands: water between an island and the mainland is drawn as water.",
    "Two lines. A border between regions is the bright line. A coast is a thin faint line, "
    "except British Columbia's, which carries the bright line drawn inside the shore so a "
    "narrow channel stays dark.",
    "The seven regions are the study's regions, filled in one shade. The map shows where they "
    "are; it does not show climate zones, and no shading inside a region means anything.",
    "NorCal and SoCal are too narrow for their names, so each name sits in a pill over the "
    "ocean with a line to the region.",
    "The credit '{credit}' is on screen wherever the map is (credits.md in the first bundle).",
    "The film stays at {max_seconds} s at most. Nothing else in it changes.",
)
RETURNS = (
    "Which scenes' maps were redrawn, with a still of each.",
    "Anything in the pictures the film's map could not follow, and why.",
)
PROMPT = (
    "Addendum 2 to the bundle you already hold: addendum2.md and {n} pictures of the region "
    "map, addendum2_map_*_dark.png.",
    "Redraw the film's map illustrations to match the look in these pictures, as addendum2.md "
    "describes. Keep map.json for positions.",
    "Change nothing else in the film. Send back what addendum2.md lists under 'What comes "
    "back'.",
)


def view(path: Path, window: tuple[float, float, float, float], lines: int) -> Path:
    """The card's map alone, cut to `window`, its shapes at ZOOM times
    their size on the card and its lines and labels at `lines` times."""
    kind, _ = banner.SITE_PREVIEW[0]
    lay = banner.LAYOUTS[kind]
    left, top, right, bottom = lay["map"]
    width, height = right - left, bottom - top
    x0, y0, x1, y1 = window
    c = theme.colours(FILM_THEME)
    dpi = banner.DPI * lines
    fig = Figure(figsize=((x1 - x0) * width * ZOOM / dpi, (y1 - y0) * height * ZOOM / dpi),
                 dpi=dpi, facecolor=c["page"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(x0 * width, x1 * width)
    ax.set_ylim(y1 * height, y0 * height)
    ax.axis("off")
    x, y, size = lay["credit"]
    alone = {**lay, "map": (0, 0, width, height), "credit": (x - left, y - top, size)}
    # matplotlib keeps a drawn font file open, which blocks its removal on
    # Windows; the copies are then left for the system to clear.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        fonts = banner.static_fonts(Path(folder))
        banner.draw_map(ax, alone, c, fonts, lambda s: s * 72 / banner.DPI)
        fig.savefig(path, dpi=dpi)
    return path


def pictures(out: Path) -> dict[str, str]:
    """One file per view; name by view. The whole map is the card's
    drawing enlarged; a closer view keeps thinner lines so the shapes
    show."""
    names = {name: f"addendum2_map_{name}_{FILM_THEME}.png" for name in VIEWS}
    for name, (window, _) in VIEWS.items():
        view(out / names[name], window, ZOOM if name == "whole" else CLOSE_LINES)
    return names


def brief(names: dict[str, str]) -> str:
    film = {**handoff.FILM, "credit": banner.MAP_CREDIT, "n": len(names)}
    lines = ["# Addendum 2: pictures of the region map", "",
             "For the film already in this chat. The site's link card has a finer map than the "
             "shapes in the first bundle, with islands kept. These pictures show it whole and "
             "in closer views, so the film's map illustrations can follow its look.", "",
             "## The pictures", "", "| File | Shows |", "|---|---|"]
    lines += [f"| `{names[view]}` | {what} |" for view, (_, what) in VIEWS.items()]
    lines += ["", f"The first picture is the card's map enlarged {ZOOM} times, lines and labels "
              f"with it. A closer view has its shapes at {ZOOM} times and its lines and labels "
              f"at {CLOSE_LINES} times, so narrow channels show.", "", "## Rules", ""]
    lines += [f"- {rule.format(**film)}" for rule in RULES]
    lines += ["", "## What comes back", ""] + [f"- {item}" for item in RETURNS]
    lines += ["", "## Prompt to paste", ""] + [line.format(**film) + "\n" for line in PROMPT]
    lines += ["## Files and why each may leave the repository", "",
              "| File | Why |", "|---|---|",
              "| `addendum2.md` | this note; no figure of the study in it |",
              "| the pictures | drawn by code from results/figures/card_map_shapes.json, "
              "public in the repository; the same map is public on the site's link card; "
              "(c) Dace Roberts, land from Natural Earth (public domain) |"]
    return "\n".join(lines) + "\n"


def build(out: Path) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "addendum2.md").write_bytes(brief(pictures(out)).encode("utf-8"))
    names = sorted(path.name for path in out.iterdir())
    for name in names:
        if (out / name).is_dir() or any(mark in name for mark in "@[]()"):
            raise ValueError(f"{name} would not survive the upload.")
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    for name in build(args.out):
        print(f"wrote {args.out / name}")


if __name__ == "__main__":
    main()
