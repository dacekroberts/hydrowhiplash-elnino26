"""Regenerate the five Phase 2 figures from the committed tables, without the
notebooks.

Writes to results/figures/, as notebooks 02 (cells 6, 8) and 03 (cells 8, 14,
16) do, with <index> = ENSO_INDEX in lower case:
  whiplash_series_<index>.png               SPEI-3 JJA minus DJF per region
  swe_april1_series_<index>.png             ERA5-Land April 1 SWE per region
  swe_april1_stations_vs_era5_<index>.png   station index next to ERA5-Land
  snowfall_fraction_series_<index>.png      snowfall share of Nov-Mar precipitation
  soil_moisture_jja_series_<index>.png      JJA root-zone soil water

Reads only results/tables/ (whiplash_swe, station_swe and snow_soil
region x year tables), so results/ can be rebuilt by code alone (pre-freeze
audit, finding 9). Region choices follow rules rather than names: the SWE
series leaves out regions whose ERA5-Land April 1 normal is below
ERA5_SWE_MIN_NORMAL_MM (SoCal, 0.06 mm), and the station comparison shows the
regions that have a station index.

Run:  python -m src.phase2_figures
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import (ENSO_INDEX, ERA5_SWE_MIN_NORMAL_MM, RESULTS, SNOW_SOIL_TABLE,
                        STATION_INDEX_TABLE, STATION_NORMAL_YEARS)
from src.figures import FIGURES, winter_series, winter_series_columns
from src.phase2 import COMMITTED as PHASE2_TABLE
from src.stations import swe_normal_ok

TABLES = RESULTS / "tables"
STATION_TABLE_COMMITTED = TABLES / STATION_INDEX_TABLE.name
SNOW_SOIL_COMMITTED = TABLES / SNOW_SOIL_TABLE.name


def swe_regions(table: pd.DataFrame, min_normal_mm: float = ERA5_SWE_MIN_NORMAL_MM) -> list[str]:
    """Regions whose April 1 SWE normal (mean over STATION_NORMAL_YEARS) is at
    least `min_normal_mm`, in table order: stations.swe_normal_ok, the rule
    behind the ERA5-Land % and z in stations.compare_era5."""
    return [r for r, g in table.groupby("region", sort=False)
            if swe_normal_ok(g["swe_apr1_mm"], g["year"], min_normal_mm)]


def station_regions(index: pd.DataFrame) -> list[str]:
    """Regions with at least one station index value, in table order."""
    has = index.groupby("region", sort=False)["station_swe_pct"].apply(lambda s: s.notna().any())
    return [r for r in dict.fromkeys(index["region"]) if has.get(r, False)]


def whiplash_figure(phase2: pd.DataFrame, out_dir: Path = FIGURES,
                    enso_index: str = ENSO_INDEX) -> Path:
    return winter_series(
        phase2.dropna(subset=["whiplash"]), "whiplash", "SPEI-3 JJA minus DJF (SD)", enso_index,
        out_dir / f"whiplash_series_{enso_index.lower()}.png", signed=True,
        xlabel="Winter (Dec-Feb) and the following summer (Jun-Aug); "
               "year Y = winter (Y-1)-Y and summer Y")


def swe_figure(phase2: pd.DataFrame, out_dir: Path = FIGURES,
               enso_index: str = ENSO_INDEX) -> Path:
    swe = phase2[phase2["region"].isin(swe_regions(phase2))].dropna(subset=["swe_apr1_mm"])
    return winter_series(swe, "swe_apr1_mm", "April 1 SWE (mm)", enso_index,
                         out_dir / f"swe_april1_series_{enso_index.lower()}.png", family="snow")


def stations_vs_era5_figure(index: pd.DataFrame, out_dir: Path = FIGURES,
                            enso_index: str = ENSO_INDEX) -> Path:
    first, last = STATION_NORMAL_YEARS
    return winter_series_columns(
        index[index["region"].isin(station_regions(index))],
        {"stations, median % of normal": "station_swe_pct",
         "ERA5-Land, % of normal": "era5_swe_pct"},
        f"April 1 SWE, % of {first}-{last}", enso_index,
        out_dir / f"swe_april1_stations_vs_era5_{enso_index.lower()}.png")


def snowfall_figure(snow_soil: pd.DataFrame, out_dir: Path = FIGURES,
                    enso_index: str = ENSO_INDEX) -> Path:
    ss = snow_soil.assign(snowfall_pct=100 * snow_soil["snowfall_frac"])
    return winter_series(
        ss.dropna(subset=["snowfall_pct"]), "snowfall_pct", "Snowfall, % of Nov-Mar precip",
        enso_index, out_dir / f"snowfall_fraction_series_{enso_index.lower()}.png",
        xlabel="Winter (Nov-Mar); year Y = November Y-1 to March Y", family="snow")


def soil_figure(snow_soil: pd.DataFrame, out_dir: Path = FIGURES,
                enso_index: str = ENSO_INDEX) -> Path:
    return winter_series(
        snow_soil.dropna(subset=["soil_moisture"]), "soil_moisture", "Soil water, m³/m³",
        enso_index, out_dir / f"soil_moisture_jja_series_{enso_index.lower()}.png",
        xlabel="Summer (Jun-Aug) of year Y, after winter (Y-1)-Y")


def make_figures(phase2: pd.DataFrame, index: pd.DataFrame, snow_soil: pd.DataFrame,
                 out_dir: Path = FIGURES, enso_index: str = ENSO_INDEX) -> list[Path]:
    """Write the five figures; return their paths in the order listed above.
    Notebooks 02 and 03 call the single-figure functions, so each figure has
    one generator (PR #20 review, 2026-10-06)."""
    return [whiplash_figure(phase2, out_dir, enso_index),
            swe_figure(phase2, out_dir, enso_index),
            stations_vs_era5_figure(index, out_dir, enso_index),
            snowfall_figure(snow_soil, out_dir, enso_index),
            soil_figure(snow_soil, out_dir, enso_index)]


def main() -> None:
    tables = {name: pd.read_csv(path) for name, path in
              (("phase2", PHASE2_TABLE), ("index", STATION_TABLE_COMMITTED),
               ("snow_soil", SNOW_SOIL_COMMITTED))}
    for name, table in tables.items():
        found = set(table["enso_index"].dropna())
        if found != {ENSO_INDEX}:
            raise SystemExit(f"{name} table is classified by {sorted(found)}, not {ENSO_INDEX}; "
                             f"rebuild it first.")
    for path in make_figures(tables["phase2"], tables["index"], tables["snow_soil"]):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
