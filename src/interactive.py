"""Interactive region panels for the site (Plotly), one builder for every
chart of the kind "one panel per region, every year, El Nino winters
marked".

Each chart is written as an HTML fragment (one div, no library) that a site
page includes as is. The page loads plotly.js once, from the copy bundled
with the site (site/libs/plotly.min.js, written here from the installed
plotly package; MIT licence, stated in the file's first lines), so a
reader's browser contacts no third party (owner, 2026-10-12). Every panel carries its own year labels,
the chart has an x-axis title, a y-axis title per panel and one legend
(owner, 2026-10-12: "we need some sort of static year labelling", "legend
for each section", "y-axis label should exist, as should x-axis label").
Drawn in the light theme on the `surface` ground, like the PNG figures.

  winter_rain_html(table)  December to February precipitation per region,
                           every winter, as a departure from the region's
                           mean over the winters shown

Run:  python -m src.interactive
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from src import figures, theme
from src.config import ENSO_INDEX, REGIONS

PANEL_HEIGHT = 200  # px per region panel, tick labels included
RAIN_TABLE = "climate_controls_region_year.csv"
PLOTLY_LIB = Path(__file__).resolve().parents[1] / "site" / "libs" / "plotly.min.js"


def write_plotly_lib(out: Path = PLOTLY_LIB) -> Path:
    """The plotly.js that matches the installed plotly package, for the
    site to serve itself. Rewrite it whenever that package changes."""
    from plotly.offline import get_plotlyjs

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(get_plotlyjs().encode("utf-8"))
    return out
RAIN_VALUE = "precip_djf_mm"
READOUT_HINT = "Tap or click a bar to keep its details here."
# Shown under a chart's year slider on a phone before a year is chosen; a
# draft for the owner (2026-10-13).
YEAR_HINT = "Slide to a year, or tap a bar, to read every region."
# a picked bar stays as drawn; the panel's other bars fade to this
UNPICKED_OPACITY = 0.3


def theme_swaps() -> dict[str, dict[str, str]]:
    """For every theme after the first: the first theme's value of each
    colour token a chart can use, mapped to that theme's value. The page
    script recolours a chart with it when the reader's theme changes."""
    names = theme.themes()
    tokens = [*figures.COLOUR_TOKENS.values(), *figures.FAMILY_TOKENS]
    first = theme.colours(names[0])
    swaps = {}
    for name in names[1:]:
        other = theme.colours(name)
        swap = {first[t].lower(): other[t] for t in tokens}
        if len(swap) != len(tokens):  # two tokens share a first-theme value
            raise ValueError(f"Chart colours of theme {names[0]} are not distinct.")
        swaps[name] = swap
    return swaps


