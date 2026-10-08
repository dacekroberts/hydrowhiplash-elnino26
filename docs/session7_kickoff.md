# Session 7 kickoff: Phase 4, pre-results audit gate

Written at the end of session 6 (2026-10-07 15:35-21:00, main checkout;
main at 2184cdf or later). Part 1 is the handoff: the state the next
session starts from. Part 2 is the prompt to paste into a new Claude Code
session in the main checkout.

## Part 1 · Handoff

**Where things stand.**

- **Phase 3 is done.** `results/tables/fire_region_year.csv` (291 rows:
  PNW, AK, NorCal, SoCal 1984-2025; BC, AB, YT 1984-2024) with `burn_ha`
  (union area), `log_burn`, `n_fires`, `season_days`, flags and the ENSO
  columns; `data/processed/fire_events.csv` (one row per fire-region
  piece, not committed). Built by `python -m src.fire` (about 25 min) from
  `src.download_mtbs`, `src.download_wfigs`, `src.download_cnfdb` (versions
  and access dates in `DATA_SOURCES.md`). Every rule and count:
  `docs/methods_register.md` "Fire".
- **Fire data has been opened.** Attribute profiles, MTBS counts and acres
  by state and year, MTBS-WFIGS comparisons by region for 2021-2024, and
  once (a sanity printout) 2023-2025 burned area beside the ENSO phase. No
  hypothesis test has run.
- **Post-freeze fire rules, all in the frozen plan's deviations log (rows
  3-6), each stating what had been seen:** MTBS "Other" read as "Unknown"
  (D58); CNFDB fires without month counted by YEAR (D59); MTBS for
  ignitions through 2023, WFIGS from 2024, union area per region, season
  and source, and the source-agreement rule re-run on 2023 (D60, D61; it
  passed, |d| at most 0.032, so the frozen years stand); a frozen-rules
  robustness run (D62). Text above the log identical to the tag
  `analysis-plan-frozen` (checked 2026-10-07).
- **The firm line on fire rules (D62, `ACTION_PLAN.md` Phase 4):**

  > The same audit also reviews the fire build (`src/fire.py`, the
  > download scripts and `results/tables/fire_region_year.csv`); until it
  > closes, a fire record rule changes only for a defect a check finds,
  > logged with before-and-after numbers, and after it, before the first
  > test, only bug fixes. No view that sets burned area beside ENSO until
  > Phase 4 [mid-project: D62].

- Deviations: up to D64. Main numbers its own from D65.
- pytest 232 passed.

**Phase 4 starts with the pre-results audit gate (D51):**

> **Pre-results audit gate** [mid-project: D51]: every piece of statistics
> code the plan needs but `src/stats.py` lacks at the freeze (one-sided
> p-values, `use_t`, Driscoll-Kraay errors with df = years - 1, the H4
> contrast and its F test, expanding-window validation, zero-fire
> indicators, the Holm/BH family runner) and every variable not yet built
> (`temp_jja`, `temp_mam`, `precip_anom`) is built and tested on synthetic
> data with known answers first, then checked by a read-only audit with a
> neutral prompt, before any of it runs on the fire table. No hypothesis
> result is computed until that audit's findings are settled.

Also needed for the tests: `burn_detr` (residuals of `log_burn ~ year`
per region, permutation and bootstrap tests) and the frozen-rules variant
table (D62: summed area, MTBS Other dropped, undated CNFDB dropped, the
frozen years). The Claude Code Project is decided after the audit (owner,
2026-10-08, D63): the gate's code is built in the main session, and the
go/no-go is for the hypothesis runs that follow.

**Owner's go-ahead (2026-10-08):** the gate's steps as explained at the end
of session 6 (synthetic-data tests of the statistics code, the four
variables, the D62 frozen-rules table) agreed; the audit runs in rounds
until one finds nothing high (D64); the Claude Code Project is decided
after the last round (D63); the test plan (step 6: every registered test,
the robustness layer, validation and the 2027 forecast) agreed.

**Traps the gate code must test** (probed on statsmodels 0.15.0, scipy
1.18.1, numpy 2.5.3, 2026-10-08, toy data; beyond those already in the
register; owner, 2026-10-08: address all eleven):

1. Driscoll-Kraay df reaches the tests too: `wald_test(use_f=True)` gave
   F(4, 4) and `t_test` df 4 on a 5-region, 41-year panel, not 40.
   Compute the H4 contrast t and the F statistic from the fit and take p
   from `scipy.stats` with df = years - 1; check against a hand
   calculation.
2. `C(region)` takes AB as the reference (alphabetical). H4 needs
   `Treatment(reference="SoCal")`; test the coefficient names.
3. HAC `use_correction` is False by default (no n/(n - k) correction);
   the frozen plan is silent. **Decide before any result** (lean: off, the
   default) and log it in the plan's deviations log as an execution
   detail.
4. The formula API drops rows with a missing value silently (41 rows to
   40); `fit_ols_hac` already refuses gaps, `fit_pooled` does not: make it
   refuse, so H4's panel cannot unbalance.
5. `t_test` p-values are two-sided; one-sided p from the t statistic in
   the stated direction.
6. pandas `std` is ddof 1, numpy's ddof 0 (1.528 vs 1.247): one z-score
   helper with ddof = 1.
7. Pin the inputs: RONI is revised monthly and WFIGS is live; run the
   tests on the committed tables and the downloads of 2026-10-07, record
   checksums, no re-download until results are in.
8. Expanding-window leakage: the 1991-2020 normals and the 1951-2020 SPEI
   calibration include later years (frozen; state as a limitation).
