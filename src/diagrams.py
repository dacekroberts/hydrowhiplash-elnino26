"""Data-free diagrams for the explainer site, written to results/figures/.

The site only reads from results/, so every figure it shows is drawn from
code. Data figures live in src/figures.py; this module needs no data and no
geospatial imports. Run from the repo root: python -m src.diagrams

Each diagram is saved as SVG (for the page) and PNG (for reuse elsewhere).
SVG output is byte-identical between runs and machines: fixed hash salt, no
date stamp, LF line endings, and the font pinned to DejaVu Sans (bundled with
matplotlib), so global font settings elsewhere (src/figures.py sets
rcParams on import) can't change it. tests/test_diagrams.py fails when the
committed SVGs no longer match this code and src/config.py; re-run this
module and commit results/figures/ when it does.
"""
from __future__ import annotations

import io
import textwrap
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from src.config import REGIONS, RESULTS

FIGURES = RESULTS / "figures"
FONT = "DejaVu Sans"

# Colours: categorical slots 1-2 of the dataviz reference palette, validated
# as a pair on a light surface (CVD dE 24.7, normal-vision dE 33.6); the same
# orange and blue src/figures.py uses. Dry north in orange, wet south in
# blue; text stays in neutral ink.
INK = "#0b0b0b"
INK_MUTED = "#52514e"
NEUTRAL_EDGE = "#8a8984"
NEUTRAL_FILL = "#f2f2ef"
NORTH_COLOUR = "#eb6834"
SOUTH_COLOUR = "#2a78d6"

# Pathway membership for the mechanism diagram. North is every primary region;
# the south pathway is SoCal only. Every other region is named in a footnote
# by its role rather than drawn, because its expected response is not set
# before the analysis plan is frozen (DECISIONS.md, 2026-10-04 "Mechanism
# diagram").
NORTH_REGIONS = tuple(r for r, role in REGIONS.items() if role == "primary")
SOUTH_REGIONS = ("SoCal",)
UNDRAWN_REGIONS = tuple(r for r in REGIONS if r not in NORTH_REGIONS + SOUTH_REGIONS)

# Footnote wording per role: (singular noun, plural noun, singular reason,
# plural reason). A new role needs its own wording before the diagram draws.
ROLE_NOTES = {
    "contrast": ("a contrast region", "contrast regions",
                 "its expected response is", "their expected responses are"),
    "north": ("a northern region", "northern regions",
              "its hypotheses are", "their hypotheses are"),
}

# Two layouts of the same diagram. Positions are in diagram units: 0-100
# across, and 100 units per `unit_h` inches up, with the diagram drawn above
# y_cut. The footnote area below grows with its number of lines. The narrow
# layout is for phone-width pages: at 375 px the wide layout's text shrinks
# to about 6 px, the narrow one's to about 11 px.
MECHANISM_LAYOUTS = {
    "mechanism": dict(
        width=9, unit_h=7, y_cut=11.5, font=12.5, head_font=14, foot_font=10.5,
        top_w=70, top_h=8, top_ys=(92, 78), split=(74, 65),
        head_y=61.5, head_sep=": ", rule_y=58.6, cols=(26, 74),
        box_w=42, box_h=9.5, box_ys=(48, 33, 18),
        wrap_top=80, wrap_box=34, wrap_foot=70),
    "mechanism_narrow": dict(
        width=4.6, unit_h=7.8, y_cut=16.5, font=11, head_font=12, foot_font=9.5,
        top_w=92, top_h=9, top_ys=(93, 81.5), split=(77, 71.5),
        head_y=67, head_sep="\n", rule_y=62.6, cols=(25, 75),
        box_w=46, box_h=11, box_ys=(53, 38.5, 24),
        wrap_top=40, wrap_box=18, wrap_foot=50),
}

_SVG_HASHSALT = "hydrowhiplash-elnino26"


def _wrap(text: str, width: int) -> str:
    return textwrap.fill(text, width, break_on_hyphens=False)


def _tint(hex_colour: str, amount: float) -> str:
    """Mix a colour with white; amount is the share of the original colour."""
    r, g, b = mpl.colors.to_rgb(hex_colour)
    return mpl.colors.to_hex([1 - amount * (1 - c) for c in (r, g, b)])


def _box(ax, x: float, y: float, w: float, h: float, text: str, fontsize: float,
         edge: str, fill: str, weight: str = "normal") -> None:
    """Rounded box centred on (x, y) in diagram units, with centred text.

    Lines are placed one by one at a fixed spacing: matplotlib's multi-line
    text spaces lines by their own glyph heights, so a line without
    descenders sits visibly closer to the next one.
    """
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                linewidth=1.5, edgecolor=edge, facecolor=fill))
    lines = text.split("\n")
    lo, hi = ax.get_ylim()
    units_per_inch = (hi - lo) / (ax.get_position().height * ax.figure.get_figheight())
    step = 1.3 * fontsize / 72 * units_per_inch
    for i, line in enumerate(lines):
        ax.text(x, y + ((len(lines) - 1) / 2 - i) * step, line, ha="center",
                va="center_baseline", fontsize=fontsize, color=INK, fontweight=weight,
                fontfamily=FONT)


def _arrow(ax, start: tuple[float, float], end: tuple[float, float], colour: str) -> None:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=1.5,
                                mutation_scale=14, shrinkA=0, shrinkB=0))


