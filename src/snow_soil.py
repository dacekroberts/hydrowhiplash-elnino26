"""ERA5-Land snowfall fraction and summer soil moisture per region and year.

Descriptive columns (ACTION_PLAN.md Phase 2; D13): how much of a winter's
precipitation fell as snow, and how wet the upper soil was in summer.
Settings in src/config.py; reasoning in DECISIONS.md 2026-10-05 "Snowfall
fraction and soil moisture columns".

  snowfall_fraction()  regional mean snowfall / regional mean precipitation,
                       both summed over SNOWFALL_MONTHS (Nov-Mar), labelled by
                       the March year (winter (Y-1)-Y, as everywhere)
  soil_moisture()      SOIL_LAYER_WEIGHTS-weighted 0-28 cm volumetric soil
                       water, mean over SOIL_MONTHS (JJA), regional mean
  snow_soil_table()    tidy region x year table with the ENSO columns

Regional means use src.geo.regional_mean (cos(latitude) weights) through
src.era5.regional_series. Snowfall and soil moisture come from the
"snow_soil" variable set; precipitation from the core set.

Run:  python -m src.snow_soil   (writes data/processed/snow_soil_region_year.csv
                                 and its committed copy in results/tables/)

The committed copy holds values derived from ERA5-Land (CC-BY 4.0) and the
ENSO index (public domain); they stay under those terms (LICENSE-CONTENT).
"""
from __future__ import annotations

import pandas as pd
import xarray as xr

from src.config import (DATA_RAW, ERA5_DOMAINS,
                        ERA5_VARIABLE_SETS, REGIONS, RESULTS, SNOW_SOIL_TABLE,
                        SNOWFALL_MONTHS, SOIL_LAYER_WEIGHTS, SOIL_MONTHS)
from src.era5 import TIME, join_enso, regional_series, winter_total

COMMITTED = RESULTS / "tables" / SNOW_SOIL_TABLE.name


def snowfall_fraction(sf: xr.DataArray, tp: xr.DataArray, masks: xr.DataArray,
                      months: tuple[int, ...] = SNOWFALL_MONTHS) -> xr.Dataset:
    """Seasonal regional totals (mm) and their ratio, per region and year.
    Seasons missing a month are dropped (winter_total)."""
    sf_total = regional_series(winter_total(sf, months), masks)
    tp_total = regional_series(winter_total(tp, months), masks)
    return xr.Dataset({"sf_season_mm": sf_total, "tp_season_mm": tp_total,
                       "snowfall_frac": sf_total / tp_total})


def soil_moisture(ds: xr.Dataset, masks: xr.DataArray,
                  months: tuple[int, ...] = SOIL_MONTHS,
                  weights: dict[str, float] = SOIL_LAYER_WEIGHTS) -> xr.DataArray:
    """Regional mean of the depth-weighted layers, averaged over `months`
    (m3/m3). Years missing a month are dropped."""
    layered = sum(ds[name] * w for name, w in weights.items()) / sum(weights.values())
    season_mean = winter_total(layered, months) / len(months)
    return regional_series(season_mean, masks).rename("soil_moisture")


def snow_soil_table(regional: xr.Dataset, winters: pd.DataFrame) -> pd.DataFrame:
    """Tidy region x year table; every year kept, whatever its phase. Years
    before the first ENSO winter (1950) are dropped (era5.join_enso)."""
    table = regional.to_dataframe().reset_index()
    table["year"] = table["year"].astype(int)
    table = join_enso(table, winters)
    return table[["region", "year", "winter", "snowfall_frac", "sf_season_mm", "tp_season_mm",
                  "soil_moisture", "enso_index", "enso_djf", "phase", "strong"]]


def snow_soil_dir(domain: str):
    return DATA_RAW / f"{ERA5_DOMAINS[domain][1]}{ERA5_VARIABLE_SETS['snow_soil'][1]}"


def main(rebuild: bool = False, stamp: str | None = None,
         index_stamp: str | None = None) -> None:
    from src import later, pin_inputs
    from src.era5 import assign_domains, open_domains, open_era5, region_masks
    from src.regions import load_regions

    ctx = later.paths(stamp, index_stamp)
    # the committed copy is a pinned input: refused without --rebuild. A
    # stamped rebuild writes beside it instead (D88).
    if not stamp:
        pin_inputs.guard_write([COMMITTED], rebuild)

    regions = load_regions()
    domains = assign_domains(regions)
    names = sorted(set(domains), key=list(ERA5_DOMAINS).index)
    core = open_domains(names, ctx)
    winters = ctx.winters()
    parts = []
    for name in names:
        snow_soil = open_era5(snow_soil_dir(name), ctx.era5_paths(snow_soil_dir(name)))
        xr.align(snow_soil.isel({TIME: 0}), core[name].isel({TIME: 0}), join="exact")
        masks = region_masks(regions[regions["region"].map(domains) == name], snow_soil)
        regional = snowfall_fraction(snow_soil["sf"], core[name]["tp"], masks)
        # SOIL_MONTHS lie inside one calendar year, so the season label is that year.
        regional["soil_moisture"] = soil_moisture(snow_soil, masks)
        parts.append(snow_soil_table(regional.compute(), winters))
    table = pd.concat(parts)
    table["region"] = pd.Categorical(table["region"], categories=list(REGIONS), ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    written = [ctx.processed(SNOW_SOIL_TABLE), ctx.table(COMMITTED)]
    for path in written:
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(table)} rows, years {table['year'].min()}-{table['year'].max()}")
    pin_inputs.report_pinned(written)
    print(table.groupby("region", sort=False)[["snowfall_frac", "soil_moisture"]].agg(
        ["mean", "min", "max"]).round(3).to_string())
    ctx.close("snow_soil")


if __name__ == "__main__":
    import sys

    from src import later as _later

    _argv = sys.argv[1:]
    _index = _later.take_index_stamp(_argv)
    _stamp = _later.take_stamp(_argv)
    main(rebuild="--rebuild" in _argv, stamp=_stamp, index_stamp=_index)
