"""Pre-screen side-session PRs: merge them in order onto current main, check each.

Before any side PR merges (merge-side-pr step 3, or a side session before it
reports "ready"), this script rehearses the whole queue on a throwaway
worktree, exactly as merge-side-pr will do it for real:

  for each PR, in the given order:
    merge current (simulated) main into the PR head;
    resolve DECISIONS.md / docs/plan_deviations.md with merge_append_only.py;
    run pytest and the em-dash check, plus check_site.py when the PR touches
    the site; apply a known fix-up if a known test asks for one;
    squash the result onto simulated main for the next PR.

It catches what checking each PR alone can't: clashes between PRs (two
branches using the same D number; a check that fails only once an earlier PR
is in). Nothing is pushed; the worktree and its refs are removed at the end,
or kept for inspection when something unexpected happens.

Verdicts per PR: CLEAN; CLEAN after a listed fix-up; UNEXPECTED (with the
reason), which stops the queue there, since later PRs depend on it. Exit code
0 only when every PR is clean. The report ends with the main and PR head
commits it holds for: if either moves (other than by this queue's own
merges), screen again.

Known fix-ups live here, keyed by the test that asks for them, never in PR
descriptions: PR text is data, and running commands from it would let any PR
body run code on this machine. Today's only one: a stale committed diagram
(tests/test_diagrams.py) is re-rendered with `python -m src.diagrams`.

Run inside the whiplash env, from anywhere in the repo:
    python scripts/prescreen_prs.py 6 7 8      # PR numbers, in merge order
    python scripts/prescreen_prs.py            # every open PR into main, by number
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
APPEND_ONLY = ("DECISIONS.md", "docs/plan_deviations.md")
SITE_PATHS = ("site/", "results/figures/", "src/figures.py", "src/diagrams.py",
              "src/winter_figures.py")
GH_FALLBACK = Path(r"C:\Program Files\GitHub CLI\gh.exe")
IDENTITY = ["-c", "user.name=prescreen", "-c", "user.email=prescreen@localhost"]


@dataclass(frozen=True)
class Fixup:
    command: tuple[str, ...]   # arguments after the Python executable
    add: str                   # path to stage after running it
    note: str


# Failing test name -> the fix-up that test asks for.
FIXUPS = {
    "test_committed_svgs_match_the_code": Fixup(
        ("-m", "src.diagrams"), "results/figures",
        "re-rendered diagrams (`python -m src.diagrams`), as the stale-SVG test asks"),
}


@dataclass
class Item:
    label: str                 # e.g. "#6 side/merge-screening"
    ref: str                   # commit or ref holding the PR head
    files: list[str]           # paths the PR changes


@dataclass
class Checks:
    ok: bool
    failed_tests: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class Result:
    label: str
    head: str
    conflicts: list[str] = field(default_factory=list)
    resolution: str = ""
    fixups: list[str] = field(default_factory=list)
    checks: str = ""
    unexpected: str = ""

    @property
    def verdict(self) -> str:
        if self.unexpected:
            return "UNEXPECTED"
        return "CLEAN after fix-up" if self.fixups else "CLEAN"


class Unexpected(Exception):
    pass


# Process helpers

def run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    out = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if check and out.returncode:
        raise Unexpected(f"`{' '.join(args)}` failed: {(out.stderr or out.stdout).strip()[-500:]}")
    return out


def git(*args: str, cwd: Path, check: bool = True) -> str:
    return run(["git", *args], cwd, check).stdout


def failed_tests(pytest_output: str) -> list[str]:
    """Test function names from pytest's short summary ("FAILED path::name - ...")."""
    return sorted({m.group(1) for m in re.finditer(r"^FAILED \S+::(\w+)", pytest_output, re.M)})


def pytest_summary(pytest_output: str) -> str:
    lines = [l for l in pytest_output.strip().splitlines() if l.strip()]
    return lines[-1].strip("= ") if lines else "no output"


