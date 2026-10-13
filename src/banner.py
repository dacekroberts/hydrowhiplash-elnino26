"""GitHub banner images (session 12, sample visuals).

Writes to results/figures/:
  banner_social_dark.png            1280 x 640, the repository's social preview
  banner_readme_<theme>.png         1280 x 320, the README header, one per theme

Each is the question the project asks, the site's address and a motif: the
seven regions' fire seasons since FIRE_FIRST_YEAR, stacked north to south
on one scale, seasons after an El Nino winter banded. It is a motif, not a
chart: no axis and no values, so the README carries the sources' credit.

Reads the pinned, committed results/tables/fire_region_year.csv through
pin_inputs.load_input and keeps the seasons the registered tests use
(fire_figures.test_seasons), so no held-back season is drawn. No polygon is
opened. Colours come from theme/tokens.json. The design typefaces are
variable fonts, which matplotlib draws at one weight only, so fixed-weight
copies are made in a temporary folder at draw time and never committed
(SIL OFL 1.1; none of the three licences in site/fonts/ declares a
reserved font name).

Run:  python -m src.banner
"""
from __future__ import annotations

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
from matplotlib.patches import Arc, Rectangle  # noqa: E402

from src import figures, fire_figures, pin_inputs, theme  # noqa: E402
from src.config import FIRE_FIRST_YEAR, FORECAST_YEAR  # noqa: E402

DPI = 100
# Wording on the banner: the owner's choice of 2026-10-13 ("The question"),
# reworded the same day to name El Nino (owner: "we need to include el nino
# somehow"); a draft for the owner to word.
QUESTION = "Does an El Niño winter say how much the next fire season will burn?"
ADDRESS = "hydrowhiplash.dacekroberts.dev"
# Regions from north to south, the order of the rows.
ROWS = ("AK", "YT", "BC", "AB", "PNW", "NorCal", "SoCal")
# (font file in site/fonts/, weight) by role.
FACES = {"title": ("NationalPark-wght.ttf", 800), "label": ("JetBrainsMono-wght.ttf", 500)}
# Pixel layouts. title: left, top of the first line, size, line step and the
# number of lines the question is wrapped to; strip: left, top, right, bottom.
LAYOUTS = {
    "social": {"size": (1280, 640), "title": (64, 64, 58, 68, 2), "address": (64, 222, 20),
               "strip": (64, 290, 1216, 584), "label": 13, "arcs": (1250, -40)},
    "readme": {"size": (1280, 320), "title": (48, 48, 38, 46, 3), "address": (48, 216, 16),
               "strip": (560, 40, 1240, 284), "label": 11, "arcs": None},
}
BANNERS = (("social", "dark"), ("readme", "light"), ("readme", "dark"))


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

    if lay["arcs"]:  # the contour motif, clear of the strip
        for radius in range(100, 320, 44):
            ax.add_patch(Arc(lay["arcs"], 2 * radius, 2 * radius, theta1=80, theta2=200,
                             edgecolor=c["rule"], linewidth=1))
    x, y, size, step, lines = lay["title"]
    for i, line in enumerate(wrap(QUESTION, lines)):
        ax.text(x, y + i * step, line, fontproperties=fonts["title"], fontsize=px(size),
                color=c["ink"], va="top", ha="left")
    x, y, size = lay["address"]
    ax.text(x, y, ADDRESS, fontproperties=fonts["label"], fontsize=px(size),
            color=c["evergreen"], va="top", ha="left")

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


def write(out_dir: Path = figures.FIGURES) -> list[Path]:
    table, paths = seasons(), []
    # matplotlib keeps a drawn font file open, which blocks its removal on
    # Windows; the copies are then left for the system to clear.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        fonts = static_fonts(Path(folder))
        for kind, theme_name in BANNERS:
            path = out_dir / f"banner_{kind}_{theme_name}.png"
            draw(table, kind, theme_name, fonts).savefig(path, dpi=DPI)
            paths.append(path)
    return paths


if __name__ == "__main__":
    for written in write():
        print(f"wrote {written}")
