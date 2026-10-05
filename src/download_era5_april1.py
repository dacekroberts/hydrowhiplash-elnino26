"""Download the 1 April 00:00 UTC snow water equivalent field from hourly ERA5-Land.

April 1 SWE is the snapshot snow surveys measure; the monthly-means product
only has an April mean centred mid-month (DECISIONS.md 2026-10-04, "ERA5-Land
SWE: glacier exclusion and April 1"). One request per domain, every year in
one file: data/raw/<domain folder>_april1/era5_land_april1.nc. The file is
small (one field per year), so a re-run downloads it again in full.

Dataset: reanalysis-era5-land (DOI 10.24381/cds.e2161bac), CC-BY 4.0; ledger
row and notices in DATA_SOURCES.md. Needs the same .cdsapirc as
src/download_era5.py.

UNITS: sd is metres of water equivalent (mm = sd * 1000), an instantaneous
value at 00:00 UTC (late afternoon of 31 March local time in the study area).
Time dimension "valid_time", one step per year.

Run:  python -m src.download_era5_april1            every domain
      python -m src.download_era5_april1 north      one domain
"""
import sys
from datetime import date, timedelta

import cdsapi

from src.config import (APRIL1_FOLDER_SUFFIX, CLIMATE_FIRST_YEAR, DATA_RAW,
                        ERA5_DOMAINS, ERA5_HOURLY_DATASET, ERA5_HOURLY_LAG_DAYS)
from src.download_era5 import is_access_error

RAW = DATA_RAW
VARIABLE = "snow_depth_water_equivalent"
FILENAME = "era5_land_april1.nc"


def april1_years(today: date) -> list[int]:
    """Years whose 1 April field is published, allowing for the hourly lag."""
    last = today.year if today - timedelta(days=ERA5_HOURLY_LAG_DAYS) >= date(today.year, 4, 1) \
        else today.year - 1
    return list(range(CLIMATE_FIRST_YEAR, last + 1))


def request(years: list[int], area: list[float]) -> dict:
    return {
        "product_type": ["reanalysis"],
        "variable": [VARIABLE],
        "year": [str(y) for y in years],
        "month": ["04"],
        "day": ["01"],
        "time": ["00:00"],
        "area": area,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }


def download_domain(client: cdsapi.Client, name: str, today: date) -> None:
    area, folder = ERA5_DOMAINS[name]
    out = RAW / f"{folder}{APRIL1_FOLDER_SUFFIX}"
    out.mkdir(parents=True, exist_ok=True)
    years = april1_years(today)
    target = out / FILENAME
    tmp = target.with_suffix(".tmp")
    print(f"domain {name}: 1 April 00:00 UTC SWE, {years[0]}-{years[-1]} -> {target}")
    try:
        client.retrieve(ERA5_HOURLY_DATASET, request(years, area), str(tmp))
    except Exception as err:
        if is_access_error(err):
            raise SystemExit(
                "Stopped: access refused (HTTP 401/403). Accept the dataset licence "
                "on the CDS page for reanalysis-era5-land, then re-run.") from err
        raise
    tmp.replace(target)  # write-then-rename: never leave a truncated file


def main(domains: list[str] | None = None) -> None:
    domains = domains or list(ERA5_DOMAINS)
    unknown = set(domains) - set(ERA5_DOMAINS)
    if unknown:
        raise SystemExit(f"Unknown domain(s) {sorted(unknown)}; choose from {list(ERA5_DOMAINS)}.")
    client = cdsapi.Client()
    today = date.today()
    for name in domains:
        download_domain(client, name, today)


if __name__ == "__main__":
    main(sys.argv[1:])
