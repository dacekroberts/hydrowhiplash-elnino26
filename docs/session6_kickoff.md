# Session 6 kickoff: Phase 3, fire data

Written at the end of session 5 (2026-10-06 23:15 to 2026-10-07 15:25, main
checkout; main at e08cb16 or later). Part 1 is the handoff: the state the
next session starts from. Part 2 is the prompt to paste into a new Claude
Code session in the main checkout.

## Part 1 · Handoff

**Where things stand.**

- **`ANALYSIS_PLAN.md` is frozen**: commit acf7a80, 2026-10-07 13:35
  (UTC-07:00), annotated tag `analysis-plan-frozen`, pushed. No fire data
  had been downloaded or opened. The text above its deviations log must
  never change again; any change to a registered test is a dated row in
  that log, mirrored in `docs/plan_deviations.md`.
- **Two post-freeze rows are already in the plan's deviations log**, both
  decided before any fire data:
  1. `ERA5_LAG_MONTHS` 3 to 1 at the first tracker update (D55).
  2. BC, AB and YT fire tests use seasons 1984-2024, the other regions
     1984-2025; H4 pooled 1984-2024; CNFDB 2025 reported beside the results
     when released, never substituted (D57; config `CNFDB_LAST_YEAR`,
     `FIRE_LAST_YEAR_BY_REGION`, `POOLED_LAST_YEAR`).
- **Audits before the freeze:** a targeted audit
  (`docs/audit_2026-10-07_prefreeze.md`) and two fix reviews
  (`docs/audit_2026-10-07_fixreview.md`, `..._fixreview2.md`), all cold
  read-only sessions; nothing high by the last round. Changes from them:
  SPEI as in the R SPEI reference (summed monthly amounts, constant
  0.01792; D49; both domains refit), snowy-year station dedupe with
  shared-row priority (18 pairs), and the plan's execution choices closed
  (D50, D52, D53; trend-only baseline and skill score added, descriptive).
- **Fire licences read** (PR #21): MTBS public domain (notice 8); WFIGS
  freely accessible, its disclaimer travels with the data (notice 9);
  CNFDB OGL-Canada 2.0 with citation and licence link (notice 10). NBAC
  read too (PR #22, notice 11, used only if NBAC is ever used; it is not).
- **Tracker:** `TRACKER_WINDOW` 2026-10-01 to 2027-04-30,
  `TRACKER_DATA_DAY` 7, `TRACKER_FREEZE_DATE` 2026-10-07. ERA5-Land monthly
  means arrive within about a week (CDS probe, 2026-10-07: September 2026
  already out).
- Deviations: up to D57. Main numbers its own from D58.

**Hard-line item (early November 2026, the first tracker update; ACTION_PLAN
Phase 5, D55):** set `ERA5_LAG_MONTHS` from 3 to 1 in `src/config.py`,
download every published 2026 month (both domains, both variable sets),
refit SPEI (about 55 min) and rebuild the tables, figures and notebooks,
report the changed numbers (2026's summer values fill in; no registered test
changes), and recheck `TRACKER_DATA_DAY` against when October's data
appeared. Already logged in the frozen plan's deviations table.

**Phase 3 notes from the licence reads.**

- WFIGS perimeters start in 2021, so the MTBS-to-WFIGS cutover cannot be
  earlier; fix the cutover year at download and record it; compare the last
  overlapping year as the plan says.
- Alaska is not named in the WFIGS description: confirm its coverage at
  download.
- MTBS and WFIGS both hold prescribed fires; the WFIGS fields have no coded
  values, so the filter is written explicitly (the plan keeps Wildfire,
  Wildland Fire Use and Unknown).
- CNFDB to 2024 for BC, AB and YT; read its release PDFs and update log at
  download (date fields: report versus start date, pre-1972 split).
- Every dataset gets a download script in `src/`, its version and access
  date in `DATA_SOURCES.md`, area only via `src.geo.area_ha`, the 405 ha
  floor on each whole fire before clipping.

**Pre-results audit gate (Phase 4, D51):** the statistics code the plan
needs but `src/stats.py` lacks (one-sided p, `use_t`, Driscoll-Kraay with
df = years - 1, the H4 contrast and F test, expanding window with the
trend-only skill score, zero-fire indicators, the family runner) and the
unbuilt variables (`temp_jja`, `temp_mam`, `precip_anom`) are built and
tested on synthetic data, then audited read-only, before anything runs on
the fire table. When that work starts, raise the Claude Code Project
decision (memory note).

**Stale wording left as written (owner's prose; logged):** as in session 5's
kickoff (D9, D41-D43, D45, D48), plus D54 (superseded by D55) and D56
(settled by D57). The plan's precedence sentence covers the frozen text.

**Flagged, not done.**

- A labelled exploratory NBAC re-run of the Canadian tests (1986-2025):
  scope, not decided.
- Possible descriptive check with the NOAA NCEI Interior Alaska boundary in
  Phase 4 (scope; not decided).
- Elevation-matched ERA5-Land comparison: scope addition, not approved.
- Site coordinates in `dedupe_sites` come from an ID's first row (known
  limitation, register).
- Roadmap artifact: offered for update at the end of session 5.

## Part 2 · Prompt for session 6

Paste everything below into a new Claude Code session in the main checkout.

```text
Session 6 for hydrowhiplash-elnino26: Phase 3, fire data.

1. Orient: read CLAUDE.md, docs/session6_kickoff.md (Part 1), the latest log
   in logs/ ("Next" and the session 5 block), ANALYSIS_PLAN.md's
   "Execution details", "Data rules" and deviations log (frozen: never edit
   above the log), DATA_SOURCES.md's MTBS, WFIGS and CNFDB rows, D54-D57 in
   docs/plan_deviations.md and the top of DECISIONS.md. Then read the
   roadmap artifact with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D58.

2. Explain each data type and concept as it comes up, and give a short
   summary beside every hypothesis ID (memory notes).

3. If it is early November or later, do the hard-line item in Part 1 first
   (ERA5_LAG_MONTHS 3 to 1, download, SPEI refit, report changed numbers).

4. Phase 3: write download scripts in src/ for MTBS, WFIGS (from 2021) and
   CNFDB (to 2024), record versions and access dates in DATA_SOURCES.md,
   fix the MTBS-to-WFIGS cutover year at download, confirm Alaska in
   WFIGS, filter prescribed fires explicitly, then clip to regions with the
   405 ha floor on each whole fire (area only via src.geo.area_ha) and
   build the region x year burned-area table (both table locations) with
   season length and ENSO phase. Record every rule and count in
   docs/methods_register.md. No hypothesis test is run in this phase.

5. Side PRs, if any are open: pre-screen and merge only with the
   merge-side-pr skill and my yes.

6. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push; refresh the data
   guide artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and
   offer to update the roadmap artifact; write the next kickoff the same
   way.
```
