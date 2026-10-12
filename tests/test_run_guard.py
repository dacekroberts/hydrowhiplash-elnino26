"""Tests for src/run_guard.py and the pin guards added with it (audit
2026-10-08 round 5 S2-S6): throwaway git repositories and folders, plus
checks of the real size table and builders that read no data."""
import json
import subprocess

import pandas as pd
import pytest

from src import pin_inputs, run_guard
from src.config import CORRECTION_FAMILIES, PINNED_RESULT_TABLES, ROOT, TEST_DIRECTIONS
from src.stats import family_tests

PLAN_TEXT = "# Plan\n\nH1 stays as written.\n\n## Deviations log\n\n| Date | Change |\n|---|---|\n"


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "t")
    git(tmp_path, "config", "core.autocrlf", "false")
    (tmp_path / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.encode())
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "freeze")
    git(tmp_path, "tag", "analysis-plan-frozen")
    return tmp_path


# --- S4: frozen plan text ---------------------------------------------------

def test_plan_check_passes_on_the_tagged_text_and_new_log_rows(repo):
    assert run_guard.plan_frozen_problems(repo) == []
    plan = repo / "ANALYSIS_PLAN.md"
    plan.write_bytes((PLAN_TEXT + "| 2026-10-11 | a logged change |\n").encode())
    assert run_guard.plan_frozen_problems(repo) == []


def test_plan_check_ignores_line_endings(repo):
    (repo / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.replace("\n", "\r\n").encode())
    assert run_guard.plan_frozen_problems(repo) == []


def test_plan_check_reports_an_edit_above_the_log(repo):
    (repo / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.replace("stays", "changes").encode())
    problems = run_guard.plan_frozen_problems(repo)
    assert "differs from analysis-plan-frozen" in problems[0]
    assert "+H1 changes as written." in problems


def test_plan_check_reports_a_missing_tag_or_heading(repo):
    assert "not found" in run_guard.plan_frozen_problems(repo, tag="no-such-tag")[0]
    (repo / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.replace("## Deviations log", "## Log").encode())
    assert "exactly once" in run_guard.plan_frozen_problems(repo)[0]


def test_plan_check_refuses_a_moved_tag(repo):
    # Cold check M4: edit the plan, commit, move the tag
    freeze = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                            text=True).stdout.strip()
    (repo / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.replace("stays", "changes").encode())
    git(repo, "commit", "-q", "-am", "edit")
    git(repo, "tag", "-f", "analysis-plan-frozen")
    assert run_guard.plan_frozen_problems(repo) == []  # no commit to hold it to
    problems = run_guard.plan_frozen_problems(repo, expect_commit=freeze)
    assert "not the freeze commit" in problems[0]


def test_plan_check_reports_an_edited_or_removed_log_row(repo):
    # Cold check L6: rows are added, never edited or removed
    plan = repo / "ANALYSIS_PLAN.md"
    plan.write_bytes((PLAN_TEXT + "| 2026-10-08 | row one |\n").encode())
    git(repo, "commit", "-q", "-am", "row one")
    plan.write_bytes((PLAN_TEXT + "| 2026-10-08 | row one |\n| 2026-10-11 | row two |\n").encode())
    assert run_guard.plan_frozen_problems(repo) == []
    plan.write_bytes((PLAN_TEXT + "| 2026-10-08 | row 1, reworded |\n").encode())
    assert "edited or removed" in run_guard.plan_frozen_problems(repo)[0]


