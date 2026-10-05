"""Download the Yukon snow survey network record (Yukon Water Data API v2), as published.

Two CSV files (YUKON_SNOW_URLS in src/config.py) to data/raw/stations/yukon/:
snow_survey_data.csv (every measurement) and snow_survey_metadata.csv (one row
per location, with coordinates and survey counts). The API varies its answer
on the Accept header (a HEAD request reported JSON), so text/csv is asked for
explicitly. Bytes are saved unchanged; each file goes to a .tmp name, is
checked for its column header, then renamed. Re-runs skip files already
present; --refresh downloads both again.

DATA COLUMNS: location_code, location_name, parameter, units, sample_date,
  target_date, year, month, result, flag. Long format: one row per location,
  survey and parameter ("snow water equivalent" in mm, "snow depth" in cm).
APRIL 1: rows with target_date 1 April (month 4); sample_date is the actual
  sampling date. month 5.5 is the 15 May survey.
FLAGS: "Actual" = averaged from measured depth and SWE; "Estimated SWE" = SWE
  estimated from measured depth and average historical density.
TRAPS: the files open with comment lines that are themselves quoted
  ('"# Description: ..."') plus an empty '""' line, so pandas comment="#"
  does not skip them; skip lines until the one starting "location_code".
  location_code prefix gives the drainage (08 Alsek, 09 Yukon, 10 Mackenzie).

Run:  python -m src.download_yukon_snow              skip files already present
      python -m src.download_yukon_snow --refresh    download both again
"""
import sys
from pathlib import Path

import requests

from src.config import YUKON_SNOW_RAW, YUKON_SNOW_URLS
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = YUKON_SNOW_RAW
HEADERS = {"Accept": "text/csv"}
HEADER_START = "location_code,"


def check_header(path: Path) -> None:
    """The column header must follow the comment block; otherwise it is an
    error page or a JSON answer."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(HEADER_START):
                return
            if not (line.startswith('"#') or line.startswith("#") or line.strip() in ("", '""')):
                break
    raise ValueError(f"{path.name}: no '{HEADER_START}' header after the comment block")


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    refresh = "--refresh" in args
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    for name, url in YUKON_SNOW_URLS.items():
        target = out / name
        if target.exists() and not refresh:
            print(f"skip {name} (already downloaded)")
            continue
        print(f"{name} <- {url}")
        try:
            download(session, url, target, headers=HEADERS, check=check_header)
        except ClientError as err:
            raise stop_on_client_error(err) from err
        print(f"  {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
