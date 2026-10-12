# Session 12 kickoff: the owner's wording, the DeepSeek pilot, before the hard-line item

Written at the end of session 11 (2026-10-12). Part 1 is the handoff;
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout.

## Part 1 · Handoff

**Where things stand.**

- **Nothing in `results/tables/run1/` is edited, renamed or deleted.**
  Any change that can move a registered number follows
  `docs/post_results_protocol.md`.
- **Figures and charts (work item 1 of session 11, done).** Every data
  figure in `src/figures.py` takes its colours from `theme/tokens.json`
  (no hex value is typed in the file). `src/results_figures.py` draws one
  chart per headline from `run1` into `results/figures/headline*.png`;
  `src/fire_figures.py` also writes a Plotly version of the season
  history (`burned_area_season_history_roni.html`) with an empty slot
  for 2027. `site/methods.qmd` embeds the four charts and
  `site/index.qmd` the Plotly one. Not yet looked at in a browser. The
  1997-98 map was not redrawn (it reads polygons: ask first).
- **Typefaces.** The three design typefaces are bundled in `site/fonts/`
  and the site loads them itself. The figures stay on the system sans:
  matplotlib draws a variable font at its default weight only. Owner,
  2026-10-12: "leave font for now, address how we can work around this
  when the time comes". Ways round, when it matters: static Regular and
  Bold files made from the variable ones (read each licence's
  reserved-name clause first), or figures as SVG with text left as text
  so the browser sets the type.
- **Verification sources (D93).** "in fall 2027 the panel covers PNW and
  AK (WFIGS, provisional); BC, AB and YT are verified from NBAC, marked
  provisional, when it holds 2027 (about May 2028), and CNFDB 2027 is
  set beside it when it arrives (about January 2029)." The rollout
  calendar holds 20 items, 14 shown on the tracker page; 12 reminders are
  scheduled (the two new ones: 2028-04-28 and 2028-12-29).
- **The 2026 season (D95)** is redrawn after 31 January 2027, at the
  4 February 2027 reminder: WFIGS to a stamped path, US regions,
  described only. Reads polygons: ask first.
- **Stamped rebuilds** can name the index retrieval they read
  (`--index-stamp YYYY-MM-DD`); without it the latest closed one is
  taken.
- **Sibling repository (D94).** `climate-whiplash-prediction`, private,
  at `..\climate-whiplash-prediction` and on GitHub; it holds licence
  files, a README and `docs/kickoff.md` only. It reads this project at
  the tag `prediction-handoff` (a669813). Its first session is its own
  stage 0; its roadmap is https://claude.ai/artifact/1HcVPoH7YdwFBFUxwLGtcg.
  Its `docs/kickoff.md` has one uncommitted line removed (the settled
  "create the repository" question); commit it there.
