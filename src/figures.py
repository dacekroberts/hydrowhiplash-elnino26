"""Figures for the explainer site, written to results/figures/.

The site only reads from results/, so every figure it shows is drawn here
from code. Run from the repo root: python -m src.figures

Each figure is saved as SVG (for the page) and PNG (for reuse elsewhere).
SVG output is byte-identical between runs (fixed hash salt, no date stamp),
so a later drift check can compare committed figures with regenerated ones.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from src.config import REGIONS, RESULTS

FIGURES = RESULTS / "figures"

# Colours: categorical slots 1-2 of the dataviz reference palette, validated
# as a pair on a light surface (CVD dE 24.7, normal-vision dE 33.6). Dry
# north in orange, wet south in blue; text stays in neutral ink.
INK = "#0b0b0b"
INK_MUTED = "#52514e"
NEUTRAL_EDGE = "#8a8984"
NEUTRAL_FILL = "#f2f2ef"
NORTH_COLOUR = "#eb6834"
SOUTH_COLOUR = "#2a78d6"

# Pathway membership for the mechanism diagram. North is every primary region;
# the south pathway is SoCal only. Regions in neither are named in a footnote
# rather than drawn, because their expected response is not set before the
# analysis plan is frozen (DECISIONS.md, 2026-10-04 "Mechanism diagram").
NORTH_REGIONS = tuple(r for r, role in REGIONS.items() if role == "primary")
SOUTH_REGIONS = ("SoCal",)
UNDRAWN_REGIONS = tuple(r for r in REGIONS if r not in NORTH_REGIONS + SOUTH_REGIONS)

_SVG_HASHSALT = "hydrowhiplash-elnino26"


def _tint(hex_colour: str, amount: float) -> str:
    """Mix a colour with white; amount is the share of the original colour."""
    r, g, b = mpl.colors.to_rgb(hex_colour)
    return mpl.colors.to_hex([1 - amount * (1 - c) for c in (r, g, b)])


def _box(ax, x: float, y: float, w: float, h: float, text: str,
         edge: str, fill: str, weight: str = "normal") -> None:
    """Rounded box centred on (x, y) in axes data units, with centred text."""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                linewidth=1.5, edgecolor=edge, facecolor=fill))
    ax.text(x, y, text, ha="center", va="center", fontsize=12.5, color=INK,
            fontweight=weight, linespacing=1.3)


def _arrow(ax, start: tuple[float, float], end: tuple[float, float], colour: str) -> None:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=1.5,
                                mutation_scale=14, shrinkA=0, shrinkB=0))


def _save(fig: Figure, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    svg, png = out_dir / f"{stem}.svg", out_dir / f"{stem}.png"
    with mpl.rc_context({"svg.hashsalt": _SVG_HASHSALT}):
        fig.savefig(svg, format="svg", metadata={"Date": None})
    fig.savefig(png, format="png", dpi=200, metadata={"Software": None})
    return [svg, png]


def mechanism_diagram(out_dir: Path = FIGURES) -> list[Path]:
    """Draw the two El Niño pathways and save mechanism.svg and mechanism.png.

    Shared cause at the top, then one chain per pathway: dry, mild winter to
    low snowpack to an earlier or longer fire season in the north; wet winter
    to grass growth to grass fires in SoCal. No timing is stated for the
    SoCal chain, since the lag of the grass effect is an open question in
    ANALYSIS_PLAN.md. Returns the paths written.
    """
    fig = Figure(figsize=(9, 7), facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Shared cause
    _box(ax, 50, 92, 70, 8, "El Niño: warm water in the central-eastern tropical Pacific",
         NEUTRAL_EDGE, NEUTRAL_FILL, weight="bold")
    _arrow(ax, (50, 88), (50, 82), NEUTRAL_EDGE)
    _box(ax, 50, 78, 70, 8, "Pacific jet stream extends east and shifts south",
         NEUTRAL_EDGE, NEUTRAL_FILL)

    columns = [
        (26, NORTH_COLOUR, "North: " + " · ".join(NORTH_REGIONS),
         ["Drier, milder winter", "Less snow, earlier melt",
          "Earlier or longer fire season"]),
        (74, SOUTH_COLOUR, "South: " + " · ".join(SOUTH_REGIONS),
         ["Wetter winter", "More grass growth",
          "More fine fuel once grass cures,\nlarger grass fires"]),
    ]
    box_w, box_h, step_ys = 42, 9.5, (48, 33, 18)
    for x, colour, header, steps in columns:
        _arrow(ax, (50 + (x - 50) * 0.25, 74), (x, 65), NEUTRAL_EDGE)
        ax.text(x, 61.5, header, ha="center", va="center", fontsize=14,
                fontweight="bold", color=INK)
        ax.plot([x - box_w / 2, x + box_w / 2], [58.6, 58.6], color=colour,
                linewidth=3, solid_capstyle="round")
        for i, (y, step) in enumerate(zip(step_ys, steps)):
            _box(ax, x, y, box_w, box_h, step, colour, _tint(colour, 0.12))
            if i < len(steps) - 1:
                _arrow(ax, (x, y - box_h / 2), (x, step_ys[i + 1] + box_h / 2), colour)

    footer = ["Expected pathways, tested in this study."]
    if UNDRAWN_REGIONS:
        names = " and ".join(UNDRAWN_REGIONS)
        if len(UNDRAWN_REGIONS) == 1:
            words = ("is", "a contrast region", "it", "its expected response is")
        else:
            words = ("are", "contrast regions", "them", "their expected responses are")
        footer.append("{} {} also analysed, as {}; no pathway is drawn for {} because "
                      "{} not yet set.".format(names, *words))
    ax.text(50, 5.5, "\n".join(textwrap.fill(line, 70) for line in footer),
            ha="center", va="center", fontsize=10.5, color=INK_MUTED, linespacing=1.4)

    return _save(fig, out_dir, "mechanism")


if __name__ == "__main__":
    for path in mechanism_diagram():
        print(path)
