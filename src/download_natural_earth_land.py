"""Download Natural Earth's 1:50m land polygons, the backdrop of the map
page: land outside the seven regions, drawn under them and over the ocean
panels (D99). Display only: nothing is measured from these shapes, and no
registered test, reported run or forecast reads them.

SOURCE: Natural Earth, 1:50m physical vectors, `ne_50m_land`
  (NATURAL_EARTH_LAND_URL, served from naciscdn.org).
TERMS: public domain (DATA_SOURCES.md, the Natural Earth rows; terms read
  2026-10-04). No credit required.
UNITS: polygons in EPSG:4326, split at the 180th meridian.

Run:  python -m src.download_natural_earth_land              skip if present at full size
      python -m src.download_natural_earth_land --refresh    download again
"""
import sys

import requests

from src.config import NATURAL_EARTH_LAND_RAW, NATURAL_EARTH_LAND_URL
from src.download_cnfdb import size_check
from src.download_mtbs import IDENTITY, now_utc, server_headers, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error


def main(args: list[str] | None = None) -> None:
    refresh = "--refresh" in list(args or [])
    target = NATURAL_EARTH_LAND_RAW
    target.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    try:
        headers = server_headers(session, NATURAL_EARTH_LAND_URL)
        expected = int(headers["Content-Length"])
        fetched = refresh or not target.exists() or target.stat().st_size != expected
        if fetched:
            download(session, NATURAL_EARTH_LAND_URL, target, headers=IDENTITY,
                     check=size_check(expected, False))
    except ClientError as err:
        raise stop_on_client_error(err) from err
    write_manifest(target.parent / "manifest.json",
                   {"url": NATURAL_EARTH_LAND_URL, "accessed_utc": now_utc(),
                    "files": {target.name: {**headers, "bytes": expected}}})
    print(f"{target.name}: {expected:,} bytes, {'downloaded' if fetched else 'already present'}; "
          "manifest.json written")


if __name__ == "__main__":
    main(sys.argv[1:])
