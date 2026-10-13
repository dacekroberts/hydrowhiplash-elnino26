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

from src import figures, pin_inputs
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
    empty outlined slot marks FORECAST_YEAR. Built by interactive.panels, so
    every panel has its year labels and the chart its axis titles and legend."""
    import numpy as np

    from src import interactive

    table = figures.season_anomaly(test_seasons(fire))
    groups = []
    for region in dict.fromkeys(table["region"]):
        g = table[table["region"] == region].sort_values("year")
        burned = g[g["anomaly"].notna()]
        typical = float(np.expm1(burned["log_burn"].mean()))
        lim = float(np.nanmax(np.abs(g["anomaly"])) * 1.25)
        hover = [f"<b>{int(y)}</b> · {ha:,.0f} ha<br>{np.exp(a):.2g} times the typical season"
                 f"<br>after {'an' if ph == 'el_nino' and not s else 'a'} "
                 f"{interactive.winter_words(ph, bool(s))} (DJF {ENSO_INDEX} {e:+.2f})"
                 for y, ha, a, ph, s, e in zip(burned["year"], burned["burn_ha"],
                                               burned["anomaly"], burned["phase"],
                                               burned["strong"], burned["enso_djf"])]
        none = g[g["anomaly"].isna()]
        decades = range(int(np.ceil(-lim / np.log(10))), int(np.floor(lim / np.log(10))) + 1)
        groups.append({"title": f"<b>{region}</b> · typical season {typical:,.0f} ha",
                       "years": burned["year"], "values": burned["anomaly"], "hover": hover,
                       "nino": g[g["phase"] == "el_nino"],
                       "nina": g[g["phase"] == "la_nina"]["year"], "lim": lim,
                       "tickvals": [d * np.log(10) for d in decades],
                       "ticktext": [f"×{10.0 ** d:g}" for d in decades],
                       "missing": none["year"],
                       "missing_hover": [f"<b>{int(y)}</b> · no fire of {MIN_FIRE_HA} ha or more"
                                         for y in none["year"]]})
    return interactive.panels(
        groups, figures.FAMILIES["fire"], "Burned area of the fire season",
        "× typical season", "Fire season (year); each follows the winter that ends in it",
        (FIRE_FIRST_YEAR - 1, FORECAST_YEAR + 1),
        out_dir / f"burned_area_season_history_{ENSO_INDEX.lower()}.html", "season-history",
        slot_year=FORECAST_YEAR, slot_label=f"{FORECAST_YEAR}: not yet happened",
        missing_label=f"No fire of {MIN_FIRE_HA} ha or more")


def main() -> None:
    fire = pin_inputs.load_input(FIRE_TABLE)
    print(f"wrote {series_figure(fire)}")
    print(f"wrote {history_html(fire)}")


if __name__ == "__main__":
    main()
