"""Download raw NRCS snow water equivalent for WA, OR, ID and AK from the AWDB REST API.

Two networks per state (NRCS_NETWORKS in src/config.py): SNTL (SNOTEL snow
pillows) and SNOW (manual snow courses). Element WTEQ, CLIMATE_FIRST_YEAR-01-01
to today, raw and unfiltered: flags returned, suspect data kept. Cleaning
happens later, never here.

Files under data/raw/stations/nrcs/:
  stations_<ST>.json            station metadata, discontinued sites included
  data_<ST>_<NET>_<NNN>.json    data, one file per batch of NRCS_BATCH_SIZE
  manifest.json                 request settings and the triplets in each batch
Every file is written to a .tmp name, checked to parse as JSON, then renamed,
so an interrupted run never leaves a truncated file. Re-runs skip files
already present; --refresh downloads everything again. Batches are cut from
the saved station metadata, so a resumed run batches the same way.

UNITS: inches of water. mm = in * 25.4.
DURATIONS AND DATES (checked against the API 2026-10-05):
  SNTL  MONTHLY, periodRef START: {"year", "month", "value"}; month 4 is the
        midnight reading that opens 1 April (equals the DAILY value dated
        31 March under the default periodRef END).
  SNOW  SEMIMONTHLY, periodRef START: {"year", "month", "monthPart",
        "collectionDate", "value"}; the April 1 survey is month 4, monthPart
        "1", usually collected in the last days of March. Under periodRef END
        the same value is labelled month 3, monthPart "2". Some older
        collectionDate values are implausible (21C11:WA:SNOW in 2000 shows
        the 1 Feb survey collected 2000-03-01 and the 1 Mar survey 2000-05-01);
        check them before trusting a date.
FLAGS: qaFlag U (unapproved), R (reviewed), P (provisional), A (approved).
  qcFlag includes V (valid), E (edited or estimated), S (suspect) and B (back
  estimate by regression, used to homogenise a snow course and its
  replacement pillow; not a measurement).
TRAPS: the stations endpoint defaults to activeOnly=true, which silently drops
  discontinued sites (WA: 131 active of 315); always activeOnly=false. The
  data endpoint defaults to periodRef END and drops suspect values unless
  returnSuspectData=true.

Run:  python -m src.download_nrcs_snow                 every state
      python -m src.download_nrcs_snow WA OR           some states
      python -m src.download_nrcs_snow --refresh       download again
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

import requests

from src.config import (CLIMATE_FIRST_YEAR, HTTP_BACKOFF_S, HTTP_RETRIES,
                        HTTP_TIMEOUT_S, NRCS_AWDB_URL, NRCS_BATCH_SIZE,
                        NRCS_ELEMENT, NRCS_NETWORKS, NRCS_PAUSE_S,
                        NRCS_SNOW_RAW, NRCS_STATES)

OUT = NRCS_SNOW_RAW
RETRY_STATUS = {429, 500, 502, 503, 504}
RETRY_ERRORS = (requests.ConnectionError, requests.Timeout,
                requests.exceptions.ChunkedEncodingError)


class ClientError(Exception):
    """HTTP 4xx other than 429: the request itself is wrong, so retrying or
    moving on to the next batch would fail the same way."""


def stop_on_client_error(err: ClientError) -> SystemExit:
    return SystemExit(f"Stopped: {err}. Check the URL and parameters in "
                      "src/config.py, then re-run; finished files are skipped.")


def write_atomic(response, target: Path, check=None) -> None:
    """Stream a response to target via a .tmp file, renamed only after the
    whole body arrived and check(tmp) passed. On any failure the .tmp file is
    removed and target is left as it was."""
    tmp = target.with_name(target.name + ".tmp")
    try:
        with open(tmp, "wb") as fh:
            for chunk in response.iter_content(chunk_size=1 << 16):
                fh.write(chunk)
        if check is not None:
            check(tmp)
        tmp.replace(target)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def download(session, url: str, target: Path, params: dict | None = None,
             headers: dict | None = None, check=None) -> None:
    """GET url into target with retries on 5xx, 429 and network errors.

    Raises ClientError on any other 4xx, and the last error once
    HTTP_RETRIES retries are spent.
    """
    for attempt in range(HTTP_RETRIES + 1):
        try:
            response = session.get(url, params=params, headers=headers,
                                   timeout=HTTP_TIMEOUT_S, stream=True)
            status = response.status_code
            if 400 <= status < 500 and status not in RETRY_STATUS:
                raise ClientError(f"HTTP {status} for {url}")
            if status in RETRY_STATUS:
                raise requests.HTTPError(f"HTTP {status} for {url}")
            response.raise_for_status()
            write_atomic(response, target, check)
            return
        except (requests.HTTPError, *RETRY_ERRORS) as err:
            if attempt == HTTP_RETRIES:
                raise
            wait = HTTP_BACKOFF_S * 2 ** attempt
            print(f"  {target.name}: {err}; retry {attempt + 1} of {HTTP_RETRIES} "
                  f"in {wait:.0f} s")
            time.sleep(wait)


def check_json_list(path: Path) -> None:
    """The AWDB endpoints answer with a JSON list; anything else is an error page."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name}: expected a JSON list, got {type(payload).__name__}")


