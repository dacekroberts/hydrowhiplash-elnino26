# Session 11 kickoff: site charts, the sibling prediction project, before the hard-line item

Written at the end of session 10 (2026-10-12). Part 1 is the handoff;
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout; Part 3 is the sibling prediction project, to be drafted with
the owner in session 11.

## Part 1 · Handoff

**Where things stand.**

- **Nothing in `results/tables/run1/` is edited, renamed or deleted.**
  Any change that can move a registered number follows
  `docs/post_results_protocol.md`. `python -m src.pin_inputs --verify`
  passed at the end of session 10 (30 files).
- **Design system adopted (D86).** Master copy `theme/tokens.json`, read
  by `src/theme.py`; the Design System artifact mirrors it
  (https://claude.ai/artifact/JEsfHNH6vN7VknKmkVLP3M). Applied to the
  Quarto site (light and dark), the results page, the methods reading
  copy, both diagrams and the data guide. Not yet restyled: the data
  figures in `src/figures.py` and the roadmap artifact.
- **Hosting decided (D84):** "hosted as the static Quarto build on the
  owner's own domain through Cloudflare, not on GitHub Pages". Nothing
  is deployed; the setup is settled when the first piece is ready.
- **Map page agreed (D85):** "all seven regions with a toggle per
  dataset (fire, snowpack, rainfall, temperature) ... no trend
  statistic. *After the stamped download paths and the hard-line
  item.*" Not started.
- **Rollout calendar (D87).** `src/rollout.py` builds 18 arrivals from
  `src/config.py` into `results/tables/rollout_calendar.json`;
  `site/tracker.qmd` shows a timetable of 12 of them (its sentences and
  row wording are drafts for the owner). Ten look-and-report reminders
  are scheduled as one-time tasks (ids `whiplash-rollout-...`, in the
  owner's `~/.claude/scheduled-tasks/`): 2026-11-04, 2026-12-04,
  2027-01-04, 2027-02-04, 2027-02-26, 2027-03-04, 2027-04-04,
  2027-05-11, 2027-10-28, 2028-01-28. A task reads its item from the
  calendar file but its own run date is fixed: if a calendar date
  changes, move the task by hand.
- **The 2027 forecast is published in two stages (owner, D76, D87):**
  at CPC's first RONI release after February 2027 (expected 1 to 14
  March; the frozen plan fixes that release as the input, "with its
  retrieval date recorded"), from the H3a model (El Niño strength on
  burned area, trend only); and after the 1 April snowpack (about
  8 April 2027), adding the two secondary H6 forecasts. H3a showed no
  gain over a trend-only model in `run1` (-0.03 to +0.01); the first
  stage's wording has to say so.
- **Stamped paths built (D73, D88; work item 1 done).** Every download
  script takes `--stamp [YYYY-MM-DD]` and then writes to
  `data/raw/later/<stamp>/`, closed by `retrieval.json`. Six climate
  builders (`era5`, `snow`, `whiplash`, `phase2`, `climate_vars`,
  `snow_soil`) take the same flag, read the latest closed retrieval over
  the files on disk and write to `results/tables/tracker/<stamp>/` with
  `rebuild.json` and `changed_cells.csv`. Tested on made-up files only;
  no stamped download has been run; `ERA5_LAG_MONTHS` is still 3. Not
  built: a stamp for the station snow index and the fire builders, and
  the tracker's own region x month table and tiles.
- **Methods page (work item 3 done).** Its eight measured numbers are
  read from `results/tables/methods_numbers.csv`
  (`python scripts/methods_numbers.py`; D89); no dagger is left. The
  notices were confirmed against each publisher on 2026-10-12 and the
  three missing entries added. The page is still a draft: the prose is
  the owner's to sign off.
- **Prediction model merged (PR #24, squash commit a669813; D90 to
  D92).** Versions 1, 1b and 1c are the in-project exploratory record;
  spring inputs beat a trend-only model by about 0.01 (best variant
  0.012, 95% interval -0.001 to 0.032); with the summer's means known,
  which cannot forecast, 0.126 (0.061 to 0.231). Machine learning was
  not tried. Owner: further prediction work goes to its own repository
  (Part 3).
- Private pages, all current at the end of session 10: results page
  https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk, methods draft
  https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf, data guide
  https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P. The roadmap
  (https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT) was not updated in
  session 10 and still has the old look.

**Yours to word or decide (flagged in session 10, nothing changed):**

- The tracker page's sentences and timetable row wording.
- On the methods page: two numbers now differ from what was typed (the
  overlap reads 101,000 ha, was 127,000; the station correlation reads
  0.77 to 0.95, was 0.78 to 0.95); two draft notice lines (the hourly
  "changes made" sentence, the MTBS access line); the sources table
  calls WFIGS "Public domain" while the ledger's verdict is "No licence
  named"; the NRCS line has no access date or address.
- `DATA_SOURCES.md`, MTBS row: one cell says the in-zip metadata was
  read, another says "unread".
- The mechanism diagram's north pathway is now teal (snowpack), not
  orange; say if a warm colour should come back.
- BC, AB and YT have no registered burned-area source for the fall 2027
  verification (on its release record CNFDB 2027 arrives about January
  2029). Decide before October 2027.
- Whether the 2026 season is redrawn once California's season closes at
  the end of January 2027 (no task exists).
- Whether a stamped rebuild should name the index retrieval it reads,
  apart from the ERA5-Land one (today it takes the latest of each).
- Google Fonts are hot-linked on the site; matplotlib uses the new
  typefaces only where the font files are installed.

**Housekeeping first (owner, end of session 10: "clean these up in
session 11"):**

- Update the roadmap artifact to the end of session 10, in the new
  design.
- Remove the side session's worktree
  `..\hydrowhiplash-elnino26-prediction-model` and its local branch:
  `git worktree list` and `git status` in it first, and ask if it holds
  anything uncommitted.

**Next work, in order:**

1. The site charts for Headlines 1 to 4 in the new design, with the
   data figures in `src/figures.py` restyled from `theme/tokens.json`.
   The 1997-98 map reads polygons: ask first.
2. The sibling prediction project: its kickoff and roadmap (Part 3).
3. D77, after the runs: the delegated-build pilot (the pin report after
   `--rebuild`) and the methods-page line on where DeepSeek was used.
   Each DeepSeek call needs its own yes; flash at peak hours, pro
   off-peak.
4. From the portfolio review: three methods-page items as one scope
   addition (next free deviation number).
5. The hard-line item, when the 4 November reminder fires (ACTION_PLAN
   Phase 5; D55, D88): `ERA5_LAG_MONTHS` 3 to 1, download every
   published 2026 month with `--stamp`, refit SPEI (about 55 minutes),
   rebuild with `--stamp`, report `changed_cells.csv`, recheck
   `TRACKER_DATA_DAY`. Then the tracker's month table and tiles.
6. The map page (D85), after item 5.

**Open, low:** pins walk one folder level (review F3); two tests need
the tag `analysis-plan-frozen` in the clone; `scripts/methods_numbers.py`
and the matching need `data/`; the side session's worktree
`..\hydrowhiplash-elnino26-prediction-model` still exists with its local
branch (the remote branch is deleted).

**Carried over, unchanged:** `data/` stays out of reach of every
DeepSeek plan; ask before any run that reads polygons; ask before every
DeepSeek call; the going-public question is a leaning, not a decision.

**Next free deviation number: D93.** The frozen plan's deviations log
is at row 19.

## Part 2 · Prompt for session 11

```text
Session 11 for hydrowhiplash-elnino26: site charts in the new design,
the sibling prediction project, and readiness for the hard-line item.

1. Orient: read CLAUDE.md, docs/session11_kickoff.md (Parts 1 and 3),
   logs/2026-10-12.md, the top of DECISIONS.md (2026-10-12 entries),
   docs/plan_deviations.md D84-D92, docs/post_results_protocol.md,
   docs/data_dictionary.md sections 8a to 8e, site/methods.qmd,
   site/tracker.qmd, results/tables/rollout_calendar.json,
   docs/prediction_sibling_kickoff.md, ANALYSIS_PLAN.md (frozen: never
   edit above the deviations log) and ACTION_PLAN.md Phases 4 and 5.
   Read with the Artifact tool (action "read"):
   the design system, https://claude.ai/artifact/JEsfHNH6vN7VknKmkVLP3M
   the roadmap, https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D93.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is 4 November 2026 or later, read the hard-line item in Part 1
   (item 5) before anything else, and tell me what the reminder found.

5. Do the two housekeeping items in Part 1 (roadmap artifact, the side
   session's worktree). Then the list "Yours to word or decide": put
   each to me briefly, with a recommendation where you have one.

6. Then the work list in Part 1, in order. Ask me before any run that
   reads polygons, and before every DeepSeek call. Flag scope additions
   rather than building them.

7. For the sibling prediction project (Part 3): bring me the open
   decisions with a recommendation each, then draft its kickoff and its
   roadmap with me. Nothing is created (no repository, no tag) without
   my yes.

8. My interpretation of the results is mine to write. Discuss the
   numbers, flag stale or inconsistent wording, and suggest; don't
   rewrite.

9. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   python scripts/check_site.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild
   the results page and the methods reading copy if they changed, update
   the roadmap artifact in the new design, and write the next kickoff
   the same way.
```

## Part 3 · The sibling prediction project

Owner, 2026-10-12 (`DECISIONS.md` "Prediction model: the in-project
record stops at version 1c; further work goes to its own repository"):
the model gets its own repository, as a sibling of this project; the
main session drafts its kickoff, with `docs/prediction_sibling_kickoff.md`
as source material; a roadmap for it is essential. Owner, end of session
10: the kickoff is drafted in session 11.

What that file holds (the side session's proposals; none adopted):

- Section 2: what versions 1 to 1c established, with intervals.
- Section 3: what carries over (the committed region x year tables, the
  scoring on unseen years, the trend-only baseline).
- Section 4: candidate work in a suggested order: later issue dates,
  summer forecasts as inputs, spring fuel dryness, fuel amount
  (satellite greenness), smaller units, a longer fire record (before
  1984), other targets, and a grid-cell model for machine learning.
  Owner: machine learning is "to be tried later after other items". The
  ceiling check and last season's burned area are already done in
  version 1c.
- Section 5: the decisions still open for the owner before a first
  session.
- A suggestion to tag PR #24's squash commit (a669813) as the handoff
  point for the new repository's pinned inputs. Not done; needs the
  owner's yes.

To settle with the owner in session 11, each with a recommendation: the
repository's name and whether it is private; which tables it copies and
how they are pinned to this project's commit; its licence split (this
project: MIT for code, all rights reserved for writing and figures);
whether it keeps this project's rules (a frozen plan before any fit, a
deviations log, a daily log); the first piece of work from section 4;
and the roadmap's form (an artifact in the design system, as here).
The registered 2027 forecast stays the H3a model in this project
whatever the sibling finds.
