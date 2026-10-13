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
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

from src import figures, theme
from src.config import MIN_FIRE_HA, REGIONS, RESULTS

FIGURES = RESULTS / "figures"
FONT = "DejaVu Sans"

# Colours come from theme/tokens.json (D86): the light theme, and a second
# drawing per extra theme for the site's dark mode (owner, 2026-10-13; the
# files take the theme's name as a suffix). The north pathway
# runs through snowpack and takes the snow colour, the south pathway runs
# through rain and takes the water colour; the fire colour is kept for burned
# area. The two differ in lightness as well as hue (contrast 1.9:1), and each
# column is headed North or South in text. Text stays in ink.
COLOUR_TOKENS = {"INK": "ink", "INK_MUTED": "ink-muted", "NEUTRAL_EDGE": "rule-strong",
                 "NEUTRAL_FILL": "surface-sunk", "PAPER": "surface", "NORTH_COLOUR": "snow",
                 "SOUTH_COLOUR": "water"}


def _set_theme(name: str) -> None:
    """Point this module's colour constants at theme `name`; the drawing
    code reads them when it runs."""
    values = theme.colours(name)
    globals().update({const: values[token] for const, token in COLOUR_TOKENS.items()})


_set_theme(theme.themes()[0])


def _themes(stem: str):
    """Yield (theme, file stem) for every theme, with that theme's colours
    in force here and in src.figures (the credit line) while the caller
    draws: the first theme keeps `stem`, another gets `<stem>_<theme>`."""
    first = theme.themes()[0]
    for name in theme.themes():
        with figures.themed(name):
            _set_theme(name)
            try:
                yield name, stem if name == first else f"{stem}_{name}"
            finally:
                _set_theme(first)

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

# Methods flowchart (DECISIONS.md, 2026-10-08 "Site methods flowchart").
# Structure only: every label names a source, a variable or a step, and none
# carries a result, an estimate or a data value. Each column pairs a group of
# sources with the variables made from that group; arrows are drawn per
# group, not per source. Labels are short and literal; the wording is the
# owner's to change here.
FLOW_STAGES = ("Sources", "Variables")
FLOW_COLUMNS = (
    (("ONI and RONI",), ("ENSO index per winter",)),
    (("ERA5-Land", "Snow stations"), ("Winter precipitation", "Whiplash", "Snowpack")),
    (("MTBS and WFIGS", "CNFDB"), ("Burned area per region and season",)),
)
FLOW_SPINE = ("Region × year table", "Pre-registered tests", "Site charts")
# Drawn dashed, beside the tests it re-runs, not among the main sources.
FLOW_SENSITIVITY = "NBAC (sensitivity check)"
# Printed under the chart so the reading of the arrows travels with the
# image. Wording approved by the owner, 2026-10-11.
FLOW_NOTES = ("Arrows show groups, not single sources.",
              "Snow stations are used only to check the ERA5-Land snowpack.")

# Two layouts of the flowchart, in the same units as MECHANISM_LAYOUTS (0-100
# across, 100 units per `unit_h` inches down). Heights are built from the
# box sizes, so the figure grows with the tallest column. All boxes are
# neutral: teal and blue mean north and south in the mechanism diagram.
FLOW_LAYOUTS = {
    "methods_flow": dict(
        width=9, unit_h=7, font=12, head_font=12, margin=2, pad=3, head_h=5,
        gap=2.5, stage_gap=7, cols=(17.5, 50, 82.5), box_w=29, src_h=7, var_h=8.5,
        spine_x=50, spine_w=36, spine_h=7.5, side_x=85.5, side_w=25, side_h=12,
        wrap_box=24, wrap_side=16, foot_font=10.5, wrap_foot=90, note_gap=4),
    "methods_flow_narrow": dict(
        width=4.6, unit_h=7, font=10, head_font=10.5, margin=2, pad=3, head_h=5,
        gap=2.5, stage_gap=7, cols=(17.5, 50, 82.5), box_w=29, src_h=8.5, var_h=11,
        spine_x=32, spine_w=58, spine_h=7.5, side_x=83.5, side_w=29, side_h=11,
        wrap_box=13, wrap_side=12, foot_font=9.5, wrap_foot=50, note_gap=4),
}

_SVG_HASHSALT = "hydrowhiplash-elnino26"


def _wrap(text: str, width: int) -> str:
    return textwrap.fill(text, width, break_on_hyphens=False)


