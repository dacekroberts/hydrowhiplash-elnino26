"""Safeguards around the hypothesis runs (audit 2026-10-08 round 5 S4-S6;
D73; docs/post_results_protocol.md). The runner calls preflight() first,
opens tables only through src.pin_inputs.load_input, takes every size label
from size_label(), and writes every result through write_result().

  plan_frozen_problems()  ANALYSIS_PLAN.md above "## Deviations log" against
            the tag analysis-plan-frozen; empty list when identical (S4)
  preflight()  clean working tree, pinned inputs verified, frozen plan text,
            the statistics tests; raises listing every problem, else returns
            the commit the run is made on (S4)
  size_shape(test, region) / size_label(shape)  the one label row of
            TEST_SIZE_TABLE for a registered robust test (S6 point 3; D66);
            plain_ols_shape(test, region) the row of its plain OLS check
  provenance() / write_result()  a result table plus a provenance file
            beside it; an existing result is never overwritten (S5, S6
            point 1)

Run:  python scripts/preflight.py            (all checks)
      python scripts/check_plan_frozen.py    (frozen text only)
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from src import pin_inputs
from src.config import (FROZEN_PLAN_COMMIT, INPUT_PINS_TABLE, RANDOM_SEED, RESULTS, ROOT,
                        TEST_DIRECTIONS, TEST_SIZE_TABLE)

PLAN = "ANALYSIS_PLAN.md"
FROZEN_TAG = "analysis-plan-frozen"
LOG_HEADING = "## Deviations log"
STATS_TESTS = ("tests/test_stats.py", "tests/test_stats_gate.py")
PACKAGES = ("statsmodels", "scipy", "numpy", "pandas", "patsy")

# Registered robust test -> the `shape` prefix of its row in TEST_SIZE_TABLE
# (scripts/stats_size_check.py). The per-region shapes end in the sidedness
# the region's test has in TEST_DIRECTIONS. H1 and H2 are permutation tests
# and carry no size label (D66 covers Newey-West, Driscoll-Kraay and the
# joint F). H5 and H6 share the persistent-predictor shape.
REGION_SHAPES = {"H3a": "H3a, NW", "H3b": "H3b, NW",
                 "H5_lag0": "persistent predictor, NW", "H5_lag1": "persistent predictor, NW",
                 "H6_swe": "persistent predictor, NW", "H6_spei": "persistent predictor, NW",
                 "C1": "C1 interaction, NW", "C2": "C2 interaction, NW"}
H4_SHAPES = {"contrast": "H4 contrast, DK", "joint_f": "H4 joint F, DK",
             "contrast_clustered": "H4 contrast, clustered",
             "joint_f_clustered": "H4 joint F, clustered"}
# Plain OLS check beside the registered p (D66), kept where its measured size
# is near 5%: H3a, H3b, C1, C2; not H4 (D68), not H5 or H6. The check has the
# sidedness of the registered test it sits beside (owner, 2026-10-11, D80):
# plain_ols_shape appends it, as size_shape does.
PLAIN_OLS_SHAPES = {"H3a": "H3a, plain OLS", "H3b": "H3b, plain OLS",
                    "C1": "C1 interaction, plain OLS", "C2": "C2 interaction, plain OLS"}


def _git(*args: str, root: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def _split_log(text: str) -> tuple[str, str] | None:
    """(text above the log heading, the log below it), or None unless the
    heading appears exactly once."""
    text = text.replace("\r\n", "\n")
    if text.count("\n" + LOG_HEADING + "\n") != 1:
        return None
    above, log = text.split("\n" + LOG_HEADING + "\n")
    return above, log


def _dirty(root: Path = ROOT, run: str | None = None) -> str:
    """`git status --porcelain`, leaving out the run folder being written
    (results/tables/<run>/): its files are untracked until the run is
    committed, and would otherwise mark every result after the first as
    dirty (cold check 2026-10-11 M3)."""
    # every untracked file listed: git otherwise shows only the top new folder
    lines = _git("status", "--porcelain", "--untracked-files=all", root=root).splitlines()
    if run:
        lines = [ln for ln in lines if not ln[3:].strip('"').startswith(f"results/tables/{run}/")]
    return "\n".join(lines)


def plan_frozen_problems(root: Path = ROOT, tag: str = FROZEN_TAG,
                         expect_commit: str | None = None) -> list[str]:
    """Problems with the working ANALYSIS_PLAN.md (line endings ignored):
    the tag pointing at another commit than `expect_commit` (for the real
    repository FROZEN_PLAN_COMMIT, since a local tag can be moved); any
    difference from the tagged text above the deviations log; a log that no
    longer starts with the log committed at HEAD (rows are added, never
    edited or removed). Empty list when all hold."""
    if expect_commit is None and Path(root).resolve() == ROOT.resolve():
        expect_commit = FROZEN_PLAN_COMMIT
    try:
        tagged = _git("rev-parse", f"{tag}^{{}}", root=root).strip()
        frozen = _split_log(_git("show", f"{tag}:{PLAN}", root=root))
    except subprocess.CalledProcessError:
        return [f"tag {tag} not found, or it holds no {PLAN}"]
    if expect_commit and tagged != expect_commit:
        return [f"tag {tag} points at {tagged}, not the freeze commit {expect_commit}"]
    now = _split_log((root / PLAN).read_bytes().decode("utf-8"))
    if frozen is None or now is None:
        return [f'{PLAN} must hold the line "{LOG_HEADING}" exactly once (tag and working copy)']
    problems = []
    if frozen[0] != now[0]:
        diff = difflib.unified_diff(frozen[0].splitlines(), now[0].splitlines(), tag,
                                    "working copy", lineterm="", n=0)
        problems += [f"{PLAN} differs from {tag} above the deviations log:"] + list(diff)[:40]
    try:
        head = _split_log(_git("show", f"HEAD:{PLAN}", root=root))
    except subprocess.CalledProcessError:
        head = None
    # Against every commit since the tag that changed the plan, as well as
    # HEAD: an edited row that was committed passes the HEAD check from then
    # on (audit 2026-10-17). Empty placeholder rows ("| | | |"), replaced by
    # the first real row, are skipped.
    try:
        commits = _git("rev-list", f"{tag}..HEAD", "--", PLAN, root=root).split()
    except subprocess.CalledProcessError:
        commits = []
    for commit in commits:
        past = _split_log(_git("show", f"{commit}:{PLAN}", root=root))
        if past is None:
            continue
        rows = "\n".join(line for line in past[1].splitlines()
                         if "|" not in line or line.replace("|", "").strip())
        if not now[1].rstrip("\n").startswith(rows.rstrip("\n")):
            problems.append(f"{PLAN}: the deviations log no longer starts with the log at "
                            f"{commit[:7]} (a row was edited or removed; rows are only added)")
            break
    if head is not None and not now[1].rstrip("\n").startswith(head[1].rstrip("\n")):
        problems.append(f"{PLAN}: the deviations log no longer starts with the log at HEAD "
                        "(a row was edited or removed; rows are only added)")
    return problems


def preflight(run_tests: bool = True, root: Path = ROOT, run: str | None = None) -> dict:
    """Every check a hypothesis run needs first. Raises RuntimeError listing
    all problems; otherwise returns {"commit", "checked_utc"}. `run` names
    the run folder being written, whose own files do not count as an unclean
    tree."""
    problems = []
    dirty = _dirty(root, run)
    if dirty:
        problems.append("working tree not clean:\n    " + dirty.replace("\n", "\n    "))
    problems += plan_frozen_problems(root)
    try:
        pin_inputs.verify()
    except (ValueError, FileNotFoundError) as err:
        problems.append(str(err))
    if run_tests:
        tests = subprocess.run([sys.executable, "-m", "pytest", "-q", *STATS_TESTS], cwd=root,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace")
        if tests.returncode != 0:
            problems.append("statistics tests failed:\n" + tests.stdout[-2000:])
    if problems:
        raise RuntimeError("Preflight failed; no hypothesis run:\n  " + "\n  ".join(problems))
    return {"commit": _git("rev-parse", "HEAD", root=root).strip(),
            "checked_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def size_shape(test: str, region: str | None = None) -> str | None:
    """`shape` of the size-table row for a registered test. Per-region
    tests take (test, region); H4 takes test "H4" with region one of
    H4_SHAPES ("contrast", "joint_f", and their year-clustered versions).
    None for the permutation tests H1 and H2. Raises where the region has no
    test (TEST_DIRECTIONS None)."""
    if test in ("H1", "H2"):
        return None
    if test == "H4":
        if (region or "contrast") not in H4_SHAPES:
            raise ValueError(f"H4 takes one of {sorted(H4_SHAPES)}, not {region!r}.")
        return H4_SHAPES[region or "contrast"]
    alternative = TEST_DIRECTIONS[test][region]
    if alternative is None:
        raise ValueError(f"{test} is not tested in {region}.")
    sided = "two-sided" if alternative == "two-sided" else "one-sided"
    return f"{REGION_SHAPES[test]} {sided}"


def plain_ols_shape(test: str, region: str) -> str | None:
    """`shape` of the size-table row for the plain OLS check beside a
    registered test, in that test's own sidedness; None where no check is
    reported (H1, H2, H4, H5, H6)."""
    if test not in PLAIN_OLS_SHAPES:
        return None
    alternative = TEST_DIRECTIONS[test][region]
    if alternative is None:
        raise ValueError(f"{test} is not tested in {region}.")
    sided = "two-sided" if alternative == "two-sided" else "one-sided"
    return f"{PLAIN_OLS_SHAPES[test]} {sided}"


def size_label(shape: str, table: Path = TEST_SIZE_TABLE) -> dict:
    """The label row of `shape`: rejection_rate (the size printed beside the
    p-value), its Monte Carlo SE, reps, scenario and date measured. Exactly
    one row with label_scenario true must exist."""
    sizes = pd.read_csv(table)
    rows = sizes[(sizes["shape"] == shape) & sizes["label_scenario"].astype(bool)]
    if len(rows) != 1:
        raise ValueError(f"{len(rows)} label rows for {shape!r} in {table.name}; need exactly 1.")
    row = rows.iloc[0]
    return {"shape": shape, "size": float(row["rejection_rate"]), "mc_se": float(row["mc_se"]),
            "reps": int(row["reps"]), "scenario": row["scenario"], "measured": row["measured"]}


def provenance(seed: int = RANDOM_SEED, inputs=(), commit: str | None = None,
               root: Path = ROOT, run: str | None = None) -> dict:
    """What made a result: commit (and whether the tree was dirty, the run
    folder `run` itself left out), sha256 of the pins table and the size
    table, UTC time, seed, package versions (statsmodels' df and correction
    defaults were version-specific traps) and the input tables read."""
    return {"commit": commit or _git("rev-parse", "HEAD", root=root).strip(),
            "dirty": bool(_dirty(root, run)),
            "input_pins_sha256": pin_inputs.sha256(INPUT_PINS_TABLE),
            "test_size_sha256": pin_inputs.sha256(TEST_SIZE_TABLE),
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "seed": seed, "python": sys.version.split()[0],
            "packages": {name: version(name) for name in PACKAGES},
            "inputs": sorted(inputs)}


def write_result(table: pd.DataFrame, name: str, run: str, inputs=(),
                 seed: int = RANDOM_SEED, commit: str | None = None) -> Path:
    """Write a result table to results/tables/<run>/<name> with
    <name>.provenance.json beside it. Refuses to overwrite: the first
    results are never edited, a rerun goes in a new run folder
    (docs/post_results_protocol.md section 1)."""
    path = RESULTS / "tables" / run / name
    side = path.with_name(path.name + ".provenance.json")
    for target in (path, side):
        if target.exists():
            raise FileExistsError(f"{target} exists. Results are never overwritten; "
                                  "write the rerun to a new run folder.")
    # the record is built before anything is written, so a failure there
    # leaves no table without its provenance file (cold check 2026-10-11 M2)
    record = provenance(seed=seed, inputs=inputs, commit=commit, run=run)
    data = table.to_csv(index=False, lineterminator="\n").encode("utf-8")
    record["result"] = name
    record["result_sha256"] = hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    # both files are written under temporary names and renamed only once both
    # are complete, so an interrupted write leaves no truncated table under a
    # result's name (DeepSeek review 2026-10-12 F1)
    contents = {side: (json.dumps(record, indent=2) + "\n").encode("utf-8"), path: data}
    for target, content in contents.items():
        target.with_name(target.name + ".tmp").write_bytes(content)
    for target in contents:
        os.replace(target.with_name(target.name + ".tmp"), target)
    return path
