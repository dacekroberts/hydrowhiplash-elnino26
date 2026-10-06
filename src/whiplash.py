"""Thornthwaite PET, SPEI-3 and the whiplash index from ERA5-Land monthly means.

Pipeline (settings in src/config.py; reasoning in DECISIONS.md 2026-10-04
"SPEI settings"):
  pet_thornthwaite()   PET per cell, mm/day (xclim TW48; zero below 0 deg C)
  water_balance()      P - PET per cell, mm/day
  spei_cells()         SPEI-3 per cell: log-logistic fitted by maximum
                       likelihood per calendar month over SPEI_CAL_YEARS,
                       clipped to +-SPEI_CLIP; runs in parallel processes
  season_spei()        SPEI-3 at a season's last month, labelled by year
                       (Feb Y = DJF of winter (Y-1)-Y; Aug Y = JJA of Y)
  restandardise()      z-score over SPEI_CAL_YEARS, per region and season
  whiplash_table()     tidy region x year table: regional SPEI-3 for DJF and
                       JJA, whiplash = JJA - DJF, ENSO columns

Regional values are the cos(latitude)-weighted mean of per-cell SPEI
(src.geo.regional_mean), then re-standardised: a mean of correlated z-scores
has SD below 1, by different amounts in different regions. xclim's 3-month
window is a rolling mean of monthly rates (mm/day), equal to the 3-month sum
up to month-length weighting.

Run:  python -m src.whiplash   (per-cell SPEI cached in data/processed/,
                                table written to data/processed/)
"""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import xarray as xr

from src.config import (DATA_PROCESSED, PET_METHOD, SPEI_CAL_YEARS, SPEI_CLIP,
                        SPEI_DIST, SPEI_FIT_METHOD, SPEI_SCALE, SUMMER_MONTHS, WINTER_MONTHS)
from src.era5 import LAT, LON, TIME, join_enso, regional_series

XTIME = "time"  # xclim's time dimension name
CELL = "cell"
OUT = DATA_PROCESSED / "whiplash_region_year.csv"


def _to_xclim(da: xr.DataArray) -> xr.DataArray:
    return da.rename({TIME: XTIME}) if TIME in da.dims else da


def _from_xclim(da: xr.DataArray) -> xr.DataArray:
    return da.rename({XTIME: TIME}) if XTIME in da.dims else da


def pet_thornthwaite(t2m_c: xr.DataArray) -> xr.DataArray:
    """Thornthwaite PET in mm/day from monthly mean 2 m temperature in deg C.

    Uses latitude for day length. Zero in months at or below 0 deg C.

    The steps of xclim's TW48 method (`potential_evapotranspiration`), with
    one change: day lengths in polar day and night are set to 24 h and 0 h
    (`infill_polar_days`). xclim leaves them NaN, so PET was NaN in June and
    December north of about 68N and every DJF and JJA SPEI-3 there was
    missing (pre-freeze data audit, 2026-10-05: 15% of AK's area weight).
    South of the polar circles the day lengths, and so PET, are unchanged.
    """
    from xclim.core.units import amount2rate
    from xclim.indices.helpers import day_lengths

    if PET_METHOD != "TW48":
        raise ValueError(f"pet_thornthwaite implements TW48 only, not {PET_METHOD!r}")
    tas = _to_xclim(t2m_c).clip(min=0)
    months = tas[XTIME]
    days = xr.DataArray(
        pd.date_range(months[0].dt.strftime("%Y-%m-01").item(),
                      months[-1].dt.strftime("%Y-%m").item() + f"-{int(months[-1].dt.daysinmonth)}",
                      freq="D"), dims=XTIME, name=XTIME)
    lat = tas[LAT].assign_attrs(units="degrees_north")  # xclim reads the units
    # Thornthwaite measures day length in units of 12 hours.
    dl = day_lengths(days, lat, infill_polar_days=True) / 12
    dl_m = dl.resample({XTIME: "MS"}).mean()
    dl_m = dl_m.assign_coords({XTIME: months.values})
    heat = ((tas / 5) ** 1.514).groupby(f"{XTIME}.year").sum()  # annual heat index
    heat_m = heat.sel(year=tas[XTIME].dt.year).drop_vars("year")
    a = 6.75e-7 * heat_m**3 - 7.71e-5 * heat_m**2 + 0.01791 * heat_m + 0.49239
    pet = 10 * 1.6 * dl_m * (10 * tas / heat_m) ** a  # mm/month
    pet = amount2rate(pet.assign_attrs(units="mm"), out_units="mm/d")
    return _from_xclim(pet).assign_attrs(units="mm/d", long_name="Thornthwaite PET")