def _tint(hex_colour: str, amount: float) -> str:
    """Mix a colour with the paper; amount is the share of the original colour."""
    paper = mpl.colors.to_rgb(PAPER)
    return mpl.colors.to_hex([p + amount * (c - p)
                              for c, p in zip(mpl.colors.to_rgb(hex_colour), paper)])


def _box(ax, x: float, y: float, w: float, h: float, text: str, fontsize: float,
         edge: str, fill: str, weight: str = "normal",
         linestyle: str = "solid") -> None:
    """Rounded box centred on (x, y) in diagram units, with centred text.

    Lines are placed one by one at a fixed spacing: matplotlib's multi-line
    text spaces lines by their own glyph heights, so a line without
    descenders sits visibly closer to the next one.
    """
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                linewidth=1.5, edgecolor=edge, facecolor=fill,
                                linestyle=linestyle))
    lines = text.split("\n")
    lo, hi = ax.get_ylim()
    units_per_inch = (hi - lo) / (ax.get_position().height * ax.figure.get_figheight())
    step = 1.3 * fontsize / 72 * units_per_inch
    for i, line in enumerate(lines):
        ax.text(x, y + ((len(lines) - 1) / 2 - i) * step, line, ha="center",
                va="center_baseline", fontsize=fontsize, color=INK, fontweight=weight,
                fontfamily=FONT)


def _arrow(ax, start: tuple[float, float], end: tuple[float, float], colour: str,
           linestyle: str = "solid") -> None:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=colour, linewidth=1.5,
                                linestyle=linestyle, mutation_scale=14,
                                shrinkA=0, shrinkB=0))


def _save(fig: Figure, out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    figures.credit(fig, y=0.004, va="bottom")   # the canvas is saved whole, so inside it
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

    fig = Figure(figsize=(lay["width"], height), facecolor=PAPER)
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
        for _, themed_stem in _themes(stem):
            paths += _save(_draw_mechanism(layout), out_dir, themed_stem)
    return paths


def flow_labels() -> list[str]:
    """Every text label on the methods flowchart, in reading order."""
    labels = [FLOW_STAGES[0]] + [s for sources, _ in FLOW_COLUMNS for s in sources]
    labels += [FLOW_STAGES[1]] + [v for _, variables in FLOW_COLUMNS for v in variables]
    return labels + list(FLOW_SPINE) + [FLOW_SENSITIVITY] + list(FLOW_NOTES)


def _draw_flow(lay: dict) -> Figure:
    # Depths are measured down from the top edge, then flipped into axis
    # units once the total height is known.
    def stack_h(n: int, box_h: float) -> float:
        return n * box_h + (n - 1) * lay["gap"]

    panels = []  # (top, bottom, title, box height, labels per column)
    depth = lay["margin"]
    for idx, (title, box_h) in enumerate(zip(FLOW_STAGES, (lay["src_h"], lay["var_h"]))):
        stacks = [column[idx] for column in FLOW_COLUMNS]
        inner = stack_h(max(len(stack) for stack in stacks), box_h)
        bottom = depth + lay["pad"] + lay["head_h"] + inner + lay["pad"]
        panels.append((depth, bottom, title, box_h, stacks))
        depth = bottom + lay["stage_gap"]
    spine = []  # (top, bottom) of each box below the panels
    for _ in FLOW_SPINE:
        spine.append((depth, depth + lay["spine_h"]))
        depth += lay["spine_h"] + lay["stage_gap"]
    # The note sits under the chart; its height follows its line count.
    note = "\n".join(_wrap(line, lay["wrap_foot"]) for line in FLOW_NOTES)
    note_h = ((note.count("\n") + 1) * 1.4 * lay["foot_font"] / 72
              * 100 / lay["unit_h"])
    total = (depth - lay["stage_gap"] + lay["note_gap"] + note_h
             + lay["margin"])

    fig = Figure(figsize=(lay["width"], total * lay["unit_h"] / 100), facecolor=PAPER)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total)
    ax.axis("off")

    for top, bottom, title, box_h, stacks in panels:
        ax.add_patch(FancyBboxPatch((1, total - bottom), 98, bottom - top,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    linewidth=1, edgecolor=_tint(NEUTRAL_EDGE, 0.5),
                                    facecolor=PAPER))
        ax.text(3, total - (top + lay["pad"] + lay["head_h"] / 2 - 0.5), title, ha="left",
                va="center", fontsize=lay["head_font"], fontweight="bold",
                color=INK_MUTED, fontfamily=FONT)
        inner_top = top + lay["pad"] + lay["head_h"]
        inner = bottom - lay["pad"] - inner_top
        for x, stack in zip(lay["cols"], stacks):
            first = inner_top + (inner - stack_h(len(stack), box_h)) / 2 + box_h / 2
            for i, label in enumerate(stack):
                _box(ax, x, total - (first + i * (box_h + lay["gap"])), lay["box_w"], box_h,
                     _wrap(label, lay["wrap_box"]), lay["font"], NEUTRAL_EDGE, NEUTRAL_FILL)

    # Sources to variables, then variables into the table: one arrow per column.
    for upper, lower_top in ((panels[0][1], panels[1][0]), (panels[1][1], spine[0][0])):
        for x in lay["cols"]:
            _arrow(ax, (x, total - upper), (x, total - lower_top), NEUTRAL_EDGE)

    x = lay["spine_x"]
    for i, ((top, bottom), label) in enumerate(zip(spine, FLOW_SPINE)):
        # The table spans the page so that each column's arrow lands on it.
        width = 98 if i == 0 else lay["spine_w"]
        _box(ax, 50 if i == 0 else x, total - (top + bottom) / 2, width, lay["spine_h"],
             label, lay["font"], NEUTRAL_EDGE, NEUTRAL_FILL,
             weight="bold" if i == 0 else "normal")
        if i < len(spine) - 1:
            _arrow(ax, (x, total - bottom), (x, total - spine[i + 1][0]), NEUTRAL_EDGE)

    tests_y = total - sum(spine[1]) / 2
    _box(ax, lay["side_x"], tests_y, lay["side_w"], lay["side_h"],
         _wrap(FLOW_SENSITIVITY, lay["wrap_side"]), lay["font"], NEUTRAL_EDGE, PAPER,
         linestyle="dashed")
    _arrow(ax, (lay["side_x"] - lay["side_w"] / 2, tests_y),
           (x + lay["spine_w"] / 2, tests_y), NEUTRAL_EDGE, linestyle="dashed")
    ax.text(50, lay["margin"] + note_h / 2, note, ha="center", va="center",
            fontsize=lay["foot_font"], color=INK_MUTED, linespacing=1.4,
            fontfamily=FONT)
    return fig


