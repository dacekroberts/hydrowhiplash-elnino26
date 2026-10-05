"""Tests for scripts/merge_append_only.py: DECISIONS.md and plan-deviation merges."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("merge_append_only",
                                              ROOT / "scripts" / "merge_append_only.py")
mao = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mao        # dataclasses look the module up while loading
spec.loader.exec_module(mao)

DEC = mao.LAYOUTS["DECISIONS.md"]
DEV = mao.LAYOUTS["docs/plan_deviations.md"]

PRE = "# Decisions\n\nNewest first.\n\n## Changes\n\n"
OLD = "### 2026-10-03 - Old topic\n\n- **Decided old.** Text\n  continued.\n"


def when_from(times):
    """Stub dater: commit time looked up by a node's first line."""
    return lambda node: times[node.key.split("\n", 1)[0]]


def section(date, topic, *bullets):
    return f"### {date} - {topic}\n\n" + "\n\n".join(f"- **{b}**" for b in bullets) + "\n\n"


@pytest.mark.parametrize("name", list(mao.LAYOUTS))
def test_repo_files_round_trip(name):
    # The live files must parse and render back byte for byte, or every merge refuses.
    text = (ROOT / name).read_text(encoding="utf-8")
    assert mao.render(mao.parse(text, mao.LAYOUTS[name])) == text


def test_new_topics_on_both_sides_are_kept_newest_first():
    base = PRE + OLD
    ours = PRE + section("2026-10-04", "Mechanism diagram", "Decided A.") + OLD
    theirs = PRE + section("2026-10-04", "Site render check", "Decided B.") + OLD
    times = {"### 2026-10-04 - Mechanism diagram": 100, "### 2026-10-04 - Site render check": 200}
    out = mao.merge_texts(base, ours, theirs, DEC, when_from(times))
    assert out == (PRE + section("2026-10-04", "Site render check", "Decided B.")
                   + section("2026-10-04", "Mechanism diagram", "Decided A.") + OLD)


def test_later_date_goes_above_regardless_of_commit_time():
    base = PRE + OLD
    ours = PRE + section("2026-10-05", "Newer day", "Decided A.") + OLD
    theirs = PRE + section("2026-10-04", "Older day", "Decided B.") + OLD
    times = {"### 2026-10-05 - Newer day": 1, "### 2026-10-04 - Older day": 999}
    out = mao.merge_texts(base, ours, theirs, DEC, when_from(times))
    assert out.index("Newer day") < out.index("Older day")


def test_bullets_added_to_one_topic_on_both_sides_merge():
    # The bullet is the unit in DECISIONS.md: appended bullets from both sides stay,
    # oldest first at the end of the topic, and a bullet added at the top stays on top.
    base = PRE + OLD
    ours = PRE + OLD.rstrip("\n") + "\n\n- **Decided ours.**\n"
    theirs = PRE + ("### 2026-10-03 - Old topic\n\n- **Decided on top.**\n\n"
                    "- **Decided old.** Text\n  continued.\n\n- **Decided theirs.**\n")
    times = {"- **Decided ours.**": 300, "- **Decided theirs.**": 100, "- **Decided on top.**": 50}
    out = mao.merge_texts(base, ours, theirs, DEC, when_from(times))
    assert out == PRE + ("### 2026-10-03 - Old topic\n\n- **Decided on top.**\n\n"
                         "- **Decided old.** Text\n  continued.\n\n- **Decided theirs.**\n\n"
                         "- **Decided ours.**\n")


def test_tight_list_stays_tight_when_appended():
    # Some DECISIONS.md topics list bullets without blank lines between them.
    tight = "### 2026-10-03 - Old topic\n\n- **Decided one.**\n- **Decided two.**\n"
    base = PRE + tight
    ours = PRE + tight + "- **Decided three.**\n"
    theirs = PRE + section("2026-10-04", "B", "Decided B.") + tight
    times = {"- **Decided three.**": 1, "### 2026-10-04 - B": 2}
    out = mao.merge_texts(base, ours, theirs, DEC, when_from(times))
    assert out == PRE + section("2026-10-04", "B", "Decided B.") + tight + "- **Decided three.**\n"


