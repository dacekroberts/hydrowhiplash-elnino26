"""Full-record view of burned area (ACTION_PLAN Phase 4).

Writes to results/figures/:
  burned_area_anomaly_series_<index>.png   every fire season per region since
      1984 as its departure from the region's mean log burned area, seasons
      after an El Nino winter highlighted
  burned_area_season_history_<index>.html  the same record as an interactive
      chart for the site (hover per season, an empty slot for FORECAST_YEAR)

Reads the pinned, committed results/tables/fire_region_year.csv through
pin_inputs.load_input, the table the registered tests read, and keeps the
seasons the tests use (FIRE_FIRST_YEAR to FIRE_LAST_YEAR_BY_REGION). No
polygon is opened and nothing here is a test: values are raw, not detrended.
First built 2026-10-12, after the registered runs were committed (D62: no
view sets burned area beside ENSO before then).

Run:  python -m src.fire_figures
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import figures, pin_inputs, theme
from src.config import (ENSO_INDEX, FIRE_FIRST_YEAR, FIRE_LAST_YEAR_BY_REGION, FORECAST_YEAR,
                        MIN_FIRE_HA, REGIONS, RESULTS)

FIRE_TABLE = RESULTS / "tables" / "fire_region_year.csv"


def test_seasons(fire: pd.DataFrame) -> pd.DataFrame:
    """The region-seasons the registered tests use, regions in display order."""
    last = fire["region"].map(FIRE_LAST_YEAR_BY_REGION)
    out = fire[(fire["year"] >= FIRE_FIRST_YEAR) & (fire["year"] <= last)].copy()
    order = {region: i for i, region in enumerate(REGIONS)}
    return out.sort_values(["region", "year"], key=lambda s: s.map(order) if s.name == "region"
                           else s).reset_index(drop=True)


def series_figure(fire: pd.DataFrame, out_dir: Path = figures.FIGURES) -> Path:
    return figures.fire_season_series(
        test_seasons(fire), ENSO_INDEX,
        out_dir / f"burned_area_anomaly_series_{ENSO_INDEX.lower()}.png")


def history_html(fire: pd.DataFrame, out_dir: Path = figures.FIGURES) -> Path:
    """The same full record as an interactive chart for the site: one panel
    per region, hover gives the season's burned area and its winter, and an
    empty outlined slot marks FORECAST_YEAR. Written as an HTML fragment (one
    div; plotly.js loaded from its CDN) that a site page includes as is.
    Drawn in the light theme on the `surface` ground, like the PNG figures."""
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    table = figures.season_anomaly(test_seasons(fire))
    regions = list(dict.fromkeys(table["region"]))
    typical = {r: float(np.expm1(g.loc[g["anomaly"].notna(), "log_burn"].mean()))
               for r, g in table.groupby("region", sort=False)}
    fig = make_subplots(rows=len(regions), cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        subplot_titles=[f"<b>{r}</b> · typical season {typical[r]:,.0f} ha"
                                        for r in regions])
    for row, region in enumerate(regions, start=1):
        g = table[table["region"] == region].sort_values("year")
        burned = g[g["anomaly"].notna()]
        lim = float(np.nanmax(np.abs(g["anomaly"])) * 1.25)
        winter = np.where(burned["strong"] & (burned["phase"] == "el_nino"),
                          "after a strong El Niño winter",
                          np.where(burned["phase"] == "el_nino", "after an El Niño winter",
                                   "not after an El Niño winter"))
        hover = [f"<b>{int(y)}</b> · {ha:,.0f} ha<br>{np.exp(a):.2g} times the typical season"
                 f"<br>{w} (DJF {ENSO_INDEX} {e:+.2f})"
                 for y, ha, a, w, e in zip(burned["year"], burned["burn_ha"], burned["anomaly"],
                                           winter, burned["enso_djf"])]
        fig.add_bar(x=burned["year"], y=burned["anomaly"], marker_color=figures.FAMILIES["fire"],
                    marker_line_width=0, hovertext=hover, hoverinfo="text", showlegend=False,
                    row=row, col=1)
        nino = g[g["phase"] == "el_nino"]
        for _, r in nino.iterrows():
            fig.add_vrect(x0=r["year"] - 0.5, x1=r["year"] + 0.5, fillcolor=figures.ENSO_SOFT,
                          line_width=0, layer="below", row=row, col=1)
        for strong, colour, size in ((False, figures.ENSO, 9), (True, figures.ENSO_STRONG, 14)):
            marked = nino[nino["strong"] == strong]
            fig.add_scatter(x=marked["year"], y=[lim * 0.93] * len(marked), mode="markers",
                            marker={"symbol": "line-ns", "size": size,
                                    "line": {"width": 3 if strong else 2, "color": colour}},
                            hoverinfo="skip", showlegend=False, row=row, col=1)
        none = g[g["anomaly"].isna()]
        fig.add_scatter(x=none["year"], y=[-lim * 0.9] * len(none), mode="markers",
                        marker={"symbol": "triangle-down", "size": 9, "color": figures.MUTED},
                        hovertext=[f"<b>{int(y)}</b> · no fire of {MIN_FIRE_HA} ha or more"
                                   for y in none["year"]],
                        hoverinfo="text", showlegend=False, row=row, col=1)
        fig.add_vrect(x0=FORECAST_YEAR - 0.5, x1=FORECAST_YEAR + 0.5, fillcolor="rgba(0,0,0,0)",
                      line={"width": 1, "dash": "dot", "color": figures.AXIS}, row=row, col=1)
        decades = range(int(np.ceil(-lim / np.log(10))), int(np.floor(lim / np.log(10))) + 1)
        fig.update_yaxes(range=[-lim, lim], tickvals=[d * np.log(10) for d in decades],
                         ticktext=[f"×{10.0 ** d:g}" for d in decades], row=row, col=1)
    fig.update_yaxes(gridcolor=figures.GRID, zerolinecolor=figures.INK, zerolinewidth=1,
                     tickfont={"size": 11, "color": figures.MUTED}, fixedrange=True)
    fig.update_xaxes(range=[FIRE_FIRST_YEAR - 1, FORECAST_YEAR + 1], showgrid=False, dtick=5,
                     tickfont={"size": 11, "color": figures.MUTED}, linecolor=figures.AXIS,
                     fixedrange=True)
    fig.update_annotations(font={"size": 13, "color": figures.INK}, x=0, xanchor="left")
    fig.update_layout(height=175 * len(regions) + 60, bargap=0.2, hovermode="closest",
                      paper_bgcolor=figures.GROUND, plot_bgcolor=figures.GROUND,
                      font={"family": theme.families()["sans"], "color": figures.INK},
                      hoverlabel={"bgcolor": figures.GROUND, "font": {"color": figures.INK}},
                      margin={"l": 52, "r": 12, "t": 34, "b": 30})
    out = out_dir / f"burned_area_season_history_{ENSO_INDEX.lower()}.html"
    html = fig.to_html(full_html=False, include_plotlyjs="cdn", div_id="season-history",
                       config={"displayModeBar": False, "responsive": True})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(html.encode("utf-8"))  # LF on every platform
    return out


def main() -> None:
    fire = pin_inputs.load_input(FIRE_TABLE)
    print(f"wrote {series_figure(fire)}")
    print(f"wrote {history_html(fire)}")


if __name__ == "__main__":
    main()