def methods_flowchart(out_dir: Path = FIGURES) -> list[Path]:
    """Draw the methods flowchart in both layouts and save SVG and PNG.

    Sources at the top, the variables made from them, the region x year
    table, the pre-registered tests, then the site's charts; NBAC sits
    beside the tests as a sensitivity source, and a two-line note under
    the chart says how to read the arrows. Structure only: no result,
    estimate or data value is drawn, and no data is read. Writes
    methods_flow.* (page width) and methods_flow_narrow.* (phone width).
    Returns the paths written.
    """
    paths = []
    for stem, layout in FLOW_LAYOUTS.items():
        for _, themed_stem in _themes(stem):
            paths += _save(_draw_flow(layout), out_dir, themed_stem)
    return paths


# The project from its raw sources to the site's pages, grouped by stage, with
# four turns where the plan met the data (owner, 2026-10-13: "the four most
# important turns", "own page", "grouped by stage"). Each stream is: source,
# first step, the question that came up, what the answer was, what replaced
# the plan. Sources of the turns: docs/plan_deviations.md D15 and D41 (index),
# D19 (northern winter), D20 (regions), D69 (Parks Canada). No number from a
# result is drawn; the fire-size floor is read from config.
PROJECT_STREAMS = (
    ("ENSO index\nNOAA, monthly",
     "Classify every winter\nsince 1950",
     "Is ONI still\nthe index to use?",
     "No. NOAA made RONI\nits official index.",
     "RONI classifies winters;\nONI is kept as a check"),
    ("ERA5-Land\nand snow stations",
     "Regional means,\nweighted by latitude",
     "Does El Niño dry\nthe northern winter?",
     "Only faintly, in the Pacific\nNorthwest and BC.",
     "Snowpack and snowfall share\ntested too: the warm-winter path"),
    ("Region boundaries\nstates and provinces",
     "Five regions: PNW, BC,\nAB, NorCal, SoCal",
     "Do five regions\ncover the question?",
     "No. The El Niño signal\nin Alaska was worth testing.",
     "Seven regions: Alaska\nand Yukon added"),
    ("Fire perimeters\nMTBS, WFIGS, CNFDB",
     f"Burned area per season,\nfires of {MIN_FIRE_HA} ha or more",
     "Does one Canadian\nsource hold up?",
     "No. Parks Canada polygons\nare missing for six years.",
     "Four Alberta seasons flagged;\nNBAC run as a check"),
)
# One colour token per stream, by what the stream measures (owner,
# 2026-10-13): the El Nino amber, the precipitation blue for the climate
# stream (rain and snowpack), none for the regions, the burned-area red.
# The source box names each stream, so the colour is a second cue.
PROJECT_STREAM_TOKENS = ("enso", "water", None, "fire")
PROJECT_TABLE = "Region × year table\none row per region and season"
PROJECT_PLAN = "Analysis plan, frozen\nbefore any fire data was read"
PROJECT_SPINE = (("step", "Pre-registered tests,\nrun once"),
                 ("store", "Result tables\nnever edited after the run"),
                 ("step", "Figures and tables\nwritten by code to results/"),
                 ("step", "The site reads only results/"),
                 ("step", "Overview · Map · Tracker ·\nMethods and Limitations · Flowchart"))