# Draws the chart from the JSON beside it, in the page's theme, and again
# when the theme changes. The JSON holds the first theme's colours; another
# theme's are put in by replacing each six-digit hex colour in its text.
# A click or a tap on a bar keeps its details in the readout under the
# chart, which stays at the bottom left of the screen while the chart is in
# view, and dims the panel's other bars (owner, 2026-10-13: hover is hard on
# a phone). The same bar again, or the readout, lets go.
# Where the device has no hover (a phone) the bars are too narrow to tap
# reliably (owner, 2026-10-13), so a year slider stands in for the readout:
# it marks one year in every panel and lists each region's value for it. A
# tap on a bar moves the slider to that bar's year. Each hover string is
# read as "<b>label</b> · value<br>comparison<br>winter class".
_DRAW = """(function () {
  var el = document.getElementById(__ID__), swaps = __SWAPS__, shown = null;
  var out = document.getElementById(__ID__ + "-readout"), hint = out.textContent, picked = null;
  function plain(s) { return String(s).replace(/<[^>]*>/g, ""); }
  function dim(on) {
    if (picked && picked[2]) Plotly.restyle(el, {selectedpoints: [on ? [picked[1]] : null]}, [picked[0]]);
  }
  function release() {
    dim(false);
    picked = null;
    out.textContent = hint;
    out.classList.remove("on");
  }
  var series = __SERIES__, marks = __MARKS__, years = [], year = null, texts = {};
  var touch = window.matchMedia && window.matchMedia("(hover: none)").matches;
  series.forEach(function (s) { s.x.forEach(function (y) { if (years.indexOf(y) < 0) years.push(y); }); });
  years.sort(function (a, b) { return a - b; });
  var yearBox = document.createElement("div");
  yearBox.className = "chart-year";
  yearBox.innerHTML = '<div class="cy-step"><button type="button" aria-label="Earlier year">\u2039</button>' +
    '<span class="cy-y" aria-live="polite"></span><button type="button" aria-label="Later year">\u203a</button>' +
    '<button type="button" class="cy-all">All years</button></div><div class="cy-slide">' +
    '<input type="range" min="0" step="1" aria-label="Year"><div class="cy-marks"></div></div>' +
    '<p class="cy-when"></p><ul class="cy-list"></ul>';
  el.parentNode.insertBefore(yearBox, out.nextSibling);
  var buttons = yearBox.querySelectorAll("button"), slide = yearBox.querySelector("input");
  var shownYear = yearBox.querySelector(".cy-y"), when = yearBox.querySelector(".cy-when");
  var list = yearBox.querySelector(".cy-list");
  slide.max = years.length - 1;
  slide.value = years.length - 1;
  [["nino", marks.nino], ["strong", marks.strong]].forEach(function (kind) {
    kind[1].forEach(function (y) {
      var k = years.indexOf(y), mark = document.createElement("i");
      if (k < 0) return;
      mark.className = kind[0];
      mark.style.left = (100 * k / Math.max(1, years.length - 1)) + "%";
      yearBox.querySelector(".cy-marks").appendChild(mark);
    });
  });
  function bars() { return series.filter(function (s) { return s.bar; }).map(function (s) { return s.i; }); }
  function allYears() {
    year = null;
    Plotly.restyle(el, {selectedpoints: bars().map(function () { return null; })}, bars());
    shownYear.textContent = "";
    when.textContent = __YEAR_HINT__;
    list.textContent = "";
  }
  function showYear(y) {
    year = y;
    var chosen = [], label = "", rows = [];
    series.forEach(function (s) {
      var k = s.x.indexOf(y), text = k < 0 ? null : texts[s.i] && texts[s.i][k];
      if (s.bar) chosen.push(k < 0 ? [] : [k]);
      if (!text) return;
      var lines = String(text).split("<br>").map(plain), head = lines[0].split(" \u00b7 ");
      if (!label && lines[2]) label = [head[0] === String(y) ? "" : head[0], lines[2]].filter(Boolean).join(" \u00b7 ");
      rows.push([s.name, [head.slice(1).join(" \u00b7 "), lines[1] || ""].filter(Boolean).join(", ")]);
    });
    Plotly.restyle(el, {selectedpoints: chosen}, bars());
    slide.value = years.indexOf(y);
    shownYear.textContent = y;
    when.textContent = label;
    list.textContent = "";
    rows.forEach(function (row) {
      var item = document.createElement("li"), name = document.createElement("b"), value = document.createElement("span");
      name.textContent = row[0];
      value.textContent = row[1];
      item.appendChild(name);
      item.appendChild(value);
      list.appendChild(item);
    });
  }
  function step(by) {
    var k = year === null ? years.length - 1 : Math.min(years.length - 1, Math.max(0, years.indexOf(year) + by));
    showYear(years[k]);
  }
  slide.addEventListener("input", function () { showYear(years[+slide.value]); });
  buttons[0].addEventListener("click", function () { step(-1); });
  buttons[1].addEventListener("click", function () { step(year === null ? 0 : 1); });
  buttons[2].addEventListener("click", allYears);
  function pick(e) {
    var pt = e.points && e.points[0];
    var text = pt && (pt.hovertext || (pt.data.hovertext && pt.data.hovertext[pt.pointIndex]));
    if (!text) return;
    if (touch) { showYear(+pt.x); return; }
    var same = picked && picked[0] === pt.curveNumber && picked[1] === pt.pointIndex;
    release();
    if (same) return;
    picked = [pt.curveNumber, pt.pointIndex, pt.data.type === "bar"];
    dim(true);
    out.textContent = "";
    [pt.data.name || ""].concat(String(text).split("<br>")).forEach(function (line, i) {
      var part = document.createElement(i ? "span" : "strong");
      part.textContent = plain(line);
      out.appendChild(part);
    });
    out.classList.add("on");
  }
  out.addEventListener("click", release);
  var source = document.getElementById(__ID__ + "-figure").textContent;
  function scheme() {
    for (var name in swaps) if (document.body.classList.contains("quarto-" + name)) return name;
    return "";
  }
  function draw() {
    var name = scheme(), first = shown === null;
    if (name === shown) return;
    shown = name;
    var text = !name ? source : source.replace(/#[0-9a-fA-F]{6}(?![0-9a-fA-F])/g, function (hex) {
      return swaps[name][hex.toLowerCase()] || hex;
    });
    var fig = JSON.parse(text);
    series.forEach(function (s) { texts[s.i] = fig.data[s.i].hovertext; });
    Plotly.react(el, fig.data, fig.layout, __CONFIG__);
    if (first) { el.on("plotly_click", pick); allYears(); }
    else if (year !== null) showYear(year);
    else dim(true);
  }
  draw();
  new MutationObserver(draw).observe(document.body, {attributes: true, attributeFilter: ["class"]});
})();"""


