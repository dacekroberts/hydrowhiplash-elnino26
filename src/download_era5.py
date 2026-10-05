"""Download ERA5-Land monthly means for each domain and variable set.

Domains, years and variables come from src/config.py (ERA5_DOMAINS,
CLIMATE_FIRST_YEAR, ERA5_VARIABLE_SETS). Set "core" is precipitation, 2 m
temperature and SWE; set "snow_soil" is snowfall and soil moisture layers
1-2. Each domain and set has its own folder under data/raw (the domain's
folder plus the set's suffix), one NetCDF file per year, so a failed request only costs one year;
re-running skips years already downloaded.

Needs a Copernicus CDS account and a .cdsapirc file (see README).

UNITS (important):
  total_precipitation  monthly mean of daily totals, in metres per day.
                       mm/month = tp * 1000 * days_in_month
  2m_temperature       kelvin. deg C = t2m - 273.15
  snowfall             (sf) expected m water equivalent per day, the tp
                       convention; confirm on the first file.
  volumetric_soil_water_layer_1/2  (swvl1, swvl2) m3/m3, layers 0-7 and
                       7-28 cm.
  snow_depth_water_equivalent  (sd) metres of water equivalent, monthly mean
                       of the month, not a first-of-month value. mm = sd * 1000
  In new CDS NetCDF files the time dimension is called "valid_time".
  The file's tp units attribute reads "m"; the values are m/day (wettest
  cell, Feb 1950: 25.8 mm/day). Drop the leftover GRIB coordinates expver
  and number before combining years: expver can differ for recent months.
Regional means must be area-weighted: use src.geo.regional_mean.

Run:  python -m src.download_era5                       core set, every domain
      python -m src.download_era5 north                 core set, one domain
      python -m src.download_era5 --set snow_soil main  another set
"""
import sys
import zipfile
from datetime import date

import cdsapi

from src.config import (CLIMATE_FIRST_YEAR, DATA_RAW, ERA5_DATASET, ERA5_DOMAINS,
                        ERA5_LAG_MONTHS, ERA5_VARIABLE_SETS)

RAW = DATA_RAW


def request(year: int, months: list[int], area: list[float],
            variables: list[str] = ERA5_VARIABLE_SETS["core"][0]) -> dict:
    return {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": list(variables),
        "year": [str(year)],
        "month": [f"{m:02d}" for m in months],
        "time": ["00:00"],
        "area": area,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }


def months_available(year: int, today: date) -> list[int]:
    """Months of `year` expected to be published, allowing for ERA5-Land's lag."""
    # Latest safe month = current month minus the lag (Oct with a 3-month lag
    # gives July). Counted 0-based from year 0, then converted back.
    last = (today.year * 12 + today.month - 1) - ERA5_LAG_MONTHS
    last_year, last_month = divmod(last, 12)
    last_month += 1
    if year < last_year:
        return list(range(1, 13))
    if year == last_year:
        return list(range(1, last_month + 1))
    return []


def is_access_error(err: Exception) -> bool:
    """True for HTTP 401/403: a bad key or an unaccepted licence.

    These apply to the whole account, so every later year would fail the same
    way. On 2026-10-04 an unaccepted licence produced 77 identical 403s before
    this check existed.
    """
    response = getattr(err, "response", None)
    return getattr(response, "status_code", None) in (401, 403)


def retrieve(client: cdsapi.Client, year: int, months: list[int], area: list[float],
             target, variables: list[str] = ERA5_VARIABLE_SETS["core"][0]) -> None:
    """Download to a temporary file, then rename, so an interrupted download
    never leaves a truncated file that later runs would skip."""
    tmp = target.with_suffix(".tmp")
    client.retrieve(ERA5_DATASET, request(year, months, area, variables), str(tmp))
    if zipfile.is_zipfile(tmp):
        # Mixed accumulated and instantaneous variables can arrive zipped,
        # one NetCDF per variable group, even with "unarchived" requested.
        folder = target.with_suffix("")
        with zipfile.ZipFile(tmp) as zf:
            zf.extractall(folder)
        tmp.unlink()
        print(f"  {year}: archive unpacked to {folder.name}/ (one file per variable group)")
        return
    tmp.replace(target)


def download_domain(client: cdsapi.Client, name: str, today: date,
                    variable_set: str = "core") -> None:
    area, folder = ERA5_DOMAINS[name]
    variables, suffix = ERA5_VARIABLE_SETS[variable_set]
    out = RAW / f"{folder}{suffix}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"domain {name}, set {variable_set} {variables}: {area} -> {out}")
    for year in range(CLIMATE_FIRST_YEAR, today.year + 1):
        months = months_available(year, today)
        if not months:
            continue
        full = len(months) == 12
        target = out / (f"era5_land_{year}.nc" if full else f"era5_land_{year}_partial.nc")
        partial = out / f"era5_land_{year}_partial.nc"
        if full and (target.exists() or target.with_suffix("").is_dir()):
            if partial.exists():
                partial.unlink()  # full year supersedes the partial file
            print(f"skip {year} (already downloaded)")
            continue
        print(f"requesting {year} ({len(months)} months)...")
        try:
            retrieve(client, year, months, area, target, variables)
            if full and partial.exists():
                partial.unlink()
        except Exception as err:  # most recent months may not be published yet
            print(f"  {year} failed: {err}")
            if is_access_error(err):
                raise SystemExit(
                    "Stopped: access refused (HTTP 401/403). Check the key in "
                    ".cdsapirc and that the dataset licence is accepted on the CDS "
                    "Download tab, then re-run; finished years are skipped.") from err


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    variable_set = "core"
    if "--set" in args:
        i = args.index("--set")
        if i + 1 >= len(args):
            raise SystemExit(f"--set needs a name from {list(ERA5_VARIABLE_SETS)}.")
        variable_set = args[i + 1]
        del args[i:i + 2]
    if variable_set not in ERA5_VARIABLE_SETS:
        raise SystemExit(f"Unknown variable set {variable_set!r}; choose from "
                         f"{list(ERA5_VARIABLE_SETS)}.")
    domains = args or list(ERA5_DOMAINS)
    unknown = set(domains) - set(ERA5_DOMAINS)
    if unknown:
        raise SystemExit(f"Unknown domain(s) {sorted(unknown)}; choose from {list(ERA5_DOMAINS)}.")
    client = cdsapi.Client()
    today = date.today()
    for name in domains:
        download_domain(client, name, today, variable_set)


if __name__ == "__main__":
    main(sys.argv[1:])
