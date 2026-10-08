# Pre-results audit, round 1 · prompt

Written in session 7 (2026-10-08) for the D51 pre-results audit gate,
extended to the fire build by D62 and run in rounds by D64. Paste the block
below into a new Claude Code session in the main checkout. Later rounds
reuse it with the commit range and the previous reports added.

```text
Cold, read-only audit of hydrowhiplash-elnino26 at commit 6e79757 (main
checkout). You did not write any of this code. Find what is wrong, not
what is right.

Rules for this session:
- Read-only. Do not edit, create or delete anything inside the repository,
  do not change git state, and do not run any `src` module's main (several
  write tables). Scratch scripts and outputs go in your own scratchpad
  only. Import `src` functions from scratch scripts as needed.
- No hypothesis test on fire data: do not compute any registered test, or
  any statistic relating burned area to ENSO, on the real fire tables.
  Never print, plot or summarise burned area beside any ENSO column
  (`enso_djf`, `phase`, `strong`); when reading the fire tables, select
  columns without them. Synthetic data is unrestricted.
- Do not re-download anything. `python -m src.pin_inputs --verify` checks
  the inputs; run it at the start and the end.
- Run commands with
  C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash --no-capture-output python ...
  from the repo root (multi-line Python goes in a script file).

Read first: CLAUDE.md; ANALYSIS_PLAN.md in full (frozen at tag
analysis-plan-frozen; its deviations log at the bottom lists every later
change); ACTION_PLAN.md Phase 3 and Phase 4; docs/methods_register.md
"Statistics" and "Fire"; docs/data_dictionary.md sections 4d, 5 and 8;
docs/plan_deviations.md D51 and D55-D65; DECISIONS.md entries dated
2026-10-07 and 2026-10-08; docs/session7_kickoff.md Part 1 (the list of
eleven software traps).

Scope:
1. Statistics code: src/stats.py, src/climate_vars.py, src/pin_inputs.py,
   scripts/stats_size_check.py, their tests (tests/test_stats.py,
   tests/test_stats_gate.py, tests/test_climate_vars.py,
   tests/test_pin_inputs.py) and the settings they read in src/config.py.
   For every registered test and robustness run in ANALYSIS_PLAN.md
   (H1-H6, C1-C2, H4's contrast and joint test, zero-fire sensitivity,
   expanding window and skill score, strong-only and ONI runs,
   frozen-rules run, Holm/BH families): can it be computed exactly as the
   plan states with these functions, and would the result be right?
   Check degrees of freedom, sidedness, reference levels, formula terms,
   year alignment and lags, missing-value handling, sorting, seeds and
   correction families against the plan and against independent
   calculations of your own. Judge whether the tests' known-answer checks
   would catch the errors they claim to, and whether the tests have their
   nominal size on data shaped like this project's (about 41 seasons,
   5-7 regions, possibly autocorrelated).
2. Built variables: temp_jja, temp_mam, precip_octmar_mm,
   precip_anom_lag0/lag1 in results/tables/climate_controls_region_year.csv.
   Recompute some independently from the raw ERA5-Land files
   (data/raw/era5_land*, units in docs/data_dictionary.md section 2) and
   compare.
3. Fire build: src/fire.py, src/download_mtbs.py, src/download_wfigs.py,
   src/download_cnfdb.py, results/tables/fire_region_year.csv and
   results/tables/fire_region_year_frozen_rules.csv,
   data/processed/fire_events.csv. Does each rule match the frozen plan as
   amended by its deviations log rows 3-6 (D58-D62)? Do the counts in the
   methods register's "Fire" section reproduce? Is the frozen-rules
   variant the variant D62 describes? Any defect in reading, filtering,
   dating, clipping, area measurement, season assignment, union, or the
   table? You may rebuild parts in your scratchpad from the raw downloads
   (a full rebuild takes about 25 minutes).
4. Records: do the code, config, methods register, data dictionary and
   plan agree? Anything stale, missing or contradictory?

Report (plain markdown) to save unchanged as a file: for each finding an
ID, severity (high = a registered result or a fire table would be wrong
or not computable as registered; medium = a likely error, an untested
path or a misleading record; low = clarity or hygiene), the evidence
(file:line, commands and numbers you ran), and a suggested fix. Then what
you checked that passed, and what you could not check. Start the report
with the commit audited and the date. End with `python -m src.pin_inputs
--verify` and `git status` output, both before and after.
```