- **Three methods-page items (D96).** Drafts sit in `site/methods.qmd`
  as HTML comments, shown to no reader: "Why regression, not a trained
  model" (after "How the tests work"), "Who this forecast is for" (top
  of "The 2027 forecast") and "Where coverage is thin" (before "What the
  whole analysis cannot say"). The wording is the owner's.
- **DeepSeek build pilot (D77): prepared, not run.** The owner chose a
  staged copy (code only). The implement call was refused by Claude
  Code's permission check, because the worker starts with
  `--allow-bypass`; no call was made. The staged copy lived in session
  11's scratch folder and may be gone: staging again takes one command
  (the tracked files of `src/`, `tests/`,
  `scripts/check_no_em_dashes.py` and `environment.yml` into a new git
  repository outside the project). The plan's text is in `DECISIONS.md`
  2026-10-12 "the delegated-build pilot is prepared on a staged copy" in
  outline: eight modules, a goal with acceptance tests, five traps left
  out on purpose. The owner either runs the worker command in a terminal
  or allows it for the session.
- Private pages, all current at the end of session 11: roadmap
  https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT, data guide
  https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P, methods reading copy
  https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf, design system
  https://claude.ai/artifact/JEsfHNH6vN7VknKmkVLP3M. The results page
  (https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk) did not change.

**Yours to word or decide (flagged in session 11, nothing changed):**

- Captions and alt text of the four headline charts and the Plotly
  history; the three new timetable rows on the tracker page.
- The three D96 drafts, and the two agency names in the second.
- The methods page's "AI use" section, with your line "DeepSeek helper
  agents contributed here" (D77); suggested place: that section, naming
  the review.
- "What a fuller version would add" still calls a prediction model "the
  next step" and "planned"; versions 1 to 1c are merged and the work
  moved (D94).
- Whether the DeepSeek pilot runs, and how the worker is started.
- `ACTION_PLAN.md` "Historical charts" is built but not ticked: the
  owner has not seen the charts.
- The Design System artifact carries no font files and the tokens'
  `type.fonts` list is empty.

**Next work, in order:**

1. Look at the built site in a browser (the four charts, the Plotly
   history, light and dark) and put what is found to the owner.
2. The owner's wording on the list above; make approved drafts visible.
3. The DeepSeek pilot, if the owner says so; then the efficiency review
   the handoff asks for (`docs/deepseek_handoff_2026-10-11.md` section
   4).
4. The hard-line item, when the 4 November reminder fires (ACTION_PLAN
   Phase 5; D55, D88): `ERA5_LAG_MONTHS` 3 to 1, download every
   published 2026 month with `--stamp`, refit SPEI (about 55 minutes),
   rebuild with `--stamp`, report `changed_cells.csv`, recheck
   `TRACKER_DATA_DAY`. Then the tracker's month table and tiles.
5. The map page (D85), after item 4.

**Open, low:** pins walk one folder level (review F3); two tests need
the tag `analysis-plan-frozen` in the clone; `scripts/methods_numbers.py`
and the matching need `data/`; a test run in a copy without
`results/` writes a made-up `data/processed/whiplash_swe_region_year.csv`
into that copy (seen in the staged copy only; worth a look).

**Carried over, unchanged:** `data/` stays out of reach of every
DeepSeek plan; ask before any run that reads polygons; ask before every
DeepSeek call; the going-public question is a leaning, not a decision.

**Next free deviation number: D97.** The frozen plan's deviations log
is at row 19.

## Part 2 · Prompt for session 12

```text
Session 12 for hydrowhiplash-elnino26: the owner's wording on session
11's drafts, the DeepSeek pilot, and readiness for the hard-line item.

1. Orient: read CLAUDE.md, docs/session12_kickoff.md, logs/2026-10-12.md
   (the session 11 block), the top of DECISIONS.md (2026-10-12 session
   11 entries), docs/plan_deviations.md D93-D96,
   docs/post_results_protocol.md, site/methods.qmd, site/index.qmd,
   site/tracker.qmd, results/tables/rollout_calendar.json,
   ANALYSIS_PLAN.md (frozen: never edit above the deviations log) and
   ACTION_PLAN.md Phases 4 and 5 and "Second goal".
   Read with the Artifact tool (action "read"):
   the roadmap, https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D97.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is 4 November 2026 or later, read the hard-line item in Part 1
   (item 4) before anything else, and tell me what the reminder found.

5. Build the site and look at it in the browser: the four headline
   charts, the Plotly season history, light and dark. Tell me what you
   see before changing anything.

6. Then the list "Yours to word or decide": put each to me briefly, with
   a recommendation where you have one. My prose is mine to write:
   suggest, don't rewrite.

7. Then the work list in Part 1, in order. Ask me before any run that
   reads polygons, and before every DeepSeek call. Flag scope additions
   rather than building them.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   python scripts/check_site.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild
   the results page and the methods reading copy if they changed, update
   the roadmap artifact, and write the next kickoff the same way.
```
