"""Checksums of every input the registered tests read (trap 7, session 7
kickoff): RONI is revised monthly and WFIGS is a live layer, so the tests
run on the committed tables and the downloads of 2026-10-07, and nothing
is re-downloaded until the results are in.

  pin()     sha256, size and modification time of each pinned file, written
            to INPUT_PINS_TABLE (results/tables/input_pins.csv)
  verify()  recompute and compare; raises listing every file that changed,
            vanished or was added to a pinned folder

Pinned: every committed table in results/tables/ (except the pin table
itself), the ENSO index downloads and their processed copies, the fire
downloads and FIRE_EVENTS_TABLE. Re-pin only when a pinned file changes on
purpose (a rebuild after an audit fix), and say so in the log.

Run:  python -m src.pin_inputs            (write the pins)
      python -m src.pin_inputs --verify   (check them)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import (DATA_PROCESSED, DATA_RAW, FIRE_EVENTS_TABLE, FIRE_RAW,
                        INPUT_PINS_TABLE, RESULTS, ROOT)

FIXED = [DATA_RAW / "roni.ascii.txt", DATA_RAW / "oni.ascii.txt",
         DATA_PROCESSED / "el_nino_winters.csv", DATA_PROCESSED / "enso_index.csv",
         FIRE_EVENTS_TABLE]
FOLDERS = [RESULTS / "tables", FIRE_RAW / "mtbs", FIRE_RAW / "wfigs", FIRE_RAW / "cnfdb"]


def pinned_files() -> list[Path]:
    files = list(FIXED)
    for folder in FOLDERS:
        files += [p for p in sorted(folder.iterdir()) if p.is_file() and p != INPUT_PINS_TABLE]
    return files


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def describe(path: Path) -> dict:
    stat = path.stat()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": stat.st_size,
            "sha256": sha256(path),
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ")}


def pin(path: Path = INPUT_PINS_TABLE) -> pd.DataFrame:
    table = pd.DataFrame([describe(p) for p in pinned_files()])
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False, lineterminator="\n")
    return table


def verify(path: Path = INPUT_PINS_TABLE) -> None:
    pins = pd.read_csv(path).set_index("path")
    now = {d["path"]: d for d in (describe(p) for p in pinned_files() if p.exists())}
    problems = [f"missing: {p}" for p in pins.index if p not in now]
    problems += [f"not pinned: {p}" for p in now if p not in pins.index]
    problems += [f"changed: {p}" for p in pins.index
                 if p in now and now[p]["sha256"] != pins.at[p, "sha256"]]
    if problems:
        raise ValueError("Inputs differ from the pins:\n  " + "\n  ".join(problems))


def main() -> None:
    import sys

    if "--verify" in sys.argv[1:]:
        verify()
        print(f"all inputs match {INPUT_PINS_TABLE}")
    else:
        table = pin()
        print(f"wrote {INPUT_PINS_TABLE}: {len(table)} files, "
              f"{table['bytes'].sum() / 1e9:.2f} GB hashed")


if __name__ == "__main__":
    main()