PROJECT_NOTES = ("Slanted box: a source. Box: a step. Diamond: a turn in the project. "
                 "Cylinder: a stored table.",
                 "Amber: the El Niño index. Blue: rain and snow. Red: fire.",
                 "Four turns are shown; every departure from the plan is in the "
                 "project's deviations log.")
PROJECT_LAYOUT = {"width": 8.8, "unit": 0.088, "cols": (13.5, 38, 62, 86.5), "node_w": 22.5,
                  "font": 7.9, "foot_font": 7.6, "wrap_foot": 104}


def _lines(ax, x: float, y: float, text: str, fontsize: float, weight: str = "normal",
           colour: str | None = None) -> None:
    """Centred text, one line at a time at a fixed spacing (as in _box)."""
    lines = text.split("\n")
    lo, hi = ax.get_ylim()
    units_per_inch = (hi - lo) / (ax.get_position().height * ax.figure.get_figheight())
    step = 1.3 * fontsize / 72 * units_per_inch
    for i, line in enumerate(lines):
        ax.text(x, y + ((len(lines) - 1) / 2 - i) * step, line, ha="center",
                va="center_baseline", fontsize=fontsize, color=colour or INK,
                fontweight=weight, fontfamily=FONT)


def _node(ax, kind: str, x: float, y: float, w: float, h: float, text: str, fontsize: float,
          weight: str = "normal", colour: str | None = None) -> None:
    """One flowchart node centred on (x, y). `kind`: "source" (slanted box),
    "step" (box), "turn" (diamond) or "store" (cylinder). The shape carries
    the kind, so it does not rest on colour. `colour` draws the edge in a
    stream's colour over a light tint of it; without it the node is neutral."""
    left, right, low, high = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    edge = colour or NEUTRAL_EDGE
    fill = _tint(colour, 0.12) if colour else NEUTRAL_FILL
    style = dict(linewidth=1.5, edgecolor=edge, facecolor=fill)
    if kind == "step":
        _box(ax, x, y, w, h, text, fontsize, edge, fill, weight=weight)
        return
    if kind == "source":
        skew = 1.6
        ax.add_patch(Polygon([(left + skew, high), (right + skew, high), (right - skew, low),
                              (left - skew, low)], closed=True, joinstyle="round", **style))
    elif kind == "turn":
        ax.add_patch(Polygon([(x, high), (right, y), (x, low), (left, y)], closed=True,
                             joinstyle="round", **{**style, "facecolor": PAPER, "linewidth": 2.0}))
    elif kind == "store":
        cap = 1.3  # half-height of the cylinder's top and bottom ellipses
        ax.add_patch(Ellipse((x, low + cap), w, 2 * cap, **style))
        ax.add_patch(Rectangle((left, low + cap), w, h - 2 * cap, linewidth=0,
                               facecolor=fill))
        for side in (left, right):
            ax.plot([side, side], [low + cap, high - cap], color=edge, linewidth=1.5,
                    solid_capstyle="butt")
        ax.add_patch(Ellipse((x, high - cap), w, 2 * cap, **style))
        y -= cap / 2
    else:
        raise ValueError(f"No flowchart shape for kind {kind!r}.")
    _lines(ax, x, y, text, fontsize, weight)


def project_labels() -> list[str]:
    """Every label of the project flowchart, in reading order (for tests and
    for the page's alt text)."""
    labels = [text.replace("\n", " ") for stream in PROJECT_STREAMS for text in stream]
    labels += [PROJECT_TABLE.replace("\n", " "), PROJECT_PLAN.replace("\n", " ")]
    return labels + [text.replace("\n", " ") for _, text in PROJECT_SPINE] + list(PROJECT_NOTES)


