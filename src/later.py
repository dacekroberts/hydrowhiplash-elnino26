"""Stamped paths for everything fetched or rebuilt after the registered runs.

D73 (audit round 5 S1): every later download writes to a release- or
retrieval-stamped path, never over a pinned input. Owner, 2026-10-12
(DECISIONS.md "Stamped paths: one parallel tree"): downloads go to
data/raw/later/<stamp>/<the source's usual folder>, rebuilt tables to
results/tables/tracker/<stamp>/, and the pinned files are never touched, so
python -m src.pin_inputs --verify keeps passing.

A stamp is the retrieval date (ISO, local day). Every download script takes
--stamp (today) or --stamp YYYY-MM-DD. A stamped folder is closed by
record(), which writes retrieval.json with the size and sha256 of each file;
a closed folder is never written again, so a retrieval is a fixed record. An
interrupted download leaves no retrieval.json and can be re-run under the
same stamp.

  take_stamp(args)             pop --stamp from an argument list
  mirror(folder, stamp)        the stamped twin of a download folder
  open_folder(folder, stamp)   mirror + refuse a closed or pinned folder
  record(folder, stamp, ...)   close a stamped folder
  tables_dir(stamp)            where a rebuild writes its tables
  compare_tables(old, new, keys)  the cells a rebuild changed or added
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from src import pin_inputs
from src.config import DATA_RAW, LATER_RAW, TRACKER_TABLES

FLAG = "--stamp"
RECORD_NAME = "retrieval.json"


class StampedFolderError(RuntimeError):
    """A write would change a closed retrieval or land on a pinned input."""


def check_stamp(stamp: str) -> str:
    try:
        return date.fromisoformat(stamp).isoformat()
    except ValueError as err:
        raise SystemExit(f"{FLAG} needs a date as YYYY-MM-DD, got {stamp!r}.") from err


def take_stamp(args: list[str], today: date | None = None) -> str | None:
    """Remove --stamp (and its date, if one follows) from `args` in place.
    Returns the stamp, today's date for a bare flag, or None without it."""
    if FLAG not in args:
        return None
    i = args.index(FLAG)
    value = args[i + 1] if i + 1 < len(args) and args[i + 1][:1].isdigit() else None
    del args[i:i + (2 if value else 1)]
    return check_stamp(value) if value else (today or date.today()).isoformat()


def mirror(folder: Path, stamp: str, base: Path | None = None) -> Path:
    """The stamped twin of `folder`: its path under `base` (data/raw unless
    given), re-rooted at data/raw/later/<stamp>/. A folder outside `base`
    keeps its name only."""
    folder, base = Path(folder), Path(base or DATA_RAW)
    try:
        tail = folder.resolve().relative_to(base.resolve())
    except ValueError:
        tail = Path(folder.name)
    return LATER_RAW / check_stamp(stamp) / tail


def open_folder(folder: Path, stamp: str, base: Path | None = None) -> Path:
    """Create and return the stamped twin of `folder`. Raises if that twin
    is already closed, or if it would hold a pinned input."""
    out = mirror(folder, stamp, base)
    if (out / RECORD_NAME).exists():
        raise StampedFolderError(
            f"{out} is a closed retrieval ({RECORD_NAME} present) and is never rewritten. "
            f"Use another stamp.")
    pinned = {p.resolve().parent for p in pin_inputs.pinned_files()}
    if out.resolve() in pinned:
        raise StampedFolderError(f"{out} holds pinned inputs; a stamped download cannot go there.")
    out.mkdir(parents=True, exist_ok=True)
    return out


def record(folder: Path, stamp: str, source: str, note: str = "") -> Path:
    """Close a stamped folder: write retrieval.json listing every file in it
    with its size and sha256. Returns the record's path."""
    folder = Path(folder)
    leftovers = [p.name for p in folder.iterdir() if p.suffix == ".tmp"]
    if leftovers:
        raise StampedFolderError(f"Unfinished file(s) in {folder}: {leftovers}; re-run first.")
    files = {p.name: {"bytes": p.stat().st_size, "sha256": pin_inputs.sha256(p)}
             for p in sorted(folder.iterdir()) if p.is_file() and p.name != RECORD_NAME}
    if not files:
        raise StampedFolderError(f"Nothing was downloaded into {folder}; no record written.")
    content = {
        "stamp": check_stamp(stamp), "source": source, "note": note,
        "recorded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": files,
    }
    target = folder / RECORD_NAME
    target.write_bytes((json.dumps(content, indent=2) + "\n").encode("utf-8"))
    print(f"{target} written ({len(files)} file(s)); this retrieval is now closed")
    return target


def tables_dir(stamp: str) -> Path:
    """Folder for tables rebuilt from a stamped retrieval."""
    return TRACKER_TABLES / check_stamp(stamp)


def compare_tables(old: pd.DataFrame, new: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Every cell that differs between two versions of a table, one row per
    cell: the key columns, `column`, `old`, `new` and `change` ("changed",
    "added" for a key only in `new`, "removed" for a key only in `old`).
    Two missing values count as equal; floats are compared exactly, since
    the check on a rebuild is that earlier rows are identical."""
    columns = [c for c in old.columns if c not in keys]
    if set(columns) != {c for c in new.columns if c not in keys}:
        raise ValueError("The two tables have different columns: "
                         f"{sorted(set(old.columns) ^ set(new.columns))}")
    for name, table in (("old", old), ("new", new)):
        if table.duplicated(keys).any():
            raise ValueError(f"The {name} table repeats a key in {keys}.")
    a = old.set_index(keys)[columns]
    b = new.set_index(keys)[columns]
    rows = []
    for key in a.index.union(b.index):
        in_a, in_b = key in a.index, key in b.index
        change = "changed" if in_a and in_b else "added" if in_b else "removed"
        for column in columns:
            before = a.at[key, column] if in_a else None
            after = b.at[key, column] if in_b else None
            if change == "changed" and (before == after or (pd.isna(before) and pd.isna(after))):
                continue
            if change != "changed" and pd.isna(after if in_b else before):
                continue
            key_values = key if isinstance(key, tuple) else (key,)
            rows.append({**dict(zip(keys, key_values)), "column": column,
                         "old": before, "new": after, "change": change})
    return pd.DataFrame(rows, columns=[*keys, "column", "old", "new", "change"])
