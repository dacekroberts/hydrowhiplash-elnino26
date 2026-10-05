# Pull requests: a working guide

How pull requests (PRs) work, and how this project uses them. Written
2026-10-04, when the first side-session PRs were opened.

## How this project uses PRs

Side sessions (git worktrees, side branches) never commit to `main`. Each task
goes on its own branch, is pushed to GitHub, and arrives as a PR that the
owner reviews and merges (`CLAUDE.md`, "Exception, worktree and branch
sessions"; `DECISIONS.md` 2026-10-04 "Side worktree session"). The main
session's half of the arrangement is the `merge-side-pr` skill: it tests the
PR in a throwaway worktree, reports, waits for a yes, squash-merges, and folds
the side session's block into the day's log.

This differs from expanded-heatmap, where every worktree branch tracked
`origin/master` and each session merged and pushed straight to `master`
(no PRs, coordination through rules such as fetch-before-push). Here, nothing
reaches `main` without the owner's approval.

```
main ──●──────────────●── (squash merge) ──
        \            /
         ●──●──●────┘   side/mechanism-diagram  ← PR #1: "please merge this"
```

## Terms

- **Branch:** a parallel line of commits. `main` is the official line;
  `side/mechanism-diagram` is a side session's.
- **Commit:** one saved snapshot of changes, with a message.
- **Push:** upload commits to GitHub. Until then they exist only on the
  machine that made them.
- **PR (pull request):** a request to merge one branch into another. The
  **head** is the branch with the work; the **base** is where it goes
  (`main`).
- **#1, #2, #3:** the PR's number. GitHub numbers PRs and issues in one shared
  sequence per repository, so the next one after PR #3 is #4 whichever kind it
  is. A bare `#3` only means something inside its own repository; elsewhere
  write `dacekroberts/hydrowhiplash-elnino26#3` or link it.
- **Diff:** the line-by-line difference between head and base. "+192 −1"
  means 192 lines added and 1 removed. On GitHub it is the **Files changed**
  tab: green lines added, red lines removed.
- **CI (continuous integration) / checks:** automated jobs GitHub runs on
  every push to a PR, usually tests. They are defined in
  `.github/workflows/`. This repository has none yet, so the CI indicator
  stays empty; with a workflow, pytest and the em-dash check would run on
  GitHub and show ✓ or ✗ before merging.
- **Review:** reading the diff and commenting, on the whole PR or on single
  lines. PRs opened with `gh` from this machine use the owner's GitHub
  account, so GitHub won't offer "Approve" on them (no one can approve
  their own PR); merging is the approval.
- **Conflict:** two branches changed the same lines differently, so git
  can't combine them on its own. GitHub shows "This branch has conflicts" and
  someone resolves them. In this project the usual spot is the top of
  `DECISIONS.md` and `docs/plan_deviations.md`, where every branch adds new
  entries; resolve on the PR branch, never on `main` (`merge-side-pr` step 5).
- **Mergeable:** GitHub's verdict on whether the branch can merge cleanly
  right now.
- **Merge:** bring the branch into the base. Three ways:
  - **Merge commit:** keeps every commit plus one commit joining the lines.
  - **Squash and merge:** folds the whole PR into one commit on `main`. This
    project's default (`merge-side-pr` step 6): one commit per task, while
    the PR keeps the detailed history.
  - **Rebase and merge:** replays each commit onto `main` one by one.
- **Draft:** a PR marked not ready for review.
- **Close:** reject a PR without merging (it can be reopened).
- **Delete branch:** tidy-up after a merge; the PR keeps the record.

## Reviewing and merging a PR

1. Open the PR on GitHub (the side session's final message links it). Read
   the description first: what changed, why, the checks run, anything
   flagged for the owner, and the session block.
2. Open **Files changed** and read the diff. Images and figures show as
   before/after.
3. To ask for changes, comment on a line or on the PR, or tell the side
   session. It pushes new commits to the same branch and the PR updates
   itself; nothing needs reopening.
4. To merge, either:
   - in the main session, ask it to merge the PR: the `merge-side-pr` skill
     runs the checks in a throwaway worktree, resolves conflicts, asks for a
     yes, squash-merges and updates the day's log; or
   - press **Squash and merge** on GitHub, then tell the main session, so it
     pulls `main` and copies the session block into the log (skill step 7
     onward).
5. Several open PRs that all touch `DECISIONS.md` will conflict with each
   other in turn: after the first merges, the rest need `main` merged into
   their branches. The side session can do that on its own branches.

## The PR bar in the Claude desktop app

The bar above a Code session shows the state of that session's branch:

- **Create PR** (with a diff count): the branch has changes but no PR yet.
  The arrow beside it offers variants such as a draft PR.
- **#N, repository, branch, CI and ×:** a PR is open and linked to the
  session. CI summarises the checks; × unlinks the PR from the session
  (it doesn't close the PR).

The diff count follows the branch currently checked out in the session's
folder, while the PR chip follows the linked PR, so the two can disagree
when a session has moved on to another branch.