9. Strong-only bootstrap within 3 winters has 10 distinct resamples
   (exploratory; show the CI's coarseness).
10. Permutation tests assume exchangeable years; burned area is
    autocorrelated (methods note; the block bootstrap is the check).
11. One seed (2026) for every call: all regions share permutation draws
    (methods note).

Checked and harmless: Driscoll-Kraay `time` as raw years or 0-based gives
the same SE.

**Investigate before deciding (owner, 2026-10-08):** the Parks Canada gap
and the exploratory checks are measured for their worth to the final
product first, then decided. Limits for every one: no hypothesis test; no
view that sets burned area beside ENSO (D62); the frozen plan text
untouched; a fire rule changes only if the check finds a defect, before
the audit closes, with before-and-after numbers (D62); anything adopted is
a scope decision by the owner, labelled exploratory and logged as an added
reported analysis; a new dataset gets its licence read first. These need
`data/`, so they run in the main checkout, after the gate code or in
session 8.

1. **Parks Canada 2018-2020 gap.** Do the BC, AB and YT agency polygons
   cover fires inside national parks in 2018-2020 (spatial check against
   park boundaries)? What share of each Canadian region's burned area do
   Parks Canada polygons hold in 2010-2017 and 2021-2024 (fire only)? If
   the share is small, the gap stays a stated limitation; if large (Wood
   Buffalo in AB is the likely case), weigh a flag or a sensitivity run.
   Park boundaries: the CNFDB Parks Canada footprints, or a national-park
   boundary dataset after its licence read.
2. **Exploratory NBAC re-run of the Canadian tests.** Its worth depends on
   how NBAC and CNFDB differ region by region: download NBAC (licence and
   documentation already read, `docs/nbac_probe.md`, notice 11) and compare
   region-season totals with CNFDB, 1986-2024, fire only. A re-run says
   something only where they differ; it would also show the 2025 season.
3. **NOAA NCEI Interior Alaska check.** Does Alaska's climate signal change
   when the region is cut to the Interior, where most of its fire burns?
   Climate only: compare Interior and whole-Alaska DJF and JJA series
   (no fire-ENSO join); boundary licence read and a download script first.

**Hard-line item (early November 2026, the first tracker update; ACTION_PLAN
Phase 5, D55):** set `ERA5_LAG_MONTHS` from 3 to 1, download every published
2026 month (both domains, both variable sets), refit SPEI (about 55 min),
rebuild tables, figures and notebooks, report the changed numbers, recheck
`TRACKER_DATA_DAY`. Check the row's promise: every 1951-2025 value in the
committed climate tables (SPEI, whiplash, winter SPEI-3) must come out
identical, with only 2026's summer values new. If it holds, no new plan
row (a DECISIONS "applied" entry, the register's lag row re-measured); if
any historical value moves, a new dated row saying it was applied after
fire data was opened, a deviation entry, and the owner decides before any
test uses it (owner, 2026-10-08).

**Known limits, not handled (register):**

- Parks Canada sent no polygons for 2018-2020: fires inside national
  parks (Wood Buffalo, Jasper, Banff, Kluane) missing in those years unless
  the province mapped them; not measured.
- The CNFDB documentation PDF still names a pre-2022 End-User Agreement
  (internal use only); the catalogue and ISO records name OGL-Canada only.
  Read as superseded; recheck before publishing.
- `fire.py` reads WFIGS geometry only from 2023 (UTC year); fine for the
  current rules, re-measure if the cutover or check year moves earlier.

**Stale wording left as written (owner's prose; logged):** as in session
6's kickoff (D9, D41-D43, D45, D48, D54, D56). Today's DECISIONS entry
"Fire record rules settled at download" names the 2025-01-01 cutover,
superseded the same day by D61.

**Flagged, not done.**

- A labelled exploratory NBAC re-run of the Canadian tests: scope, not
  decided.
- Possible NOAA NCEI Interior Alaska check in Phase 4: scope, not decided.
- Elevation-matched ERA5-Land comparison: scope, not approved.
- Roadmap artifact: offered for update at the end of session 6.

## Part 2 · Prompt for session 7

Paste everything below into a new Claude Code session in the main checkout.

```text
Session 7 for hydrowhiplash-elnino26: Phase 4, pre-results audit gate.

1. Orient: read CLAUDE.md, docs/session7_kickoff.md (Part 1), the latest log
   in logs/ ("Next" and the session 6 block), ANALYSIS_PLAN.md (frozen:
   never edit above the deviations log), ACTION_PLAN.md Phase 4,
   docs/methods_register.md "Fire" and "Statistics", D58-D62 in
   docs/plan_deviations.md, src/stats.py and the top of DECISIONS.md.
   Then read the roadmap artifact with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D65.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. If it is early November or later, do the hard-line item in Part 1 first.

4. Build the gate's code here in the main session; the Claude Code Project
   go/no-go comes after the audit (D63), for the hypothesis runs.

5. Build and test on synthetic data with known answers, before anything
   runs on the fire table: one-sided p, use_t, Driscoll-Kraay with
   df = years - 1, the H4 contrast and F test, expanding window with the
   trend-only skill score, zero-fire indicators, the Holm/BH family
   runner, burn_detr, temp_jja, temp_mam, precip_anom, and the D62
   frozen-rules fire table. Test every trap in Part 1's list; bring me
   the HAC small-sample correction decision before any result. No hypothesis test runs on fire data, and no
   view sets burned area beside ENSO.

6. Then give me a cold read-only audit prompt covering the statistics code
   and the fire build (D51 extended by D62). The audit runs in rounds
   (D64): settle and fix each round's findings, then a fresh cold review
   of the fixes and the whole gate, until a round finds nothing high and
   I agree. Save every report unchanged in docs/.

7. Side PRs, if any are open: pre-screen and merge only with the
   merge-side-pr skill and my yes.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push; refresh the data
   guide artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and
   offer to update the roadmap artifact; write the next kickoff the same
   way.
```