def water_balance(tp_mm_month: xr.DataArray, pet_mm_day: xr.DataArray) -> xr.DataArray:
    """P - PET in mm/day; precipitation converted back from mm/month."""
    pr = tp_mm_month / tp_mm_month[TIME].dt.days_in_month
    return (pr - pet_mm_day).assign_attrs(units="mm/d", long_name="P - PET")


def _spei_block(wb: xr.DataArray) -> xr.DataArray:
    """SPEI-3 for one block of cells (dims time, cell); runs in a worker."""
    import warnings

    from xclim.indices import standardized_precipitation_evapotranspiration_index

    warnings.filterwarnings("ignore")  # scipy fit warnings on degenerate cells
    first, last = SPEI_CAL_YEARS
    out = standardized_precipitation_evapotranspiration_index(
        wb.assign_attrs(units="mm/d"), freq="MS", window=SPEI_SCALE, dist=SPEI_DIST,
        method=SPEI_FIT_METHOD, cal_start=f"{first}-01-01", cal_end=f"{last}-12-31")
    return out.load()


def spei_cells(wb: xr.DataArray, keep: xr.DataArray | None = None,
               workers: int | None = None, n_blocks: int | None = None) -> xr.DataArray:
    """SPEI-3 per grid cell, clipped to +-SPEI_CLIP.

    `wb` is P - PET in mm/day (valid_time, latitude, longitude). Only cells
    where `keep` is True (default: every cell with data) are fitted; others
    stay NaN. Cells are split into blocks fitted in parallel processes
    (workers=1 runs in this process).
    """
    if keep is None:
        keep = wb.notnull().any(TIME)
    stacked = _to_xclim(wb).stack({CELL: [LAT, LON]})
    stacked = stacked.isel({CELL: np.flatnonzero(keep.stack({CELL: [LAT, LON]}).values)})
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    n_blocks = n_blocks or max(1, min(stacked.sizes[CELL], workers * 4))
    blocks = [stacked.isel({CELL: idx}).reset_index(CELL)
              for idx in np.array_split(np.arange(stacked.sizes[CELL]), n_blocks) if len(idx)]
    if workers == 1:
        results = [_spei_block(b) for b in blocks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_spei_block, blocks))
    spei = xr.concat(results, dim=CELL)
    spei = spei.set_index({CELL: [LAT, LON]}).unstack(CELL)
    spei = _from_xclim(spei).reindex_like(wb.isel({TIME: 0}, drop=True))
    spei = spei.clip(-SPEI_CLIP, SPEI_CLIP)  # also maps +-inf to the clip
    return spei.transpose(TIME, LAT, LON).astype("float32").assign_attrs(
        units="1", long_name=f"SPEI-{SPEI_SCALE}", clip=SPEI_CLIP,
        calibration=f"{SPEI_CAL_YEARS[0]}-{SPEI_CAL_YEARS[1]}", dist=SPEI_DIST)


def season_spei(spei: xr.DataArray, months: tuple[int, ...]) -> xr.DataArray:
    """SPEI-3 for a 3-month season: the value at its last month, by year.

    The last month's year is the label, so (12, 1, 2) labelled Y is Dec of
    Y-1 to Feb of Y, matching WINTER_MONTHS and the ENSO year.
    """
    if len(months) != SPEI_SCALE:
        raise ValueError(f"Season {months} is not {SPEI_SCALE} months long.")
    end = spei.sel({TIME: spei[TIME].dt.month == months[-1]})
    return end.assign_coords(year=(TIME, end[TIME].dt.year.values)).swap_dims(
        {TIME: "year"}).drop_vars(TIME)


