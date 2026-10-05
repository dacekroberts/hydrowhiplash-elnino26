"""Tests for scripts/prescreen_prs.py on throwaway git repos, with checks stubbed."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prescreen_prs", ROOT / "scripts" / "prescreen_prs.py")
pre = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pre        # dataclasses look the module up while loading
spec.loader.exec_module(pre)

PRE = "# Decisions\n\nNewest first.\n\n## Changes\n\n"
OLD = "### 2026-10-03 - Old topic\n\n- **Decided old.**\n"
DEV_PRE = "# Plan deviations\n\nNewest first.\n\n## 2026-10-04 (Session 0)\n\n"
D16 = "### D16 · Old entry\n- **Plan:** p.\n"


def topic(name):
    return f"### 2026-10-04 - {name}\n\n- **Decided {name}.**\n\n"


def dev(number, title):
    return f"### D{number} · {title}\n- **Plan:** p.\n\n"


def _git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    out = subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout


def _write(repo, path, text):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "core.autocrlf", "false")
    _write(r, "DECISIONS.md", PRE + OLD)
    _write(r, "docs/plan_deviations.md", DEV_PRE + D16)
    _write(r, "README.md", "line\n")
    _git(r, "add", ".")
    _git(r, "commit", "-qm", "base")
    return r


def branch(repo, name, files):
    """A PR branch off the base commit with the given file contents."""
    _git(repo, "switch", "-q", "-c", name, "main")
    for path, text in files.items():
        _write(repo, path, text)
    _git(repo, "commit", "-qam", name)
    _git(repo, "switch", "-q", "main")
    return pre.Item(f"#{name}", name, list(files))


def passing(work, files):
    return pre.Checks(True, [], "pytest: 1 passed")


def worktrees(repo):
    return [l for l in _git(repo, "worktree", "list").splitlines() if l.strip()]


def test_two_prs_adding_log_entries_both_clean(repo):
    a = branch(repo, "a", {"DECISIONS.md": PRE + topic("A") + OLD})
    b = branch(repo, "b", {"DECISIONS.md": PRE + topic("B") + OLD})
    results, kept = pre.screen(repo, "main", [a, b], checks=passing)
    assert [r.verdict for r in results] == ["CLEAN", "CLEAN"]
    assert results[0].conflicts == [] and results[1].conflicts == ["DECISIONS.md"]
    assert results[1].resolution == "resolved by merge_append_only.py"
    assert kept is None and len(worktrees(repo)) == 1       # cleaned up


def test_duplicate_deviation_number_between_prs_stops_the_queue(repo):
    a = branch(repo, "a", {"docs/plan_deviations.md": DEV_PRE + dev(17, "Diagram") + D16})
    b = branch(repo, "b", {"docs/plan_deviations.md": DEV_PRE + dev(17, "Render check") + D16})
    c = branch(repo, "c", {"README.md": "line\nmore\n"})
    results, _ = pre.screen(repo, "main", [a, b, c], checks=passing)
    assert [r.verdict for r in results] == ["CLEAN", "UNEXPECTED"]   # c never screened
    assert "D17 is used by two entries" in results[1].unexpected


LONG = (DEV_PRE + "### D16 · Old entry\n- **Plan:** p.\n- **Actual:** a.\n- **Why:** w.\n\n"
        "### D15 · Older entry\n- **Plan:** p.\n")


def test_duplicate_number_in_a_clean_merge_is_caught(repo):
    # The 2026-10-04 replay: git merges the deviations file cleanly (the two D17s
    # sit at different lines), so only the always-on log check can catch it.
    _write(repo, "docs/plan_deviations.md", LONG)
    _git(repo, "commit", "-qam", "longer log")
    top = LONG.replace("### D16", dev(17, "Diagram") + "### D16", 1)
    lower = LONG.replace("### D15", dev(17, "Render check") + "### D15", 1)
    a = branch(repo, "a", {"docs/plan_deviations.md": top})
    b = branch(repo, "b", {"docs/plan_deviations.md": lower})
    results, _ = pre.screen(repo, "main", [a, b], checks=passing)
    assert results[1].conflicts == []                       # git saw no conflict
    assert "D17 is used by two entries" in results[1].unexpected


def test_conflict_outside_the_logs_is_unexpected(repo):
    a = branch(repo, "a", {"README.md": "changed by a\n"})
    b = branch(repo, "b", {"README.md": "changed by b\n"})
    results, _ = pre.screen(repo, "main", [a, b], checks=passing)
    assert results[1].verdict == "UNEXPECTED"
    assert "outside the append-only logs: README.md" in results[1].unexpected


def test_known_fixup_is_applied_and_rechecked(repo):
    a = branch(repo, "a", {"README.md": "line\nmore\n"})
    calls, fixed = [], []

    def checks(work, files):
        calls.append(1)
        if len(calls) == 1:
            return pre.Checks(False, ["test_committed_svgs_match_the_code"], "pytest: 1 failed")
        return pre.Checks(True, [], "pytest: 1 passed")

    results, _ = pre.screen(repo, "main", [a], checks=checks,
                            fixup=lambda work, fix: fixed.append(fix.note))
    assert results[0].verdict == "CLEAN after fix-up"
    assert fixed == [pre.FIXUPS["test_committed_svgs_match_the_code"].note]
    assert len(calls) == 2


def test_unknown_failure_gets_no_fixup(repo):
    a = branch(repo, "a", {"README.md": "line\nmore\n"})
    fixed = []
    results, _ = pre.screen(
        repo, "main", [a],
        checks=lambda w, f: pre.Checks(False, ["test_something_else"], "pytest: 1 failed"),
        fixup=lambda work, fix: fixed.append(fix))
    assert results[0].verdict == "UNEXPECTED" and fixed == []
    assert "no known fix-up for test_something_else" in results[0].unexpected


def test_keep_leaves_the_worktree_after_a_stop(repo):
    a = branch(repo, "a", {"README.md": "changed by a\n"})
    b = branch(repo, "b", {"README.md": "changed by b\n"})
    results, kept = pre.screen(repo, "main", [a, b], checks=passing, keep=True)
    assert kept is not None and kept.exists() and len(worktrees(repo)) == 2
    _git(repo, "worktree", "remove", "--force", str(kept))


def test_report_wording():
    ok = [pre.Result("#6 side/x", "abc1234", resolution="clean merge", checks="pytest: 1 passed")]
    text = pre.report(ok, "origin/main", "0123456789", 1, None)
    assert "**ALL CLEAN.** Merge in this order: #6." in text and "0123456" in text
    bad = ok + [pre.Result("#7 side/y", "def5678", unexpected="boom")]
    text = pre.report(bad, "origin/main", "0123456789", 3, None)
    assert "**STOP at #7 side/y:** boom" in text and "1 later PR(s) not screened" in text


def test_failed_tests_parsed_from_pytest_summary():
    out = ("..F\nFAILED tests/test_diagrams.py::test_committed_svgs_match_the_code - Assert\n"
           "FAILED tests/test_x.py::test_y - boom\n1 failed, 2 passed in 1.0s\n")
    assert pre.failed_tests(out) == ["test_committed_svgs_match_the_code", "test_y"]
    assert pre.pytest_summary(out) == "1 failed, 2 passed in 1.0s"