def stations_params(state: str) -> dict:
    return {
        "stationTriplets": ",".join(f"*:{state}:{net}" for net in NRCS_NETWORKS),
        "elements": NRCS_ELEMENT,
        "activeOnly": "false",  # the default (true) drops discontinued sites
        "returnStationElements": "true",
    }


def data_params(triplets: list[str], network: str, today: date) -> dict:
    duration, period_ref = NRCS_NETWORKS[network]
    return {
        "stationTriplets": ",".join(triplets),
        "elements": NRCS_ELEMENT,
        "duration": duration,
        "periodRef": period_ref,
        "beginDate": f"{CLIMATE_FIRST_YEAR}-01-01",
        "endDate": today.isoformat(),
        "returnFlags": "true",
        "returnSuspectData": "true",
    }


def batches(items: list[str], size: int = NRCS_BATCH_SIZE) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def network_triplets(stations: list[dict], network: str) -> list[str]:
    return sorted(s["stationTriplet"] for s in stations if s.get("networkCode") == network)


def download_state(session, state: str, today: date, refresh: bool,
                   out: Path, failures: list[str]) -> list[dict]:
    """Download one state's metadata and data batches; return manifest rows."""
    meta = out / f"stations_{state}.json"
    if refresh or not meta.exists():
        print(f"{state}: station metadata")
        download(session, NRCS_AWDB_URL + "stations", meta, stations_params(state),
                 check=check_json_list)
        time.sleep(NRCS_PAUSE_S)
    stations = json.loads(meta.read_text(encoding="utf-8"))
    rows = []
    for network, (duration, period_ref) in NRCS_NETWORKS.items():
        triplets = network_triplets(stations, network)
        groups = batches(triplets)
        print(f"{state} {network}: {len(triplets)} stations, {len(groups)} batches")
        for n, group in enumerate(groups, 1):
            target = out / f"data_{state}_{network}_{n:03d}.json"
            rows.append({"file": target.name, "state": state, "network": network,
                         "duration": duration, "periodRef": period_ref,
                         "triplets": group})
            if target.exists() and not refresh:
                continue
            try:
                download(session, NRCS_AWDB_URL + "data", target,
                         data_params(group, network, today), check=check_json_list)
            except ClientError:
                raise
            except Exception as err:  # spent retries: note it, carry on, re-run later
                print(f"  {target.name} failed: {err}")
                failures.append(target.name)
            time.sleep(NRCS_PAUSE_S)
    return rows


def write_manifest(rows: list[dict], today: date, out: Path) -> None:
    manifest = {
        "source": NRCS_AWDB_URL,
        "element": NRCS_ELEMENT,
        "units": "in",
        "beginDate": f"{CLIMATE_FIRST_YEAR}-01-01",
        "endDate": today.isoformat(),
        "written": today.isoformat(),
        "networks": {k: {"duration": d, "periodRef": p} for k, (d, p) in NRCS_NETWORKS.items()},
        "files": rows,
    }
    target = out / "manifest.json"
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_bytes(json.dumps(manifest, indent=1).encode("utf-8"))
    tmp.replace(target)


def main(args: list[str] | None = None) -> None:
    args = list(args or [])
    refresh = "--refresh" in args
    states = [a for a in args if a != "--refresh"] or list(NRCS_STATES)
    unknown = set(states) - set(NRCS_STATES)
    if unknown:
        raise SystemExit(f"Unknown state(s) {sorted(unknown)}; choose from {NRCS_STATES}.")
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    today = date.today()
    session = requests.Session()
    rows, failures = [], []
    try:
        for state in states:
            rows += download_state(session, state, today, refresh, out, failures)
    except ClientError as err:
        raise stop_on_client_error(err) from err
    manifest_path = out / "manifest.json"
    if manifest_path.exists() and set(states) != set(NRCS_STATES):
        old = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
        rows = [r for r in old if r["state"] not in states] + rows
    write_manifest(rows, today, out)
    if failures:
        raise SystemExit(f"{len(failures)} batch(es) failed after retries: {failures}. "
                         "Re-run to fetch them; finished files are skipped.")
    print(f"done: {len(rows)} data files listed in {manifest_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
