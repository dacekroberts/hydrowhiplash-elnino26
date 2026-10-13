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
  function pick(e) {
    var pt = e.points && e.points[0];
    var text = pt && (pt.hovertext || (pt.data.hovertext && pt.data.hovertext[pt.pointIndex]));
    if (!text) return;
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
    Plotly.react(el, fig.data, fig.layout, __CONFIG__);
    if (first) el.on("plotly_click", pick); else dim(true);
  }
  draw();
  new MutationObserver(draw).observe(document.body, {attributes: true, attributeFilter: ["class"]});
})();"""


def fragment(fig, div_id: str) -> str:
    """The chart as a page fragment: its div, its figure as JSON, and the
    script that draws it in the page's theme. The page loads plotly.js."""
    import json

    figure = fig.to_json().replace("<", "\\u003c").replace(">", "\\u003e")
    draw = (_DRAW.replace("__ID__", json.dumps(div_id))
            .replace("__SWAPS__", json.dumps(theme_swaps()))
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
    out.write_bytes(fragment(fig, div_id).encode("utf-8"))  # LF on every platform
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
