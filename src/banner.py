"""GitHub banner images (session 12, sample visuals).

Writes to results/figures/:
  banner_social_dark.png            1280 x 640, the repository's social preview
  banner_readme_<theme>.png         1280 x 320, the README header, one per theme
and to site/preview.png the picture a link to the site shows (og:image):
the same question and address beside a map of the seven regions.

Each is the question the project asks, the site's address and a motif: the
seven regions' fire seasons since FIRE_FIRST_YEAR, stacked north to south
on one scale, seasons after an El Nino winter banded. It is a motif, not a
chart: no axis and no values, so the README carries the sources' credit.

Reads the pinned, committed results/tables/fire_region_year.csv through
pin_inputs.load_input and keeps the seasons the registered tests use
(fire_figures.test_seasons), so no held-back season is drawn. No polygon is
opened: the map card's outlines are read from the committed
results/figures/card_map_shapes.json (python -m src.map_page --card, which
does read the region polygons and is run only when that file is remade). Colours come from theme/tokens.json. The design typefaces are
variable fonts, which matplotlib draws at one weight only, so fixed-weight
copies are made in a temporary folder at draw time and never committed
(SIL OFL 1.1; none of the three licences in site/fonts/ declares a
reserved font name).

Run:  python -m src.banner
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path as Outline  # noqa: E402

from src import figures, fire_figures, map_page, pin_inputs, theme  # noqa: E402
from src.config import FIRE_FIRST_YEAR, FORECAST_YEAR  # noqa: E402

DPI = 100
# Wording on the banner: the owner's choice of 2026-10-13 ("The question"),
# reworded the same day to name El Nino (owner: "we need to include el nino
# somehow"); approved by the owner 2026-10-13.
QUESTION = "Does an El Niño winter say how much the next fire season will burn?"
ADDRESS = "hydrowhiplash.dacekroberts.dev"
# Regions from north to south, the order of the rows.
ROWS = ("AK", "YT", "BC", "AB", "PNW", "NorCal", "SoCal")
# (font file in site/fonts/, weight) by role.
FACES = {"title": ("NationalPark-wght.ttf", 800), "label": ("JetBrainsMono-wght.ttf", 500),
         # the site's text face, for the region codes on the map card
         "region": ("PublicSans-wght.ttf", 600)}
# Pixel layouts. title: left, top of the first line, size, line step and the
# number of lines the question is wrapped to; strip and map: left, top,
# right, bottom; credit: right edge, baseline and size of the map's credit.
LAYOUTS = {
    "social": {"size": (1280, 640), "title": (64, 64, 58, 68, 2), "address": (64, 222, 20),
               "strip": (64, 290, 1216, 584), "label": 13},
    "readme": {"size": (1280, 320), "title": (48, 48, 38, 46, 3), "address": (48, 216, 16),
               "strip": (560, 40, 1240, 284), "label": 11},
    "site": {"size": (1280, 640), "title": (64, 150, 52, 62, 3), "address": (64, 366, 20),
             "map": (716, 36, 1236, 588), "label": 19, "credit": (1236, 616, 11)},
}
BANNERS = (("social", "dark"), ("readme", "light"), ("readme", "dark"))
# The site's link preview (og:image in site/_quarto.yml): the map card
# (owner, 2026-10-13: "the region map [my pick]"). Quarto leaves out images
# linked from outside site/, so it is written inside it, by this module
# only, never by hand.
SITE_PREVIEW = (("site", "dark"), theme.SITE_FONTS_DIR.parent / "preview.png")
# The map's outlines and land are Natural Earth (public domain, no credit
# required); the domain's own rule asks for a credit wherever a map appears.
MAP_CREDIT = "Map: Natural Earth"
# A region's code moved from the map page's label point, in that page's box
# units (x right, y down): Alaska's sits low on the card, toward the
# peninsula, so it is lifted over the mainland (owner, 2026-10-13).
LABEL_SHIFT = {"AK": (14.0, -42.0)}
# A region too narrow for its code: the code sits in a pill over the ocean,
# this far from the label point in the same units, with a line back to it
# (owner, 2026-10-13: "pill labels from ocean with lines drawing to land").
# Regions whose whole perimeter, islands included, carries the bright border
# line on the map card (owner, 2026-10-13). The rest keep a thin coast.
FULL_PERIMETER = ("BC",)
# Width in points of that line, all of it on the land side of the shore.
COAST_INSIDE = 0.9
# Colour token of that line.
COAST_TOKEN = "evergreen"
LABEL_CALLOUT = {"NorCal": (-92.0, 4.0), "SoCal": (-112.0, 24.0)}


def static_fonts(folder: Path) -> dict[str, FontProperties]:
    """Fixed-weight copies of the design typefaces, written into `folder`."""
    out = {}
    for role, (name, weight) in FACES.items():
        font = instancer.instantiateVariableFont(TTFont(theme.SITE_FONTS_DIR / name),
                                                 {"wght": weight})
        path = folder / f"{Path(name).stem}-{weight}.ttf"
        font.save(path)
        out[role] = FontProperties(fname=str(path))
    return out


def wrap(text: str, lines: int) -> list[str]:
    """`text` broken into `lines` lines of near-equal length, at spaces."""
    words, out = text.split(), []
    for left in range(lines, 0, -1):
        target = len(" ".join(words)) / left
        line = [words.pop(0)]
        while words and left > 1 and len(" ".join(line + [words[0]])) <= target + 2:
            line.append(words.pop(0))
        if left == 1:
            line += words
            words = []
        out.append(" ".join(line))
    return out


def seasons() -> pd.DataFrame:
    """Every season the tests use, with its log departure from the region's mean."""
    return figures.season_anomaly(fire_figures.test_seasons(
        pin_inputs.load_input(fire_figures.FIRE_TABLE)))


