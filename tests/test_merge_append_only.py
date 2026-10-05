"""Tests for scripts/merge_append_only.py: DECISIONS.md and plan-deviation merges.

"ours" is always the PR branch and "theirs" is main, as in merge-side-pr step 5.
"""
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


def section(date, topic, *bullets):
    return f"### {date} - {topic}\n\n" + "\n\n".join(f"- **{b}**" for b in bullets) + "\n\n"


def dec(*sections):
    return PRE + "".join(sections) + OLD


@pytest.mark.parametrize("name", list(mao.LAYOUTS))
def test_repo_files_round_trip(name):
    # The live files must parse and render back byte for byte, or every merge refuses.
    text = (ROOT / name).read_text(encoding="utf-8")
    assert mao.render(mao.parse(text, mao.LAYOUTS[name])) == text


def test_same_date_topics_put_the_pr_above_main():
    pr = section("2026-10-04", "Mechanism diagram", "Decided A.")
    main = section("2026-10-04", "Site render check", "Decided B.")
    out = mao.merge_texts(dec(), dec(pr), dec(main), DEC)
    assert out == dec(pr, main)


def test_later_date_goes_above_regardless_of_side():
    pr = section("2026-10-04", "Older day", "Decided A.")
    main = section("2026-10-05", "Newer day", "Decided B.")
    assert mao.merge_texts(dec(), dec(pr), dec(main), DEC) == dec(main, pr)


def test_each_sides_own_order_is_kept():
    # main already settled [Append, Site]; re-sorting them would undo that.
    append = section("2026-10-04", "Append-only merge script", "Decided C.")
    site = section("2026-10-04", "Site render check", "Decided B.")
    pr = section("2026-10-04", "Mechanism diagram", "Decided A.")
    assert mao.merge_texts(dec(), dec(pr), dec(append, site), DEC) == dec(pr, append, site)


def test_once_or_after_every_merge_gives_the_same_file():
    # The two ways to keep a PR mergeable: merge main in once, just before the PR
    # merges, or after every other PR merges. Both must give the same file.
    p1 = section("2026-10-04", "First merged", "Decided 1.")
    p2 = section("2026-10-04", "Second merged", "Decided 2.")
    pr = section("2026-10-04", "This PR", "Decided 3.")
    main1 = mao.merge_texts(dec(), dec(p1), dec(), DEC)                  # PR 1 merges
    main2 = mao.merge_texts(dec(), dec(p2), main1, DEC)                  # PR 2 merges
    once = mao.merge_texts(dec(), dec(pr), main2, DEC)
    step = mao.merge_texts(dec(), dec(pr), main1, DEC)                   # update after PR 1
    step = mao.merge_texts(main1, step, main2, DEC)                      # update after PR 2
    assert once == step == dec(pr, p2, p1)


def test_bullets_added_to_one_topic_on_both_sides_merge():
    # The bullet is the unit in DECISIONS.md: appended bullets from both sides stay
    # (main's first, then the PR's), and a bullet added at the top stays on top.
    base = PRE + OLD
    ours = PRE + OLD.rstrip("\n") + "\n\n- **Decided ours.**\n"
    theirs = PRE + ("### 2026-10-03 - Old topic\n\n- **Decided on top.**\n\n"
                    "- **Decided old.** Text\n  continued.\n\n- **Decided theirs.**\n")
    out = mao.merge_texts(base, ours, theirs, DEC)
    assert out == PRE + ("### 2026-10-03 - Old topic\n\n- **Decided on top.**\n\n"
                         "- **Decided old.** Text\n  continued.\n\n- **Decided theirs.**\n\n"
                         "- **Decided ours.**\n")


def test_tight_list_stays_tight_when_appended():
    # Some DECISIONS.md topics list bullets without blank lines between them.
    tight = "### 2026-10-03 - Old topic\n\n- **Decided one.**\n- **Decided two.**\n"
    new = section("2026-10-04", "B", "Decided B.")
    out = mao.merge_texts(PRE + tight, PRE + tight + "- **Decided three.**\n",
                          PRE + new + tight, DEC)
    assert out == PRE + new + tight + "- **Decided three.**\n"


