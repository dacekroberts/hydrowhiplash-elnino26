"""Load ERA5-Land monthly files, convert units and build regional series.

Pipeline:
  open_era5()           all yearly files -> one Dataset in project units
  region_masks()        boolean region x lat x lon masks on the ERA5 grid
  winter_total()        seasonal totals per grid cell, labelled by winter year
  regional_series()     cos(latitude)-weighted regional means (src.geo)
  winter_precip_table() tidy region x year table with the ENSO columns

Units after open_era5 (raw units in docs/data_dictionary.md, section 2):
  tp   mm/month  (raw: monthly mean of daily totals in m/day)
  sf   mm/month  (raw: m/day, as tp)
  t2m  deg C     (raw: K)
  sd   mm water equivalent, clipped at 0 (raw: m; tiny negatives are noise)

Year label: the winter labelled Y is Dec of Y-1 plus Jan and Feb of Y, paired
with ENSO DJF value Y and fire season Y.

Each region is read from the first ERA5_DOMAINS box that contains it.

Run:  python -m src.era5   (writes data/processed/djf_precip_region_year.csv)
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import regionmask
import xarray as xr

from src.config import (DATA_PROCESSED, DATA_RAW, ENSO_INDEX, ERA5_DOMAINS, REGIONS,
                        WINTER_MONTHS)
from src.geo import regional_mean

ERA5_DIR = DATA_RAW / ERA5_DOMAINS["main"][1]
TIME = "valid_time"
LAT, LON = "latitude", "longitude"
GRIB_LEFTOVERS = ["expver", "number"]
GRID_DECIMALS = 4  # the 0.1 deg grid is snapped to this many decimals
OUT = DATA_PROCESSED / "djf_precip_region_year.csv"


def drop_grib_coords(ds: xr.Dataset) -> xr.Dataset:
    """Drop leftover GRIB coordinates; expver can differ for recent months."""
    return ds.drop_vars([c for c in GRIB_LEFTOVERS if c in ds.variables])


def snap_grid(ds: xr.Dataset) -> xr.Dataset:
    """Round lat/lon to their nominal values.

    The files store some rows with float noise (35.5 is 35.499999999999645),
    which would decide by accident which side of CA_SPLIT_LAT a row falls on
    and can break alignment between files and masks.
    """
    return ds.assign_coords({LAT: ds[LAT].round(GRID_DECIMALS),
                             LON: ds[LON].round(GRID_DECIMALS)})


def convert_units(ds: xr.Dataset) -> xr.Dataset:
    """Convert ERA5-Land monthly means to project units (see module docstring).

    Precipitation uses each month's own length, so February has 29 days in
    leap years.
    """
    out = ds.copy()
    if "tp" in ds:
        days = ds[TIME].dt.days_in_month
        out["tp"] = ds["tp"] * 1000 * days
        out["tp"].attrs = {"long_name": "Total precipitation", "units": "mm/month"}
    if "sf" in ds:  # same m/day convention as tp (sf/tp <= 0.9996, 2026-10-04)
        out["sf"] = ds["sf"] * 1000 * ds[TIME].dt.days_in_month
        out["sf"].attrs = {"long_name": "Snowfall", "units": "mm/month"}
    if "t2m" in ds:
        out["t2m"] = ds["t2m"] - 273.15
        out["t2m"].attrs = {"long_name": "2 m temperature", "units": "degC"}
    if "sd" in ds:
        out["sd"] = (ds["sd"] * 1000).clip(min=0)
        out["sd"].attrs = {"long_name": "Snow water equivalent", "units": "mm"}
    return out


def open_era5(directory: Path = ERA5_DIR) -> xr.Dataset:
    """Every yearly file as one lazily loaded Dataset, in project units.

    Raises if a year was unpacked into a folder (a zipped CDS reply, see
    src.download_era5.retrieve), which the file glob would skip, or if the
    months are not contiguous: either would silently drop winters, because
    seasons missing a month are dropped (Phase 1 audit, finding 3).
    """
    paths = sorted(directory.glob("era5_land_*.nc"))
    if not paths:
        raise FileNotFoundError(f"No ERA5-Land files in {directory}; run python -m src.download_era5.")
    folders = sorted(p.name for p in directory.glob("era5_land_*") if p.is_dir())
    if folders:
        raise ValueError(f"Unpacked year folders in {directory} are not read: {folders}. "
                         "Merge their files into one NetCDF per year first.")
    ds = xr.open_mfdataset(paths, preprocess=lambda d: snap_grid(drop_grib_coords(d)),
                           combine="nested", concat_dim=TIME, data_vars="all",
                           coords="minimal", compat="override", join="exact")
    ds = ds.sortby(TIME)
    if not ds.indexes[TIME].is_unique:
        raise ValueError("Duplicate months across ERA5-Land files.")
    times = ds.indexes[TIME]
    expected = pd.date_range(times[0], times[-1], freq="MS")
    if len(times) != len(expected) or not (times == expected).all():
        missing = expected.difference(times)
        raise ValueError(f"ERA5-Land months are not contiguous in {directory}: "
                         f"{len(missing)} missing, first {missing[0].date() if len(missing) else '?'}.")
    return convert_units(ds)


def region_masks(regions: gpd.GeoDataFrame, grid: xr.Dataset | xr.DataArray) -> xr.DataArray:
    """Boolean mask (region, latitude, longitude): a cell is in a region when
    its centre lies inside the polygon (regionmask's rule).

    Regions keep the order of the GeoDataFrame and are labelled by its
    `region` column. Raises if any cell centre lies inside two polygons'
    interiors (overlapping regions): the overlap=False mask assigns each cell
    to one region by construction, so the check uses overlap=True instead.
    Cells exactly on a shared edge (the 35.5N row) are not overlaps.
    """
    rm = regionmask.from_geopandas(regions, names="region", name="study_regions",
                                   overlap=False)
    mask = rm.mask_3D(grid[LON], grid[LAT], drop=False)
    mask = mask.assign_coords(region=mask["names"].values).drop_vars(["names", "abbrevs"])
    both = regionmask.from_geopandas(regions, names="region", overlap=True).mask_3D(
        grid[LON], grid[LAT], drop=False)
    if (both.sum("region") > 1).any():
        raise ValueError("Region polygons overlap: a grid cell centre lies in more than one region.")
    return mask


def winter_total(da: xr.DataArray, months: tuple[int, ...] = WINTER_MONTHS) -> xr.DataArray:
    """Sum of `da` over the season's months, one value per winter and cell.

    The season may cross the new year (e.g. (12, 1, 2)); months from the
    first month through December are counted with the following year's label.
    Seasons missing any month are dropped (the first and the current winter).
    NaN cells (ocean) stay NaN instead of summing to 0.
    """
    t = da[TIME]
    season = da.sel({TIME: t.dt.month.isin(list(months))})
    month = season[TIME].dt.month
    wraps = months[0] > months[-1]
    year = (season[TIME].dt.year + (wraps & (month >= months[0]))).rename("year")
    total = season.groupby(year).sum(TIME, skipna=False)
    n_months = season[TIME].groupby(year).count()
    return total.where(n_months == len(months), drop=True).astype(da.dtype)


def regional_series(da: xr.DataArray, masks: xr.DataArray) -> xr.DataArray:
    """cos(latitude)-weighted mean of `da` over each region in `masks`."""
    return xr.concat([regional_mean(da, masks.sel(region=r, drop=True))
                      for r in masks["region"].values],
                     dim=pd.Index(masks["region"].values, name="region"))


def winter_precip_table(ds: xr.Dataset, masks: xr.DataArray,
                        winters: pd.DataFrame) -> pd.DataFrame:
    """Tidy region x year table of winter precipitation with ENSO columns.

    `winters` is data/processed/el_nino_winters.csv (year, winter, enso_djf,
    phase, strong). Every winter is kept, whatever its phase.
    """
    series = regional_series(winter_total(ds["tp"]), masks).compute()
    table = series.rename("precip_djf_mm").to_dataframe().reset_index()
    table = table[["region", "year", "precip_djf_mm"]]
    table["year"] = table["year"].astype(int)
    table = table.merge(winters, on="year", how="left", validate="many_to_one")
    table["enso_index"] = ENSO_INDEX
    return table[["region", "year", "winter", "precip_djf_mm", "enso_index",
                  "enso_djf", "phase", "strong"]]


def domain_dir(name: str) -> Path:
    return DATA_RAW / ERA5_DOMAINS[name][1]


def assign_domains(regions: gpd.GeoDataFrame) -> pd.Series:
    """region -> the first domain in ERA5_DOMAINS whose box contains it."""
    out = {}
    for _, r in regions.iterrows():
        west, south, east, north = r.geometry.bounds
        for name, (area, _) in ERA5_DOMAINS.items():
            n, w, s, e = area
            if w <= west and east <= e and s <= south and north <= n:
                out[r["region"]] = name
                break
        else:
            raise ValueError(f"{r['region']} lies in no single ERA5 domain.")
    return pd.Series(out, name="domain")


def open_domains(names) -> dict[str, xr.Dataset]:
    """Open each named domain; raises if a domain has not been downloaded."""
    missing = [n for n in names if not any(domain_dir(n).glob("era5_land_*.nc"))]
    if missing:
        raise FileNotFoundError(f"ERA5 domain(s) {missing} not downloaded; run "
                                f"python -m src.download_era5 {' '.join(missing)}.")
    return {n: open_era5(domain_dir(n)) for n in names}


def build_winter_precip_table(regions: gpd.GeoDataFrame, winters: pd.DataFrame,
                              datasets: dict[str, xr.Dataset]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Winter precipitation table across domains, in `regions` order.

    Returns the table and a per-region cell count (cells in the mask, and
    cells with data; coastal cells inside a polygon can be ocean in ERA5-Land).
    """
    domains = assign_domains(regions)
    parts, cells = [], []
    for name, ds in datasets.items():
        sub = regions[regions["region"].map(domains) == name]
        if sub.empty:
            continue
        masks = region_masks(sub, ds)
        parts.append(winter_precip_table(ds, masks, winters))
        with_data = masks.where(ds["tp"].isel({TIME: 0}).notnull(), False)
        cells.append(pd.DataFrame({"domain": name,
                                   "cells": masks.sum([LAT, LON]).to_series(),
                                   "cells_with_data": with_data.sum([LAT, LON]).to_series()}))
    order = list(regions["region"])
    table = pd.concat(parts)
    table["region"] = pd.Categorical(table["region"], categories=order, ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    return table, pd.concat(cells).loc[order]


def main() -> None:
    from src.regions import load_regions

    regions = load_regions()
    datasets = open_domains(sorted(set(assign_domains(regions)), key=list(ERA5_DOMAINS).index))
    winters = pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv")
    table, cells = build_winter_precip_table(regions, winters, datasets)
    if list(dict.fromkeys(table["region"])) != list(REGIONS):
        raise SystemExit("Region list differs from config.REGIONS.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(table)} rows, winters "
          f"{table['winter'].iloc[0]} to {table['winter'].iloc[-1]}")
    print(cells.to_string())


if __name__ == "__main__":
    main()
