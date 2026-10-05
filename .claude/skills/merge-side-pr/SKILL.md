---
name: merge-side-pr
description: Review and merge pull requests from worktree or side-branch sessions into main, then fold each session block into the day's log. Use in the main-checkout session when a side session reports a PR, or when the owner asks to review or merge one or several. Pre-screens the whole queue first, then merges one PR at a time in the screened order.
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
3. **Pre-screen the whole queue, merged, before anyone approves.** Decide the
   merge order (dependencies first; a PR that adds tooling the others use goes
   first), then run, from the main checkout:
   ```
   python scripts/prescreen_prs.py <N1> <N2> ...      # in merge order
   ```
   It merges every PR in order onto current main in a throwaway worktree,
   resolves `DECISIONS.md` and `docs/plan_deviations.md` with
   `merge_append_only.py`, runs pytest, the em-dash check and (for PRs
   touching `site/`, `results/figures/`, `src/figures.py` or
   `src/diagrams.py`) `check_site.py` after each merge, applies the known
   fix-ups it lists, and prints a report: CLEAN, CLEAN after fix-up, or
   UNEXPECTED with the reason. What gets approved is then exactly what was
   tested, including clashes between PRs (a D number used twice, a check
   that fails only after an earlier PR). For changes under `src/`, also run
   `/code-review low` on each PR. Tests that need `data/` can't run there
   (data is never committed); say so instead of skipping silently.
4. **Report to the owner, or go ahead.** Show the report, the step 2 rule
   flags, anything touching their prose and any code-review findings.
   - If the owner gave a yes for the run ("merge them if the pre-screen is
     clean") and the report is ALL CLEAN with no flags or findings, go on to
     step 5 for each PR in the screened order without asking again.
   - Otherwise ask for a clear yes. The owner may prefer to merge on GitHub
     instead; then skip to step 7 once it's merged.
   **Stop and ask** (whatever was agreed) when anything is unexpected:
   the pre-screen says UNEXPECTED or `merge_append_only.py` refuses; a
   conflict outside the two logs; a check fails without a fix-up the report
   listed; a step 2 flag or code-review finding; or main or a PR head moved
   since the pre-screen other than by this run's own merges (re-run the
   pre-screen first).
5. **Merge main into the PR branch, as screened.** Do it on the PR branch,
   not on main, in a throwaway worktree (the main checkout may hold
   uncommitted work):
   ```
   git fetch origin pull/<N>/head:pr-<N>
   git worktree add ../_pr-<N> pr-<N>
   ```
   In `../_pr-<N>`: `git merge --no-commit --no-ff origin/main`, then
   `python scripts/merge_append_only.py --against origin/main`, every time,
   conflicts or not (if the branch already contains main, git opens no merge
   and the script says "nothing to check"; that is not a refusal): git
   merges the two logs cleanly whenever the additions don't touch the same
   lines, and a clean merge can still hold one D number twice. The script
   merges both logs entry by entry (newest date first, deviations by number;
   on the same date the PR's entries go above main's, so the latest merge
   ends on top), keeps every entry of both sides, and refuses if an old entry
   was edited or a D number is used twice. Repeat any fix-up the report
   listed for this PR, run the same checks, review with `git diff`, `git add`
   the files it names, commit and push. The result must
   match the report: if anything differs, stop and ask. This step is the
   main session's job: side sessions don't merge main into their open PRs
   (the owner's choice, 2026-10-04), so only one session ever pushes merge
   commits to a PR branch. If the script refuses, resolve that file by
   hand: keep every entry of both sides, never one side's whole file.
6. **Merge.** `gh pr merge <N> --squash` (no `--delete-branch`), then
   delete only the remote branch: `git push origin --delete <branch>`.
   Squash gives one commit per task on `main`; the PR keeps the detailed
   history. Never pass `--delete-branch`: it also deletes the local branch,
   and if a side session has that branch checked out, `gh` removes the
   session's whole worktree, uncommitted work included (happened with PR #2,
   2026-10-04). Delete the local branch only if `git worktree list` shows it
   checked out nowhere: `git branch -D <branch>`.
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

- Never merge without the owner's yes in this conversation. A yes may cover
  a whole run of pre-screened PRs (step 4); it never covers anything the
  pre-screen didn't predict.
- Never force-push `main` or rewrite its history.
- If the PR conflicts with work in progress on `main`, stop and ask which
  should give way.