def year_series(fig) -> list[dict]:
    """The traces a year can be read from, for the phone's year slider:
    each trace with hover text, as its index in the figure, whether it is
    a bar, its years and its region (the trace name up to its first dot)."""
    return [{"i": i, "bar": trace.type == "bar", "x": [int(year) for year in trace.x],
             "name": str(trace.name).split(" \u00b7 ")[0]}
            for i, trace in enumerate(fig.data)
            if trace.hovertext is not None and trace.x is not None and len(trace.x)
            and trace.x[0] is not None]


def fragment(fig, div_id: str, marks: dict | None = None) -> str:
    """The chart as a page fragment: its div, its figure as JSON, and the
    script that draws it in the page's theme. The page loads plotly.js.
    `marks` holds the years ticked on the phone's year slider: `nino` and
    `strong`, lists of years."""
    import json

    figure = fig.to_json().replace("<", "\\u003c").replace(">", "\\u003e")
    draw = (_DRAW.replace("__ID__", json.dumps(div_id))
            .replace("__SWAPS__", json.dumps(theme_swaps()))
            .replace("__SERIES__", json.dumps(year_series(fig)))
            .replace("__MARKS__", json.dumps(marks or {"nino": [], "strong": []}))
            .replace("__YEAR_HINT__", json.dumps(YEAR_HINT))
            .replace("__CONFIG__", json.dumps({"displayModeBar": False, "responsive": True})))
    # one box around the chart and its readout: the readout sticks inside it
    return (f'<div class="chart-box">\n<div id="{div_id}" class="plotly-graph-div" '
            f'style="height:{int(fig.layout.height)}px; width:100%;"></div>\n'
            f'<p id="{div_id}-readout" class="chart-readout" aria-live="polite">{READOUT_HINT}</p>\n'
            f'<script type="application/json" id="{div_id}-figure">{figure}</script>\n'
            f'<script>{draw}</script>\n</div>\n')


def winter_words(phase: str, strong: bool) -> str:
    if phase == "el_nino":
        return "strong El Niño winter" if strong else "El Niño winter"
    return "La Niña winter" if phase == "la_nina" else "neutral winter"


