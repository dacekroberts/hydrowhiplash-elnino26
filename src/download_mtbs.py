"""Download the MTBS burned-area boundaries (all published fires, 1984 to the latest release).

One zip of the national shapefile (MTBS_PERIMETER_URL in src/config.py), the
"MTBS Burned Areas Boundaries Dataset" of the Direct Download page, saved
unchanged to data/raw/fire/mtbs/. MTBS replaces the file at each quarterly
release and revises fires in place, so the server's Last-Modified and ETag,
the download time and the zip's member list go to manifest.json. The release
metadata inside the zip (FGDC XML) is extracted beside it for the ledger.
Re-runs skip a valid zip already present; --refresh downloads again.

Dataset: USGS EROS and USDA Forest Service, US public domain (CC0 on the
ScienceBase release); ledger row and notice 8 in DATA_SOURCES.md.

UNITS: the acreage field (BurnBndAc) is from 30 m pixel counts and is not
  used; area comes from src.geo.area_ha.
FIELDS: Event_ID, Incid_Name, Incid_Type, Ig_Date (ignition date), BurnBndAc,
  BurnBndLat, BurnBndLon, plus severity thresholds.
TRAPS: Incid_Type includes "Prescribed Fire" (dropped in src/fire.py; kept
  types in MTBS_KEEP_TYPES). Burned-area boundaries, not incident perimeters:
  unburned islands are not cut out. Recent seasons are still being mapped,
  which sets the MTBS-to-WFIGS cutover. The server sends the zip
  brotli-encoded unless asked for identity encoding.

Run:  python -m src.download_mtbs              skip if a valid zip is present
      python -m src.download_mtbs --refresh    download again
"""
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

from src import later, pin_inputs
from src.config import MTBS_PERIMETER_URL, MTBS_RAW
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = MTBS_RAW
IDENTITY = {"Accept-Encoding": "identity"}


def check_zip(path: Path) -> None:
    """Raise unless path is a zip whose every member passes its CRC check."""
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
    if bad is not None:
        raise ValueError(f"{path.name}: CRC check failed at {bad}")


def server_headers(session, url: str) -> dict:
    """Last-Modified, ETag and Content-Length of url, for the manifest."""
    r = session.head(url, headers=IDENTITY, allow_redirects=True, timeout=60)
    r.raise_for_status()
    return {k: r.headers.get(k) for k in ("Last-Modified", "ETag", "Content-Length")}


def write_manifest(path: Path, record: dict) -> None:
    path.write_bytes(json.dumps(record, indent=2).encode("utf-8"))


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def extract_metadata(zip_path: Path, out: Path) -> list[str]:
    """Copy the zip's XML and text members (release metadata) next to it."""
    names = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.lower().endswith((".xml", ".txt", ".htm", ".html", ".pdf")):
                (out / Path(name).name).write_bytes(zf.read(name))
                names.append(Path(name).name)
    return names


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
    target = out / Path(MTBS_PERIMETER_URL).name
    session = requests.Session()
    if target.exists() and not refresh:
        check_zip(target)
        print(f"skip {target.name} (present, zip valid)")
        return
    try:
        headers = server_headers(session, MTBS_PERIMETER_URL)
        print(f"{target.name} <- {MTBS_PERIMETER_URL} ({headers['Content-Length']} bytes, "
              f"Last-Modified {headers['Last-Modified']})")
        accessed = now_utc()
        download(session, MTBS_PERIMETER_URL, target, headers=IDENTITY, check=check_zip)
    except ClientError as err:
        raise stop_on_client_error(err) from err
    with zipfile.ZipFile(target) as zf:
        members = zf.namelist()
    write_manifest(out / "manifest.json", {
        "url": MTBS_PERIMETER_URL, "accessed_utc": accessed, "server": headers,
        "bytes": target.stat().st_size, "members": members,
        "metadata_extracted": extract_metadata(target, out),
    })
    print(f"  {target.stat().st_size:,} bytes, zip valid; manifest.json written")
    if stamp:
        later.record(out, stamp, MTBS_PERIMETER_URL)
    else:
        # the run rewrote a pinned folder: which of its files differ from their pins
        pin_inputs.report_folder(out)


if __name__ == "__main__":
    main(sys.argv[1:])