def _save(fig: Figure, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    svg, png = out_dir / f"{stem}.svg", out_dir / f"{stem}.png"
    buf = io.StringIO()
    with mpl.rc_context({"svg.hashsalt": _SVG_HASHSALT}):
        fig.savefig(buf, format="svg", metadata={"Date": None})
    # Written with LF on every platform: savefig to a path writes CRLF on
    # Windows, while git checks the file out with LF (.gitattributes).
    svg.write_text(buf.getvalue(), encoding="utf-8", newline="\n")
    fig.savefig(png, format="png", dpi=200, metadata={"Software": None})
    return [svg, png]


def footer_lines() -> list[str]:
    """The framing line, then one note per role of the regions not drawn."""
    lines = ["Expected pathways, tested in this study."]
    by_role: dict[str, list[str]] = {}
    for region in UNDRAWN_REGIONS:
        by_role.setdefault(REGIONS[region], []).append(region)
    for role, regions in by_role.items():
        if role not in ROLE_NOTES:
            raise ValueError(f"No footnote wording for region role {role!r}; add it to "
                             f"ROLE_NOTES before drawing the mechanism diagram.")
        one, many, reason_one, reason_many = ROLE_NOTES[role]
        names = " and ".join(regions)
        if len(regions) == 1:
            lines.append(f"{names} is also analysed, as {one}; no pathway is drawn "
                         f"for it because {reason_one} not yet set.")
        else:
            lines.append(f"{names} are also analysed, as {many}; no pathway is drawn "
                         f"for them because {reason_many} not yet set.")
    return lines


def _draw_mechanism(lay: dict) -> Figure:
    footer = "\n".join(_wrap(line, lay["wrap_foot"]) for line in footer_lines())
    n_lines = footer.count("\n") + 1
    line_in = 1.4 * lay["foot_font"] / 72
    foot_in = 0.15 + n_lines * line_in + 0.2
    diagram_in = (100 - lay["y_cut"]) * lay["unit_h"] / 100
    height = diagram_in + foot_in

    fig = Figure(figsize=(lay["width"], height), facecolor="white")
    ax = fig.add_axes((0, foot_in / height, 1, diagram_in / height))
    ax.set_xlim(0, 100)
    ax.set_ylim(lay["y_cut"], 100)
    ax.axis("off")

    # Shared cause
    cause_y, jet_y = lay["top_ys"]
    _box(ax, 50, cause_y, lay["top_w"], lay["top_h"],
         _wrap("El Niño: warm water in the central-eastern tropical Pacific", lay["wrap_top"]),
         lay["font"], NEUTRAL_EDGE, NEUTRAL_FILL, weight="bold")
    _arrow(ax, (50, cause_y - lay["top_h"] / 2), (50, jet_y + lay["top_h"] / 2), NEUTRAL_EDGE)
    _box(ax, 50, jet_y, lay["top_w"], lay["top_h"],
         _wrap("Pacific jet stream extends east and shifts south", lay["wrap_top"]),
         lay["font"], NEUTRAL_EDGE, NEUTRAL_FILL)

    north_x, south_x = lay["cols"]
    columns = [
        # "often drier": the Phase 1 DJF precipitation signal is small in PNW
        # and BC and clearer in AB (docs/plan_deviations.md D19).
        (north_x, NORTH_COLOUR, "North" + lay["head_sep"] + " · ".join(NORTH_REGIONS),
         ["Milder winter, often drier", "Less snow, earlier melt",
          "Earlier or longer fire season"]),
        (south_x, SOUTH_COLOUR, "South" + lay["head_sep"] + " · ".join(SOUTH_REGIONS),
         ["Wetter winter", "More grass growth",
          "More fine fuel once grass cures, larger grass fires"]),
    ]
    box_w, box_h, box_ys = lay["box_w"], lay["box_h"], lay["box_ys"]
    split_top, split_bottom = lay["split"]
    for x, colour, header, steps in columns:
        _arrow(ax, (50 + (x - 50) * 0.25, split_top), (x, split_bottom), NEUTRAL_EDGE)
        ax.text(x, lay["head_y"], header, ha="center", va="center", fontfamily=FONT,
                fontsize=lay["head_font"], fontweight="bold", color=INK, linespacing=1.3)
        ax.plot([x - box_w / 2, x + box_w / 2], [lay["rule_y"]] * 2, color=colour,
                linewidth=3, solid_capstyle="round")
        for i, (y, step) in enumerate(zip(box_ys, steps)):
            _box(ax, x, y, box_w, box_h, _wrap(step, lay["wrap_box"]), lay["font"],
                 colour, _tint(colour, 0.12))
            if i < len(steps) - 1:
                _arrow(ax, (x, y - box_h / 2), (x, box_ys[i + 1] + box_h / 2), colour)

    fig.text(0.5, (0.2 + n_lines * line_in / 2) / height, footer, ha="center", va="center",
             fontsize=lay["foot_font"], color=INK_MUTED, linespacing=1.4, fontfamily=FONT)
    return fig


def mechanism_diagram(out_dir: Path = FIGURES) -> list[Path]:
    """Draw the two El Niño pathways in both layouts and save SVG and PNG.

    Shared cause at the top, then one chain per pathway: milder, often drier
    winter to low snowpack to an earlier or longer fire season in the north;
    wet winter to grass growth to grass fires in SoCal. No timing is stated
    for the SoCal chain, since the lag of the grass effect is an open question
    in ANALYSIS_PLAN.md. Writes mechanism.* (page width) and
    mechanism_narrow.* (phone width). Returns the paths written.
    """
    paths = []
    for stem, layout in MECHANISM_LAYOUTS.items():
        paths += _save(_draw_mechanism(layout), out_dir, stem)
    return paths


if __name__ == "__main__":
    for path in mechanism_diagram():
        print(path)
