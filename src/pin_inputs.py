"""Checksums of every input the registered tests read (trap 7, session 7
kickoff): RONI is revised monthly and WFIGS is a live layer, so the tests
run on the pinned input tables and downloads (fire 2026-10-07, NBAC
2026-10-08), and nothing is re-downloaded until the results are in.

  pin()     sha256, size and modification time of each pinned file, written
            to INPUT_PINS_TABLE (results/tables/input_pins.csv)
  verify()  recompute and compare; raises listing every file that changed,
            vanished or was added to a pinned folder
  assert_pinned(path)  raises unless the path is a pinned input; the
            hypothesis loaders call it on every table they open, so an input
            table added to results/tables/ without a pin fails loudly (audit
            2026-10-08 round 4 L6: pinning by name dropped the folder trap)

Pinned: the committed input tables named in PINNED_RESULT_TABLES (by name,
not the results/tables/ folder, so tables the hypothesis runs write there
are neither refused nor pinned as inputs; audit 2026-10-08 round 3 M1), the
ENSO index downloads and their processed copies, every file in the fire
download folders (MTBS, WFIGS, CNFDB, and NBAC for the Parks Canada
sensitivity run, D69) and FIRE_EVENTS_TABLE. Re-pin only when a pinned file changes on
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
                        INPUT_PINS_TABLE, NBAC_RAW, PINNED_RESULT_TABLES, RESULTS, ROOT)

FIXED = [DATA_RAW / "roni.ascii.txt", DATA_RAW / "oni.ascii.txt",
         DATA_PROCESSED / "el_nino_winters.csv", DATA_PROCESSED / "enso_index.csv",
         FIRE_EVENTS_TABLE] + [RESULTS / "tables" / name for name in PINNED_RESULT_TABLES]
FOLDERS = [FIRE_RAW / "mtbs", FIRE_RAW / "wfigs", FIRE_RAW / "cnfdb", NBAC_RAW]


def pinned_files() -> list[Path]:
    files = list(FIXED)
    for folder in FOLDERS:
        files += [p for p in sorted(folder.iterdir()) if p.is_file()]
    return files


def assert_pinned(path: Path) -> Path:
    """Return `path` if it is one of pinned_files(), else raise."""
    path = Path(path).resolve()
    if path not in {p.resolve() for p in pinned_files()}:
        raise ValueError(f"Not a pinned input: {path}. Add it to PINNED_RESULT_TABLES "
                         "(or pin_inputs.FIXED), re-pin, and log why.")
    return path


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