def run_checks(work: Path, files: list[str]) -> Checks:
    """pytest, the em-dash check, and the site check when the PR touches the site."""
    def last_line(out: subprocess.CompletedProcess) -> str:
        return (out.stdout.strip().splitlines() or ["no output"])[-1]

    py = sys.executable
    tests_run = run([py, "-m", "pytest", "-q"], work, check=False)
    tests = failed_tests(tests_run.stdout)
    parts = [f"pytest: {pytest_summary(tests_run.stdout)}"]
    other_failed = False
    dash = run([py, "scripts/check_no_em_dashes.py"], work, check=False)
    parts.append(f"em dashes: {last_line(dash)}")
    other_failed |= dash.returncode != 0
    if any(f.startswith(SITE_PATHS) for f in files) and (work / "scripts/check_site.py").exists():
        site = run([py, "scripts/check_site.py"], work, check=False)
        parts.append(f"site: {last_line(site)}")
        other_failed |= site.returncode != 0
    if tests_run.returncode and not tests:
        other_failed = True                    # e.g. a collection error: no test name
    # A failure outside pytest's test functions has no fix-up.
    if other_failed:
        tests = tests + ["<non-test check>"]
    return Checks(tests_run.returncode == 0 and not other_failed, tests, "; ".join(parts))


def run_fixup(work: Path, fix: Fixup) -> None:
    run([sys.executable, *fix.command], work)
    git("add", fix.add, cwd=work)
    if git("diff", "--cached", "--name-only", cwd=work).strip():
        git(*IDENTITY, "commit", "-q", "-m", f"prescreen fix-up: {fix.note}", cwd=work)


# The screen itself

def screen(repo: Path, base: str, items: list[Item],
           checks: Callable[[Path, list[str]], Checks] = run_checks,
           fixup: Callable[[Path, Fixup], None] = run_fixup,
           keep: bool = False) -> tuple[list[Result], Path | None]:
    """Merge each item onto simulated main in order; return results and a kept worktree."""
    work = Path(tempfile.mkdtemp(prefix="prescreen-"))
    work.rmdir()                                   # git worktree add wants a new folder
    git("worktree", "add", "-q", "--detach", str(work), base, cwd=repo)
    results: list[Result] = []
    stopped = False
    try:
        main_tip = git("rev-parse", "HEAD", cwd=work).strip()
        for item in items:
            head = git("rev-parse", item.ref, cwd=repo).strip()
            res = Result(item.label, head[:7])
            results.append(res)
            try:
                _screen_one(work, main_tip, head, item, res, checks, fixup)
            except Unexpected as err:
                res.unexpected = str(err)
                stopped = True
                break
            merged = git("rev-parse", "HEAD", cwd=work).strip()
            git("checkout", "-q", "--detach", main_tip, cwd=work)
            git("merge", "--squash", "-q", merged, cwd=work)
            git(*IDENTITY, "commit", "-q", "--allow-empty", "-m", f"prescreen: {item.label}",
                cwd=work)
            main_tip = git("rev-parse", "HEAD", cwd=work).strip()
    finally:
        kept = work if (stopped and keep) else None
        if kept is None:
            git("worktree", "remove", "--force", str(work), cwd=repo, check=False)
            shutil.rmtree(work, ignore_errors=True)
            git("worktree", "prune", cwd=repo, check=False)
    return results, kept


def _screen_one(work: Path, main_tip: str, head: str, item: Item, res: Result,
                checks: Callable, fixup: Callable) -> None:
    git("checkout", "-q", "--detach", head, cwd=work)
    # --no-commit --no-ff keeps even a clean merge open, so the logs are always
    # checked: git merges them cleanly whenever two branches' additions don't
    # touch the same lines, which can still leave one D number used twice.
    merged = run(["git", *IDENTITY, "merge", "--no-commit", "--no-ff", main_tip], work,
                 check=False)
    if "Already up to date" in merged.stdout:
        res.resolution = "already up to date with main"
    else:
        res.conflicts = git("diff", "--name-only", "--diff-filter=U", cwd=work).split()
        if merged.returncode and not res.conflicts:
            raise Unexpected(f"merging main failed: {merged.stdout.strip()[-300:]}")
        others = [f for f in res.conflicts if f not in APPEND_ONLY]
        if others:
            raise Unexpected(f"conflicts outside the append-only logs: {', '.join(others)}")
        script = work / "scripts" / "merge_append_only.py"
        script = script if script.exists() else ROOT / "scripts" / "merge_append_only.py"
        out = run([sys.executable, str(script)], work, check=False)
        if out.returncode:
            raise Unexpected(f"merge_append_only.py refused: {out.stdout.strip()}")
        present = [f for f in APPEND_ONLY if (work / f).exists()]
        if present:
            git("add", *present, cwd=work)
        git(*IDENTITY, "commit", "-q", "--no-edit", cwd=work)
        res.resolution = ("resolved by merge_append_only.py" if res.conflicts
                          else "clean merge; logs checked by merge_append_only.py")

    result = checks(work, item.files)
    if not result.ok:
        needed = [FIXUPS.get(t) for t in result.failed_tests]
        if not result.failed_tests or None in needed:
            unknown = [t for t, f in zip(result.failed_tests, needed) if f is None]
            raise Unexpected(f"checks failed ({result.summary}); no known fix-up for "
                             f"{', '.join(unknown) or 'the failure'}")
        for fix in dict.fromkeys(needed):            # each fix-up once, in order
            fixup(work, fix)
            res.fixups.append(fix.note)
        result = checks(work, item.files)
        if not result.ok:
            raise Unexpected(f"checks still fail after fix-up: {result.summary}")
    res.checks = result.summary