def restandardise(series: xr.DataArray, years: tuple[int, int] = SPEI_CAL_YEARS) -> xr.DataArray:
    """z-score along `year` using the mean and SD (ddof=1) of `years`, inclusive.

    Sorted by year first: a label slice on unsorted years selects the wrong
    span or nothing. Raises when a series has fewer than 2 calibration values
    (no SD), instead of returning NaN.
    """
    series = series.sortby("year")
    cal = series.sel(year=slice(*years))
    n = cal.count("year")
    if (n < 2).any():
        raise ValueError(f"Fewer than 2 values in {years[0]}-{years[1]} to standardise "
                         f"against (smallest count {int(n.min())}).")
    return (series - cal.mean("year")) / cal.std("year", ddof=1)


def regional_spei(spei: xr.DataArray, masks: xr.DataArray) -> xr.Dataset:
    """Regional SPEI-3 for DJF and JJA: cell means, then re-standardised."""
    out = {}
    for name, months in (("djf", WINTER_MONTHS), ("jja", SUMMER_MONTHS)):
        mean = regional_series(season_spei(spei, months), masks)
        out[f"spei3_{name}_cellmean"] = mean
        out[f"spei3_{name}"] = restandardise(mean)
    ds = xr.Dataset(out)
    ds["whiplash"] = ds["spei3_jja"] - ds["spei3_djf"]
    return ds


def whiplash_table(regional: xr.Dataset, winters: pd.DataFrame) -> pd.DataFrame:
    """Tidy region x year table with ENSO columns; years without a DJF value
    (the first year) are dropped; a year whose summer is not yet published
    keeps its DJF value and has NaN whiplash."""
    table = regional.to_dataframe().reset_index()
    table = table.dropna(subset=["spei3_djf"])
    table["year"] = table["year"].astype(int)
    table = join_enso(table, winters)
    return table[["region", "year", "winter", "spei3_djf", "spei3_jja", "whiplash",
                  "spei3_djf_cellmean", "spei3_jja_cellmean", "enso_index", "enso_djf",
                  "phase", "strong"]]


def spei_cache_path(domain: str):
    return DATA_PROCESSED / f"spei3_cells_{domain}.nc"


def domain_spei(domain: str, ds: xr.Dataset, keep: xr.DataArray, refresh: bool = False) -> xr.DataArray:
    """Per-cell SPEI-3 for one domain, cached as NetCDF (the fit takes about
    an hour per domain)."""
    path = spei_cache_path(domain)
    if path.exists() and not refresh:
        return xr.open_dataarray(path)
    wb = water_balance(ds["tp"], pet_thornthwaite(ds["t2m"])).load()
    spei = spei_cells(wb, keep=keep)
    path.parent.mkdir(parents=True, exist_ok=True)
    spei.rename("spei3").to_netcdf(path, encoding={"spei3": {"zlib": True, "complevel": 4}})
    return spei


def main(refresh: bool = False) -> None:
    import time

    from src.config import ERA5_DOMAINS, REGIONS
    from src.era5 import assign_domains, open_domains, region_masks
    from src.regions import load_regions

    regions = load_regions()
    domains = assign_domains(regions)
    names = sorted(set(domains), key=list(ERA5_DOMAINS).index)
    datasets = open_domains(names)
    winters = pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv")
    parts = []
    for name in names:
        sub = regions[regions["region"].map(domains) == name]
        ds = datasets[name]
        masks = region_masks(sub, ds)
        keep = masks.any("region") & ds["tp"].isel({TIME: 0}).notnull()
        t0 = time.time()
        print(f"{name}: SPEI-3 for {int(keep.sum())} region cells...", flush=True)
        spei = domain_spei(name, ds, keep, refresh=refresh)
        print(f"{name}: done in {time.time() - t0:.0f} s", flush=True)
        parts.append(whiplash_table(regional_spei(spei, masks).compute(), winters))
    table = pd.concat(parts)
    table["region"] = pd.Categorical(table["region"], categories=list(REGIONS), ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(table)} rows, years {table['year'].min()}-{table['year'].max()}")


if __name__ == "__main__":
    import sys

    main(refresh="--refresh" in sys.argv[1:])
