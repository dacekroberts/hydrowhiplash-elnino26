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
  load_input(name)  the hypothesis runner's only way to open a table: the
            committed copy in results/tables/, refused unless it is pinned
            and its sha256 equals the pin (audit round 5 S3; the config
            *_TABLE constants name the unpinned data/processed/ copies)
  guard_write(paths, rebuild)  the table builders and downloaders call it
            before any work: raises if a target is an existing pinned input
            and --rebuild was not passed (audit round 5 S2; after the gate a
            rebuild is a deliberate act, D62)
  repin(reason)  pin() plus a row in INPUT_PINS_LOG (when, commit, reason,
            files changed); the command line offers no re-pin without a
            reason

Pinned: the committed input tables named in PINNED_RESULT_TABLES (by name,
not the results/tables/ folder, so tables the hypothesis runs write there
are neither refused nor pinned as inputs; audit 2026-10-08 round 3 M1), the
ENSO index downloads and their processed copies, every file in the fire
download folders (MTBS, WFIGS, CNFDB, and NBAC for the Parks Canada
sensitivity run, D69) and FIRE_EVENTS_TABLE. Re-pin only when a pinned file changes on
purpose (a rebuild after an audit fix), and say so in the log.

Run:  python -m src.pin_inputs --verify            (check the pins)
      python -m src.pin_inputs --repin "<reason>"  (rewrite them, logged)
"""
from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import (DATA_PROCESSED, DATA_RAW, FIRE_EVENTS_TABLE, FIRE_RAW,
                        INPUT_PINS_LOG, INPUT_PINS_TABLE, NBAC_RAW, PINNED_RESULT_TABLES,
                        RESULTS, ROOT)

FIXED = [DATA_RAW / "roni.ascii.txt", DATA_RAW / "oni.ascii.txt",
         DATA_PROCESSED / "el_nino_winters.csv", DATA_PROCESSED / "enso_index.csv",
         FIRE_EVENTS_TABLE] + [RESULTS / "tables" / name for name in PINNED_RESULT_TABLES]
FOLDERS = [FIRE_RAW / "mtbs", FIRE_RAW / "wfigs", FIRE_RAW / "cnfdb", NBAC_RAW]


def pinned_files() -> list[Path]:
    """Every pinned path. A download folder absent from the checkout (a
    worktree or cloud thread holds no data/) adds nothing here; verify()
    then reports its pinned files as missing."""
    files = list(FIXED)
    for folder in FOLDERS:
        if folder.is_dir():
            files += [p for p in sorted(folder.iterdir()) if p.is_file()]
    return files


class PinnedInputError(RuntimeError):
    """A write would replace a pinned input, or a pinned input differs
    from its pin."""


def guard_write(paths, rebuild: bool = False) -> None:
    """Raise PinnedInputError if any of `paths` is an existing pinned input
    and `rebuild` is False. Called first by every builder and downloader
    whose output is pinned, so a refusal costs no compute."""
    pinned = {p.resolve() for p in pinned_files()}
    hit = [Path(p) for p in paths if Path(p).resolve() in pinned and Path(p).exists()]
    if hit and not rebuild:
        raise PinnedInputError(
            "Refusing to overwrite pinned input(s): " + ", ".join(p.name for p in hit)
            + ". After the pre-results gate a rebuild is a deliberate act (D62, D73): "
            "pass --rebuild, then re-pin with python -m src.pin_inputs --repin <reason> "
            "and follow docs/post_results_protocol.md.")


def guard_folder(folder: Path, rebuild: bool = False) -> None:
    """guard_write for every file already in a download folder."""
    guard_write([p for p in folder.iterdir() if p.is_file()] if folder.is_dir() else [], rebuild)


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


def differences(path: Path = INPUT_PINS_TABLE, only=None) -> list[str]:
    """"missing: p", "not pinned: p" and "changed: p" for every pinned file
    that differs from the pins table. `only` limits the check to those
    paths (a builder reporting on the files it has just written)."""
    pins = pd.read_csv(path).set_index("path")
    files = pinned_files()
    if only is not None:
        keep = {Path(p).resolve() for p in only}
        files = [p for p in files if p.resolve() in keep]
        pins = pins.loc[[p for p in pins.index if (ROOT / p).resolve() in keep]]
    now = {d["path"]: d for d in (describe(p) for p in files if p.exists())}
    problems = [f"missing: {p}" for p in pins.index if p not in now]
    problems += [f"not pinned: {p}" for p in now if p not in pins.index]
    problems += [f"changed: {p}" for p in pins.index
                 if p in now and now[p]["sha256"] != pins.at[p, "sha256"]]
    return problems


def verify(path: Path = INPUT_PINS_TABLE) -> None:
    problems = differences(path)
    if problems:
        raise ValueError("Inputs differ from the pins:\n  " + "\n  ".join(problems))


def report_rebuild(paths) -> None:
    """Printed by a builder after a --rebuild write: which of the files it
    wrote now differ from their pins."""
    changed = differences(only=paths)
    if changed:
        print("pinned inputs now differing from input_pins.csv:\n  " + "\n  ".join(changed)
              + "\nre-pin with: python -m src.pin_inputs --repin <reason>")
    else:
        print("rebuilt files are byte-identical to their pins; no re-pin needed")


def head_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def repin(reason: str, path: Path = INPUT_PINS_TABLE, log: Path = INPUT_PINS_LOG,
          commit: str | None = None) -> pd.DataFrame:
    """Rewrite the pins and append one row to the re-pin log: UTC time, the
    HEAD commit the re-pin was made on, the reason, and the differences
    from the old pins. An empty reason is refused."""
    if not reason or not reason.strip():
        raise ValueError("A re-pin needs a reason (--repin <reason>).")
    changes = differences(path) if path.exists() else ["first pin"]
    table = pin(path)
    row = pd.DataFrame([{"repinned_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "commit": commit or head_commit(), "reason": reason.strip(),
                         "n_changes": len(changes), "changes": "; ".join(changes)}])
    row.to_csv(log, mode="a", header=not log.exists(), index=False, lineterminator="\n")
    return table


def load_input(name: str, usecols=None, path: Path = INPUT_PINS_TABLE) -> pd.DataFrame:
    """Read the committed input table `name` from results/tables/. Raises
    unless it is pinned and its sha256 equals its pin, so a test never runs
    on an unpinned or altered table."""
    target = assert_pinned(RESULTS / "tables" / name)
    if target.parent != (RESULTS / "tables").resolve():
        raise PinnedInputError(f"{name} is not a table in results/tables/.")
    key = target.relative_to(ROOT.resolve()).as_posix()
    pins = pd.read_csv(path).set_index("path")
    if key not in pins.index:
        raise PinnedInputError(f"{key} has no row in {path.name}.")
    if sha256(target) != pins.at[key, "sha256"]:
        raise PinnedInputError(f"{key} differs from its pin in {path.name}.")
    return pd.read_csv(target, usecols=usecols)


def main() -> None:
    import sys

    args = sys.argv[1:]
    if "--verify" in args:
        verify()
        print(f"all inputs match {INPUT_PINS_TABLE}")
    elif "--repin" in args and len(args) > args.index("--repin") + 1:
        table = repin(args[args.index("--repin") + 1])
        print(f"wrote {INPUT_PINS_TABLE}: {len(table)} files, "
              f"{table['bytes'].sum() / 1e9:.2f} GB hashed; reason logged in {INPUT_PINS_LOG}")
    else:
        raise SystemExit("usage: python -m src.pin_inputs --verify | --repin <reason>")


if __name__ == "__main__":
    main()
