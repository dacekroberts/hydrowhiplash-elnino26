"""ERA5-Land snow water equivalent: glacier mask and April 1 regional SWE.

Settings in src/config.py; reasoning in DECISIONS.md 2026-10-04 "ERA5-Land
SWE: glacier exclusion and April 1"; measured effects in
docs/methods_register.md.

  glacier_mask()   fixed mask of cells excluded from every SWE regional mean:
                   cells at the 10 m cap (SWE_CAP_MM) in any month, or cells
                   keeping more than PERENNIAL_MIN_MM of snow at the yearly
                   minimum in at least PERENNIAL_YEAR_FRACTION of the years
                   (GLACIER_MASK_YEARS). Built from the monthly means.
  open_april1()    1 April 00:00 UTC SWE from hourly ERA5-Land, in mm,
                   labelled by year (April 1 of Y belongs to winter (Y-1)-Y)
  april1_table()   tidy region x year table, glacier cells excluded, with the
                   all-cells value alongside and the ENSO columns

Run:  python -m src.snow   (writes data/processed/swe_april1_region_year.csv
                            and the glacier masks)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import xarray as xr

from src.config import (APRIL1_FOLDER_SUFFIX, DATA_PROCESSED, DATA_RAW, ENSO_INDEX,
                        ERA5_DOMAINS, GLACIER_MASK_YEARS, PERENNIAL_MIN_MM,
                        PERENNIAL_YEAR_FRACTION, SWE_CAP_MM)
from src.era5 import LAT, LON, TIME, drop_grib_coords, regional_series, snap_grid

APRIL1_FILE = "era5_land_april1.nc"
OUT = DATA_PROCESSED / "swe_april1_region_year.csv"


def glacier_mask(sd_mm: xr.DataArray, years: tuple[int, int] = GLACIER_MASK_YEARS) -> xr.DataArray:
    """Boolean (latitude, longitude): True where a cell is excluded as glacier
    or perennial snow. `sd_mm` is monthly SWE in mm; only complete years in
    `years` (inclusive) are used. Ocean cells (all NaN) are False."""
    first, last = years
    sd = sd_mm.sel({TIME: slice(f"{first}-01-01", f"{last}-12-31")})
    capped = (sd >= SWE_CAP_MM).any(TIME)
    yearly_min = sd.groupby(sd[TIME].dt.year).min(TIME)
    perennial = (yearly_min > PERENNIAL_MIN_MM).mean("year") >= PERENNIAL_YEAR_FRACTION
    mask = (capped | perennial) & sd.notnull().any(TIME)
    return mask.rename("glacier").assign_attrs(
        description=f"cap >= {SWE_CAP_MM} mm in any month, or > {PERENNIAL_MIN_MM} mm at the "
                    f"yearly minimum in >= {PERENNIAL_YEAR_FRACTION:.0%} of {first}-{last}")


def april1_dir(domain: str) -> Path:
    return DATA_RAW / f"{ERA5_DOMAINS[domain][1]}{APRIL1_FOLDER_SUFFIX}"


def open_april1(directory: Path) -> xr.DataArray:
    """April 1 SWE in mm (year, latitude, longitude), clipped at 0."""
    path = directory / APRIL1_FILE
    if not path.exists():
        raise FileNotFoundError(f"{path} missing; run python -m src.download_era5_april1.")
    ds = snap_grid(drop_grib_coords(xr.open_dataset(path)))
    sd = ds["sd"]
    if not ((sd[TIME].dt.month == 4) & (sd[TIME].dt.day == 1)).all():
        raise ValueError("April 1 file holds times other than 1 April.")
    sd = (sd * 1000).clip(min=0)
    sd = sd.assign_coords(year=(TIME, sd[TIME].dt.year.values)).swap_dims({TIME: "year"})
    return sd.drop_vars(TIME).rename("swe_apr1").assign_attrs(
        units="mm", long_name="Snow water equivalent, 1 April 00:00 UTC")


def april1_regional(april1: xr.DataArray, masks: xr.DataArray,
                    glacier: xr.DataArray) -> xr.Dataset:
    """Regional April 1 SWE with glacier cells excluded, and over all cells."""
    xr.align(april1.isel(year=0), glacier, join="exact")  # same grid or raise
    return xr.Dataset({
        "swe_apr1_mm": regional_series(april1, masks & ~glacier),
        "swe_apr1_mm_all_cells": regional_series(april1, masks),
    })


def april1_table(regional: xr.Dataset, winters: pd.DataFrame) -> pd.DataFrame:
    """Tidy region x year table; every winter kept, whatever its phase."""
    table = regional.to_dataframe().reset_index()
    table["year"] = table["year"].astype(int)
    table = table.merge(winters, on="year", how="inner", validate="many_to_one")
    table["enso_index"] = ENSO_INDEX
    return table[["region", "year", "winter", "swe_apr1_mm", "swe_apr1_mm_all_cells",
                  "enso_index", "enso_djf", "phase", "strong"]]


def excluded_cells(masks: xr.DataArray, glacier: xr.DataArray) -> pd.Series:
    """Glacier cells per region."""
    return (masks & glacier).sum([LAT, LON]).to_series().rename("glacier_cells")


def main() -> None:
    from src.config import REGIONS
    from src.era5 import assign_domains, open_domains, region_masks
    from src.regions import load_regions

    regions = load_regions()
    domains = assign_domains(regions)
    names = sorted(set(domains), key=list(ERA5_DOMAINS).index)
    datasets = open_domains(names)
    winters = pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv")
    parts, counts = [], []
    for name in names:
        sub = regions[regions["region"].map(domains) == name]
        ds = datasets[name]
        masks = region_masks(sub, ds)
        glacier = glacier_mask(ds["sd"]).compute()
        glacier.to_netcdf(DATA_PROCESSED / f"glacier_mask_{name}.nc")
        april1 = open_april1(april1_dir(name))
        parts.append(april1_table(april1_regional(april1, masks, glacier).compute(), winters))
        counts.append(excluded_cells(masks, glacier))
        print(f"{name}: {int(glacier.sum())} glacier cells in the domain")
    table = pd.concat(parts)
    table["region"] = pd.Categorical(table["region"], categories=list(REGIONS), ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    table.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(table)} rows, years {table['year'].min()}-{table['year'].max()}")
    summary = table.groupby("region", sort=False)[["swe_apr1_mm", "swe_apr1_mm_all_cells"]].mean()
    print(pd.concat([pd.concat(counts), summary.round(0)], axis=1).to_string())


if __name__ == "__main__":
    main()
