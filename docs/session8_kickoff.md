# Session 8 kickoff: Phase 4, before the first hypothesis test

Written at the end of session 7 (2026-10-08). Part 1 is the handoff; Part 2
is the prompt to paste into a new Claude Code session in the main checkout.

## Part 1 · Handoff

**Where things stand.**

- The pre-results audit gate (D51, in rounds by D64) ran five cold rounds on
  2026-10-08, all on Fable 5.1, read-only, reports saved unchanged in
  `docs/audit_2026-10-08_preresults_round1.md` to `round5.md`. Round 5
  found no high and no medium (6 low, fixed), which meets the owner's
  standard, so **the gate closed on round 5**: tag
  `pre-results-gate-closed` (DECISIONS 2026-10-08 "Audit round 5 settled;
  pre-results gate closed").
- Built in session 7: the gate's statistics code (`src/stats.py`), the
  climate controls (`src/climate_vars.py`), the frozen-rules fire table
  (D62), input pins by name (`src/pin_inputs.py`, `assert_pinned` for the
  hypothesis loaders), the size table (`results/tables/test_size.csv`),
  the Parks Canada sensitivity table (`src/parks_gap.py`, D69) and the NBAC
  download (`src/download_nbac.py`, release v20260513).
- Decisions in session 7: D65 (small-sample correction on everywhere), D66
  (size labels; plain OLS check where its size is near 5%), D67 (CNFDB
  parts merged only within 1 km), D68 (no plain OLS check for the H4
  contrast), D69 (AB 2016-2019 flagged; NBAC park area sensitivity run),
  D70 and D71 (record corrections; defence lands a stated limitation),
  D72 (corrections to D71), D73 (registered runs committed by 2026-11-06;
  runner safeguards before the first run), D74 (site methods flowchart).
- No hypothesis test has run on fire data, and no view has set burned
  area beside ENSO.

**Decide before the first hypothesis test (owner, 2026-10-08).** No
hypothesis test runs while either is open:

1. **Exploratory NBAC re-run of the Canadian tests.** NBAC vs CNFDB,
   1986-2024 (NBAC by calendar year, CNFDB by season window): log-series
   correlation BC 0.990, AB 0.994, YT 0.997; NBAC totals 84%, 94%, 91% of
   CNFDB; seasons differing by more than 0.25 in log_burn BC 11, AB 9, YT 4
   of 39. A re-run needs its own date rule (NBAC has no ignition date).
   F1 (`scripts/nbac_coverage.py`, run 2026-10-08, about 90 minutes;
   `data/processed/nbac_coverage.csv`): NBAC fire area (>= 405 ha) with no
   same-YEAR CNFDB polygon under it, 1984-2024: AB 7.7%, BC 6.2%, YT 6.9%.
   Under the provincial labels AB 393,140 ha (4.8%), BC 501,894 ha (6.1%),
   YT 430,841 ha (6.8%); Wood Buffalo 303,904 of 2,078,447 ha (14.6%; the
   2016-2019 gap is about 175,000 of it); defence lands 109,773 ha (100%,
   D71). Seasons over 20% uncovered: AB 1986, 1991, 2000, 2001, 2005-2007,
   2013, 2017, 2018, 2020; BC 1985, 1986, 1989, 1991, 1992, 1996, 1998-2000;
   YT 1986, 2000, 2019 (88,243 ha, 33%). Not yet split into edge slivers
   (two perimeter products disagreeing at a fire's edge) vs whole fires
   CNFDB lacks or files under another YEAR: a per-fire breakdown is the
   first step if the re-run is considered. Round 5 L6 measured the rim
   floor on AB 2011, 2015 and 2019: 0.3-1.2% of a season's NBAC area, so
   AB's provincial 4.8% is well above it and some seasons (likely
   2005-2007) may hold whole fires CNFDB lacks; split per fire at an
   uncovered share above 0.5 (missing) vs below (rim).
2. **NOAA NCEI Interior Alaska check** (climate only; boundary licence
   read and a download script first).

**Deadline: the registered runs computed and committed by Friday
2026-11-06** (D73), the day before October's ERA5-Land data is expected
(`TRACKER_DATA_DAY` 7) and the first tracker update can touch a pinned
input. If missed: only the climate tables re-pinned, logged, and only if
every value a registered test reads is identical.

**Before the first run (D73, audit round 5):** write the protocol for
changes after results (S6) first, then build the rebuild guard and re-pin
log (S2), `pin_inputs.load_input` (S3), `scripts/check_plan_frozen.py` and
a preflight (S4), a provenance record beside every result (S5), and wire
the size labels from `test_size.csv`; tests, then a short cold check of
that code. Ask the owner where the offline copy of the 30 pinned inputs
(3.38 GB) goes (S1).

**Record check:** the register's "Union area" row gives WFIGS overlap
79,443 ha, but the table's 291 seasons hold 52,834 for WFIGS (100,813 in
all, which matches the row's by-region list); likely 2026 WFIGS seasons
outside the table. Confirm and word it.

**Then the Claude Code Project go/no-go (D63),** for running H1-H6 and the
site pages as parallel threads (`docs/claude_code_project_setup.md`).

**Housekeeping (owner, 2026-10-08):** compare `side/fire-licence-reads`
(3 commits) and `side/nbac-probe` (1 commit) with main; delete each branch
whose content is fully absorbed (likely squash-merged), and report any
difference first.

**Site methods flowchart (owner, 2026-10-08; scope addition, ACTION_PLAN
"Second goal" item and DECISIONS entry written at the end of session 7):**
a plain-language flowchart for `site/methods.qmd` (sources, derived
variables, region x year table, pre-registered tests, site charts), built
in code like the mechanism diagram. Needs no data, so a worktree session
can take it.

**Hard-line item (early November 2026, ACTION_PLAN Phase 5, D55):** as in
the session 7 kickoff; do it first if the date has come.

**Portfolio review handoff (added 2026-10-11; DECISIONS 2026-10-11
"Portfolio review handoff"):** nothing from it starts before the
registered runs are committed. Noted for later:

- After the runs: add three methods-page items to ACTION_PLAN's "Second
  goal" as one scope addition (next free deviation number, markers): why
  regression and not a trained ML model, a responsibility statement, where
  coverage is thin. Drafts for the owner to word.
- When the owner brings them: the tone guide (about 2026-11-07 onward),
  a "system map" section in `CLAUDE.md`, the glossary export.
- Shared machine memory is 32 GB and another project's batch runs in the
  week of 2026-10-12; the owner handles it as needed. Say so before a run
  that reads polygons (NBAC, WFIGS).
- No task goes to the DeepSeek worker until the owner says its
  integration is finished.
- Still open, ask the owner: whether the 2026-11-06 commit also covers
  the runs reported beside the registered tests (ONI robustness,
  frozen-rules, Parks Canada sensitivity, strong-only); whether
  historical results go public in November and the forecast in spring
  2027; when to check the licence verdicts for commercial-use terms
  before any tip link.

**Known limits, recorded (register):** CNFDB `YEAR` = -9999 polygons (M2 of
round 1); defence lands in AB (D71); Parks Canada gap in BC and YT (under
1%); NBAC park area more likely low than high (round 4 F3); AB 2020 and
1991 as leverage seasons (round 4 F2).

## Part 2 · Prompt for session 8

```text
Session 8 for hydrowhiplash-elnino26: Phase 4, from the closed gate to
the first hypothesis test.

1. Orient: read CLAUDE.md, docs/session8_kickoff.md (Part 1), the session
   7 blocks in logs/2026-10-08.md, the top of DECISIONS.md (2026-10-08
   entries), docs/plan_deviations.md D65-D74, ANALYSIS_PLAN.md (frozen:
   never edit above the deviations log) and ACTION_PLAN.md Phase 4. Read
   the roadmap artifact with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D75.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. If it is early November or later, do the hard-line item first.

4. Bring me the two decide-before-any-test items with their numbers (NBAC
   re-run, with F1's coverage figures and a per-fire split against the
   rim floor; Interior Alaska check, measured for its worth within the
   session 7 limits). Nothing is adopted without my yes, and no hypothesis
   test runs while either is open.

5. Then the Claude Code Project go/no-go (D63).

6. Housekeeping: compare side/fire-licence-reads and side/nbac-probe with
   main and delete each if fully absorbed; report differences first.

7. Side-session candidate: the site methods flowchart (Part 1); it needs
   no data, so it suits a worktree session.

8. Before the first run: write the post-results change protocol (S6),
   then build the runner safeguards S2-S5 with tests, and a short cold
   check of that code. Then plan the first hypothesis runs with me
   (tables only through pin_inputs.load_input; size labels from
   results/tables/test_size.csv; effect sizes and CIs before p-values).
   Deadline: registered runs committed by Friday 2026-11-06 (D73).

9. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push; refresh the data
   guide artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and
   offer to update the roadmap artifact; write the next kickoff the same
   way.
```