def test_entry_added_away_from_the_conflict_is_kept():
    # A conflict region doesn't show everything a side added: main also adds a
    # bullet far below the top. Rebuilding from the full versions keeps it.
    lower = section("2026-10-01", "Scaffold", "Decided scaffold.").rstrip("\n") + "\n"
    base = PRE + OLD + "\n" + lower
    ours = PRE + section("2026-10-04", "A", "Decided A.") + OLD + "\n" + lower
    theirs = (PRE + section("2026-10-04", "B", "Decided B.") + OLD + "\n"
              + lower + "\n- **Decided late addition.**\n")
    out = mao.merge_texts(base, ours, theirs, DEC)
    assert "Decided late addition." in out and "Decided A." in out and "Decided B." in out


def test_edited_old_entry_is_refused():
    ours = PRE + OLD.replace("Decided old.", "Decided old, reworded.")
    with pytest.raises(mao.Refusal, match="removed or edited"):
        mao.merge_texts(dec(), ours, dec(section("2026-10-04", "B", "Decided B.")), DEC)


DEV_PRE = "# Plan deviations\n\nNewest first.\n\n## 2026-10-04 (Session 0)\n\n"
D16 = "### D16 · Parallel worktree session\n- **Plan:** one session.\n- **Actual:** two.\n"


def dev(*numbers):
    return DEV_PRE + "".join(f"### D{n} · Entry {n}\n- **Plan:** p.\n- **Actual:** a.\n\n"
                             for n in numbers) + D16


def test_deviations_sorted_by_number():
    assert mao.merge_texts(dev(), dev(18, 17), dev(19), DEV) == dev(19, 18, 17)


def test_deviations_below_an_already_merged_entry_stay_newest_first():
    # After a PR has merged main in once, its entries sit below main's newest.
    assert mao.merge_texts(dev(20), dev(20, 18, 17), dev(20, 19), DEV) == dev(20, 19, 18, 17)


def test_same_deviation_number_twice_is_refused():
    ours = DEV_PRE + "### D17 · Diagram\n- **Plan:** p.\n\n" + D16
    theirs = DEV_PRE + "### D17 · Render check\n- **Plan:** p.\n\n" + D16
    with pytest.raises(mao.Refusal, match="D17 is used by two entries"):
        mao.merge_texts(dev(), ours, theirs, DEV)


def test_edited_deviation_is_refused():
    ours = DEV_PRE + D16.replace("two.", "two sessions.")
    with pytest.raises(mao.Refusal, match="existing entry edited"):
        mao.merge_texts(dev(), ours, dev(17), DEV)


def test_unrecognised_layout_is_refused():
    with pytest.raises(mao.Refusal, match="layout not recognised"):
        mao.merge_texts(dec(), dec(), dec() + "\n", DEC)


def _git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True)


def test_end_to_end_conflicted_merge(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "core.autocrlf", "false")
    f = repo / "DECISIONS.md"
    pr = section("2026-10-04", "From PR", "Decided PR.")
    main = section("2026-10-04", "From main", "Decided main.")
    f.write_text(dec(), encoding="utf-8", newline="\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "base")
    _git(repo, "switch", "-qc", "pr")
    f.write_text(dec(pr), encoding="utf-8", newline="\n")
    _git(repo, "commit", "-qam", "pr")
    _git(repo, "switch", "-q", "main")
    f.write_text(dec(main), encoding="utf-8", newline="\n")
    _git(repo, "commit", "-qam", "main")
    _git(repo, "switch", "-q", "pr")
    assert _git(repo, "merge", "main").returncode != 0      # a real conflict

    assert mao.main([], cwd=repo) == 0
    assert f.read_text(encoding="utf-8") == dec(pr, main)
    assert "Next: review" in capsys.readouterr().out