def outline(d: str, scale: float, left: float, top: float) -> Outline:
    """SVG path data of M, L and Z commands as a matplotlib path, scaled
    and moved to (`left`, `top`)."""
    points, codes = [], []
    for command, body in re.findall(r"([MLZ])([^MLZ]*)", d):
        if command == "Z":
            points.append((0.0, 0.0))
            codes.append(Outline.CLOSEPOLY)
            continue
        values = [float(v) for v in body.replace(",", " ").split()]
        for i in range(0, len(values), 2):
            points.append((left + values[i] * scale, top + values[i + 1] * scale))
            codes.append(Outline.MOVETO if command == "M" and i == 0 else Outline.LINETO)
    return Outline(points, codes)


def draw_map(ax, lay: dict, c: dict, fonts: dict[str, FontProperties], px) -> None:
    """The seven regions on the land around them, fitted into the layout's
    map box, each named by its code. A picture: nothing is measured from it.
    A region too narrow for its code has it in a pill over the ocean, with a
    line to the region (LABEL_CALLOUT)."""
    shapes = json.loads(map_page.CARD_OUT.read_text("utf-8"))
    left, top, right, bottom = lay["map"]
    scale = min((right - left) / shapes["width"], (bottom - top) / shapes["height"])
    left += (right - left - shapes["width"] * scale) / 2
    top += (bottom - top - shapes["height"] * scale) / 2

    def at(x: float, y: float) -> tuple[float, float]:
        return left + x * scale, top + y * scale

    ax.add_patch(PathPatch(outline(shapes["coast"], scale, left, top), facecolor=c["surface"],
                           edgecolor="none"))
    # Every part keeps its shape and is filled solid, so the water between
    # islands stays water. The coast is a thin line and only a border
    # carries the bright one: bright lines on both sides of every channel
    # read as noise at card size.
    fills = {}
    for region in ROWS:
        fills[region] = ax.add_patch(PathPatch(
            outline(shapes["regions"][region]["d"], scale, left, top),
            facecolor=c["lichen"], edgecolor="none", zorder=1))
    for kind in ("coast", "border"):
        for region in ROWS:
            d = shapes["regions"][region][kind]
            if not d:
                continue
            inside = kind == "coast" and region in FULL_PERIMETER
            width, alpha = (0.5, 0.55) if kind == "coast" and not inside else (1.3, 1.0)
            # A full-perimeter coast is drawn at twice the width and clipped
            # to the land, so the line lies inside the shore and a channel
            # narrower than the line stays water.
            line = ax.add_patch(PathPatch(
                outline(d, scale, left, top), facecolor="none",
                edgecolor=c[COAST_TOKEN if inside else "evergreen"],
                linewidth=2 * COAST_INSIDE if inside else width, alpha=alpha,
                joinstyle="round", capstyle="round", zorder=2))
            if inside:
                line.set_clip_path(fills[region])
    for region in ROWS:
        x, y = (float(v) for v in shapes["regions"][region]["label"].split())
        dx, dy = LABEL_SHIFT.get(region, (0.0, 0.0))
        style = {"fontproperties": fonts["region"], "fontsize": px(lay["label"]),
                 "color": c["ink"], "va": "center", "ha": "center"}
        if region in LABEL_CALLOUT:
            ox, oy = LABEL_CALLOUT[region]
            (x0, y0), (x1, y1) = at(x, y), at(x + ox, y + oy)
            ax.plot([x1, x0], [y1, y0], color=c["ink-muted"], linewidth=1, zorder=4)
            ax.plot([x0], [y0], marker="o", markersize=3.5, color=c["ink"], zorder=4)
            ax.text(x1, y1, region, zorder=5, **style,
                    bbox={"boxstyle": "round,pad=0.4,rounding_size=0.9", "linewidth": 0.8,
                          "facecolor": c["surface"], "edgecolor": c["rule-strong"]})
        else:
            ax.text(*at(x + dx, y + dy), region, **style)
    x, y, size = lay["credit"]
    ax.text(x, y, MAP_CREDIT, fontproperties=fonts["label"], fontsize=px(size),
            color=c["ink-muted"], va="baseline", ha="right")


