"""Full-record view of burned area (ACTION_PLAN Phase 4).

Writes to results/figures/:
  burned_area_anomaly_series_<index>.png   every fire season per region since
      1984 as its departure from the region's mean log burned area, seasons
      after an El Nino winter highlighted

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
from src.config import (ENSO_INDEX, FIRE_FIRST_YEAR, FIRE_LAST_YEAR_BY_REGION, REGIONS,
                        RESULTS)

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


def main() -> None:
    print(f"wrote {series_figure(pin_inputs.load_input(FIRE_TABLE))}")


if __name__ == "__main__":
    main()