def test_real_tag_is_the_freeze_commit():
    from src.config import FROZEN_PLAN_COMMIT
    tagged = subprocess.run(["git", "rev-parse", "analysis-plan-frozen^{}"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    assert tagged == FROZEN_PLAN_COMMIT


def test_real_plan_matches_its_tag():
    assert run_guard.plan_frozen_problems() == []


def test_preflight_lists_every_problem_and_passes_when_clean(repo, monkeypatch):
    monkeypatch.setattr(pin_inputs, "verify", lambda: None)
    ok = run_guard.preflight(run_tests=False, root=repo)
    assert len(ok["commit"]) == 40

    def changed():
        raise ValueError("Inputs differ from the pins:\n  changed: roni.txt")

    monkeypatch.setattr(pin_inputs, "verify", changed)
    (repo / "ANALYSIS_PLAN.md").write_bytes(PLAN_TEXT.replace("stays", "changes").encode())
    with pytest.raises(RuntimeError) as err:
        run_guard.preflight(run_tests=False, root=repo)
    msg = str(err.value)
    assert "working tree not clean" in msg
    assert "differs from analysis-plan-frozen" in msg
    assert "changed: roni.txt" in msg


def test_the_run_folder_being_written_does_not_count_as_dirty(repo, monkeypatch):
    # Cold check M3: run1/ is untracked until the run is committed
    monkeypatch.setattr(pin_inputs, "verify", lambda: None)
    (repo / "results" / "tables" / "run1").mkdir(parents=True)
    (repo / "results" / "tables" / "run1" / "h3a.csv").write_bytes(b"x\n")
    assert run_guard._dirty(repo, "run1") == ""
    assert run_guard._dirty(repo) != ""
    run_guard.preflight(run_tests=False, root=repo, run="run1")
    with pytest.raises(RuntimeError, match="working tree not clean"):
        run_guard.preflight(run_tests=False, root=repo, run="run2")


# --- S6 point 3: size labels --------------------------------------------------

def registered_robust_tests():
    tests = {pair for family in CORRECTION_FAMILIES for pair in family_tests(family)}
    return sorted(t for t in tests if t[0] not in ("H1", "H2"))


def test_every_registered_robust_test_maps_to_exactly_one_label_row():
    pairs = registered_robust_tests()
    assert len(pairs) == 7 + 7 + 10 + 9 + 3 + 3  # H3a, H3b (5 + 2 each), H5, H6, C1, C2
    for test, region in pairs:
        label = run_guard.size_label(run_guard.size_shape(test, region))
        assert 0.03 < label["size"] < 0.15 and label["reps"] >= 1000
    for part in run_guard.H4_SHAPES:
        assert run_guard.size_label(run_guard.size_shape("H4", part))["size"] > 0
    for shape in run_guard.PLAIN_OLS_SHAPES.values():
        assert 0.03 < run_guard.size_label(shape)["size"] < 0.07  # near 5% (D66)


def test_size_shape_follows_the_registered_sidedness():
    assert run_guard.size_shape("H3a", "PNW") == "H3a, NW one-sided"
    assert run_guard.size_shape("H3a", "SoCal") == "H3a, NW two-sided"
    assert run_guard.size_shape("H5_lag1", "SoCal") == "persistent predictor, NW one-sided"
    assert run_guard.size_shape("C2", "AB") == "C2 interaction, NW two-sided"
    assert run_guard.size_shape("H4") == "H4 contrast, DK"
    assert run_guard.size_shape("H2", "PNW") is None  # permutation test: no label
    with pytest.raises(ValueError, match="H4 takes one of"):
        run_guard.size_shape("H4", "PNW")
    assert TEST_DIRECTIONS["H6_swe"]["SoCal"] is None
    with pytest.raises(ValueError, match="not tested"):
        run_guard.size_shape("H6_swe", "SoCal")


def test_size_label_refuses_zero_or_two_label_rows(tmp_path):
    table = tmp_path / "sizes.csv"
    row = {"shape": "x", "label_scenario": True, "rejection_rate": 0.07, "mc_se": 0.005,
           "reps": 2000, "scenario": "s", "measured": "2026-10-08"}
    pd.DataFrame([row, row, {**row, "shape": "y", "label_scenario": False}]).to_csv(table, index=False)
    with pytest.raises(ValueError, match="2 label rows"):
        run_guard.size_label("x", table)
    with pytest.raises(ValueError, match="0 label rows"):
        run_guard.size_label("y", table)


# --- S5, S6 point 1: results and provenance ------------------------------------

def test_write_result_adds_provenance_and_never_overwrites(tmp_path, monkeypatch):
    monkeypatch.setattr(run_guard, "RESULTS", tmp_path)
    table = pd.DataFrame({"test": ["H3a"], "region": ["PNW"], "estimate": [0.1]})
    path = run_guard.write_result(table, "h3a.csv", "run1", inputs=["fire_region_year.csv"],
                                  commit="c" * 40)
    assert path == tmp_path / "tables" / "run1" / "h3a.csv"
    assert b"\r" not in path.read_bytes()
    record = json.loads((tmp_path / "tables" / "run1" / "h3a.csv.provenance.json").read_text())
    assert record["commit"] == "c" * 40 and record["seed"] == 2026
    assert record["inputs"] == ["fire_region_year.csv"]
    assert record["result_sha256"] == pin_inputs.sha256(path)
    assert len(record["input_pins_sha256"]) == len(record["test_size_sha256"]) == 64
    assert set(record["packages"]) == set(run_guard.PACKAGES) and record["run_utc"].endswith("Z")
    with pytest.raises(FileExistsError, match="never overwritten"):
        run_guard.write_result(table, "h3a.csv", "run1")
    run_guard.write_result(table, "h3a.csv", "run2")  # a rerun goes beside it


def test_write_result_leaves_nothing_behind_when_provenance_fails(tmp_path, monkeypatch):
    # Cold check M2: no table without its provenance file
    monkeypatch.setattr(run_guard, "RESULTS", tmp_path)

    def broken(**kwargs):
        raise RuntimeError("git not found")

    monkeypatch.setattr(run_guard, "provenance", broken)
    with pytest.raises(RuntimeError, match="git not found"):
        run_guard.write_result(pd.DataFrame({"x": [1]}), "h3a.csv", "run1")
    assert not (tmp_path / "tables" / "run1" / "h3a.csv").exists()


# --- S2: rebuild guard and re-pin log -------------------------------------------

@pytest.fixture
def tree(tmp_path, monkeypatch):
    tables = tmp_path / "results" / "tables"
    tables.mkdir(parents=True)
    (tables / "a.csv").write_bytes(b"x,y\n1,2\n")
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "z.zip").write_bytes(b"zip")
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(pin_inputs, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(pin_inputs, "FIXED", [tables / "a.csv"])
    monkeypatch.setattr(pin_inputs, "FOLDERS", [raw, tmp_path / "absent"])
    pins = tables / "input_pins.csv"
    monkeypatch.setattr(pin_inputs, "INPUT_PINS_TABLE", pins)
    pin_inputs.pin(pins)
    return tmp_path, pins


def test_guard_refuses_a_pinned_target_without_rebuild(tree):
    root, pins = tree
    a = root / "results" / "tables" / "a.csv"
    with pytest.raises(pin_inputs.PinnedInputError, match="a.csv"):
        pin_inputs.guard_write([root / "elsewhere.csv", a])
    pin_inputs.guard_write([a], rebuild=True)
    pin_inputs.guard_write([root / "results" / "tables" / "h3a_results.csv"])  # not pinned
    with pytest.raises(pin_inputs.PinnedInputError, match="z.zip"):
        pin_inputs.guard_folder(root / "raw")
    pin_inputs.guard_folder(root / "absent")  # nothing there yet: a first download


def test_differences_can_be_limited_to_the_files_just_written(tree):
    root, pins = tree
    a = root / "results" / "tables" / "a.csv"
    (root / "raw" / "z.zip").write_bytes(b"changed")
    assert pin_inputs.differences(pins, only=[a]) == []
    assert pin_inputs.differences(pins) == ["changed: raw/z.zip"]
    a.write_bytes(b"x,y\n1,3\n")
    assert pin_inputs.differences(pins, only=[a]) == ["changed: results/tables/a.csv"]


def test_repin_needs_a_reason_and_logs_what_changed(tree):
    root, pins = tree
    log = root / "pins_log.csv"
    with pytest.raises(ValueError, match="reason"):
        pin_inputs.repin("  ", pins, log, commit="c" * 40)
    assert not log.exists()
    (root / "results" / "tables" / "a.csv").write_bytes(b"x,y\n1,3\n")
    pin_inputs.repin("audit fix: a.csv rebuilt", pins, log, commit="c" * 40)
    pin_inputs.verify(pins)
    pin_inputs.repin("second", pins, log, commit="d" * 40)
    rows = pd.read_csv(log)
    assert list(rows["reason"]) == ["audit fix: a.csv rebuilt", "second"]
    assert rows.loc[0, "changes"] == "changed: results/tables/a.csv" and rows.loc[0, "n_changes"] == 1
    assert rows.loc[1, "n_changes"] == 0 and rows.loc[0, "commit"] == "c" * 40


def test_command_line_offers_no_repin_without_a_reason(monkeypatch):
    for argv in (["pin_inputs"], ["pin_inputs", "--repin"]):
        monkeypatch.setattr("sys.argv", argv)
        with pytest.raises(SystemExit, match="usage"):
            pin_inputs.main()


# --- S3: the pinned loader -------------------------------------------------------

def test_load_input_reads_a_pinned_table_and_refuses_the_rest(tree):
    root, pins = tree
    assert pin_inputs.load_input("a.csv", path=pins).to_dict("list") == {"x": [1], "y": [2]}
    assert list(pin_inputs.load_input("a.csv", usecols=["y"], path=pins).columns) == ["y"]
    (root / "results" / "tables" / "new.csv").write_bytes(b"x\n1\n")
    with pytest.raises(ValueError, match="Not a pinned input"):
        pin_inputs.load_input("new.csv", path=pins)
    with pytest.raises(pin_inputs.PinnedInputError, match="not a table in results/tables/"):
        pin_inputs.load_input("../../raw/z.zip", path=pins)  # pinned, but not a table (L5)
    (root / "results" / "tables" / "a.csv").write_bytes(b"x,y\n1,3\n")
    with pytest.raises(pin_inputs.PinnedInputError, match="differs from its pin"):
        pin_inputs.load_input("a.csv", path=pins)


def test_every_pinned_result_table_loads_through_load_input():
    # committed tables only, so this also runs in a checkout without data/
    for name in PINNED_RESULT_TABLES:
        table = pin_inputs.load_input(name)
        assert {"region", "year"} <= set(table.columns) and len(table) > 0


# --- S2: the real builders refuse before reading anything -------------------------

def test_real_builders_refuse_to_overwrite_their_pinned_tables(monkeypatch):
    from src import climate_vars, fire, parks_gap, phase2, snow_soil, stations

    with pytest.raises(pin_inputs.PinnedInputError):  # the writers too, as a notebook
        phase2.write_tables(pd.DataFrame())           # cell calls them (cold check M1)
    with pytest.raises(pin_inputs.PinnedInputError):
        fire.write_tables(pd.DataFrame())
    monkeypatch.setattr("sys.argv", ["builder"])
    for build in (fire.main, fire.main_frozen, parks_gap.main, climate_vars.main,
                  snow_soil.main, stations.main, phase2.main):
        with pytest.raises(pin_inputs.PinnedInputError, match="Refusing to overwrite"):
            build()
    assert (ROOT / "results" / "tables" / "fire_region_year.csv").exists()
