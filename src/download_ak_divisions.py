"""Download the NOAA NCEI Alaska climate division boundaries (13 polygons,
Bieniek et al. 2012), for the descriptive Interior Alaska check (owner,
2026-10-11): climate only, no registered test reads it.

SOURCE: NOAA National Centers for Environmental Information, nClimDiv
  (doi:10.7289/V5M32STR), file AK_climate_divisions.zip in the monthly
  "current" folder (AK_DIVISIONS_URL; the older /pub/data/cirs/climdiv/
  address redirects there).
TERMS: read 2026-10-11 (DATA_SOURCES.md row "Alaska climate divisions"):
  citation asked, warranty disclaimers, no restriction on use.
UNITS: polygons only; no area field is used.

Run:  python -m src.download_ak_divisions              skip files present at full size
      python -m src.download_ak_divisions --refresh    download again
"""
import sys

import requests

from src.config import AK_DIVISIONS_FILES, AK_DIVISIONS_RAW, AK_DIVISIONS_URL
from src.download_cnfdb import size_check
from src.download_mtbs import IDENTITY, now_utc, server_headers, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = AK_DIVISIONS_RAW


def main(args: list[str] | None = None) -> None:
    refresh = "--refresh" in (args or [])
    OUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    record = {"url": AK_DIVISIONS_URL, "accessed_utc": now_utc(), "files": {}}
    try:
        for name in AK_DIVISIONS_FILES:
            url = AK_DIVISIONS_URL + name
            headers = server_headers(session, url)
            expected = int(headers["Content-Length"])
            target = OUT / name
            record["files"][name] = {**headers, "bytes": expected}
            if target.exists() and not refresh and target.stat().st_size == expected:
                print(f"skip {name} (present, {expected:,} bytes)")
                continue
            print(f"{name} <- {url} ({expected:,} bytes)")
            download(session, url, target, headers=IDENTITY,
                     check=size_check(expected, name.endswith(".zip")))
    except ClientError as err:
        raise stop_on_client_error(err) from err
    write_manifest(OUT / "manifest.json", record)
    print("manifest.json written")


if __name__ == "__main__":
    main(sys.argv[1:])
