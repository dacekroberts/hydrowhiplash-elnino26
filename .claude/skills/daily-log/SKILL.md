---
name: daily-log
description: Write or update today's project log in logs/YYYY-MM-DD.md. Required at the end of every work session, and whenever the user asks to log progress. Appends a session block; never rewrites earlier sessions or earlier days.
---

# Daily log

Every working day has one file, `logs/YYYY-MM-DD.md` (local date), with the
same frontmatter and headings as `logs/_TEMPLATE.md`. The user pulls these
into their own catalogue, so the structure must stay identical every day.

## When

- At the end of every work session, before the final commit. Required, not
  optional.
- When the user asks to log, summarise or wrap up.

## Steps

1. Get the current local date and time:
   `python -c "import datetime; print(datetime.datetime.now().isoformat(timespec='minutes'))"`
2. `python scripts/log.py new` creates today's file from the template if it
   doesn't exist yet. If it exists, keep everything already in it.
3. Add one `### HH:MM-HH:MM · Claude Code` block under `## Sessions`, after
   any earlier blocks (chronological, oldest first). Inside it, timestamped
   bullets in the order things happened: what was run, which files changed,
   what was checked and how, what was learned. Specific enough that the work
   could be reconstructed from the log alone.
4. Add to the other sections rather than replacing them:
   - **Decisions:** one line each, pointing at the `DECISIONS.md` entry (or
     the `ANALYSIS_PLAN.md` deviations log). If a decision was made but not
     logged there yet, log it there first.
   - **Results and numbers:** copy figures from output files, with the file
     path. Never type a number from memory.
   - **Problems and fixes**, **Files changed** (`git diff --stat` helps).
   - **Next:** replace with the first concrete step for the next session.
5. Update the frontmatter: `phase`, add this session to `sessions`, add its
   hours to `hours`, merge new `tags`, and rewrite `summary` (one or two
   sentences) to cover the whole day so far.
6. Check the file still parses: `python scripts/log.py list`.
7. Commit the log with the session's other changes.

## Rules

- Never edit a previous day's log. A correction goes in today's log, naming
  the earlier date.
- Side-session blocks (worktree or branch sessions, which don't edit
  `logs/`) are folded in by `merge-side-pr` step 8 into the log of the day
  the PR is merged, the same rule as above: never into an earlier day's log.
  A block whose work happened on an earlier day keeps its times and says
  its work date in its heading (`worked YYYY-MM-DD`) and `sessions` entry.
- Neutral, factual voice, past tense. No em dashes in the frontmatter.
- Work done in claude.ai doesn't reach the repo by itself: when the user
  pastes a summary of a claude.ai session, add it as its own
  `### HH:MM-HH:MM · claude.ai` block.
