"""Download ERA5-Land monthly precipitation and 2 m temperature.

Domain, years and variables come from src/config.py (ERA5_AREA,
CLIMATE_FIRST_YEAR, ERA5_VARIABLES). One NetCDF file per year, so a failed
request only costs one year; re-running skips years already downloaded.

Needs a Copernicus CDS account and a .cdsapirc file (see README).

UNITS (important):
  total_precipitation  monthly mean of daily totals, in metres per day.
                       mm/month = tp * 1000 * days_in_month
  2m_temperature       kelvin. deg C = t2m - 273.15
  In new CDS NetCDF files the time dimension is called "valid_time".
Regional means must be area-weighted: use src.geo.regional_mean.

Run:  python -m src.download_era5
"""
import zipfile
from datetime import date

import cdsapi

from src.config import (CLIMATE_FIRST_YEAR, DATA_RAW, ERA5_AREA, ERA5_DATASET,
                        ERA5_LAG_MONTHS, ERA5_VARIABLES)

OUT = DATA_RAW / "era5_land"


def request(year: int, months: list[int]) -> dict:
    return {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ERA5_VARIABLES,
        "year": [str(year)],
        "month": [f"{m:02d}" for m in months],
        "time": ["00:00"],
        "area": ERA5_AREA,
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


def retrieve(client: cdsapi.Client, year: int, months: list[int], target) -> None:
    """Download to a temporary file, then rename, so an interrupted download
    never leaves a truncated file that later runs would skip."""
    tmp = target.with_suffix(".tmp")
    client.retrieve(ERA5_DATASET, request(year, months), str(tmp))
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client()
    today = date.today()

    for year in range(CLIMATE_FIRST_YEAR, today.year + 1):
        months = months_available(year, today)
        if not months:
            continue
        full = len(months) == 12
        target = OUT / (f"era5_land_{year}.nc" if full else f"era5_land_{year}_partial.nc")
        partial = OUT / f"era5_land_{year}_partial.nc"
        if full and (target.exists() or target.with_suffix("").is_dir()):
            if partial.exists():
                partial.unlink()  # full year supersedes the partial file
            print(f"skip {year} (already downloaded)")
            continue
        print(f"requesting {year} ({len(months)} months)...")
        try:
            retrieve(client, year, months, target)
            if full and partial.exists():
                partial.unlink()
        except Exception as err:  # most recent months may not be published yet
            print(f"  {year} failed: {err}")


if __name__ == "__main__":
    main()