def panels(groups: list[dict], colour: str, bar_label: str, y_title: str, x_title: str,
           x_range: tuple[float, float], out: Path, div_id: str,
           slot_year: int | None = None, slot_label: str = "",
           missing_label: str = "") -> Path:
    """Write one chart. Each group is one region's panel:
    title, years, values, hover (one string per year), nino (frame with
    year and strong), lim (half-height of the y range), tickvals, ticktext,
    and optionally missing (years drawn as a marker, with missing_hover)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=len(groups), cols=1, shared_xaxes=False, vertical_spacing=0.055,
                        subplot_titles=[g["title"] for g in groups])
    for row, g in enumerate(groups, start=1):
        lim = g["lim"]
        name = re.sub(r"<[^>]*>", "", g["title"])  # the readout's first line
        fig.add_bar(x=g["years"], y=g["values"], marker_color=colour, marker_line_width=0,
                    hovertext=g["hover"], hoverinfo="text", showlegend=False, name=name,
                    selected={"marker": {"opacity": 1}},
                    unselected={"marker": {"opacity": UNPICKED_OPACITY}}, row=row, col=1)
        nino = g["nino"]
        for year in nino["year"]:
            fig.add_vrect(x0=year - 0.5, x1=year + 0.5, fillcolor=figures.ENSO_SOFT,
                          line_width=0, layer="below", row=row, col=1)
        for strong, tick, size in ((False, figures.ENSO, 9), (True, figures.ENSO_STRONG, 14)):
            marked = nino[nino["strong"] == strong]
            fig.add_scatter(x=marked["year"], y=[lim * 0.93] * len(marked), mode="markers",
                            marker={"symbol": "line-ns", "size": size,
                                    "line": {"width": 3 if strong else 2, "color": tick}},
                            hoverinfo="skip", showlegend=False, row=row, col=1)
        missing = list(g.get("missing", []))
        if missing:
            fig.add_scatter(x=missing, y=[-lim * 0.9] * len(missing), mode="markers",
                            marker={"symbol": "triangle-down", "size": 9, "color": figures.MUTED},
                            hovertext=g["missing_hover"], hoverinfo="text", showlegend=False,
                            name=name, row=row, col=1)
        if slot_year is not None:
            fig.add_vrect(x0=slot_year - 0.5, x1=slot_year + 0.5, fillcolor="rgba(0,0,0,0)",
                          line={"width": 1, "dash": "dot", "color": figures.AXIS}, row=row, col=1)
        fig.update_yaxes(range=[-lim, lim], tickvals=g["tickvals"], ticktext=g["ticktext"],
                         title_text=y_title, row=row, col=1)
    # the legend: entries drawn off the data, so a click hides nothing
    key = {"x": [None], "y": [None], "hoverinfo": "skip", "showlegend": True}
    fig.add_bar(marker_color=colour, name=bar_label, **key)
    fig.add_scatter(mode="markers", name="El Niño winter (shaded year)",
                    marker={"symbol": "square", "size": 12, "color": figures.ENSO_SOFT,
                            "line": {"width": 1, "color": figures.ENSO}}, **key)
    fig.add_scatter(mode="markers", name="Strong El Niño (darker tick)",
                    marker={"symbol": "line-ns", "size": 13,
                            "line": {"width": 3, "color": figures.ENSO_STRONG}}, **key)
    if missing_label:
        fig.add_scatter(mode="markers", name=missing_label,
                        marker={"symbol": "triangle-down", "size": 9, "color": figures.MUTED},
                        **key)
    if slot_year is not None:
        fig.add_scatter(mode="lines", name=slot_label,
                        line={"width": 1, "dash": "dot", "color": figures.AXIS}, **key)
    fig.update_yaxes(gridcolor=figures.GRID, zerolinecolor=figures.INK, zerolinewidth=1,
                     tickfont={"size": 11, "color": figures.MUTED}, fixedrange=True,
                     title_font={"size": 11, "color": figures.MUTED}, title_standoff=6)
    fig.update_xaxes(range=list(x_range), showgrid=False, dtick=5, showticklabels=True,
                     ticks="outside", ticklen=3, tickcolor=figures.AXIS,
                     tickfont={"size": 11, "color": figures.MUTED}, linecolor=figures.AXIS,
                     fixedrange=True)
    fig.update_xaxes(title_text=x_title, title_font={"size": 12, "color": figures.INK},
                     row=len(groups), col=1)
    fig.update_annotations(font={"size": 13, "color": figures.INK}, x=0, xanchor="left")
    fig.update_layout(height=PANEL_HEIGHT * len(groups) + 110, bargap=0.2, hovermode="closest",
                      paper_bgcolor=figures.GROUND, plot_bgcolor=figures.GROUND,
                      font={"family": theme.families()["sans"], "color": figures.INK},
                      hoverlabel={"bgcolor": figures.GROUND, "font": {"color": figures.INK}},
                      legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.0,
                              "yanchor": "bottom", "yref": "container", "font": {"size": 12},
                              "itemclick": False, "itemdoubleclick": False,
                              "bgcolor": "rgba(0,0,0,0)"},
                      margin={"l": 64, "r": 12, "t": 96, "b": 54})
    fig.update_layout(legend={"y": 0.995, "yanchor": "top"})
    out.parent.mkdir(parents=True, exist_ok=True)
    nino = groups[0]["nino"]
    marks = {kind: [int(year) for year in nino[nino["strong"] == strong]["year"]]
             for kind, strong in (("nino", False), ("strong", True))}
    out.write_bytes(fragment(fig, div_id, marks).encode("utf-8"))  # LF on every platform
    return out


def winter_rain_html(table: pd.DataFrame, out_dir: Path = figures.FIGURES) -> Path:
    """Every winter's December to February precipitation per region, as a
    percent departure from the region's mean over the winters in `table`
    (raw values, not detrended: the trend rule's "raw values in figures").
    Hover gives the millimetres and the winter's ENSO class."""
    order = {region: i for i, region in enumerate(REGIONS)}
    table = table.dropna(subset=[RAIN_VALUE]).sort_values("year")
    groups = []
    for region in sorted(table["region"].unique(), key=order.get):
        g = table[table["region"] == region]
        mean = float(g[RAIN_VALUE].mean())
        pct = 100 * (g[RAIN_VALUE] / mean - 1)
        lim = float(np.ceil(np.abs(pct).max() * 1.25 / 25) * 25)
        step = 50 if lim > 100 else 25
        ticks = [t for t in range(-int(lim), int(lim) + 1, step) if abs(t) < lim]
        hover = [f"<b>Winter {int(y) - 1}-{int(y) % 100:02d}</b> · {mm:,.0f} mm"
                 f"<br>{100 + p:.0f}% of the average winter"
                 f"<br>{winter_words(ph, bool(s))} (DJF {ENSO_INDEX} {e:+.2f})"
                 for y, mm, p, ph, s, e in zip(g["year"], g[RAIN_VALUE], pct, g["phase"],
                                               g["strong"], g["enso_djf"])]
        groups.append({"title": f"<b>{region}</b> · average winter {mean:,.0f} mm",
                       "years": g["year"], "values": pct, "hover": hover,
                       "nino": g[g["phase"] == "el_nino"], "lim": lim, "tickvals": ticks,
                       "ticktext": [f"{t:+d}%" if t else "average" for t in ticks]})
    years = table["year"]
    return panels(groups, figures.FAMILIES["water"], "December to February precipitation",
                  "vs average winter",
                  "Winter, labelled by its January year (1998 is December 1997 to February 1998)",
                  (int(years.min()) - 1, int(years.max()) + 1),
                  out_dir / f"djf_precip_history_{ENSO_INDEX.lower()}.html", "winter-rain-history")


def main() -> None:
    from src import pin_inputs

    print(f"wrote {winter_rain_html(pin_inputs.load_input(RAIN_TABLE))}")
    print(f"wrote {write_plotly_lib()}")


if __name__ == "__main__":
    main()