## Round 2 · prompt

Written after round 1 was settled (`docs/audit_2026-10-08_preresults_round1.md`;
fixes in 32e8d42; DECISIONS 2026-10-08 "Audit round 1 settled"; D66).

```text
Cold, read-only review, round 2 of the pre-results audit of
hydrowhiplash-elnino26, main checkout at commit 32e8d42. You did not
write any of this code and did not take part in round 1. Find what is
wrong, not what is right.

Rules for this session:
- Read-only. Do not edit, create or delete anything inside the repository,
  do not change git state, and do not run any `src` module's main (several
  write tables). Scratch scripts, outputs and your report go in your own
  scratchpad only; the main session copies the report into docs/.
- No hypothesis test on fire data: do not compute any registered test, or
  any statistic relating burned area to ENSO, on the real fire tables.
  Never print, plot or summarise burned area beside any ENSO column
  (`enso_djf`, `phase`, `strong`); when reading the fire tables, select
  columns without them. Synthetic data is unrestricted.
- Do not re-download anything. Run `python -m src.pin_inputs --verify` at
  the start and the end.
- Run commands with
  C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash --no-capture-output python ...
  from the repo root (multi-line Python goes in a script file).

Read first: CLAUDE.md; ANALYSIS_PLAN.md in full (frozen at tag
analysis-plan-frozen; its deviations log lists every later change);
ACTION_PLAN.md Phases 3-4; docs/audit_2026-10-08_preresults_round1.md;
DECISIONS.md entries dated 2026-10-07 and 2026-10-08;
docs/plan_deviations.md D51 and D55-D66; docs/methods_register.md
"Statistics" and "Fire"; docs/data_dictionary.md sections 4d, 5 and 8;
docs/session7_kickoff.md Part 1 (eleven software traps).

Scope:
1. The fixes: `git diff 6e79757..32e8d42`. Does each settled round 1
   finding (M1-M4, L1-L11) do what its DECISIONS entry says, correctly,
   with nothing broken around it? In particular: the CNFDB dissolve in
   src/fire.py (grouping key, blank ids, the attributes a merged fire
   keeps, effect on dates, season assignment, the floor and both fire
   tables; the before-and-after numbers in the register); the size checks
   (fit_ols_plain, block_bootstrap_p, scripts/stats_size_check.py) and
   whether the measured sizes and the keep or drop calls in D66 hold up
   on your own simulations; the new helpers (strong_flags, center_year,
   percent_change, lag1_autocorrelation, ols_prediction).
2. The whole gate again, as round 1 scoped it: for every registered test
   and reported run in ANALYSIS_PLAN.md and its deviations log (H1-H6,
   C1-C2, H4 contrast and joint test, zero-fire sensitivity, expanding
   window and skill score, strong-only and the near-threshold flip, ONI
   runs, frozen-rules run, size labels and checks, Holm/BH families), can
   it be computed exactly as stated with these functions, and would the
   result be right? Check against independent calculations of your own.
3. Built variables and fire tables: results/tables/climate_controls_region_year.csv
   (including precip_djf_mm), results/tables/fire_region_year.csv,
   results/tables/fire_region_year_frozen_rules.csv,
   data/processed/fire_events.csv; reproduce parts from the raw downloads.
4. Nulls and placeholders: for every field the pipeline filters, dates
   or fills on (all sources, all tables, geometry), find any row dropped,
   filled or misread silently because of a null, a placeholder value
   (e.g. -9999, 0, blank, a fixed date) or an empty or invalid geometry.
   Compare with the register's "Null and placeholder sweep" row.
5. Records: do code, config, register, data dictionary, plan deviations
   and DECISIONS agree? Anything stale, missing or contradictory?

Report (plain markdown, saved in your scratchpad and sent to the owner):
start with the commit reviewed, the date and the model you ran on; then
for each finding an ID, severity (high = a registered result or a fire
table would be wrong or not computable as registered; medium = a likely
error, an untested path or a misleading record; low = clarity or
hygiene), the evidence (file:line, commands and numbers you ran) and a
suggested fix; then what you checked that passed and what you could not
check. End with `python -m src.pin_inputs --verify` and `git status`
output, both before and after.
```

