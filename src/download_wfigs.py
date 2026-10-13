"""Download WFIGS Interagency Fire Perimeters (all years) as one snapshot.

The layer is live (edited about every 5 minutes), so it is not paged through
the query API, where a reload mid-download could skip or repeat features.
Instead the ArcGIS Hub export (WFIGS_EXPORT_URL in src/config.py) is asked
for an up-to-date GeoJSON of the whole layer, polled until ready, and saved
unchanged to data/raw/fire/wfigs/wfigs_perimeters.geojson. The item and
layer JSON are saved beside it, and manifest.json records the export's
record count and time, the layer's dataLastEditDate and the download time.
The file is renamed into place only once it holds as many features as the
export reported. Re-runs skip a file already present; --refresh asks for a
new snapshot.

Dataset: National Interagency Fire Center, WFIGS group; freely accessible,
the item's disclaimer travels with the data; ledger row and notice 9 in
DATA_SOURCES.md.

COVERAGE: "only certified perimeters and new perimeters captured starting in
  2021"; data before 2021 incomplete, so the MTBS-to-WFIGS cutover cannot be
  earlier. Alaska included (US-AK origin perimeters, checked 2026-10-07).
FIELDS: attr_IncidentTypeCategory (WF wildfire, RX prescribed; no coded
  values), attr_FireDiscoveryDateTime (UTC), attr_POOState, attr_IrwinID,
  attr_IsCpxChild and attr_CpxID (complexes), poly_FeatureCategory.
TRAPS: poly_GISAcres and poly_Acres_AutoCalc are not used (area from
  src.geo.area_ha). Dates are epoch milliseconds in UTC.

Run:  python -m src.download_wfigs              skip if the snapshot is present
      python -m src.download_wfigs --refresh    take a new snapshot
"""
import json
import sys
import time
from pathlib import Path

import pyogrio
import requests

from src import later, pin_inputs
from src.config import (WFIGS_EXPORT_URL, WFIGS_EXPORT_WAIT_S, WFIGS_ITEM_URL,
                        WFIGS_LAYER_URL, WFIGS_RAW)
from src.download_mtbs import IDENTITY, now_utc, write_manifest
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = WFIGS_RAW
TARGET = OUT / "wfigs_perimeters.geojson"
POLL_S = 15


def request_export(session) -> dict:
    """Poll the Hub export until it reports Completed; return its status JSON."""
    deadline = time.monotonic() + WFIGS_EXPORT_WAIT_S
    while True:
        r = session.get(WFIGS_EXPORT_URL, params={"redirect": "false", "layers": "0"},
                        timeout=120)
        status = r.json()
        if status.get("status") == "Completed":
            return status
        if time.monotonic() > deadline:
            raise SystemExit(f"Hub export not ready after {WFIGS_EXPORT_WAIT_S} s: {status}")
        print(f"  export {status.get('status')} {status.get('progressInPercent', '')}%")
        time.sleep(POLL_S)


def count_check(expected: int | None):
    def check(path: Path) -> None:
        n = pyogrio.read_info(path)["features"]
        if expected is not None and n != expected:
            raise ValueError(f"{path.name}: {n} features, export reported {expected}")
    return check


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
    target = out / TARGET.name
    if target.exists() and not refresh:
        print(f"skip {target.name} (present)")
        return
    session = requests.Session()
    try:
        download(session, WFIGS_ITEM_URL, out / "item.json", params={"f": "json"})
        download(session, WFIGS_LAYER_URL, out / "layer.json", params={"f": "json"})
        # Ask for a fresh snapshot first, so the export cannot be an old cache.
        session.get(WFIGS_EXPORT_URL, params={"redirect": "false", "layers": "0"}, timeout=120)
        status = request_export(session)
        accessed = now_utc()
        print(f"{target.name} <- {status['resultUrl']}")
        download(session, status["resultUrl"], target, headers=IDENTITY,
                 check=count_check(status.get("recordCount")))
    except ClientError as err:
        raise stop_on_client_error(err) from err
    layer = json.loads((out / "layer.json").read_text(encoding="utf-8"))
    write_manifest(out / "manifest.json", {
        "export_url": WFIGS_EXPORT_URL, "result_url": status["resultUrl"],
        "export_status": status, "accessed_utc": accessed,
        "layer_editing_info": layer.get("editingInfo"),
        "bytes": target.stat().st_size,
        "features": pyogrio.read_info(target)["features"],
    })
    print(f"  {target.stat().st_size:,} bytes; manifest.json written")
    if stamp:
        later.record(out, stamp, WFIGS_EXPORT_URL)
    else:
        # the run rewrote a pinned folder: which of its files differ from their pins
        pin_inputs.report_folder(out)


if __name__ == "__main__":
    main(sys.argv[1:])