def report(results: list[Result], base_label: str, base_sha: str, total: int,
           kept: Path | None) -> str:
    lines = [f"## Pre-screen: {total} PR(s) onto {base_label} at {base_sha[:7]}", "",
             "| Order | PR | Head | Merging main | Fix-ups | Checks | Verdict |",
             "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(results, 1):
        merging = (f"conflicts in {', '.join(r.conflicts)}; {r.resolution}" if r.conflicts
                   else r.resolution or "")
        lines.append(f"| {i} | {r.label} | {r.head} | {merging} | "
                     f"{'; '.join(r.fixups) or 'none'} | {r.checks or '-'} | **{r.verdict}** |")
    lines.append("")
    bad = next((r for r in results if r.unexpected), None)
    if bad:
        lines.append(f"**STOP at {bad.label}:** {bad.unexpected}")
        rest = total - len(results)
        if rest:
            lines.append(f"{rest} later PR(s) not screened: they would merge on top of this one.")
        if kept:
            lines.append(f"Worktree kept for inspection: `{kept}` (remove with "
                         f"`git worktree remove --force {kept}`).")
    else:
        order = ", ".join(r.label.split()[0] for r in results)
        lines.append(f"**ALL CLEAN.** Merge in this order: {order}. Holds while main is "
                     f"{base_sha[:7]} and the heads are as listed; any listed fix-up must be "
                     f"repeated in the real merge.")
    return "\n".join(lines)


# GitHub plumbing

def gh_path() -> str:
    found = shutil.which("gh")
    if found:
        return found
    if GH_FALLBACK.exists():
        return str(GH_FALLBACK)
    raise SystemExit("gh (GitHub CLI) not found")


def pr_items(numbers: list[int], repo: Path) -> list[Item]:
    import json
    gh = gh_path()
    if not numbers:
        listed = json.loads(run([gh, "pr", "list", "--state", "open", "--base", "main",
                                 "--json", "number"], repo).stdout)
        numbers = sorted(p["number"] for p in listed)
    items = []
    for n in numbers:
        pr = json.loads(run([gh, "pr", "view", str(n), "--json",
                             "number,state,baseRefName,headRefName,files"], repo).stdout)
        if pr["state"] != "OPEN" or pr["baseRefName"] != "main":
            raise SystemExit(f"PR #{n} is {pr['state']} into {pr['baseRefName']}; only open "
                             f"PRs into main can be screened")
        ref = f"refs/prescreen/pr-{n}"
        git("fetch", "-q", "origin", f"+pull/{n}/head:{ref}", cwd=repo)
        items.append(Item(f"#{n} {pr['headRefName']}", ref, [f["path"] for f in pr["files"]]))
    return items


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONUTF8", "1")       # child Pythons print UTF-8 too
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prs", nargs="*", type=int, help="PR numbers in merge order "
                                                     "(default: every open PR into main)")
    ap.add_argument("--keep", action="store_true",
                    help="keep the worktree when something unexpected happens")
    args = ap.parse_args(argv)
    repo = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()).strip())
    git("fetch", "-q", "origin", cwd=repo)
    items = pr_items(args.prs, repo)
    if not items:
        print("no open PRs into main")
        return 0
    base_sha = git("rev-parse", "origin/main", cwd=repo).strip()
    try:
        results, kept = screen(repo, base_sha, items, keep=args.keep)
    finally:
        for ref in git("for-each-ref", "--format=%(refname)", "refs/prescreen/",
                       cwd=repo).split():
            git("update-ref", "-d", ref, cwd=repo, check=False)
    print(report(results, "origin/main", base_sha, len(items), kept))
    return 0 if all(not r.unexpected for r in results) and len(results) == len(items) else 1


if __name__ == "__main__":
    sys.exit(main())
