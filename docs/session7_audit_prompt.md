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
