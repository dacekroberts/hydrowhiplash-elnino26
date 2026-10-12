"""Climate controls and the H5 predictor per region and year (Phase 4 gate, D51).

  season_mean()       mean of monthly values over a season, labelled as in
                      era5.winter_total (a season crossing the new year takes
                      the year of its last month); seasons missing a month
                      are dropped
  climate_regional()  temp_jja, temp_mam (deg C), precip_djf_mm (H1; the
                      same values as src.era5's DJF table, committed here so
                      H1's input is pinned, audit 2026-10-08 M4) and
                      precip_octmar_mm per
                      region, cos(latitude)-weighted (src.geo.regional_mean
                      via src.era5.regional_series), every land cell in the
                      region, glacier cells included (ANALYSIS_PLAN
                      "Execution details", built variables)
  add_precip_anom()   precip_anom_lag0 = z of the Oct-Mar total against the
                      region's PRECIP_ANOM_NORMAL_YEARS mean and SD (ddof 1,
                      src.stats.zscore); precip_anom_lag1 = the same z of
                      the Oct-Mar before (year - 1)
  climate_controls_table()  tidy region x year table with the ENSO columns

Year labels: temp_jja and temp_mam Y are June-August and March-May of Y,
inside or before fire season Y; precip Oct-Mar Y is October Y-1 to March Y,
ending before every fire window opens (H5 lag0 for fire season Y).

Temperature is the mean of the monthly means (months not weighted by their
length; a 31-day and a 30-day month count the same).

Run:  python -m src.climate_vars   (writes CLIMATE_CONTROLS_TABLE and its
                                    committed copy in results/tables/)

The committed copy holds values derived from ERA5-Land (CC-BY 4.0) and the
ENSO index (public domain); they stay under those terms (LICENSE-CONTENT).
"""
from __future__ import annotations

import pandas as pd
import xarray as xr

from src.config import (CLIMATE_CONTROLS_TABLE, ERA5_DOMAINS,
                        PRECIP_ANOM_MONTHS, PRECIP_ANOM_NORMAL_YEARS, REGIONS, RESULTS,
                        SPRING_MONTHS, SUMMER_MONTHS, WINTER_MONTHS)
from src.era5 import join_enso, regional_series, winter_total
from src.stats import zscore

COMMITTED = RESULTS / "tables" / CLIMATE_CONTROLS_TABLE.name
COLUMNS = ["region", "year", "winter", "temp_jja", "temp_mam", "precip_djf_mm", "precip_octmar_mm",
           "precip_anom_lag0", "precip_anom_lag1", "enso_index", "enso_djf", "phase", "strong"]


def season_mean(da: xr.DataArray, months: tuple[int, ...]) -> xr.DataArray:
    """Mean of `da` over the season's months per year and cell; seasons
    missing a month are dropped (era5.winter_total)."""
    return winter_total(da, months) / len(months)


def climate_regional(ds: xr.Dataset, masks: xr.DataArray) -> xr.Dataset:
    """Regional temp_jja, temp_mam (deg C), DJF and Oct-Mar precipitation (mm)
    for one ERA5-Land domain (`t2m` in deg C, `tp` in mm/month, as
    era5.open_era5 returns them)."""
    return xr.Dataset({
        "temp_jja": regional_series(season_mean(ds["t2m"], SUMMER_MONTHS), masks),
        "temp_mam": regional_series(season_mean(ds["t2m"], SPRING_MONTHS), masks),
        "precip_djf_mm": regional_series(winter_total(ds["tp"], WINTER_MONTHS), masks),
        "precip_octmar_mm": regional_series(winter_total(ds["tp"], PRECIP_ANOM_MONTHS), masks),
    })


def add_precip_anom(table: pd.DataFrame,
                    normal_years: tuple[int, int] = PRECIP_ANOM_NORMAL_YEARS) -> pd.DataFrame:
    """precip_anom_lag0 and precip_anom_lag1 per region (see module
    docstring). lag1 is matched on year - 1, so a missing winter leaves
    lag1 empty rather than shifting a value from two winters back."""
    out = []
    for _, g in table.groupby("region", sort=False):
        g = g.copy()
        has = g["precip_octmar_mm"].notna()
        ref = g.loc[has, "year"].between(*normal_years)
        z = pd.Series(float("nan"), index=g.index)
        z[has] = zscore(g.loc[has, "precip_octmar_mm"], reference=ref)
        g["precip_anom_lag0"] = z
        prev = dict(zip(g["year"] + 1, z))
        g["precip_anom_lag1"] = g["year"].map(prev)
        out.append(g)
    return pd.concat(out)


def climate_controls_table(regional: xr.Dataset, winters: pd.DataFrame) -> pd.DataFrame:
    """Tidy region x year table; every year kept, whatever its phase. Years
    before the first ENSO winter (1950) are dropped (era5.join_enso), after
    the anomalies are computed."""
    table = regional.to_dataframe().reset_index()
    table["year"] = table["year"].astype(int)
    table = add_precip_anom(table.sort_values(["region", "year"]))
    return join_enso(table, winters)[COLUMNS]


def main(rebuild: bool = False, stamp: str | None = None,
         index_stamp: str | None = None) -> None:
    from src import later, pin_inputs
    from src.era5 import assign_domains, open_domains, region_masks
    from src.regions import load_regions

    ctx = later.paths(stamp, index_stamp)
    # the committed copy is a pinned input: refused without --rebuild. A
    # stamped rebuild writes beside it instead (D88).
    if not stamp:
        pin_inputs.guard_write([COMMITTED], rebuild)

    regions = load_regions()
    domains = assign_domains(regions)
    names = sorted(set(domains), key=list(ERA5_DOMAINS).index)
    datasets = open_domains(names, ctx)
    winters = ctx.winters()
    parts = []
    for name in names:
        masks = region_masks(regions[regions["region"].map(domains) == name], datasets[name])
        regional = climate_regional(datasets[name], masks).compute()
        parts.append(climate_controls_table(regional, winters))
    table = pd.concat(parts)
    table["region"] = pd.Categorical(table["region"], categories=list(REGIONS), ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    for path in (ctx.processed(CLIMATE_CONTROLS_TABLE), ctx.table(COMMITTED)):
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(table)} rows, years {table['year'].min()}-{table['year'].max()}")
    if not stamp:
        pin_inputs.report_rebuild([COMMITTED])
    ctx.close("climate_vars")
    print(table.groupby("region", sort=False)[["temp_jja", "temp_mam", "precip_octmar_mm"]]
          .agg(["mean", "count"]).round(2).to_string())


if __name__ == "__main__":
    import sys

    from src import later as _later

    _argv = sys.argv[1:]
    _index = _later.take_index_stamp(_argv)
    _stamp = _later.take_stamp(_argv)
    main(rebuild="--rebuild" in _argv, stamp=_stamp, index_stamp=_index)