def draw(table: pd.DataFrame, kind: str, theme_name: str, fonts: dict[str, FontProperties]) -> Figure:
    lay, c = LAYOUTS[kind], theme.colours(theme_name)
    width, height = lay["size"]
    fig = Figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=c["page"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    def px(size: float) -> float:
        return size * 72 / DPI

    x, y, size, step, lines = lay["title"]
    for i, line in enumerate(wrap(QUESTION, lines)):
        ax.text(x, y + i * step, line, fontproperties=fonts["title"], fontsize=px(size),
                color=c["ink"], va="top", ha="left")
    x, y, size = lay["address"]
    ax.text(x, y, ADDRESS, fontproperties=fonts["label"], fontsize=px(size),
            color=c["evergreen"], va="top", ha="left")
    if "map" in lay:
        draw_map(ax, lay, c, fonts, px)
        return fig

    left, top, right, bottom = lay["strip"]
    gutter, foot = 4.2 * lay["label"], 1.9 * lay["label"]
    years = range(FIRE_FIRST_YEAR, FORECAST_YEAR + 1)
    slot = (right - left - gutter) / len(years)
    row = (bottom - foot - top) / len(ROWS)
    limit = float(np.nanmax(np.abs(table["anomaly"]))) * 1.04

    def x_of(year: int) -> float:
        return left + gutter + (year - FIRE_FIRST_YEAR) * slot

    winters = table.drop_duplicates("year").set_index("year")
    for year in years:
        if year in winters.index and winters.loc[year, "phase"] == "el_nino":
            strong = bool(winters.loc[year, "strong"])
            ax.add_patch(Rectangle((x_of(year), top), slot, bottom - foot - top,
                                   facecolor=c["enso-soft"], edgecolor="none"))
            ax.add_patch(Rectangle((x_of(year) + 1, bottom - foot + 3), slot - 2, 4,
                                   facecolor=c["enso-strong" if strong else "enso"],
                                   edgecolor="none"))
            if strong:
                ax.text(x_of(year) + slot / 2, bottom, str(year), fontproperties=fonts["label"],
                        fontsize=px(lay["label"]), color=c["ink"], va="bottom", ha="center")
    ax.add_patch(Rectangle((x_of(FORECAST_YEAR) + 1, top + 1), slot - 2, bottom - foot - top - 2,
                           facecolor="none", edgecolor=c["rule-strong"], linewidth=1,
                           linestyle=(0, (2, 2))))
    # the empty slot named, in the muted ink: no season is drawn there
    ax.text(x_of(FORECAST_YEAR) + slot / 2, bottom, str(FORECAST_YEAR),
            fontproperties=fonts["label"], fontsize=px(lay["label"]), color=c["ink-muted"],
            va="bottom", ha="center")
    for i, region in enumerate(ROWS):
        mid = top + (i + 0.5) * row
        ax.plot([left + gutter, right], [mid, mid], color=c["rule-strong"], linewidth=0.8)
        ax.text(left, mid, region, fontproperties=fonts["label"], fontsize=px(lay["label"]),
                color=c["ink-muted"], va="center", ha="left")
        g = table[(table["region"] == region) & table["anomaly"].notna()]
        for year, value in zip(g["year"], g["anomaly"]):
            tall = value / limit * (row / 2 - 2)
            ax.add_patch(Rectangle((x_of(int(year)) + 1, mid - max(tall, 0)), max(slot - 2, 1.5),
                                   max(abs(tall), 1), facecolor=c["fire"], edgecolor="none"))
    return fig


def write(out_dir: Path = figures.FIGURES, preview: Path | None = SITE_PREVIEW[1]) -> list[Path]:
    """The three banners into `out_dir`, and the site's map card to
    `preview` (None to skip it)."""
    table, paths = seasons(), []
    # matplotlib keeps a drawn font file open, which blocks its removal on
    # Windows; the copies are then left for the system to clear.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        fonts = static_fonts(Path(folder))
        for kind, theme_name in BANNERS:
            path = out_dir / f"banner_{kind}_{theme_name}.png"
            draw(table, kind, theme_name, fonts).savefig(path, dpi=DPI)
            paths.append(path)
        if preview is not None:
            draw(table, *SITE_PREVIEW[0], fonts).savefig(preview, dpi=DPI)
            paths.append(preview)
    return paths


if __name__ == "__main__":
    for written in write():
        print(f"wrote {written}")
