---
name: merge-side-pr
description: Review and merge a pull request from a worktree or side-branch session into main, then fold its session block into the day's log. Use in the main-checkout session when a side session reports a PR, or when the owner asks to review or merge one. One PR per run.
---

# Merge a side-session PR

Side sessions (git worktrees, side branches, later the Claude Code Project's
threads) don't edit `logs/` and can't merge. This skill is the main session's
half of that arrangement (`CLAUDE.md`, "Exception, worktree and branch
sessions"). The owner approves every merge.

`gh` may not be on PATH: call `"C:\Program Files\GitHub CLI\gh.exe"`. Run
Python through `C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash
--no-capture-output`.

## Steps

1. **Read the PR.** `gh pr view <N> --json number,title,headRefName,baseRefName,body,files,mergeable,commits`
   and `gh pr diff <N>`. Base must be `main`.
2. **Check the side-session rules.** Flag, and don't merge until resolved, if
   the PR:
   - adds anything under `data/`, or reads or summarises fire data before
     `ANALYSIS_PLAN.md` is frozen;
   - edits `logs/`;
   - edits `ANALYSIS_PLAN.md` above its deviations log after the freeze;
   - changes `LICENSE`, `LICENSE-CONTENT` or `environment.yml` without the
     owner having asked;
   - rewrites the owner's prose (findings, interpretation, site text);
   - hard-codes a value that belongs in `src/config.py`, or measures area or
     regional means outside `src.geo`;
   - has no session block in its description (ask the side session for it;
     never write one on its behalf).
3. **Test the PR's code without touching the main checkout.** The main
   checkout may hold uncommitted work, so use a throwaway worktree:
   ```
   git fetch origin pull/<N>/head:pr-<N>
   git worktree add ../_pr-<N> pr-<N>
   ```
   In `../_pr-<N>`: `python -m pytest` and
   `python scripts/check_no_em_dashes.py`. For changes under `src/`, also run
   `/code-review low` on the PR. If the PR touches `site/`, `results/figures/`
   or `src/figures.py`, also run `python scripts/check_site.py`: it renders a
   copy of the site and fails on any unrendered page or broken local link
   (a bare `quarto render` exits 0 on both). Tests that need `data/` can't run there
   (data is never committed); say so instead of skipping silently.
4. **Report to the owner and wait.** In a few lines: what the PR changes,
   check results, rule flags, anything touching their prose, merge
   conflicts. Ask for a clear yes before merging. The owner may prefer to
   merge on GitHub instead; then skip to step 7 once it's merged.
5. **Resolve conflicts on the PR branch, not on main.** Expected spots:
   the top of `DECISIONS.md` and `docs/plan_deviations.md` (both newest
   first). In `../_pr-<N>`: `git merge origin/main`, keep both entries, newest
   date first (same date: keep main's entry above the PR's), commit, push,
   re-run step 3's checks.
6. **Merge.** `gh pr merge <N> --squash --delete-branch`. Squash gives one
   commit per task on `main`; the PR keeps the detailed history.
7. **Update the main checkout.** `git status` first: if it has uncommitted
   changes, ask before doing anything with them (never stash silently). Then
   `git pull --ff-only`.
8. **Fold the session block into the day's log** (`logs/YYYY-MM-DD.md` for
   the day the side session worked; create it with
   `python scripts/log.py new` if missing):
   - paste the block under `## Sessions` in order of start time; its heading
     stays `### HH:MM-HH:MM · Claude Code (worktree: <branch>)`;
   - add `"claude-code-worktree HH:MM-HH:MM"` to `sessions`. Don't add its
     hours to `hours`: it ran in parallel with the owner's main session, and
     `hours` counts the owner's hands-on time. Merge its `tags`;
   - copy its decisions under `## Decisions` and its files under
     `## Files changed`, each marked "(PR #<N>)";
   - add a bullet to the current main session's block: "Merged PR #<N>
     (<title>), squash commit <hash>".
9. **Clean up.** `git worktree remove ../_pr-<N>` and `git branch -D pr-<N>`.
10. **Check and commit.** `python scripts/log.py list`,
    `python scripts/check_no_em_dashes.py`, then commit the log with
    "Log PR #<N> session block" and push.

## Rules

- Never merge without the owner's yes in this conversation.
- Never force-push `main` or rewrite its history.
- If the PR conflicts with work in progress on `main`, stop and ask which
  should give way.
