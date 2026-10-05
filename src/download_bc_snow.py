"""Download the BC manual snow survey record (BC River Forecast Centre), as published.

Two CSV files (BC_SNOW_URLS in src/config.py) to data/raw/stations/bc/:
allmss_archive.csv (the historical record) and allmss_current.csv (the
current season). Bytes are saved unchanged; parsing happens later. Each file
goes to a .tmp name, its header is checked, then it is renamed, so an
interrupted run never leaves a truncated file. Re-runs skip files already
present; --refresh downloads both again (the current file changes during the
snow season).

COLUMNS: Snow Course Name, Number, Elev. metres, Date of Survey, Snow Depth cm,
  Water Equiv. mm, Survey Code, Snow Line Elev. m, Density %, Survey Period.
UNITS: SWE (Water Equiv.) mm, depth cm, elevation m, density percent.
APRIL 1: the survey with Survey Period "01-Apr"; Date of Survey is the actual
  sampling date (yyyy/mm/dd), often a few days either side of 1 April.
TRAPS: header names carry leading spaces (" Number", "  Survey Code"), so
  strip them after reading. Lines end in CRLF. Course numbers with a letter
  suffix (1A06A) can be a relocated replacement of the course without it.

Run:  python -m src.download_bc_snow              skip files already present
      python -m src.download_bc_snow --refresh    download both again
"""
import sys
from pathlib import Path

import requests

from src.config import BC_SNOW_RAW, BC_SNOW_URLS
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = BC_SNOW_RAW
HEADER_START = "Snow Course Name"


def check_header(path: Path) -> None:
    """A real file starts with the column header; anything else is an error page."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
    if not first.startswith(HEADER_START):
        raise ValueError(f"{path.name}: unexpected first line {first[:80]!r}")


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    refresh = "--refresh" in args
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    for name, url in BC_SNOW_URLS.items():
        target = out / name
        if target.exists() and not refresh:
            print(f"skip {name} (already downloaded)")
            continue
        print(f"{name} <- {url}")
        try:
            download(session, url, target, check=check_header)
        except ClientError as err:
            raise stop_on_client_error(err) from err
        print(f"  {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
