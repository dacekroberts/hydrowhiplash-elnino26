"""Download the National Burned Area Composite (NBAC) fire polygons and metadata.

Files in NBAC_FILES (src/config.py) from NBAC_URL, saved unchanged to
data/raw/fire/nbac/: the whole-record polygon zip of release NBAC_RELEASE
(1972-2025) and its metadata PDF. The folder listing is saved as
listing.html (it carries the release file dates), and manifest.json records
each file's Last-Modified, size and the download time. A file is written to
a .tmp name and renamed only once its size matches the server's
Content-Length (zips also pass a CRC check). Re-runs skip a file already
present at the server's size; --refresh downloads again.

Dataset: Natural Resources Canada, Canadian Forest Service, Open Government
Licence - Canada 2.0 with the provider's citation; ledger row and notice 11
in DATA_SOURCES.md; documentation probe in docs/nbac_probe.md.

USE: the Parks Canada sensitivity run (D69, src.parks_gap) and the
  exploratory NBAC vs CNFDB comparison (owner, 2026-10-08). Not an input
  to any registered test.
UNIT: polygons split at provincial, territorial and national park
  boundaries; NFIREID and GID link the parts of one fire event.
DATES: no ignition date; AG_SDATE (agency start) and HS_SDATE (first
  hotspot, from 1989).
UNITS: area fields are not used; area comes from src.geo.area_ha.

Run:  python -m src.download_nbac              skip files present at full size
      python -m src.download_nbac --refresh    download again
"""
import sys

import requests

from src import later, pin_inputs
from src.config import NBAC_FILES, NBAC_RAW, NBAC_URL
from src.download_cnfdb import size_check
from src.download_mtbs import IDENTITY, now_utc, server_headers, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = NBAC_RAW


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    stamp = later.take_stamp(args)
    refresh = "--refresh" in args
    if stamp:
        # a later download: its own stamped folder, never the pinned one (D73)
        out = later.open_folder(OUT, stamp)
    else:
        # every file in this folder is a pinned input, and each run rewrites the
        # listing and manifest: refused without --rebuild (audit round 5 S1, S2)
        out = OUT
        pin_inputs.guard_folder(out, "--rebuild" in args)
        out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    record = {"url": NBAC_URL, "accessed_utc": now_utc(), "files": {}}
    try:
        download(session, NBAC_URL, out / "listing.html", headers=IDENTITY)
        for name in NBAC_FILES:
            url = NBAC_URL + name
            headers = server_headers(session, url)
            expected = int(headers["Content-Length"])
            target = out / name
            record["files"][name] = {**headers, "bytes": expected}
            if target.exists() and not refresh and target.stat().st_size == expected:
                print(f"skip {name} (present, {expected:,} bytes)")
                continue
            print(f"{name} <- {url} ({expected:,} bytes)")
            download(session, url, target, headers=IDENTITY,
                     check=size_check(expected, name.endswith(".zip")))
    except ClientError as err:
        raise stop_on_client_error(err) from err
    write_manifest(out / "manifest.json", record)
    print("manifest.json written")
    if stamp:
        later.record(out, stamp, NBAC_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