def test_entry_added_away_from_the_conflict_is_kept():
    # A conflict region doesn't show everything a side added: theirs also adds a
    # bullet far below the top. Rebuilding from the full versions keeps it.
    lower = section("2026-10-01", "Scaffold", "Decided scaffold.")
    base = PRE + OLD + "\n" + lower
    ours = PRE + section("2026-10-04", "A", "Decided A.") + OLD + "\n" + lower
    theirs = (PRE + section("2026-10-04", "B", "Decided B.") + OLD + "\n"
              + lower + "- **Decided late addition.**\n")
    base, ours, theirs = (t.rstrip("\n") + "\n" for t in (base, ours, theirs))
    times = {"### 2026-10-04 - A": 1, "### 2026-10-04 - B": 2, "- **Decided late addition.**": 3}
    out = mao.merge_texts(base, ours, theirs, DEC, when_from(times))
    assert "Decided late addition." in out and "Decided A." in out and "Decided B." in out


def test_edited_old_entry_is_refused():
    base = PRE + OLD
    ours = PRE + OLD.replace("Decided old.", "Decided old, reworded.")
    theirs = PRE + section("2026-10-04", "B", "Decided B.") + OLD
    with pytest.raises(mao.Refusal, match="removed or edited"):
        mao.merge_texts(base, ours, theirs, DEC, when_from({"### 2026-10-04 - B": 1}))


DEV_PRE = "# Plan deviations\n\nNewest first.\n\n## 2026-10-04 (Session 0)\n\n"
D16 = "### D16 · Parallel worktree session\n- **Plan:** one session.\n- **Actual:** two.\n"


def dev(number, title):
    return f"### D{number} · {title}\n- **Plan:** p.\n- **Actual:** a.\n\n"


def test_deviations_sorted_by_number():
    base = DEV_PRE + D16
    ours = DEV_PRE + dev(18, "Embed") + dev(17, "Diagram") + D16
    theirs = DEV_PRE + dev(19, "Render check") + D16
    out = mao.merge_texts(base, ours, theirs, DEV, lambda node: 0)
    assert out == DEV_PRE + dev(19, "Render check") + dev(18, "Embed") + dev(17, "Diagram") + D16


def test_same_deviation_number_twice_is_refused():
    base = DEV_PRE + D16
    ours = DEV_PRE + dev(17, "Diagram") + D16
    theirs = DEV_PRE + dev(17, "Render check") + D16
    with pytest.raises(mao.Refusal, match="D17 is used by two entries"):
        mao.merge_texts(base, ours, theirs, DEV, lambda node: 0)


def test_edited_deviation_is_refused():
    base = DEV_PRE + D16
    ours = DEV_PRE + D16.replace("two.", "two sessions.")
    theirs = DEV_PRE + dev(17, "Diagram") + D16
    with pytest.raises(mao.Refusal, match="existing entry edited"):
        mao.merge_texts(base, ours, theirs, DEV, lambda node: 0)


def test_unrecognised_layout_is_refused():
    base = PRE + OLD
    with pytest.raises(mao.Refusal, match="layout not recognised"):
        mao.merge_texts(base, base, base + "\n", DEC, lambda node: 0)


def _git(repo, *args, when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True)


def test_end_to_end_conflicted_merge(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "core.autocrlf", "false")
    f = repo / "DECISIONS.md"
    f.write_text(PRE + OLD, encoding="utf-8", newline="\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "base", when="2026-10-04T10:00:00")
    _git(repo, "switch", "-qc", "pr")
    f.write_text(PRE + section("2026-10-04", "From PR", "Decided PR.") + OLD,
                 encoding="utf-8", newline="\n")
    _git(repo, "commit", "-qam", "pr", when="2026-10-04T11:00:00")
    _git(repo, "switch", "-q", "main")
    f.write_text(PRE + section("2026-10-04", "From main", "Decided main.") + OLD,
                 encoding="utf-8", newline="\n")
    _git(repo, "commit", "-qam", "main", when="2026-10-04T12:00:00")
    _git(repo, "switch", "-q", "pr")
    assert _git(repo, "merge", "main").returncode != 0      # a real conflict

    assert mao.main([], cwd=repo) == 0
    out = f.read_text(encoding="utf-8")
    assert "<<<<<<<" not in out
    # main's entry was committed later, so it goes on top.
    assert out == (PRE + section("2026-10-04", "From main", "Decided main.")
                   + section("2026-10-04", "From PR", "Decided PR.") + OLD)
    assert "Next: review" in capsys.readouterr().out
