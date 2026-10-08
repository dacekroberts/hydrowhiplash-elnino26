"""Download the CNFDB agency fire polygons (NFDB polygons) and their documentation.

Files in CNFDB_FILES (src/config.py) from the current-version folder
(CNFDB_URL), saved unchanged to data/raw/fire/cnfdb/: the whole-record
polygon zip, the English documentation, the update log, the shapefile
metadata and the ISO 19115 record. The folder listing is saved as
listing.html (it carries the release file dates), and manifest.json records
each file's Last-Modified, size and the download time. A file is written to
a .tmp name and renamed only once its size matches the server's
Content-Length (zips also pass a CRC check). Re-runs skip a file already
present at the server's size; --refresh downloads again.

Dataset: Natural Resources Canada, Canadian Forest Service, Open Government
Licence - Canada 2.0 with the provider's citation; ledger row and notice 10
in DATA_SOURCES.md.

COVERAGE: polygons end in 2024 (BC 1917-2024, AB 1931-2024, YT 1946-2024;
  D56, D57); only agency-mapped fires.
UNITS: SIZE_HA (agency) and CALC_HA (CFS) are not used; area comes from
  src.geo.area_ha.
DATES AND FLAGS: read from NFDB_documentation_EN.pdf at download; see
  docs/data_dictionary.md section 5.

Run:  python -m src.download_cnfdb              skip files present at full size
      python -m src.download_cnfdb --refresh    download again
"""
import sys
from pathlib import Path

import requests

from src.config import CNFDB_FILES, CNFDB_RAW, CNFDB_URL
from src.download_mtbs import IDENTITY, check_zip, now_utc, server_headers, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = CNFDB_RAW


def size_check(expected: int, is_zip: bool):
    def check(path: Path) -> None:
        got = path.stat().st_size
        if got != expected:
            raise ValueError(f"{path.name}: {got} bytes, server says {expected}")
        if is_zip:
            check_zip(path)
    return check


def main(args: list[str] | None = None) -> None:
    refresh = "--refresh" in (args or [])
    OUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    record = {"url": CNFDB_URL, "accessed_utc": now_utc(), "files": {}}
    try:
        download(session, CNFDB_URL, OUT / "listing.html", headers=IDENTITY)
        for name in CNFDB_FILES:
            url = CNFDB_URL + name
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