def _draw_project(lay: dict) -> Figure:
    note = "\n".join(_wrap(line, lay["wrap_foot"]) for line in PROJECT_NOTES)
    # Depths down from the top edge, in units; one unit is lay["unit"] inches
    # both ways, so shapes keep their proportions.
    rows = {"source": 5.5, "step": 16, "turn": 31.5, "answer": 43.5, "fix": 53, "table": 67}
    spine_first, spine_step = 80, 12.5
    total = spine_first + spine_step * (len(PROJECT_SPINE) - 1) + 14
    fig = Figure(figsize=(lay["width"], total * lay["unit"]), facecolor=PAPER)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total)
    ax.axis("off")

    def at(depth: float) -> float:
        return total - depth

    w, font = lay["node_w"], lay["font"]
    values = theme.colours(figures.THEME)
    for x, token, (source, step, turn, answer, fix) in zip(lay["cols"], PROJECT_STREAM_TOKENS,
                                                           PROJECT_STREAMS):
        colour = values[token] if token else None
        line = colour or NEUTRAL_EDGE
        _node(ax, "source", x, at(rows["source"]), w - 3, 6.5, source, font, weight="bold",
              colour=colour)
        _arrow(ax, (x, at(rows["source"] + 3.25)), (x, at(rows["step"] - 3.5)), line)
        _node(ax, "step", x, at(rows["step"]), w, 7, step, font, colour=colour)
        _arrow(ax, (x, at(rows["step"] + 3.5)), (x, at(rows["turn"] - 8.5)), line)
        _node(ax, "turn", x, at(rows["turn"]), w - 1, 17, turn, font, weight="bold",
              colour=colour)
        _lines(ax, x, at(rows["answer"]), answer, font, colour=INK_MUTED)
        _arrow(ax, (x, at(rows["answer"] + 2.6)), (x, at(rows["fix"] - 3.75)), line)
        _node(ax, "step", x, at(rows["fix"]), w, 7.5, fix, font, colour=colour)
        _arrow(ax, (x, at(rows["fix"] + 3.75)), (x, at(rows["table"] - 4.4)), line)
    # the table spans the page so that each stream's arrow lands on it
    _node(ax, "store", 50, at(rows["table"]), 96, 9.5, PROJECT_TABLE, font, weight="bold")
    _arrow(ax, (50, at(rows["table"] + 4.75)), (50, at(spine_first - 3.5)), NEUTRAL_EDGE)
    for i, (kind, text) in enumerate(PROJECT_SPINE):
        depth = spine_first + i * spine_step
        height = 8.5 if kind == "store" else 7
        _node(ax, kind, 50, at(depth), 36, height, text, font)
        if i < len(PROJECT_SPINE) - 1:
            _arrow(ax, (50, at(depth + height / 2)), (50, at(depth + spine_step - 3.5
                                                          - (0.75 if PROJECT_SPINE[i + 1][0] == "store" else 0))),
                   NEUTRAL_EDGE)
    # the frozen plan enters at the tests, from the side
    _box(ax, 84, at(spine_first), 26, 7, PROJECT_PLAN, font, NEUTRAL_EDGE, PAPER,
         linestyle="dashed")
    _arrow(ax, (71, at(spine_first)), (68, at(spine_first)), NEUTRAL_EDGE, linestyle="dashed")
    ax.text(50, 5.2, note, ha="center", va="center", fontsize=lay["foot_font"],
            color=INK_MUTED, linespacing=1.4, fontfamily=FONT)
    return fig


def project_flowchart(out_dir: Path = FIGURES) -> list[Path]:
    """Draw the whole-project flowchart and save SVG and PNG, once per theme.

    Four streams (index, climate, regions, fire), each with the turn it took,
    meet in the region x year table; below it the frozen plan and the tests,
    the result tables, the figures and the site's pages. Structure only: no
    result is drawn and no data is read. One layout: it is taller than it is
    wide and is scaled to the page's width. Returns the paths written.
    """
    paths = []
    for _, themed_stem in _themes("project_flow"):
        paths += _save(_draw_project(PROJECT_LAYOUT), out_dir, themed_stem)
    return paths


# Every diagram this module writes; tests/test_diagrams.py checks each one.
DIAGRAMS = (mechanism_diagram, methods_flowchart, project_flowchart)


if __name__ == "__main__":
    for diagram in DIAGRAMS:
        for path in diagram():
            print(path)
