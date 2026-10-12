"""Download CanSWE v8 (Canadian historical snow water equivalent, 1928-2025) from Zenodo.

The file list and md5 checksums come from the Zenodo record API
(CANSWE_RECORD_URL in src/config.py); the record JSON is saved alongside as
zenodo_record.json for provenance. Only CANSWE_FILES are downloaded, the
NetCDF and the English ReadMe, to data/raw/stations/canswe/; the CSV zip holds
the same data. Each file goes to a .tmp name, its md5 is checked against the
record, then it is renamed, so a truncated or corrupted file never lands.
Re-runs skip a file already present whose md5 matches; --refresh downloads
again.

Dataset: version DOI 10.5281/zenodo.19075529 (concept DOI
10.5281/zenodo.4734371), Open Government Licence - Canada; ledger row and
notices in DATA_SOURCES.md.

UNITS: snw (SWE) kg m-2, which equals mm of water. snd (depth) m. den
  (density) kg m-3.
DATES: the daily time axis holds the actual sampling dates, not nominal
  survey dates. Data end 31 July 2025.
FLAGS (data_flag_snw, agency): B = manual survey outside the nominal sampling
  period; Y = precise sampling date not available (NWT dates set to 1 April,
  Manitoba within a week of the reported date). qc_flag_snw: values failing
  QC (V automatic outlier, D density outside 25-700 kg m-3) are already NaN,
  with the flag kept; W marks SWE > 3000 kg m-2 (> 8000 west of 113 W).
  type_mes: 0 manual multi-point snow survey, 2 snow pillow or scale, 3
  passive gamma.
STATION IDS: prefix gives the agency: ALE- Alberta Environment, BCE- BC
  Environment, YT- Yukon, SCD- Meteorological Service of Canada.
TRAPS: exclude Hydro-Quebec stations (station_id prefix "HQ"): CC BY-NC-SA
  rather than the open licence, and outside the study area anyway.

Run:  python -m src.download_canswe              skip files whose md5 matches
      python -m src.download_canswe --refresh    download again
"""
import hashlib
import json
import sys
from pathlib import Path

import requests

from src import later
from src.config import CANSWE_FILES, CANSWE_RAW, CANSWE_RECORD_URL
from src.download_nrcs_snow import ClientError, download, stop_on_client_error

OUT = CANSWE_RAW
RECORD_NAME = "zenodo_record.json"


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_files(record: dict, wanted: list[str] = CANSWE_FILES) -> list[dict]:
    """Record entries for the wanted keys, as {"key", "url", "md5"}, in that order."""
    by_key = {f["key"]: f for f in record["files"]}
    missing = [k for k in wanted if k not in by_key]
    if missing:
        raise SystemExit(f"Not in the Zenodo record: {missing}; found {sorted(by_key)}.")
    picked = []
    for key in wanted:
        entry = by_key[key]
        algo, _, value = entry["checksum"].partition(":")
        if algo != "md5":
            raise SystemExit(f"{key}: expected an md5 checksum, got {entry['checksum']!r}.")
        links = entry["links"]
        picked.append({"key": key, "url": links.get("content") or links["self"], "md5": value})
    return picked


def md5_check(expected: str):
    def check(path: Path) -> None:
        got = md5(path)
        if got != expected:
            raise ValueError(f"md5 mismatch: got {got}, record says {expected}")
    return check


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    stamp = later.take_stamp(args)
    refresh = "--refresh" in args
    out = later.open_folder(OUT, stamp) if stamp else OUT
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    try:
        record_path = out / RECORD_NAME
        download(session, CANSWE_RECORD_URL, record_path,
                 headers={"Accept": "application/json"},
                 check=lambda p: json.loads(p.read_text(encoding="utf-8"))["files"])
        record = json.loads(record_path.read_text(encoding="utf-8"))
        for entry in select_files(record):
            target = out / entry["key"]
            if target.exists() and not refresh and md5(target) == entry["md5"]:
                print(f"skip {entry['key']} (present, md5 matches)")
                continue
            print(f"{entry['key']} <- {entry['url']}")
            download(session, entry["url"], target, check=md5_check(entry["md5"]))
            print(f"  {target.stat().st_size:,} bytes, md5 OK")
    except ClientError as err:
        raise stop_on_client_error(err) from err
    if stamp:
        later.record(out, stamp, CANSWE_RECORD_URL)


if __name__ == "__main__":
    main(sys.argv[1:])
