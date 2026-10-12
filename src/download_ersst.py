"""Download NOAA ERSST v6 monthly sea-surface temperature, the December,
January and February files only, for the map page's ocean panels (D99).
Visualisation only: no registered test, no reported run and no forecast
reads these files, and they are not pinned inputs.

SOURCE: NOAA National Centers for Environmental Information, Extended
  Reconstructed Sea Surface Temperature version 6, one NetCDF file per
  month (ERSST_URL, ersst.v6.YYYYMM.nc). Version 6 is the version NOAA
  CPC computes ONI and RONI from (CPC's RONI page, read 2026-10-12).
TERMS: read 2026-10-12 (DATA_SOURCES.md row "ERSST v6"): the files' own
  `license` attribute is "No constraints on data access or use"; an
  acknowledgment and two papers to cite.
UNITS: `sst` in degrees Celsius on a 2 degree grid (lat -88 to 88, lon 0 to
  358 east); `ssta` is NOAA's anomaly against 1991-2020 and is not used
  (src.ocean computes its own, so the base period is a setting here).
  Land and ice-covered cells are missing.

Run:  python -m src.download_ersst              skip files present at full size
      python -m src.download_ersst --refresh    download again
"""
import sys

import requests

from src import later
from src.config import CLIMATE_FIRST_YEAR, ERSST_LAST_WINTER, ERSST_RAW, ERSST_URL, SST_MONTHS
from src.download_cnfdb import size_check
from src.download_mtbs import IDENTITY, now_utc, server_headers, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = ERSST_RAW


def file_names() -> list[str]:
    """Every file of every winter from the first full one: winter Y is
    December Y-1 with January and February Y."""
    names = []
    for winter in range(CLIMATE_FIRST_YEAR + 1, ERSST_LAST_WINTER + 1):
        for month in SST_MONTHS:
            year = winter - 1 if month == 12 else winter
            names.append(f"ersst.v6.{year}{month:02d}.nc")
    return names


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    stamp = later.take_stamp(args)
    refresh = "--refresh" in args
    out = later.open_folder(OUT, stamp) if stamp else OUT
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    record = {"url": ERSST_URL, "accessed_utc": now_utc(), "files": {}}
    fetched = 0
    try:
        for name in file_names():
            url = ERSST_URL + name
            headers = server_headers(session, url)
            expected = int(headers["Content-Length"])
            target = out / name
            record["files"][name] = {**headers, "bytes": expected}
            if target.exists() and not refresh and target.stat().st_size == expected:
                continue
            download(session, url, target, headers=IDENTITY, check=size_check(expected, False))
            fetched += 1
    except ClientError as err:
        raise stop_on_client_error(err) from err
    write_manifest(out / "manifest.json", record)
    print(f"{len(record['files'])} files listed, {fetched} downloaded; manifest.json written")
    if stamp:
        later.record(out, stamp, ERSST_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
