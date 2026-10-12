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
  paths(stamp)                 Base() or Rebuild(stamp): where a builder
                               reads raw files and writes its outputs
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from src import pin_inputs
from src.config import DATA_PROCESSED, DATA_RAW, LATER_RAW, RESULTS, TRACKER_TABLES

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


ERA5_YEAR_FILE = re.compile(r"era5_land_(\d{4})(_partial)?\.nc$")
REBUILD_RECORD = "rebuild.json"
CHANGES_NAME = "changed_cells.csv"
TABLE_KEYS = ["region", "year"]


def latest(folder: Path, stamp: str, base: Path | None = None) -> Path | None:
    """The closed retrieval of `folder` with the latest stamp not after
    `stamp`, or None if there is none. Open (unrecorded) folders are not
    read: an interrupted download is not an input."""
    stamp = check_stamp(stamp)
    if not LATER_RAW.is_dir():
        return None
    found = None
    for candidate in sorted(p.name for p in LATER_RAW.iterdir() if p.is_dir()):
        if candidate <= stamp and (mirror(folder, candidate, base) / RECORD_NAME).exists():
            found = mirror(folder, candidate, base)
    return found


class Base:
    """The paths a builder uses without a stamp: data/raw, data/processed
    and results/tables, exactly as before D73."""
    stamp = None

    def era5_paths(self, directory: Path, base: Path | None = None) -> list[Path] | None:
        return None  # open_era5 globs the directory itself

    def raw_file(self, directory: Path, name: str, base: Path | None = None) -> Path:
        return Path(directory) / name

    def processed(self, path: Path) -> Path:
        return Path(path)

    def table(self, path: Path) -> Path:
        return Path(path)

    def winters(self) -> pd.DataFrame:
        return pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv")

    def close(self, builder: str) -> None:
        return None


class Rebuild(Base):
    """The paths of a rebuild under a stamp (D88). Raw files: the files on
    disk, with the latest closed retrieval not after the stamp laid over
    them. Intermediate files: data/processed/later/<stamp>/. Tables:
    results/tables/tracker/<stamp>/. Nothing pinned is written. close()
    records what was read and lists every cell that differs from the
    pinned table of the same name."""

    def __init__(self, stamp: str):
        self.stamp = check_stamp(stamp)
        self.read: dict[str, str] = {}
        self.written: dict[str, Path] = {}

    def _source(self, directory: Path, base: Path | None) -> Path | None:
        found = latest(directory, self.stamp, base)
        if found is not None:
            self.read[found.relative_to(LATER_RAW).as_posix()] = \
                pin_inputs.sha256(found / RECORD_NAME)
        return found

    def era5_paths(self, directory: Path, base: Path | None = None) -> list[Path] | None:
        """Yearly files of `directory`, a stamped file replacing the file on
        disk for the same year (a fuller partial year, or the full year)."""
        found = self._source(directory, base)
        if found is None:
            return None
        by_year: dict[str, Path] = {}
        for folder in (Path(directory), found):
            for path in sorted(folder.glob("era5_land_*.nc")):
                match = ERA5_YEAR_FILE.search(path.name)
                if match:
                    by_year[match.group(1)] = path
        return [by_year[year] for year in sorted(by_year)]

    def raw_file(self, directory: Path, name: str, base: Path | None = None) -> Path:
        found = self._source(directory, base)
        if found is not None and (found / name).exists():
            return found / name
        return Path(directory) / name

    def processed(self, path: Path) -> Path:
        out = DATA_PROCESSED / "later" / self.stamp / Path(path).name
        out.parent.mkdir(parents=True, exist_ok=True)
        return out

    def table(self, path: Path) -> Path:
        out = tables_dir(self.stamp) / Path(path).name
        if out.resolve() in {p.resolve() for p in pin_inputs.pinned_files()}:
            raise StampedFolderError(f"{out} is a pinned input.")
        out.parent.mkdir(parents=True, exist_ok=True)
        self.written[Path(path).name] = out
        return out

    def winters(self) -> pd.DataFrame:
        """Winters from the latest stamped index retrieval, if there is one;
        otherwise the pinned table. CPC revises recent values, so a stamped
        retrieval can differ from the pinned winters; close() lists every
        cell that does."""
        from src import download_oni
        from src.config import ENSO_INDEX

        base = DATA_RAW / "enso"
        raw = self.raw_file(base, f"{ENSO_INDEX.lower()}.ascii.txt")
        if raw.parent == base:  # no stamped retrieval
            return super().winters()
        return download_oni.classify_winters(download_oni.parse(raw), ENSO_INDEX)

    def close(self, builder: str) -> None:
        """Add this builder to rebuild.json and rewrite changed_cells.csv
        for every table written so far that has a pinned counterpart."""
        folder = tables_dir(self.stamp)
        folder.mkdir(parents=True, exist_ok=True)
        record_path = folder / REBUILD_RECORD
        content = (json.loads(record_path.read_text("utf-8")) if record_path.exists()
                   else {"stamp": self.stamp, "builders": {}})
        content["builders"][builder] = {
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commit": pin_inputs.head_commit(),
            "retrievals_read": dict(sorted(self.read.items())),
            "tables": sorted(self.written),
        }
        record_path.write_bytes((json.dumps(content, indent=2) + "\n").encode("utf-8"))
        parts = []
        for path in sorted(folder.glob("*.csv")):
            pinned = RESULTS / "tables" / path.name
            if path.name == CHANGES_NAME or not pinned.exists():
                continue
            diff = compare_tables(pd.read_csv(pinned), pd.read_csv(path), TABLE_KEYS)
            diff.insert(0, "table", path.name)
            parts.append(diff)
            print(f"{path.name}: {len(diff)} cell(s) differ from the pinned table "
                  f"({int((diff['change'] == 'changed').sum())} changed, "
                  f"{int((diff['change'] == 'added').sum())} added)")
        if parts:
            pd.concat(parts).to_csv(folder / CHANGES_NAME, index=False, lineterminator="\n")


def paths(stamp: str | None) -> Base:
    """Rebuild(stamp) for a stamped rebuild, Base() for the usual paths."""
    return Rebuild(stamp) if stamp else Base()