## Round 3 · prompt

Written after round 2 was settled (`docs/audit_2026-10-08_preresults_round2.md`;
fixes in 309de6a; DECISIONS 2026-10-08 "Audit round 2 settled"; D67, D68).

```text
Cold, read-only review, round 3 of the pre-results audit of
hydrowhiplash-elnino26, main checkout at commit 309de6a. You did not
write any of this code and did not take part in rounds 1 or 2. Find what
is wrong, not what is right.

Rules for this session:
- Read-only. Do not edit, create or delete anything inside the repository,
  do not change git state, and do not run any `src` module's main (several
  write tables or download). Scratch scripts, outputs and your report go
  in your own scratchpad only; the main session copies the report into
  docs/.
- No hypothesis test on fire data: do not compute any registered test, or
  any statistic relating burned area to ENSO, on the real fire tables.
  Never print, plot or summarise burned area beside any ENSO column
  (`enso_djf`, `phase`, `strong`); when reading the fire tables, select
  columns without them. Synthetic data is unrestricted.
- Do not re-download anything. Run `python -m src.pin_inputs --verify` at
  the start and the end. data/raw/fire/nbac/ (NBAC, downloaded for
  exploratory checks) is outside this review's scope; do not open it.
- Run commands with
  C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash --no-capture-output python ...
  from the repo root (multi-line Python goes in a script file).

Read first: CLAUDE.md; ANALYSIS_PLAN.md in full (frozen at tag
analysis-plan-frozen; its deviations log lists every later change);
ACTION_PLAN.md Phases 3-4; docs/audit_2026-10-08_preresults_round1.md and
docs/audit_2026-10-08_preresults_round2.md; DECISIONS.md entries dated
2026-10-08; docs/plan_deviations.md D62 and D65-D68;
docs/methods_register.md "Statistics" and "Fire"; docs/data_dictionary.md
sections 5 and 8.

Scope:
1. The fixes: `git diff 32e8d42..309de6a`. Does each settled round 2
   finding (H1, M1, L1-L7) do what DECISIONS "Audit round 2 settled",
   D67 and D68 say, correctly, with nothing broken around it? In
   particular: `merge_components` and `dissolve_cnfdb` in src/fire.py
   (the distance rule, chaining, the CRS the distance is measured in,
   invalid geometries, split groups keeping their own attributes, the
   attributes a merged fire keeps, effect on dates, seasons, the floor
   and both fire tables); recompute the merged groups from the raw CNFDB
   download independently and check the before-and-after numbers in the
   register and D67 against the committed tables at 6e79757, 32e8d42 and
   309de6a; the size table (scripts/stats_size_check.py,
   results/tables/test_size.csv): are the shapes the right stand-ins for
   the tests they label, and do the numbers hold on your own
   simulations?; lag1_autocorrelation; the strengthened tests.
2. Anything the round 2 fix could have broken elsewhere in the gate
   (statistics code, fire build, pins) and anything rounds 1 and 2 missed
   that you find on the way.
3. Records: do code, config, register, data dictionary, plan deviations,
   the plan's deviations log and DECISIONS agree? Anything stale, missing
   or contradictory?

Report (plain markdown, saved in your scratchpad and sent to the owner):
start with the commit reviewed, the date and the model you ran on; then
for each finding an ID, severity (high = a registered result or a fire
table would be wrong or not computable as registered; medium = a likely
error, an untested path or a misleading record; low = clarity or
hygiene), the evidence (file:line, commands and numbers you ran) and a
suggested fix; then what you checked that passed and what you could not
check. End with `python -m src.pin_inputs --verify` and `git status`
output, both before and after.
```
