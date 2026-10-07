# Decisions

Judgment calls, with the reasoning and the alternatives rejected. Newest
first. Never edit an old entry: add a new one that supersedes it and links
back. Changes to pre-registered tests go in the deviations log in
`ANALYSIS_PLAN.md` instead.

**Entry format:** one bullet per decision. A bold one-sentence statement, then
prose with real numbers, rejected alternatives and affected files. Neutral
past tense ("Decided", "Found", "Dropped"), no first person.

**What qualifies:** judgment calls with rejected alternatives, scope
changes, data sources added or ruled out, bug fixes with numeric
consequences (old and new numbers), superseded decisions, verification runs
with counts. **Not:** copy edits, routine mechanics, open work (that's
`ACTION_PLAN.md`).

## Changes

### 2026-10-07 - Freeze and tracker

- **Froze `ANALYSIS_PLAN.md` (owner's explicit yes)**: commit acf7a80,
  2026-10-07 13:35:38 UTC-07:00, tag `analysis-plan-frozen` (annotated,
  pushed), building on 96a1908; the "Frozen on" line gives the minute
  (owner's request). No fire data had been downloaded or opened anywhere.
  Three audit rounds that day (one prefreeze audit, two fix reviews, the
  last on a whole-plan read) found nothing high by the end.
- **Decided (owner) to keep the Claude Code Project on standby and decide
  when the Phase 4 statistics code starts** (the D51 gate), and to send the
  three fire licence reads (MTBS, WFIGS/NIFC, CNFDB) to the standing side
  session. Rejected setting the Project up at the freeze: its draft
  instructions predate the frozen plan, and the licence reads fit the side
  session's existing rules. The reminder note moved to the statistics
  code.
- **Added the settled tracker settings to `src/config.py`**
  (`TRACKER_WINDOW` 2026-10-01 to 2027-04-30, `TRACKER_FREEZE_DATE`),
  from PR #19's table; verification dates follow `FIRE_SEASON_MONTHS`.
  **Left out the data-arrival dates** (D54): PR #19 assumed monthly data by
  the 6th of the next month (October's data in early November) and flagged
  it as an assumption to measure; the project's own measured lag
  (`ERA5_LAG_MONTHS` = 3) has ERA5-Land monthly means ending in July 2026
  on 2026-10-07, so October would arrive about January. Owner's decision
  pending.

### 2026-10-07 - Second fix review settled

- **Ran a second read-only review in a fresh cold session** (owner's
  choice, "one more just to be safe"; the first review session retired),
  of ee9503d..b9153a4 and the whole `ANALYSIS_PLAN.md` as it would be
  frozen. Report: `docs/audit_2026-10-07_fixreview2.md` (the session's own
  file, line endings normalised). Nothing high; one medium-low open choice,
  eight low items. It confirmed the station outputs byte-identical to
  ee9503d, that each new test fails under the rule it guards against
  (the SC04/SC05 test under the rejected best-row rule), every plan
  setting against `config.py`, and the four dedupe variants' dry-run
  numbers. The owner accepted every recommendation below.
- **Decided (owner) that the ONI robustness runs use ONI's own strong set
  and near-threshold band** (finding 1; D53), by the same rules: within
  0.06 of 1.5 after rounding, 1972-73 1.55, 1991-92 1.54, 2009-10 1.47
  (checked from the cached ONI file); ONI's strong set adds 2023-24 and
  drops 1965-66. Rejected flipping RONI's three winters under ONI (1.24,
  1.18, 1.47 there) and no flip under ONI.
- **Decided (owner) on the strong-only scope** (finding 8): the regions of
  the parent test (H1 the five main regions, H2 all seven), every test
  two-sided and uncorrected, exploratory. Rejected carrying H2's one-sided
  directions to 3 strong seasons.
- **Decided (owner) to report leave-one-year-out coverage for the two
  single-predictor H6 forecasts too** (finding 9), as for H3a.
- **Closed the zero-fire wording gap** (finding 2): a dated pointer on the
  2026-10-05 "Zero-fire years" note to "Execution details", and the
  `ZERO_YEAR_PCT_LIMIT` comment in `config.py`. The precedence sentence
  covers original text against a dated note, not two dated notes.
- **Records** (findings 3-7): the `dedupe_sites` docstring now states the
  tie-break the code uses (shared-row rank, then the ID's best rank, then
  values, then ID) and that site coordinates come from an ID's first row,
  a known limitation left unchanged at the freeze (checking every
  coordinate could find new pairs); register: YT first has 3 stations in
  1968, not 1965 (2 in 1965-67); the strong-only row carries D52 and D53;
  "every headline test" replaced in the register, dictionary and
  `config.py` by every registered test that uses the index.
- **Corrected** "Fix review findings settled" (this date): restricting the
  ONI runs to the four headline methods would have left C1 and C2 without
  the index check, not "C1, C2 and H4's contrast" (H4 is headline method
  3). Season length's dating (ignition) is in the data dictionary, not the
  plan; left (descriptive).

### 2026-10-07 - Fix review findings settled

- **Ran a read-only review of the pre-freeze fixes (97663e5..ee9503d) in a
  cold session with a neutral prompt, on a different model (Fable 5.1)**
  (owner's choice). Report saved as `docs/audit_2026-10-07_fixreview.md`
  (the session's own file, unchanged but for line endings). Nothing high or
  medium; every number recorded at ee9503d reproduced, the SPEI cache again
  the ML optimum, the three D49 claims confirmed against the R source. The
  owner accepted every recommendation below.
- **Fixed the duplicate-site priority for station IDs that mix sources**
  (F1). The review found the priority read from an ID's first row (5
  provincial IDs ranked as CanSWE) and proposed the best source present.
  That rule changed the table: CanSWE files Yukon course 09CA-SC04's
  1978-84 values under SC05, the course that replaced it 15 km away, so
  SC05 ranked as Yukon-file, kept the CanSWE copies and SC04 vanished
  (2,167 stations; the index changed). Decided instead to read priority
  from each copy's rows in the shared years: the copy holding the
  lower-priority rows there loses them. Output byte-identical to ee9503d
  (18 pairs, 509 station-years, 2,168 stations). Tests for the shared-row
  rule and the SC04/SC05 pattern, and for the snowy-years case the first
  test missed (F2: 21 shared years, 3 snowy, all disagreeing).
- **Corrected two records of 2026-10-07** (F3, Info): one of the six pairs
  no longer merged (22F05/710:OR:SNTL) agreed in its single snowy year and
  dropped out for having fewer than 3, not for disagreeing ("Pre-freeze
  audit findings settled" says all six disagree); and the offset
  near-duplicates under the snowy-years rule number 5, not 11. Register:
  933 stations with a normal (YT 54).
- **Decided (owner) on four plan clarifications** (F4, F5; D52): the R
  SPEI note covers only its three points (the fit stays ML, heat index and
  calibration 1951-2020); one-sided permutation p is (count + 1) / (n + 1);
  zero-fire indicator fits have slightly different HAC and Driscoll-Kraay
  standard errors from a fit without those years (accepted); the
  near-threshold flip is one run with all three winters flipped together;
  ONI robustness runs cover every registered test that uses the ENSO index
  (H1, H2, H3a, H3b, H4, C1, C2, strong-only), not H5 and H6. Rejected the
  four headline methods only (would leave C1, C2 and H4's contrast
  without the index check).
- **Recorded, not changed** (G1-G3): no test checks Thornthwaite against an
  independently published worked example (R not installed; no PET values
  written from memory; constants confirmed against the R source by two
  sessions). The per-cell change statistics of the refit (0.03 and 0.01
  SD, largest 0.77) come from the refit session's comparison with a scratch
  backup of the old cache, not kept in the repo. Notebooks 02-03 were
  re-executed with nbconvert in ee9503d (the review compared their outputs
  but did not run them).

### 2026-10-07 - Pre-freeze audit findings settled

- **Ran a targeted read-only audit in a separate cold session with a neutral
  prompt** (owner's choice; Part 3 of `docs/session5_kickoff.md`) over
  every change since bfbc802 and the plan's executability. Report saved
  unchanged as `docs/audit_2026-10-07_prefreeze.md` (eeebbe5). Nothing high:
  every committed table and every recorded refit number reproduced
  independently, and a multi-start optimiser found no better SPEI fit than
  the cache. Findings P1-P6 (medium to low), stale records (R), two info
  items. The owner accepted every recommendation below.
- **Decided (owner) that the zero-fire sensitivity keeps every row in the
  regressions and gives each zero region-year its own 0/1 indicator**
  (P1; D50): one dummy per year fits that year exactly, so the coefficients
  and residual df equal a fit without it, while the series stays one row
  per year for the HAC and Driscoll-Kraay lags (`fit_ols_hac` refuses
  gaps, as decided 2026-10-06). Permutation tests (H2) drop the zero years.
  Rejected the longest gap-free run (could discard many years) and HAC
  across gaps (the fault removed on 2026-10-06).
- **Decided (owner) on a precedence sentence under "Frozen on"** in
  `ANALYSIS_PLAN.md` (P2; owner's wording): where the original text and a
  dated decided note or "Execution details" disagree, the dated note
  governs, with the deviations listed. Rejected rewriting the stale
  passages (owner's prose).
- **Decided (owner) on six open execution choices** (P3; "Execution
  details"): regression one-sided p is the tail in the stated direction (an
  opposite-sign estimate gives p above 0.5); the 2027 intervals are OLS
  prediction intervals from the full training fit, with LOYO and
  expanding-window coverage reported; expanding-window validation covers
  H3a and the two single-predictor H6 models, error as RMSE and MAE of
  `log_burn`; the H4 joint Wald test is F(4, years - 1), matching `use_t`
  and the frozen df (chi-square rejected as large-sample); `temp_jja`,
  `temp_mam`, `precip_anom` and `precip_djf_mm` use all land cells, glacier
  cells included (only SWE and SPEI exclude them); strong-only exploratory
  results cover H1 and H2 and their near-threshold flip. Also clarified
  (owner) that Holm decides significance at α = 0.05 after correction,
  BH reported alongside (the Inference note; "Reporting rules" did not
  name the correction).
- **Decided (owner) to add a trend-only baseline to the expanding-window
  validation** (scope addition, before any fire data; D50): RMSE and MAE
  of `log_burn ~ year` per region, and a skill score 1 - RMSE(model) /
  RMSE(trend-only) for H3a and the two single-predictor H6 models;
  descriptive, no significance test. A significant H3a slope shows El
  Niño relates to burned area; the skill score shows whether it improves
  the forecast over the region's trend, which is the 2027 forecast's
  claim. Registered now so either outcome is clean. Rejected adding it
  later as exploratory (a baseline chosen after the results) and a
  Diebold-Mariano test (22 held-out seasons give it little power).
- **Decided (owner) that duplicate station sites must agree in years with
  snow** (P4): agreement within 2.6 mm counts only where either site holds
  more than 2.6 mm, at least 3 such years. Two bare low sites had agreed
  every snow-free year. Dry run: 18 pairs instead of 24, 509 station-years
  dropped instead of 576, 71,250 rows and 2,168 stations; all 6 pairs no
  longer merged are low Oregon sites with 0-3 snowy shared years that
  disagree in them (the audit named 3; the rule found 3 more of the same
  kind); station z changes by at most 0.016 (PNW). The 11 near-identical
  pairs 3-12 km apart stay unmerged, recorded as a known gap (no effect on
  the index today). Rejected a wider distance threshold (one more arbitrary
  cut).
- **Decided (owner) that PET and SPEI follow the SPEI reference
  implementation (R package SPEI)** (P5, P6; D49): exponent constant
  0.01792 (xclim's 0.01791 changed PET by at most 0.14%); the power law at
  every temperature, as `SPEI::thornthwaite` does (Thornthwaite's 1948
  table for monthly means at or above 26.5 °C is not used; the R source was
  read 2026-10-07); the 3-month window sums monthly amounts of P - PET in mm
  (the code averaged daily rates, so February counted as a full month).
  xclim accepts `mm/month` input; its rolling mean of three amounts is
  their sum / 3, which standardises identically (6e-6 in a 60-year test).
  Rejected rewording only (the freeze is the last cheap refit) and the
  hot-range formula (departs from the SPEI reference). Measured (full
  refit of both domains, 2026-10-07; main 1,586 s, north 1,618 s):
  per-cell mean change 0.03 SD in February, 0.01 in August, largest 0.77;
  regional series against the 2026-10-06 values over 1951-2025, DJF
  SPEI-3 r 0.9990-0.9995 (largest change 0.15, AB), JJA r 0.9999 (0.05),
  whiplash r 0.9994-0.9997 (0.16); El Niño minus neutral moves by at most
  0.02 (PNW whiplash +0.60 to +0.58, PNW DJF -0.42 to -0.40, BC JJA +0.33
  to +0.34); DJF 2026 SoCal -0.72 to -0.70 (cells at the clip 9.9% to
  9.0%), NorCal +0.17 to +0.15, AK +0.75 to +0.69, YT +2.16 to +2.10;
  calibration mean -0.0069/-0.0076, SD 0.985; fitted cells unchanged
  (33,867 main, 33,850 north). Station index after the dedupe change:
  PNW z by at most 0.016 (one station in one year), other regions
  unchanged. Tables, Phase 2 figures and notebooks 02-03 rebuilt; of the
  figures only `whiplash_series_roni.png` changed (the rest byte-identical).
- **Decided (owner) on two checks for the gaps the audits leave**: a short
  read-only review of this session's fix diff by a fresh session or agent
  with a neutral prompt before the freeze; and a pre-results audit gate in
  Phase 4 (D51): the statistics code and variables not yet built are
  tested on synthetic data and audited before anything runs on the fire
  table. Rejected freezing on self-review of the fixes alone (the bias the
  cold sessions exist to avoid).
- **Fixed the stale records the audit listed** (R): data dictionary station
  counts, BC summer SPEI, PET and SPEI wording; `config.py` comments
  (`PET_METHOD`, `SPEI_SCALE`, station minimum frozen at 5); every
  `file.py:line` reference in `docs/methods_register.md` replaced by a
  function name. Recorded the log-logistic shape running to about 1e7-1e8
  in some cell-months (no finite optimum, effectively a logistic; values
  stable to 0.003) in the register.

- **Decided (owner) to compute Thornthwaite PET as Thornthwaite (1948)
  defined it: a climatological heat index per cell from its 1951-2020
  monthly mean temperatures, the N/30 month-length factor, PET 0 at or below
  0 °C** (`pet_thornthwaite`, `PET_HEAT_INDEX_YEARS`; D47). Supersedes the
  PET part of 2026-10-04 "SPEI settings" (xclim TW48). xclim recomputes the
  index from each calendar year: in the incomplete 2026 it was about half
  size and PET 1.5-2.1 times too high in January-April; the 2027 forecast
  input (January-February only) would have been worse; years with no month
  above 0 °C gave 0/0 = NaN (the 46 icefield cells with no February value,
  22 AK and 24 YT); and a per-year index damps PET's warming response
  (independent audit: JJA sensitivity 0.14 vs 0.22 mm/day per °C). Found by
  the re-audit and the independent audit, missed by the first audit.
  Rejected the climatological index without N/30 and complete-year indices.
- **Decided (owner) to leave glacier cells out of SPEI**, as out of the SWE
  means (`GLACIER_SPEI_EXCLUDED`): main 33,867 and north 33,850 fitted cells.
- **Measured (full refit, 2026-10-06):** correlation with the old regional
  series over 1951-2025, DJF SPEI-3 0.992 (SoCal) to 1.000, JJA 0.947 (AK)
  to 0.998, whiplash 0.973 to 0.998. El Niño minus neutral: DJF within 0.04
  of before (SoCal +0.93 to +0.89); JJA smaller by 0.01-0.08 (PNW +0.21 to
  +0.18, BC +0.41 to +0.33, AB +0.48 to +0.44, AK -0.11 to -0.18); whiplash
  PNW +0.63 to +0.60, BC +0.96 to +0.89, AB +1.08 to +1.03, SoCal -0.99 to
  -0.96. DJF 2026: SoCal -1.37 to -0.72, NorCal -0.02 to +0.17, PNW -0.32
  to -0.26. Calibration mean -0.007 and -0.008, SD 0.985 in both domains; no
  fitted cell lacks a February value. SoCal's 2025-26 winter was 3.0 °C
  above its 1951-2020 DJF mean (12.6 vs 9.6 °C), so its DJF 2026 SPEI ranks
  58 of 76 though its precipitation ranks 20, with 9.9% of cells at the
  clip (0% in 2015 and 1998): real warmth, amplified by Thornthwaite's
  temperature sensitivity, a known limitation to state with the 2027
  forecast input. Station index after the dedupe: YT z changed by at most
  0.070, PNW 0.016, others unchanged.

### 2026-10-06 - Plan gaps closed

- **Decided (owner) on the execution details the audits found open, as one
  package** (`ANALYSIS_PLAN.md` "Execution details"): fire tests on seasons
  1984-2025 (`FIRE_LAST_YEAR`; CNFDB 2026 not out in time, WFIGS 2026
  provisional, California's 2026 season closes February 2027), 2027
  (`FORECAST_YEAR`) never in training, expanding-window predictions
  2004-2025 (22, correcting "about 23" in "Inference"); one-sided p = the
  tail in the stated direction, CIs always two-sided 95%; H4's registered
  model without `temp_jja`, its joint Wald test with the same Driscoll-Kraay
  errors; the 2027 forecast from H3a for all seven regions, H6
  single-predictor forecasts secondary, RONI input from CPC's first release
  after February 2027 with the retrieval date, revisions reported; the H3a
  minus H3b gap CI by moving-block bootstrap (3 years, 10,000 draws); the
  block bootstrap checks the `enso_djf` coefficients of H3a and H3b;
  zero-year sensitivity over every burned-area test with `burn_detr`
  re-detrended; station minimum frozen at 5 (no widening for AB or YT);
  `temp_jja`, `temp_mam` via `src.geo.regional_mean`, z-scores with ddof 1;
  strong-only runs against all other years. Rejected going through each
  item separately (owner's choice). Sources: the plan-versus-config re-audit
  and the independent audit (`docs/audit_2026-10-06_climate.md` s.3).
- **Decided (owner): HAC fits use contiguous runs of years only**, and
  `stats.fit_ols_hac` raises otherwise. The fire tests are contiguous
  (1984-2025); station-z checks use each region's contiguous record (AK
  1960+, AB 1963-2025, YT 1975+). Rejected allowing gaps (HAC would treat
  the years either side of a gap as neighbours).
- **Fixed the near-threshold band comparison**: distances to 1.5 are rounded
  to the index's 2 published decimals before comparing (`ENSO_DECIMALS`);
  abs(1.44 - 1.5) is 0.06000000000000005, so 2009-10 would have dropped out
  of the band the plan names (independent audit F7). The earlier config test
  had hidden this with a `+1e-9` tolerance; it now checks the rounded rule.

### 2026-10-06 - Duplicate station sites

- **Decided (owner) to count one site once when two station IDs hold the
  same record:** within 3 km (geodesic, WGS84) and at least 80% of at least
  3 shared years within 2.6 mm (0.1 inch); the lower-priority copy (NRCS,
  then provincial files, then CanSWE; then more values) loses its shared
  years and keeps the rest (`src.stations.dedupe_sites`). Dry run on the
  current table: 24 pairs, 576 station-years dropped (PNW 419, YT 123, AK
  34), 71,759 to 71,183 rows; e.g. NRCS 19A01:WA:SNOW and BC's BCE-WA07 (51
  identical years), Yukon 09BA-SC02 and SC02A. Rejected the narrower rule
  first chosen (same coordinates within about 100 m, identical values):
  the independent audit showed most duplicates sit across networks with
  slightly different coordinates. Affects only the station index (the
  robustness check). `SITE_DUP_*`, `SITE_SOURCE_PRIORITY`.

### 2026-10-06 - stats.py guards

- **Fixed (owner's choice, before Phase 4) four latent faults the
  independent audit found:** `permutation_test` returned the smallest
  possible p (1/(n + 1)) for a NaN difference, now raises on a missing value
  (as `bootstrap_ci_diff` and `adjust_pvalues`, where a NaN counted in the
  Holm family size); `fit_ols_hac` depended on row order (an SE moved from
  0.320 to 0.290 when rows were shuffled) and treated gaps as adjacent, now
  raises unless the rows used are consecutive years in order; `fit_pooled`
  broke on repeated index labels from `pd.concat`, now resets the index.
  Rejected leaving them to Phase 4. Tests added.

### 2026-10-06 - PR #20 review fixes

- **Fixed the six review findings on PR #20 in the main session**, after
  merging it (owner's choice): `join_enso` keeps years after the last
  published ENSO winter with empty ENSO columns (a missing year inside the
  record still raises), so a monthly tracker run before CPC posts DJF 2027
  doesn't stop; `classify_winters` needs the index name (no default that
  could label ONI values RONI); `effects_by_group` skips a region with no
  elevations; malformed BC survey dates are counted as missing, not fatal;
  one SWE-normal rule (`stations.swe_normal_ok`) for `compare_era5` and the
  figures; notebooks 02 and 03 call `src.phase2_figures`, one generator per
  figure. Rejected sending them back to the side session.

### 2026-10-06 - Independent audit and re-audits

- **Ran two re-audits from the main session and an independent audit in a
  separate session with a neutral prompt (owner's choice, for less bias),
  then compared.** Reports: `docs/audit_2026-10-06_climate.md` (independent,
  commit bfbc802) and the follow-up section of
  `docs/audit_2026-10-05_phase2.md`. All three agreed on the high finding
  (the per-year heat index); only the independent audit found the damped
  warming response, the float band fault and the `stats.py` NaN p-value;
  the first audit had missed the heat index and the duplicates. Its claim
  that the 46 cells were all in AK was wrong (22 AK, 24 YT); their cause is
  the 0/0 heat index.

### 2026-10-06 - Phase 2 audit fixes (side session)

- **Fixed the low-severity code findings of the pre-freeze audit in a side
  PR, code only, each with a test** (owner's choice, relayed by the main
  session; `docs/audit_2026-10-05_phase2.md` findings 5, 6, 8, 9, 11-15).
  `snow.glacier_mask` uses complete years only; `whiplash.restandardise`
  sorts by year and raises below 2 calibration values; `stations.anomalies`
  raises below 2 normal years; `stations.effects_by_group` leaves out
  stations with no elevation instead of crashing in `qcut`;
  `el_nino_winters.csv` gains `enso_index`; the `data/processed/` writers in
  `era5`, `snow`, `download_oni` and `stations` write LF; the em-dash check
  scans notebook code cells; `python -m src.phase2_figures` rebuilds the
  five Phase 2 figures from `results/tables/`. Expected effect after the
  re-runs: values unchanged; line endings and the new column differ. Files:
  `src/era5.py`, `src/snow.py`, `src/snow_soil.py`, `src/whiplash.py`,
  `src/stations.py`, `src/download_oni.py`, `src/phase2_figures.py`,
  `scripts/check_no_em_dashes.py`, tests.

- **Decided one ENSO join for every region x year table
  (`era5.join_enso`).** A left join validated many-to-one; years before the
  first ENSO winter are dropped (April 1 1950 and soil moisture 1950 have no
  December 1949 before them, which the inner joins dropped without saying
  so); any later year with no ENSO value raises. `winters`' own
  `enso_index` must name `ENSO_INDEX`, and the table keeps one such column,
  so the new column can't duplicate in a merge. Applied to
  `era5.winter_precip_table` as well as the three tables named in the
  audit, so all four follow one rule. Rejected raising on 1950 too: those
  rows are expected and every table already starts in 1951.

- **Decided that a survey with no date is counted as "missing date", never
  as "outside window".** `stations.nearest_in_window` now refuses undated
  rows, so every caller has to drop and count them first
  (`drop_missing_dates`: NRCS snow courses, BC, Yukon). CanSWE dates come
  from the file's time axis and can't be missing. Rejected counting inside
  `nearest_in_window`, which returns only rows and would need a second
  return value at every call.

- **Decided that `src.phase2_figures` picks regions by rule, not by name.**
  The SWE series leaves out regions whose ERA5-Land April 1 normal is below
  `ERA5_SWE_MIN_NORMAL_MM` (the rule `compare_era5` already uses; SoCal
  0.06 mm), and the station comparison shows regions with a station index.
  Same regions as notebooks 02 and 03 today; the notebooks' own literals
  (finding 10) are left for the main session.

- **Left for the main session:** the whiplash table's CSV writer sits in
  `whiplash.main`, outside this PR's boundary, so it still writes CRLF on
  Windows (one argument, `lineterminator="\n"`); findings 7 and 16 (in
  `stations.compare_era5` and `stations.combine`) and 10 (notebooks) were
  not part of this task. `figures.winter_series` fails with a single region
  (`plt.subplots` returns one Axes); not changed.

### 2026-10-06 - Tracker window and verification dates follow the pre-freeze decisions

- **Decided (owner) to start the season timeline in October and to split
  the verification date by region.** Deviation D46; supersedes the November
  start in "Season timeline page for the live tracker" (2026-10-05, D44).
  H5's `precip_anom` as the October-March total was decided before the
  freeze (DECISIONS.md 2026-10-05 "Hypotheses"), so October 2026 is an
  input: the first countdown now targets October's data (expected about
  6 November, an assumed lag) instead of November's (about 6 December).
  With the California fire windows running June to January of Y+1 (D43),
  the 2027 forecast can be checked in fall 2027 for PNW, BC, AB, AK and YT,
  and for NorCal and SoCal only after January 2028; the page shows both
  dates rather than holding the whole verification panel until 2028.
  Files: `ACTION_PLAN.md`.

### 2026-10-06 - Pre-freeze audit

- **Decided (owner) to audit the climate data and the Phase 2 code before
  the freeze, read-only, by two research agents** (data in the main
  checkout, code against the rules; D35's phase-boundary audit).
  Report: `docs/audit_2026-10-05_phase2.md` (commit audited 5386222). Data
  largely clean: ENSO columns, SPEI standardisation, whiplash, SWE z and the
  station index all recomputed exactly; the 111 unfitted north cells are
  glacier icefields.
- **Fixed (owner's choice): Thornthwaite PET in polar day and night.**
  xclim's TW48 leaves day length NaN there, so north of about 68N every DJF
  and JJA SPEI-3 was missing and regional means skipped those cells (AK
  15.1% and 17.4% of its weight, YT 5.1% and 6.3%). `pet_thornthwaite` now
  repeats xclim's TW48 steps with `infill_polar_days` (24 h and 0 h); main
  domain PET identical (largest difference 3e-15 mm/day), so only the north
  SPEI was refit (1,947 s). Only the AK and YT SPEI and whiplash columns
  changed (largest change 0.62 in whiplash; correlation with the old series
  AK 0.989 DJF, 0.979 JJA; YT 0.999, 0.998). AK El Niño minus neutral
  whiplash -0.01 to -0.08, YT +0.24 to +0.23 (RONI). No pre-registered test
  uses these (AK and YT SPEI and whiplash are descriptive). 46 north cells
  (59-63N, Alaska Range, Wrangell-St Elias) still have no February value;
  they predate the fix, cause open. Rejected disclosing the gap only and
  deferring the fix. Tests added.
- **Fixed (owner's choice): ERA5-Land SWE % and z empty where a region's
  1991-2020 normal is under 10 mm** (`ERA5_SWE_MIN_NORMAL_MM`), the station
  index's floor. Only SoCal is affected (normal 0.06 mm; z had reached 4.69,
  % 1,787); H6 already excluded SoCal from the SWE test.
- **Decided (owner) to pre-register the Driscoll-Kraay t degrees of freedom
  as years minus 1** (`POOLED_DF_YEARS_MINUS`): statsmodels counts them from
  row order (df 0, 4 or 100 for one dataset sorted three ways, standard error
  0.10722 in all). Removes a choice that would otherwise be made after the
  fire data.
- **Decided (owner): the low-severity findings (12 code and data items) go
  to a side-session PR**, with a main-session re-run after merging; stale
  register and dictionary wording fixed in the main session. A second,
  independent audit follows: a separate session with a neutral prompt, plus
  fresh agents from the main session, compared (owner's choice, for less
  bias).

### 2026-10-05 - H1 months and the CLAUDE.md fire window

- **Decided (owner): H1 compares DJF precipitation totals (`precip_djf_mm`),
  detrended per region.** The plan named only a "winter precipitation
  anomaly"; DJF matches the hypothesis wording and the Phase 1 values
  already shown. Rejected Oct-Mar (H5's months). `config.H1_VALUE`.
- **Decided (owner) to update `CLAUDE.md`'s fire-season window line to the
  windows chosen in D43**, since sessions follow it as an instruction;
  marked `[mid-project: D43]`.

### 2026-10-05 - Inference

- **Decided (owner): t critical values (`use_t=True`) in every HAC and
  pooled fit, and Driscoll-Kraay errors (maxlags 2) for the pooled H4
  model, with year-clustered errors reported alongside.** About 42 fire
  seasons give about 42 clusters, where normal critical values overstate
  precision; year clustering allows regions in one year to correlate but
  ignores each region's correlation with its own nearby years, which
  Driscoll-Kraay covers. Rejected `use_t` alone. `USE_T`, `POOLED_COV_TYPE`
  (statsmodels `hac-groupsum`); `src/stats.py` applies neither yet. D45.
- **Decided (owner) to add expanding-window validation: fit on 1984 to
  Y-1, predict Y, from 20 training seasons (first prediction 2004, about 23
  predictions), for H3a and the H6 models**, with coverage and error beside
  leave-one-year-out. Leave-one-year-out lets each fit see later years; the
  2027 forecast cannot. Rejected a 15-season start (shakier early fits) and
  leave-one-year-out alone. `FORWARD_MIN_TRAIN_YEARS`.
- **Decided (owner) on the correction families: one Holm family per
  hypothesis across the main regions, BH alongside** (H1 5 tests, H2 5, H3a
  5, H3b 5, H5 10, H6 9; H4 a single test; AK and YT H2, H3a, H3b 2 each;
  C1 and C2 3 each; ONI and station-z robustness runs uncorrected). H3a and
  H3b kept apart: the same coefficient estimated with and without
  `temp_jja`, so a shared family would penalise one question twice.
  Rejected H3a and H3b shared. `CORRECTION_FAMILIES`; tests check that
  every tested cell sits in exactly one family.

### 2026-10-05 - Season timeline page for the live tracker

- **Decided (owner) to build the live 2026-27 tracker as one site page in
  three states: before winter, tracking and final.** Deviation D44. The
  owner proposed a countdown page if the build finishes before November,
  kept through the winter and then replaced by the results; adopted in the
  form of a November-April season timeline, which holds both countdowns
  (to the first month of data, then to the April 1 snowpack) and becomes
  the results page's record of what arrived when. Rejected a standalone
  countdown page, deleted at the end: a bare countdown reads as a launch
  rather than a study, and the completed timeline is the evidence that the
  forecast was issued before the season, which the fall verification needs.
  The page states the freeze date, and has a state for an El Niño that comes
  in below strong. Mockup (private, example values):
  https://claude.ai/artifact/PirV1BadszhJwgQBHCtYdq. Files:
  `ACTION_PLAN.md`.

- **Decided that the countdowns target expected data arrival, not calendar
  dates.** The test season is Dec-Feb and ERA5-Land publishes each month
  after it ends, so "tracking begins" means the first month's data landing
  (November's, early December) and tracking ends when April 1 snowpack
  arrives. Counting to 1 November would show "tracking started" with nothing
  on the page. The arrival lag is an assumption until measured; the dates
  go in `src/config.py` (main session, after the freeze), and the page
  picks its state from what the pipeline has written to `results/`, so
  nobody flips it by hand.

### 2026-10-05 - Alaska stays one region

- **Decided (owner) to keep Alaska as one region (east of 169W) and state
  the coast-interior limitation for AK, BC and PNW together.** Supersedes
  the conditional in "Hypotheses" below (one region unless a probe found a
  licensed boundary). A research agent found one (read-only, no fire pages
  opened): NOAA NCEI Alaska climate divisions (Bieniek et al. 2012, 13
  polygons, 391 KB, https://www.ncei.noaa.gov/pub/data/cirs/climdiv/AK_climate_divisions.zip;
  NOAA: "in the public domain"), Interior = divisions 3, 4, 5; coastline
  from Alaska DNR, terms not read. Fallbacks EPA Level III ecoregions ("Use
  constraints: None") and USGS Unified Ecoregions (public domain). Kept one
  region because every region is a whole state or province, and BC and PNW
  share the mismatch (wet coasts that rarely burn); splitting only Alaska
  would treat one region differently, and consistency would mean splitting
  BC too. The tested predictors are standardised, which limits how much the
  coast's large totals weigh. Cost: AK predictors partly describe places
  that don't burn, likely diluting an El Niño signal toward zero; an AK
  null is read with that in mind. A descriptive check with the NCEI
  Interior boundary in Phase 4 stays a flagged option (scope), not decided.

### 2026-10-05 - Data rules

No fire data seen; choices rest on the sources and fire regimes. General
knowledge of large California fires outside June-October (Thomas, Dec 2017;
Camp and Woolsey, Nov 2018; the Los Angeles fires of January 2025) informed
the window.

- **Decided (owner) on fire windows: NorCal and SoCal June to January of the
  next year, BC April-October, PNW June-October, AB April-October, AK and YT
  April-September (no longer provisional).** A January Y+1 fire counts for
  season Y, paired with winter (Y-1)-Y. Rejected June-December (January
  fires would fall outside every season) and keeping June-October. Cost:
  California season Y closes in February Y+1, so the fall 2027 check is
  preliminary for California. `FIRE_SEASON_MONTHS` now allows a wrapping
  window ((6, 1)). D43.
- **Decided (owner) on the fire record rules:** MTBS Wildfire, Wildland Fire
  Use and Unknown kept (Unknown counted), Prescribed Fire dropped, Canadian
  prescribed burns dropped where flagged; the 405 ha floor on each fire's
  whole `area_ha`, then clipped to each region; ignition date; MTBS then
  WFIGS with the cutover recorded at download and the overlap year compared;
  CNFDB date completeness reported by decade. Rejected the floor on the
  clipped part (a large fire crossing a border would drop out of a region).
  `MTBS_KEEP_TYPES`.
- **Decided (owner): zero-fire region-years kept, counted and excluded in a
  sensitivity run; no percent change where they exceed 10% of seasons**
  (`ZERO_YEAR_PCT_LIMIT`). Rejected excluding them from the main analysis
  (drops the quietest seasons, biasing burned area up).
- **Decided (owner): near-threshold winters get a flip-flag sensitivity run
  for the strong-only (exploratory) results, no exclusion**
  (`STRONG_SENSITIVITY_BAND` 0.06; RONI 1965-66 1.53, 1986-87 1.46, 2009-10
  1.44). Rejected excluding them and doing nothing extra.

### 2026-10-05 - Hypotheses

Numbers below: El Niño minus neutral under RONI (SPEI in SPEI units, SWE as
z), 1951-2026, descriptive; no fire data seen.

- **Decided (owner) to add H6, "low April 1 snowpack and a dry winter
  predict more burned area", and keep whiplash descriptive** (option D of
  `docs/prefreeze_options.md`). `log_burn ~ swe_z + year` and
  `log_burn ~ spei3_djf + year` per region, each alone; both together
  reported, not tested (correlation PNW 0.61, BC 0.67, AB 0.65). Both are
  known by 1 April in every region, so they can feed the 2027 forecast, and
  they separate the dry-winter path (winter SPEI-3 PNW -0.42, BC -0.55, AB
  -0.60) from the warm-winter path (SWE z -0.41, -0.56, -0.69). Whiplash
  (JJA - DJF) mixes a dry winter with a wetter summer in the north (summer
  SPEI-3 +0.21, +0.41, +0.48), so its sign for fire is unclear; kept as a
  descriptive mechanism variable. Rejected whiplash as the only core
  variable, a winter-to-spring whiplash (still inside the April fire
  windows), and no new hypothesis.
- **Decided (owner): season length, snowfall fraction and summer soil
  moisture are descriptive only.** Season length is undefined with 0-1
  counted fires and CNFDB date completeness is unchecked; snowfall fraction
  and soil moisture are shown beside H6 as mechanism checks. Rejected testing
  season length and soil moisture as an H3b-style control.
- **Decided (owner) on directions and sidedness for every test**
  (`ANALYSIS_PLAN.md` "Directions and sidedness"; `config.TEST_DIRECTIONS`).
  PNW, BC, AB one-sided where theory and precursors agree (H2 higher, H3a
  and H3b positive, H5 lag0 negative, H6 negative); NorCal and SoCal
  two-sided except SoCal H5 lag1 (positive, the fuel build-up); H1
  two-sided and labelled a check, since winter precipitation was seen
  before the freeze (SoCal +62.9%, PNW -10.7%); the H3a minus H3b gap
  reported with a CI, not tested. Rejected H1 descriptive and all
  two-sided.
- **Decided (owner): H4 is one contrast, the mean `enso_djf` slope of PNW,
  BC and AB minus SoCal's, two-sided**, with the joint Wald test of the four
  interaction terms as secondary; AK and YT out of the pooled model.
  Rejected the joint Wald test as primary (four degrees of freedom for a
  one-number question).
- **Decided (owner): H5's `precip_anom` is the October-March total as a
  z-score against the region's 1991-2020 normal.** Covers California's
  autumn and March storms that DJF misses and ends before every fire window.
  Signs: north lag0 negative one-sided, lag1 two-sided; SoCal lag0
  two-sided (grass grows but a wet winter can delay the season), lag1
  positive one-sided; NorCal two-sided. Rejected DJF.
- **Decided (owner) on Alaska and Yukon as their own family (option B):**
  H2, H3a, H3b two-sided (expected higher, positive); H1 and H6
  descriptive; H4 and H5 not extended; MAM temperature as a descriptive
  spring variable. Under RONI an average El Niño barely moves AK (SWE z
  -0.11, DJF precipitation -0.1%) though strong winters do (SWE z -0.42),
  so no one-sided claim. Alaska stays one region unless a short probe finds
  a boundary with clear terms; if none is found, the skews are disclosed. Rejected
  descriptive only and one-sided (option C). D42.

### 2026-10-05 - Trend and climate change

- **Decided (owner) that the climate variables follow the burned-area
  one-method trend rule.** Permutation and bootstrap comparisons use
  residuals from `value ~ year` per region; regressions carry a `year`
  term; figures stay raw. Measured on the RONI tables (2026-10-05): trends
  are large (ERA5-Land April 1 SWE z PNW -0.21, BC -0.16 SD per decade, -1.55
  and -1.19 SD over 1951-2026; snowfall fraction -0.11 to -0.15 SD per decade
  everywhere but YT), but detrending moves the El Niño minus other-years
  differences by 0.04 SD at most (e.g. PNW SWE -0.47 to -0.51), since RONI is
  nearly unrelated to the trend. Rejected raw comparisons (two methods in
  one plan).
- **Decided (owner) to pre-register two secondary compounding tests in their
  own family:** C1 `swe_z ~ enso_djf + year_c + enso_djf:year_c` (PNW, BC,
  AB; 1951-2026; interaction expected negative, one-sided; repeated on the
  station z) and C2 the same on `log_burn` (1984+; expected positive,
  two-sided for low power). Early and late halves as a figure only.
  Rejected exploratory only (a real signal could never count as confirmed)
  and the snowpack test alone. The El Niño x year interaction was not
  computed before registering; the session 3 elevation finding (low-third
  stations -42, high third +3 points of normal) hints at C1, so the plan
  says it is only partly blind. `config.COMPOUNDING_REGIONS`.
- **Decided (owner) to report RONI as the trend-adjusted index for these
  tests, ONI as the check.** Closes the open decision in D38.

### 2026-10-05 - SWE source for the tests

- **Decided (owner) that every SWE test and the 2027 forecast use ERA5-Land
  April 1 SWE, with the station index as a named robustness check.**
  ERA5-Land covers 1951-2026 in all seven regions and is available about
  8 April 2027; the station index starts AK 1960, AB 1963, YT 1975, ends
  2025 in AB, has no NorCal series, and its sites sit high (PNW median
  station normal 3.1 times the grid mean), missing the low-elevation loss
  (strong winters: low third -42, high third +3 points of normal). Yearly z
  correlation with stations PNW 0.95, BC 0.84, AB 0.77, AK 0.80, YT 0.84.
  El Niño minus neutral under RONI (SD), ERA5-Land / stations: PNW -0.34 /
  -0.17, BC -0.53 / -0.48, AB -0.70 / -0.84. Rejected stations primary (no
  NorCal, no Alberta value until about March 2028) and both co-primary
  (doubles the SWE tests in every family). Agrees with
  `docs/alberta_swe_sources.md`.
- **Decided (owner) on the z-score against the 1991-2020 regional normal
  (`era5_swe_z`) as the predictor's unit.** Coefficients read per SD of
  snowpack, comparable across regions and with the station z. Rejected
  percent of normal (skewed; the PNW station median fell to 3.3% in 2015)
  and mm (not comparable across regions); percent stays for display.
  `config.SWE_TEST_COLUMN`, `SWE_CHECK_COLUMN`.

### 2026-10-05 - ENSO index: RONI

- **Decided (owner) on RONI as the ENSO index for every test, with ONI as
  the robustness check re-run for each headline test.** RONI is NOAA's
  official index (PIS 26-05), so the 2026-27 value the forecast uses and the
  index the models are trained on match, and it puts 1950s and 2020s winters
  on one scale. Measured 2026-10-05: correlation with ONI 0.96; 17 of 76
  winters change class; RONI 26 El Niño (7 strong), 26 neutral, 24 La Niña;
  fire record 14 El Niño (3 strong: 2023-24 falls to 1.13; 1965-66 becomes
  strong at 1.53), 9 neutral, 20 La Niña. Correlation with year: ONI -0.01,
  RONI -0.22 (1951+), -0.18 (1984+); the `year` term in the regressions
  covers this. The descriptive climate numbers point both ways (RONI widens
  El Niño minus neutral, e.g. AB SWE -0.56 to -0.70 SD, SoCal DJF
  precipitation +0.62 to +1.02 SD; ONI correlates more with northern SWE,
  PNW r -0.38 vs -0.29), so they were set aside as a reason. Rejected ONI
  primary and both co-primary (doubles the tests). Committed tables and
  figures rebuilt with RONI (figure names now end `_roni`). `ENSO_INDEX`,
  new `ENSO_ROBUSTNESS_INDEX` in `src/config.py`. D41.

### 2026-10-05 - Deviation numbers given at merge

- **Decided (owner, relayed by the main session) that side sessions write
  placeholder deviation numbers and the merge assigns the real ones.**
  Deviation D40. A new side-session entry is titled with a placeholder
  (D\?a, then D\?b, unique within the PR), used for every reference to it. When main is merged
  into the PR, `scripts/merge_append_only.py` gives each placeholder the
  next number after the highest real D on either side and rewrites the
  references in the files the PR changes; `scripts/prescreen_prs.py` does
  the same in its rehearsal, in queue order, and lists the numbers in its
  report so the owner approves the final ones. Replaces the per-session
  ranges (session 3: main D36-D39, side D40 onward). Rejected keeping ranges
  (agreed anew every session, with gaps when a range goes unused). The main
  session keeps numbering its own entries directly. Files:
  `scripts/merge_append_only.py`, `scripts/prescreen_prs.py`,
  `.claude/skills/merge-side-pr/SKILL.md`, both tests.

- **Decided to number a PR's placeholders oldest entry first, from the bottom
  of the deviations log up.** The log is newest first, so numbering in
  reading order would put D40 above D41 and break the descending order the
  log and the merge's ordering rely on. The request said "in order of
  appearance"; read here as the order the entries were written. Owner
  confirmed 2026-10-05.

- **Decided how the merge tells a placeholder from a mention of one.** The
  token is D, a question mark and lower-case letters, standing alone. In
  Markdown prose a backslash before the question mark makes a literal mention
  (it renders the same and is not numbered), as in the first bullet. The
  script, the pre-screen, their tests and the merge-side-pr skill describe
  the rule, so they are skipped, named one by one (`LITERAL_PLACEHOLDERS`,
  at the main session's request). The leftover check covers every other
  tracked file: a placeholder from main's side, or one a PR references
  without defining, stops the merge; tests show it for a `src/` comment, a
  notebook cell and a Markdown plan file. Rejected matching only inside the
  two logs, which would miss `[mid-project: ...]` markers and code comments.

- **Decided to check the day's log separately after a session block is
  folded in (`merge_append_only.py --check-log`).** The block lives in the
  PR description, which no tree check sees, and is folded into `logs/` by
  hand with the numbers the merge printed (merge-side-pr steps 8 and 10).
  Requested by the main session while the owner reviewed the risk of a
  missed reference.

### 2026-10-05 - Data guide page, refreshed every session

- **Decided (owner) to keep a private data guide page listing every data
  type, derived variable, setting and headline number, and to refresh it at
  the end of every main-checkout session.** Published 2026-10-05
  (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P, snapshot 6ad8666)
  after the owner asked for a summary of all data types and values from
  sessions 0-3, so the data set stays understandable as it grows. The repo
  stays the source of truth (data dictionary, config, methods register); the
  page is a readable snapshot. Rejected a committed Markdown copy, which
  would duplicate the data dictionary and go stale. Files: `CLAUDE.md`,
  `docs/session4_kickoff.md`.

### 2026-10-05 - Stations against ERA5-Land (verification)

- **Found that station April 1 SWE agrees with ERA5-Land on the direction
  of the El Niño difference in all five station regions, and on its size in
  BC and AB, while in PNW the station loss is smaller because the network
  sits high.** Correlation of the yearly series (% of 1991-2020 normal /
  standardised): PNW 0.94 / 0.95 (76 years), BC 0.79 / 0.84 (76), AB 0.84 /
  0.77 (63), AK 0.78 / 0.80 (67), YT 0.84 / 0.84 (52). Level ratio (median
  station normal / ERA5-Land regional mean, 1991-2020): PNW 3.10, BC 1.07,
  AB 1.26, AK 0.68, YT 0.88. Strong El Niño minus all winters, points of
  normal, stations / ERA5-Land on the same years: PNW -8.5 / -25.6, BC
  -14.3 / -13.0, AB -38.9 / -32.3, AK -4.1 / -5.0, YT -5.5 / -2.1. Checked
  before interpreting the PNW gap: units (the index is a ratio; normals
  plausible, PNW pillow median 456 mm), dates (exact-date pillows show -1.7,
  courses within 3 days of 1 April -15.1, so the ±10-day window does not
  hide a loss) and the glacier mask (no PNW cells). PNW stations split into
  elevation thirds: low (550-1,470 m) -42.3, mid -4.6, high (1,880-2,800 m)
  +3.0; BC low -20.9, high -10.9. The area-weighted grid mean is dominated
  by lower terrain. Also found: the median index collapses toward 0 in snow
  droughts (PNW 2015: 156 of 368 stations bare, median 3.3%; 2026: 153 of
  344, 4.7%) while ERA5-Land shows about 27% and 40%. Descriptive; no tests.
  An elevation-matched ERA5-Land comparison was flagged as a scope addition,
  not built. Files: `src/stations.py`, notebook 03.

### 2026-10-05 - Snowfall fraction and soil moisture columns

- **Decided (owner) to define the snowfall fraction over November-March as
  the ratio of regional totals, and summer soil moisture as the JJA mean of
  the depth-weighted 0-28 cm layer.** Nov-Mar is the accumulation season
  behind April 1 SWE (rejected: DJF, which misses November and March, when
  the rain-snow line matters most at mid elevations; Oct-Mar). Ratio of
  regional means (cos-latitude weighted, `src.geo.regional_mean`) rather
  than the mean of per-cell fractions, which is noisy in near-dry cells.
  JJA matches SPEI-3 JJA (rejected: each region's fire window, which mixes
  snowmelt-wet April-May soils into the northern means; both). Layers
  weighted 0.25 / 0.75 (7 and 21 cm thick) rather than layer 1 alone, which
  flickers with each shower. Means 1951-2026: snowfall fraction YT 0.99,
  AB 0.92, AK 0.83, BC 0.78, PNW 0.46, NorCal 0.31, SoCal 0.06; soil
  moisture 0.12 (SoCal) to 0.35 m³/m³ (AB). Descriptive unless
  `ANALYSIS_PLAN.md` adds them. Files: `src/config.py`, `src/snow_soil.py`,
  `results/tables/snow_soil_region_year.csv`.

### 2026-10-05 - Regional station index

- **Decided (owner) that the regional station index is the median across
  stations of April 1 SWE as % of each station's 1991-2020 mean, with the
  mean standardised anomaly as a second column.** Normals from stations
  with at least 20 of the 30 years (935 stations); the % column leaves out
  stations whose normal is under 10 mm, where percentages explode. A
  region-year needs 5 stations, else the index is left empty (the counts
  stay in the table); the owner may widen this for AB and YT if their
  analyses prove too short (a 3 was a misclick, corrected the same
  session). Rejected: one method only; 1951-2020 normals (more early
  stations, but normals from different parts of 70 trending years);
  1981-2010; 24 (WMO 80%) or 15 years; 3 or 10 stations. Resulting index
  starts: PNW and BC 1951, AK 1960, AB 1963, YT 1975; AB ends 2025 (CanSWE).
  Files: `src/config.py`, `src/stations.py`,
  `results/tables/station_swe_region_year.csv`.

### 2026-10-05 - Station snowpack cleaning rules

- **Decided (owner) the rules that turn the raw station files into one
  station x year table of April 1 SWE in mm**, every year kept (71,759
  station-years, 2,180 stations in five regions, 1950-2026). Measured on the
  raw files first; each rule's count is in `docs/methods_register.md`.
  - NRCS: dropped QC flags B (1,126 regression back-estimates that copy a
    snow course into a pillow record, so the course would count twice
    before 1980 and the swings are damped, SD 0.54 vs 0.61 of the station
    median) and S (9 values with data, all 8 April negatives among them).
    Kept E (minor adjustment for sensor noise; 27% of SNOTEL), K (estimate;
    782 snow-course values since 2009, median 1.00 of normal), V, N, C, X,
    with the flag in `flags`. Rejected dropping K too, or keeping B.
  - NRCS snow courses dated 1 July (2,163 values, 485 courses): kept with
    `sample_date` empty and flag `date_unknown`; their values look like
    April 1 surveys (median 0.92 of the station median vs 0.96).
  - Manual surveys, all sources: the sample nearest 1 April within ±10 days
    (98.3% of NRCS, 99.99% BC, 99.8% Yukon, 98.8% Alberta inside). Rejected
    ±7 and ±15. Pillows: SNOTEL's midnight value opening 1 April, CanSWE's
    daily value dated 1 April; each pillow is its own station.
  - BC: survey codes kept as flags except the estimates EST AREAL AVG and
    EST PILLOW (7 values); archive and current-season rows were identical
    (103) and are kept once; coordinates from CanSWE (the BC file has none),
    so 7 courses (84 values) without a CanSWE match are dropped.
  - Yukon: "Estimated SWE" kept and flagged (199 values; depth measured,
    density from history); network sites outside Yukon dropped (lowest
    licence risk; 8 stations, 315 values), as were 2 in NWT (no region).
  - CanSWE: provincial files win for the same station-year (15,373 CanSWE
    values replaced, 9,770 added: Alberta, BC and Yukon pillows, BC-run
    courses missing from the BC file). CanSWE flags kept in `flags`; flag Y
    does not occur in AB, BC or YT. Hydro-Québec is never read.
  - Regions by point in polygon, whatever the network: 15 BC-run courses in
    WA and ID count for PNW; 33 stations fall in no region (mostly Alberta-
    and BC-run sites in Montana, plus 3 Idaho stations on the edge and the 2
    NWT sites).
  - NRCS station elevations converted from feet (found while building).
  Files: `src/config.py`, `src/stations.py`, `tests/test_stations.py`.

### 2026-10-05 - Side-session blocks go in the merge day's log

- **Decided (owner, by merging this change) that a side session's block is
  folded into the log of the day its PR is merged, never into an earlier
  day's log.** `merge-side-pr` step 8 filed it under the day the side
  session worked, while `daily-log` says never edit a previous day's log;
  PR #8's block (side session 23:40-00:20) went into `logs/2026-10-04.md`
  at 00:45 on 2026-10-05. Now both skills say the same thing: today's log,
  with the work date in the block's heading (`worked YYYY-MM-DD`) and
  `sessions` entry when it differs. This keeps the daily-log rule without an
  exception and leaves exported logs unchanged, and matches `CLAUDE.md`
  ("adds the block to the day's log when it merges the PR"). PR #8's block
  stays in the 2026-10-04 log (earlier days aren't rewritten). Rejected
  filing by the work day with an exception in `daily-log` (earlier logs
  would change after export, and a block can arrive days late). Files:
  `.claude/skills/merge-side-pr/SKILL.md`, `.claude/skills/daily-log/SKILL.md`.

### 2026-10-05 - Phase 1 figures from code

- **Decided to regenerate the three Phase 1 figures with a new module,
  `python -m src.winter_figures`, instead of only by running notebook 01**
  (Phase 1 audit, finding 7; owner's direction via the main session). It
  repeats notebook 01's cells 7-13 exactly: the same `src.era5` and
  `src.figures` functions, file names, the ENSO_INDEX table from
  `data/processed/el_nino_winters.csv` and the ONI/RONI comparison from
  `download_oni.load_winters`, so `results/figures/` can be rebuilt by code
  alone. A new module rather than a `__main__` in `src/figures.py`, which
  the main session was editing (its `_legend` fix); the map's extent and
  title wording are copied unchanged, pending D28. 3 tests on synthetic
  data, with the cartopy map stubbed (it downloads Natural Earth layers);
  not run on the real data here (the worktree has none). Notebook 01 still
  holds its own copy of these cells; pointing it at the module is the main
  session's call. Files: `src/winter_figures.py`,
  `tests/test_winter_figures.py`, `README.md` (run order).

### 2026-10-05 - Phase 1 audit

- **Decided (owner) to run a read-only audit of the code against the
  project's own rules at each phase boundary, by a side session against the
  latest main, with a dated report in `docs/`.** First run: `main` at
  `9e5f73a`, Phase 1 and shared modules (`config`, `geo`, `regions`, `era5`,
  `describe`, `stats`, `figures`, both downloaders, notebook 01, their
  tests), Phase 2 work in progress left out. 7 findings (3 medium, 4 low) and
  4 methods notes; none changes a Phase 1 result. Measurement rules, year
  labels, ENSO classification and the single source of truth passed; both
  ERA5-Land domains hold 919 contiguous months. Rejected auditing after every
  session (repeats `merge-side-pr`'s per-PR review and adds noise). Report:
  `docs/audit_2026-10-05_phase1.md` (top level of `docs/`, which
  `LICENSE-CONTENT` covers; a `docs/audits/` folder would not be).
- **Fixed three `stats.py` findings (1, 2 and 4), each confirmed on
  synthetic data first.** `loyo_prediction` counted a held-out row with no
  actual value as not covered, lowering the coverage used to judge the
  forecast intervals; such rows now keep their interval with `covered`
  missing (pandas nullable boolean). `block_bootstrap_ci` gave a wrong answer
  silently on rows not sorted by year (a lag-1 autocorrelation of 0.84 came
  out as -0.08); it now raises unless there is one row per year in
  increasing order and at least `block_len` rows. `fit_pooled` failed on any
  missing value ("The weights and list don't have the same length"); it now
  fits complete cases, as plain OLS does, with the cluster groups taken from
  the same rows, giving the same coefficients and errors as fitting the
  complete rows directly. 4 tests; methods register rows updated. Files:
  `src/stats.py`, `tests/test_stats.py`, `docs/methods_register.md`.
- **Sent findings 3, 5, 6 and 7 to the main session rather than fixing them
  here:** they sit in its modules (`era5.py`, `figures.py`, notebook 01) or
  its register. Finding 5's map extent and baseline wording were already
  logged as D28; the legend thresholds are new.

### 2026-10-05 - Phase 1 audit fixes in the main session

- **Fixed audit findings 3, 5 and 6 (`docs/audit_2026-10-05_phase1.md`),
  at the owner's direction; finding 7 (Phase 1 figures only rebuildable by
  running notebook 01) went to the side session.**
  - 3: `open_era5` now raises if an `era5_land_<year>/` folder exists (a
    zipped CDS reply the `*.nc` glob would skip) or if months are not
    contiguous; either would silently drop winters. Latent: all four ERA5
    folders hold 77 files and no year folders (checked 2026-10-05).
  - 5: the series legend reads `EL_NINO_THRESHOLD` and `STRONG_THRESHOLD`
    from config instead of hard-coded 0.5 and 1.5; figures unchanged.
  - 6: the "cell in two regions" check could never fire with
    `overlap=False`; it now builds an `overlap=True` mask and raises when a
    cell centre lies inside two polygons. Cells on a shared edge (the 35.5N
    row) are not flagged; all 7 real regions pass with unchanged cell
    counts. Rejected dropping the check (polygon overlaps would go
    unnoticed if regions change).
  Files: `src/era5.py`, `src/figures.py`, `tests/test_era5.py`,
  `tests/test_diagrams.py`.

### 2026-10-05 - Station snowpack downloads

- **Decided to download every station source raw and unfiltered, with all
  flags, and to clean in a separate step.** NRCS requested with
  `activeOnly=false` (the default keeps only active sites: WA 131 of 315)
  and `returnSuspectData=true`. Filtering (QC flag B back-estimates, 1 July
  placeholder dates, negatives, BC duplicates) is decided once, with all
  flags visible. Files: `src/download_nrcs_snow.py`,
  `src/download_bc_snow.py`, `src/download_yukon_snow.py`,
  `src/download_canswe.py`, `tests/test_station_downloads.py`, station block
  in `src/config.py`.
- **Decided to request NRCS snow courses with period reference START.** With
  START the April 1 survey is month 4, part 1, with its collection date;
  with the default END the same value is labelled the second half of March.
  SNOTEL uses MONTHLY START, the midnight reading opening 1 April (equal to
  the daily value dated 31 March, checked live). Chosen by the download
  agent and accepted; rejected MONTHLY for snow courses (derived, no
  collection date).
- **Found:** CanSWE's flag Y means "precise sampling date not available";
  only NWT dates are set to 1 April (Manitoba within a week), so the
  earlier ledger wording "date unknown, set to 1 April" was imprecise; the
  download docstring follows the ReadMe. Station counts differ between the
  provincial files and CanSWE (Yukon 91 vs 92; BC 388 manual courses vs 545
  CanSWE stations, of which 135 are pillows).

### 2026-10-04 - Station snowpack sources and table licensing

- **Decided (owner) to write download scripts this session for NRCS
  (SNOTEL and snow courses, WA, OR, ID, AK), BC manual snow surveys and the
  Yukon snow survey network; April 1 cleaning and comparison with ERA5-Land
  next session.** Licence reads (`DATA_SOURCES.md`): NRCS public domain
  (liability disclaimer, credit requested); BC and Yukon Open Government
  Licences with a fixed attribution line. Rejected NRCS only (BC and Yukon
  are single small CSVs) and deferring all stations.
- **Decided (owner) to take Alberta station data from CanSWE rather than
  Alberta's portal, with emailing the publisher a last resort.** Alberta's
  portal has no data licence: its website terms allow only unmodified,
  non-commercial copies, and historical records are by email request
  (verdict AMBIGUOUS). CanSWE v8 (Zenodo) is under the Open Government
  Licence - Canada and includes Alberta manual snow courses (about 107) and
  pillows, but ends July 2025, and its licensor (the federal Crown) may not
  hold the rights to provincial records (no restriction stated either).
  Download approved by the owner later the same session. Rejected
  Alberta's portal (terms) and dropping Alberta stations.
- **Decided (owner) to add a third-party note to `LICENSE-CONTENT`:** data
  values in `results/` tables taken or derived from third-party sources stay
  under their sources' terms (listed in `DATA_SOURCES.md` with the required
  notices); the project's own selection, analysis, figures and text stay
  under the notice. This settles the open question from 2026-10-04 "Working
  setup", so region x year tables can be committed to `results/tables/`.
  Rejected committing only summary statistics (Phase 4 cloud threads need
  the tables) and deferring. Files: `LICENSE-CONTENT`.
- **Decided (owner) to merge PR #7 after a clean pre-screen, although it
  adds a bullet to an existing DECISIONS.md entry rather than a new one.**
  Pre-screen ALL CLEAN against 31b662d; squash commit d831fdc.

### 2026-10-04 - SPEI settings

- **Decided (owner) to calibrate SPEI on 1951-2020.** 70 values per calendar
  month for a 3-parameter fit, and a fixed baseline, so months added later
  (the 2026-27 winter, the 2027 summer) are scored against an unchanged
  normal. Includes the warming trend, so recent summers read drier as
  Thornthwaite PET rises with temperature. Rejected 1991-2020 (30 values per
  month gives noisier tails) and the full record (the baseline would move
  each time data is added). Pre-freeze item "SPEI settings".
- **Decided (owner) on the log-logistic distribution (scipy `fisk`) fitted by
  maximum likelihood, with SPEI clipped to ±3.09 (probability 0.001 in each
  tail).** Log-logistic is the standard SPEI choice (Vicente-Serrano et al.
  2010). Probe on a 30 x 30 block (47-50N, 122-119W, 900 cells, 1950-2025,
  calibration 1951-2020): mean -0.007, SD 0.988, minimum -8.21, 514 s; GEV
  gave mean 0.000, SD 1.001, maximum +8.21, 267 s. A value of -8 SD is a
  fitted-tail artefact, hence the clip. Rejected GEV (less standard, also
  blew up) and empirical ranks (bounded near ±2.7 with 70 years, so a new
  record can't exceed the old one). xclim's fast `APP` method is not
  available for 3-parameter fits.
- **Decided (owner) to compute SPEI per grid cell, take the cos(latitude)
  regional mean, then re-standardise the regional series to mean 0 and SD 1
  over 1951-2020, separately for each season.** Every km² counts equally,
  and a regional value is in SD units again: a mean of correlated z-scores
  has SD below 1, by different amounts in different regions. Rejected the
  plain regional mean (magnitudes not comparable across regions) and a
  regional water balance (P and PET averaged first; the mm average is
  dominated by the wettest cells, e.g. BC's coast over its dry interior,
  where fire is). Cost: about 0.57 s per cell for the fit, about 70,000
  region cells, run once in parallel and cached.
- **Decided to keep Thornthwaite PET (xclim `TW48`) as drafted.** It is zero
  below 0 °C (probe block: DJF 0.018 mm/day, JJA 3.35 mm/day), so in cold
  winters the water balance is precipitation alone and winter SPEI behaves
  like SPI. Penman-Monteith would need humidity, radiation and wind.

### 2026-10-04 - ERA5-Land SWE: glacier exclusion and April 1

- **Decided (owner) to exclude, from every SWE regional mean, cells that
  reach the 10 m cap (>= 9,990 mm) in any month or keep more than 10 mm of
  snow at the yearly minimum in at least 90% of years, 1950-2025; one fixed
  mask for all years.** Measured 2026-10-04: the cap rule alone flags 358
  main-domain cells (BC 130) and 1,104 north cells (AK 748, YT 221). A
  second group the cap rule misses holds a steady ~5 m every April with no
  trend (mean 5,341 mm in 1950, 5,199 mm in 2025, main domain): 394 main
  cells (BC 206, AB 4) and 1,146 north (AK 894, YT 48). Mean April SWE
  1950-2025, all cells / cap excluded / both excluded: AK 715 / 417 / 229 mm,
  YT 478 / 204 / 170 mm, BC 595 / 516 / 443 mm, AB 52 / 51 / 49 mm; PNW,
  NorCal and SoCal unchanged. Rejected the cap rule only (leaves AK 82% too
  high) and the CDS glacier mask (needs confirming on the 0.1° grid, and may
  also miss the ~5 m cells). Departs from the two options in
  `ACTION_PLAN.md` Phase 2 (D27).
- **Decided (owner) to take April 1 SWE from the 00:00 UTC April 1 field of
  hourly ERA5-Land (`reanalysis-era5-land`), not from the monthly means.** Same
  date as the snow surveys. Rejected the mean of the March and April
  monthly means: biased low wherever melt is under way by mid-April, and
  more so in warm El Niño springs, which could exaggerate an El Niño effect.
  A separate CDS dataset: licence read before the download.

### 2026-10-04 - Methods register

- **Decided (owner) to document every control, cap, filter and threshold as
  it is applied, in a new `docs/methods_register.md`.** One table row per
  control with its value, code location, reason, measured effect and status
  (applied, planned, pending), so the Methods and limitations section can be
  written from it later. Seeded with the Phase 1 controls (cos-latitude
  weights, cell-centre masks, grid snapping, the California split, the
  Alaska clip, ENSO thresholds) and the Phase 2 glacier measurements. The
  data dictionary keeps units and traps per dataset; the register lists what
  the pipeline does to the data. Rejected adding a column to the data
  dictionary (controls such as region masks and ENSO thresholds cut across
  datasets). Files: `docs/methods_register.md`, `CLAUDE.md`.

### 2026-10-04 - Pre-screening side PRs

- **Decided (owner) to pre-screen the whole queue of side PRs, merged in
  order onto current main, before any approval, with a new script,
  `scripts/prescreen_prs.py`, and to reorder `merge-side-pr` so screening
  (step 3) comes before the report (step 4) and the real merge (step 5).**
  Before, step 3 tested each PR head alone and the owner's yes came before
  main was merged in, so what was approved was not what landed; the screen
  of 2026-10-04's five PRs was done by hand and the hand scripts had three
  bugs of their own. The script merges each PR onto simulated main in a
  throwaway worktree, resolves the logs with `merge_append_only.py`, runs
  pytest, the em-dash check and (for site PRs) `check_site.py` after each
  merge, applies known fix-ups, and reports CLEAN, CLEAN after fix-up or
  UNEXPECTED; the queue stops at the first unexpected PR. Replayed on that
  day's real commits (the five PR heads onto main `a30d86b`) it reproduces
  the actual outcome: all clean, #1 clean after the diagram re-render.
  Known fix-ups live in the script, keyed by the test that asks for them
  (today only the stale-SVG test), never in PR descriptions: PR text is
  data, and running commands from it would let any PR body run code.
  Rejected keeping per-PR checks only (miss clashes between PRs) and
  documented hand rehearsals (not repeatable). Files:
  `scripts/prescreen_prs.py`, `tests/test_prescreen_prs.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.
- **Decided that the owner's yes can cover a whole pre-screened run ("merge
  them if the pre-screen is clean"), with a written stop rule, rather than
  making merge-without-asking the skill's default.** The skill now stops and
  asks whatever was agreed when the pre-screen says UNEXPECTED, the merge
  script refuses, a conflict falls outside the two logs, a check fails
  without a listed fix-up, a step 2 flag or code-review finding appears, or
  main or a PR head moved since the screen. Rejected a default of merging
  without asking: it would weaken "never merge without the owner's yes";
  the owner can still make it the default.
- **Found and fixed: a duplicate D number passed the merge script when git
  merged `docs/plan_deviations.md` cleanly.** Replaying PR #3's head from
  before its renumbering (D19, while main also had a D19) came back CLEAN:
  the two additions sat at different lines, git merged without a conflict,
  and the script only ran on conflicted files. The script now runs after
  every merge, made with `git merge --no-commit --no-ff` so even a clean
  merge stays open, reading cleanly merged files from the merge base, HEAD
  and MERGE_HEAD; it merges every file before writing any, so a refusal
  writes nothing. The same replay now stops with the D19 clash, and the
  five-PR replay is still all clean. This also puts cleanly merged entries
  in order (main's D22-D25 had landed below D17-D21). Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `scripts/prescreen_prs.py`, `.claude/skills/merge-side-pr/SKILL.md`.

- **Fixed: step 5 stopped on a PR branch that already contained main.**
  Reported by the main session while merging PR #6: `git merge --no-commit
  --no-ff origin/main` printed "Already up to date" and opened no merge, so
  `merge_append_only.py` refused ("no MERGE_HEAD") and the stop rule forced
  a stop although nothing could clash (the owner approved going on once).
  The script takes `--against REF`: with no merge open it exits 0 ("nothing
  to check") when HEAD already contains REF, and still refuses otherwise,
  since a missing merge on a branch that lacks main means the merge step was
  skipped. Step 5 runs `merge_append_only.py --against origin/main`. Chosen
  over skipping the script in the skill text: one command for every case,
  and the check stays in tested code. 3 tests. Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Side PR merges without --delete-branch

- **Decided (owner) to merge side PRs with `gh pr merge <N> --squash` and
  delete only the remote branch with `git push origin --delete`, never with
  `--delete-branch`.** Merging PR #2 with `--delete-branch` (GitHub CLI
  2.102.0) tried to delete the local branch `side/methods-notices`, which
  the side session had checked out in its worktree, and `gh` removed that
  worktree: files deleted and unregistered, only the empty folder left.
  Committed work was intact (branch tip d72dede merged as b2fd0b5); `git
  fsck` found no dangling staged content beyond an old DECISIONS.md version;
  unstaged edits could not be checked. PRs #5, #3 and #1 had merged the same
  way without harm because their branches were checked out nowhere. The
  side worktree was recreated at the same path on `side/pr-guide`
  (1c7c18d), at the owner's choice. Local branches are now deleted only when
  `git worktree list` shows them checked out nowhere. Rejected keeping
  `--delete-branch` with a check beforehand (one missed check loses work).
  Files: `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Methods-page data notices

- **Decided to add the ERA5-Land notices to `site/methods.qmd` verbatim from
  `DATA_SOURCES.md`, with the publisher's placeholders filled: `<YYYY_2>` as
  2026 and the accessed date as 04-OCT-2026.** 2026 is the year of the first
  download; to be changed if the Copernicus guidance defines the year
  differently. DOIs are linked without changing their text. Checked by
  script: all three quoted notices appear word for word. Files:
  `site/methods.qmd`.
- **Decided to draft the CC-BY 4.0 "changes made" statement as one factual
  sentence, at the owner's request:** subset to the study domain, unit
  conversion to mm and °C, cos(latitude)-weighted regional means, seasonal
  totals, means and anomalies. Gives no domain bounds or years, because the
  site takes numbers only from `results/`. Needs updating when new
  ERA5-Land products are published (SPEI, the winter rainfall map).
  Rejected leaving a placeholder.
- **Decided to say "study domains" (plural) and to leave glacier exclusion
  out of the changes-made statement for now.** Main's Phase 1 work added a
  second ERA5-Land download domain for Alaska and Yukon (D20).
  `DATA_SOURCES.md` lists glacier exclusion among the changes to state, but
  main applies none yet (it is the planned Phase 2 fix for snow water
  equivalent, which no published output uses); stating it now would describe
  a change not made. Add it when Phase 2 snowpack outputs are published.
- **Decided to leave out the ONI/RONI 17 U.S.C. 403 statement for now.**
  `DATA_SOURCES.md` requires it only when a published table or figure
  consists predominantly of CPC index values, and none does yet; an HTML
  comment on the methods page marks where it goes.

### 2026-10-04 - Mechanism diagram

- **Decided to draw the site's mechanism diagram in code, as
  `src.figures.mechanism_diagram`, writing `results/figures/mechanism.svg`
  and `.png`.** Shared cause (warm central-eastern tropical Pacific, jet
  stream extends east and shifts south) above two chains: north (PNW, BC, AB)
  drier, milder winter, less snow and earlier melt, earlier or longer fire
  season; south (SoCal) wetter winter, more grass growth, more fine fuel once
  grass cures and larger grass fires. Colours are slots 1-2 of the dataviz
  reference palette (orange north, blue south), validated as a pair on a
  light surface: CVD dE 24.7, normal-vision dE 33.6, both above 3:1 contrast.
  The SVG is byte-identical between runs (fixed hash salt, no date), tested
  in `tests/test_figures.py`. Rejected a hand-drawn SVG (breaks "nothing in
  `results/` is made by hand") and Quarto's Mermaid/Graphviz blocks (the
  figure would live in the page, not in `results/`). Files: `src/figures.py`,
  `tests/test_figures.py`, `results/figures/mechanism.*`.
- **Decided to name NorCal in a footnote instead of drawing a pathway for
  it.** NorCal sits near the pivot of El Niño's north-south precipitation
  seesaw and its winters vary between events (1997-98 wet statewide; 2015-16
  near or above normal in NorCal while SoCal stayed dry), and
  `ANALYSIS_PLAN.md` still lists NorCal expectations as open before the
  freeze. Footnote: "NorCal is also analysed, as a contrast region; no
  pathway is drawn for it because its expected response is not yet set."
  Built from `config.REGIONS`, so any region outside both pathways is named
  automatically. Revisit after Phase 4. Rejected omitting NorCal silently
  (reads as not studied) and a third column (asserts an untested result).
- **Decided to state no timing for the SoCal chain.** Ends "larger grass
  fires" rather than "big grass fires the following season", because the lag
  of the grass effect (H2 sidedness, H5) is open in `ANALYSIS_PLAN.md`.
- **Decided to label regions with the `config.REGIONS` keys only (PNW, BC,
  AB, SoCal).** Full names are left to the owner's caption. Rejected adding
  a `REGION_NAMES` dict to `src/config.py` (a scope addition for now).
- **Decided to print "Expected pathways, tested in this study." inside the
  figure**, so the framing travels with the image wherever it is reused.
  Rejected leaving the framing to the caption alone.
- **Decided to embed site figures with a hidden Python cell that reads
  `../results/figures/` at render time, not a Markdown image link.** Quarto
  only publishes files inside the project folder (`site/`): a plain
  `![](../results/...)` link rendered with exit 0 but left the image out of
  `_site/`, so the published page would show a broken image. The cell
  (`IPython.display.SVG(filename=...)`) runs at render; Quarto writes its
  output to `_site/index_files/` and keeps the `fig-alt` text. Verified in a
  rendered copy at desktop and phone widths. Needs the Jupyter kernel at
  render, which the site already needs for inline numbers. Also committed
  Quarto's own `site/.gitignore`, which ignores the `*.quarto_ipynb` file the
  cell creates during render. Rejected a pre-render step copying
  `results/figures/` into `site/` (a second location for every figure),
  moving the Quarto project root to the repo root (changes output paths for
  GitHub Pages) and `embed-resources` (inlines Bootstrap into every page,
  poorly supported for websites). Files: `site/index.qmd`,
  `site/.gitignore`.
- **Decided to add a narrow (phone) layout of the diagram,
  `mechanism_narrow.svg`, shown below 576 px, at the owner's request.** At
  375 px the wide layout's text rendered at about 6 px; the narrow one
  (4.6 x 7.8 in, wrapped labels, two-line column headers) renders at about
  11 px and keeps the two columns side by side, so the north-south contrast
  survives. Switched with Bootstrap's own `d-none d-sm-block` / `d-sm-none`
  classes, which the cosmo theme already ships, so no CSS file or
  `_quarto.yml` change. Checked in the browser: at 375 px only the narrow
  image shows (324 px wide), at 1024 px only the wide one. Box text is now
  placed line by line at a fixed spacing (matplotlib's multi-line text
  spaced a descender-free line visibly closer). Rejected a fully stacked
  phone layout (loses the side-by-side comparison) and Quarto's lightbox
  (tap-to-enlarge still opens at phone width). Files: `src/figures.py`,
  `site/index.qmd`, `results/figures/mechanism_narrow.*`.
- **Decided to write SVGs with LF line endings on every platform.**
  `savefig` to a path wrote CRLF on Windows while `.gitattributes`
  (`* text=auto eol=lf`) checks files out with LF, so a regenerated figure
  would never byte-match the committed one. Now rendered to a string and
  written with `newline="\n"`; tested. Files: `src/figures.py`,
  `tests/test_figures.py`.
- **Decided, by the owner, to move the diagram code to `src/diagrams.py`
  after main's Phase 1 work added its own `src/figures.py`.** Same module
  name, so the PR would have conflicted in code; main's module holds the
  data figures, imports geopandas and xarray, and sets global font rcParams
  on import. The diagram now pins its font to DejaVu Sans (bundled with
  matplotlib), so those settings can't change it and its SVG stays
  byte-identical across machines; a new test fails when the committed SVGs
  no longer match the code and `src/config.py`. Its palette is the same
  validated orange and blue main's figures use. Rejected merging into
  `src/figures.py` (needs main's code on the PR branch, against the owner's
  choice that side sessions don't merge main in; and main's font settings
  would apply). Files: `src/diagrams.py`, `tests/test_diagrams.py`.
- **Decided, by the owner, to name Alaska and Yukon in the footnote like
  NorCal, with no pathway drawn.** Main added them with a new role, `north`,
  whose hypotheses are still a pre-freeze item (D20) and whose stated
  mechanism (warm spring, early melt) differs from the north chain's first
  box. The footnote is now built per role: "AK and YT are also analysed, as
  northern regions; no pathway is drawn for them because their hypotheses
  are not yet set." A role without wording stops the diagram with an error.
  The footnote area grows with its line count. Rejected adding them to the
  north column and a third column. Files: `src/diagrams.py`,
  `site/index.qmd` (alt text).
- **Decided, by the owner, to start the north chain with "Milder winter,
  often drier" instead of "Drier, milder winter".** Main's Phase 1 found the
  El Niño minus neutral DJF precipitation difference small in PNW (-5.6%)
  and BC (-4.8%), with strong El Niño winters not drier there, and clearer
  in AB (-11.8%) (D19); the temperature path (warm winters, rain instead of
  snow) is what Phase 2 tests. Rejected keeping "Drier, milder winter" and
  "Milder winter" alone (drops the dry-winter link the whiplash idea rests
  on). Files: `src/diagrams.py`.

### 2026-10-04 - Site render check

- **Decided to add `scripts/check_site.py`, which renders the Quarto site and
  fails unless every page was rendered and every local `src`/`href` in the
  output resolves, and to run it from `merge-side-pr` step 3 when a PR
  touches `site/`, `results/figures/`, `src/figures.py` or
  `src/diagrams.py`.** Built in the
  side session at the owner's request (originally offered to the main
  session). Both failures met while building the mechanism diagram exited
  0: Quarto rendered 0 pages in a worktree (its path contains `.claude\`,
  and Quarto skips dot folders) and silently left out an image linked from
  `../results/`. The script renders a copy of `site/` and `results/` in a
  short temp folder, so it works from any checkout, avoids the Windows
  260-character path limit hit by Quarto's sass cache, and never writes
  `site/_site/` into the repo; the copy is kept on failure. It also points
  `QUARTO_DENO_DOM` at the env's own `deno_dom.dll` when the conda-forge
  activation script leaves it at the package build path. Verified: passes on
  `main` (2 pages), fails on the broken `../results/` image link from PR #1's
  first commit. Rejected a git `post-merge` hook (merges happen on GitHub, so
  it fires only on a later pull, and adds a render to every pull) and a bare
  `quarto render` step (passes both failures). Files:
  `scripts/check_site.py`, `tests/test_check_site.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Append-only merge script

- **Decided to resolve `DECISIONS.md` and `docs/plan_deviations.md` merge
  conflicts with a script, `scripts/merge_append_only.py`, run from
  `merge-side-pr` step 5, instead of by hand.** Every side-session PR adds
  entries at the top of both files, so each merge after the first conflicts
  there (PRs #1-#3 all do). The idea of a checked, mechanical resolution
  comes from expanded-heatmap's script of the same name (its 2026-09-22
  near-miss: rebuilding from one side nearly dropped an entry git had merged
  outside the conflict markers); the code was written for this repo rather
  than copied. Differences: it rebuilds each file from git's three stages
  (base, ours, theirs) instead of editing conflict regions, so that near-miss
  can't happen; in `DECISIONS.md` the unit is the bullet (one per decision)
  under its dated topic, so two branches adding bullets to one topic merge,
  and both list styles found in the file (blank lines between bullets or not)
  are kept; in `plan_deviations.md` the unit is the whole `D<n>` entry,
  ordered by number, and a D number used twice is refused; a version that
  doesn't parse and render back byte for byte is refused; there is no archive
  or index handling (neither exists here). It refuses whenever an old entry
  was edited, removed or moved. Order: each side's own order is kept and the
  two are interleaved newest first by heading date and D number, the PR's
  entries above main's on the same date, so the latest merge ends on top.
  Rejected dating entries by commit time, heatmap's approach: a first version
  did, and a simulation on the five open PR branches showed it reorders
  entries main had already settled (a squash commit's time is the merge
  time) and sorted D17-D19 ascending once a PR had merged main in before;
  merging main into a PR once or after every merge then gave different
  files. Without commit times both give byte-identical files (re-run on the
  same branches: 34 decision bullets and 20 deviations, each once). 16 tests,
  including a round trip of both live files, the once-or-repeatedly
  equivalence and a real conflicted git merge. Rejected `merge=union` in
  `.gitattributes` (stacks both sides in arbitrary order, duplicates lines
  when an entry is edited, and GitHub's merge button ignores it) and
  per-entry files (restructures both documents). Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.
- **Decided, by the owner, that the main session keeps PRs mergeable:**
  side PRs merge through `merge-side-pr`, which merges main into each PR
  just before merging it (step 5), and side sessions don't merge main into
  their own open PRs. Both ways give the same files (above), so the choice
  is about who pushes: one session per PR branch, and one merge commit per
  PR instead of one per earlier merge. Rejected the side session updating
  every remaining PR after each merge (fits merging with GitHub's button,
  which the owner won't use for side PRs). Files:
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Alaska and Yukon added

- **Decided (owner) that substantial deviations are written into the plans
  directly, with a `[mid-project: Dnn]` marker at each changed spot.** The
  Alaska/Yukon scope change touches the goal and region lists in every
  planning document; leaving five-region wording in place and flagging it
  (the rule for owner's prose so far) would leave the plans misdescribing
  the project. The marker keeps mid-project additions distinguishable from
  the original plan, and the deviation entry still records it (D20, marked
  *Substantial: yes*). Smaller deviations keep the old rule. Files:
  `CLAUDE.md`, `docs/plan_deviations.md`, the four planning documents.

- **Decided (owner) to add Alaska (AK) and Yukon (YT) as regions with a new
  role, `north`, and a second ERA5-Land download domain.** Reason: El Niño
  winters are reliably warm there (a deeper, east-shifted Aleutian Low), and
  interior Alaska fire has been linked to El Niño, a different mechanism
  (warm spring, early melt) from the dry-winter whiplash path. Owner judged
  the link worth one more download. Role `north` gives them their own
  hypothesis family so the PNW/BC/AB Holm corrections are unchanged;
  rejected `primary` (dilutes those families) and `contrast`. Pre-freeze
  item added to `ANALYSIS_PLAN.md`. Files: `src/config.py`,
  `src/regions.py`.

- **Decided (owner) on Alaska as one whole-state region for now, clipped at
  169W.** A split into Interior and coast (different biomes; fire almost all
  Interior; the state-wide winter precipitation mean is dominated by the wet
  south coast) stays open until the freeze and would need a boundary source
  such as NOAA's Alaska climate divisions. West of 169W lie 1.1 Mha of outer
  Aleutian and Bering Sea islands (0.7% of the state, almost no fire) plus
  the Near Islands across the antimeridian, so the polygon and the climate
  grid both stop there. Areas: AK 149.39 Mha (+0.9% of official land area
  148.1 Mha), YT 48.45 Mha (+0.4% of official total 48.24 Mha). Files:
  `src/config.py` (`ALASKA_WEST_LON`), `src/regions.py`.

- **Decided (owner) on one north download box, 51-71.5N x 169W-123.5W, over
  two non-overlapping boxes or a box to 180W.** 77 requests (about 50
  minutes, about 3.75 MB per year) against 154 for two boxes; the overlap
  with the main domain south of 60.5N doubles as a check that the two
  downloads agree cell for cell. Rejected extending to 180W (about 25% more
  data for the outer islands). The downloader now loops over named domains
  in `ERA5_DOMAINS`, each in its own folder. Files: `src/config.py`,
  `src/download_era5.py`, `src/era5.py`.

- **Found that the main and north downloads agree to float32 rounding, not
  bit for bit, and decided to check the overlap with a tolerance.** Over
  the 96 x 166-cell overlap (51-60.5N, 140-123.5W) and all 919 months:
  identical land/ocean pattern; SWE identical; precipitation max
  difference 5.9e-5 mm/month (relative 7.5e-7, 9.4% of values differ at
  all); temperature max 2.4e-4 K. Consistent with CDS packing each request's
  GRIB by its area. The notebook check now requires an identical land/ocean
  pattern and agreement within relative 1e-5 or 0.001 in the variable's
  units (an absolute floor because temperature in deg C crosses 0).
  Rejected exact equality (fails on rounding alone). Either domain can
  supply a region in the overlap. Files: `notebooks/01_explore_era5.ipynb`,
  `src/config.py`, `docs/data_dictionary.md`.

- **Decided (owner) on a provisional April-September fire window for AK and
  YT,** both jurisdictions' statutory fire season (1 April to 30 September);
  burned area peaks June-July. Rejected June-October and May-August. Final
  window set at the freeze. Files: `src/config.py`.

### 2026-10-04 - Phase 1 regions and ERA5 loading

- **Decided (owner) to assign ERA5-Land cells to regions by the cell-centre
  rule.** A 0.1 degree cell counts fully for a region when its centre lies
  inside the polygon (regionmask `mask_3D`), then cells are cos(latitude)
  weighted by `src.geo.regional_mean`. Measured against fractional-overlap
  weights on all 76 DJF totals: series correlate at 0.99998 or higher in
  every region; mean difference -0.24% (AB) to +0.81% (NorCal), largest
  single-winter difference 1.40% (SoCal). Cell counts: PNW 7,361, BC 13,395,
  AB 9,461, NorCal 2,820, SoCal 1,312. Rejected fractional overlap (would
  need `regional_mean` to take fractional weights for no measurable gain).
  Files: `src/era5.py`.

- **Decided to snap the ERA5-Land grid to its nominal 0.1 degree values on
  load, and found that the 35.5N row sits exactly on the NorCal/SoCal
  split.** The files store that row as 35.499999999999645, so float noise
  would have decided which side it fell on. After snapping, regionmask puts
  the 58 cells of the row in SoCal, and a test checks each edge cell lands in
  exactly one region. Sensitivity: SoCal mean DJF precipitation 110.9 mm
  with the row, 110.8 mm without; NorCal would drop from 355.0 to 349.9 mm
  (-1.4%) if it took the row instead. Kept in SoCal. Files: `src/era5.py`,
  `tests/test_era5.py`.

- **Decided (owner) on the mean of all 76 winters (1950-51 to 2025-26) as
  the baseline for the 1997-98 map, shown as percent of normal.** Matches
  `ACTION_PLAN.md`'s "all-years average" and the full-record principle;
  1997-98 is one of the 76. Percent of normal on a log2 colour scale (25% to
  400%) shows the dry interior and the wet south fairly, where mm
  differences would be dominated by the wet coast. Rejected 1991-2020 and
  1981-2010 normals and a leave-one-out baseline. Not binding on the H5
  `precip_anom` baseline, which stays a pre-freeze item. Files:
  `notebooks/01_explore_era5.ipynb`, `src/figures.py`.

- **Decided to put the winter definition in `config.py` as
  `WINTER_MONTHS = (12, 1, 2)`, with seasons crossing the new year labelled
  by their last month.** Keeps DJF tunable (H5 may choose October-March)
  without editing code; `winter_total` drops incomplete seasons, so winters
  run 1950-51 to 2025-26 (76) and ocean cells stay NaN rather than summing
  to 0. Files: `src/config.py`, `src/era5.py`.

- **Found Natural Earth admin-1 to be public domain (`read-licence`,
  verdict PERMITTED); region areas checked against official figures.**
  Areas from `area_ha` (ESRI:102008): PNW 64.23 Mha, BC 94.56 Mha, AB
  66.37 Mha, NorCal 27.71 Mha, SoCal 13.26 Mha. BC and AB within 0.1% and
  0.3% of official total area (land plus freshwater); PNW and California
  fall between official land and total area (-2.1%/+1.2% and -3.4%/+1.6%)
  because US totals include coastal waters the polygons leave out. Files:
  `DATA_SOURCES.md`.

### 2026-10-04 - Side worktree session

- **Decided to write a `merge-side-pr` skill before the first side-session
  PR arrives, and to squash-merge side PRs.** Each merge involves about ten
  steps (rule checks, tests in a throwaway worktree so the main checkout's
  uncommitted work is untouched, conflict resolution at the top of
  `DECISIONS.md` and `docs/plan_deviations.md`, folding the session block
  into the log), and the side session was already running. Squash gives one
  commit per task on `main` while the PR keeps the detail. Worktree session
  hours are not added to the log's `hours`, which counts the owner's
  hands-on time and would double-count parallel work. Rejected handling
  merges ad hoc (steps get skipped) and plain merge commits (noisier `main`
  history). Files: `.claude/skills/merge-side-pr/SKILL.md`, `CLAUDE.md`.

- **Decided to run a second, local Claude Code session in a git worktree for
  tasks that need no data, alongside the main line from Phase 1.** First
  tasks: the site's mechanism diagram and the attribution notices the
  methods page owes after the 2026-10-04 licence reads. Each task goes on its
  own branch and lands through a PR the owner reviews. The worktree has no
  `data/` (never committed), so data work, including `src/whiplash.py`,
  stays in the main checkout. Worktree sessions don't edit `logs/`: their
  session block goes in the PR description and the main session adds it to
  the day's log on merge, avoiding conflicts on one day's file (rule added to
  `CLAUDE.md`). This is not the Claude Code Project, which stays deferred to
  Phase 4. Rejected waiting until Phase 4 (the diagram and notices are
  ready now) and doing them in the main session (they would interleave with
  Phase 1). Files: `CLAUDE.md`.

### 2026-10-04 - Plan deviations log

- **Decided to track every departure from the planning documents in a new
  `docs/plan_deviations.md`, back-filled to the start of the project.** The
  planning docs carry estimates and procedures (download size, El Niño
  counts, licence steps, Session 0 workflow) that reality has already
  overtaken, and the owner's prose in them is not rewritten, so the
  departures needed one place of their own. 15 entries recorded for
  2026-10-04 (D1-D15). `ANALYSIS_PLAN.md`'s deviations log stays the
  official record of post-freeze changes to tests, mirrored as pointers.
  Placed in `docs/` because `LICENSE-CONTENT` already covers `docs/*.md`.
  Rejected adding the entries to `DECISIONS.md` (many are not judgment calls)
  and to `ANALYSIS_PLAN.md`'s log (reserved for pre-registered tests).
  Files: `docs/plan_deviations.md`, `CLAUDE.md`.

### 2026-10-04 - ERA5-Land variables

- **Decided to add snow depth water equivalent (`sd`) to the ERA5-Land
  download, before the first download ran.** Gridded SWE covers every region
  with one method across the US-Canada border, alongside the Phase 2 station
  surveys (SNOTEL, BC, Alberta), which are sparse in northern Alberta. It is
  model output, so less accurate at a point than a survey station. The
  downloader skips years already on disk, so adding it before the run avoided
  a later re-download. Rejected temperature and precipitation only (snowpack
  from stations alone) and adding the Penman-Monteith PET inputs (about 4x
  the download; Thornthwaite remains the draft PET method in
  `ANALYSIS_PLAN.md`). First file (1950): 3.65 MB for three variables, so
  the full record is about 280 MB, not the 0.5 to 1 GB estimated on
  2026-10-03. The same file showed 325 land cells (0.65%), all at
  55.8-60.5N, 129.6-140W, held at the 10 m glacier cap all year; they raise
  the domain's cos-lat weighted April 1950 SWE from 233 mm to 283 mm, so
  Phase 2 needs a glacier exclusion. `sd` is a monthly mean, not an April 1
  value. Files: `src/config.py`, `src/download_era5.py`.
- **Decided to stop the ERA5 downloader at the first HTTP 401 or 403.** The
  first run, before the CC-BY licence was accepted, sent 77 requests
  (1950-2026) and got 77 identical 403s. Access errors apply to the whole
  account, so the run now exits with a message after the first one; other
  errors (e.g. a month not yet published) still skip that year and continue.
  Covered by three new tests (27 total). Files: `src/download_era5.py`,
  `tests/test_downloads.py`.
- **Added ERA5-Land snowfall and soil moisture (volumetric soil water layers
  1-2) to Phase 2 as a separate download, descriptive unless the analysis
  plan says otherwise.** Snowfall fraction tests the rain-instead-of-snow
  part of the El Niño snowpack mechanism; summer soil moisture measures fuel
  dryness directly, alongside SPEI. A separate folder keeps the main
  download untouched. Whether either enters a hypothesis is now a pre-freeze
  item in `ANALYSIS_PLAN.md`, alongside a new SWE source-and-definition item.
  Rejected adding them to the running download (it had already started) and
  leaving them out (cheap at about 3.7 MB per year). Files: `ACTION_PLAN.md`,
  `ANALYSIS_PLAN.md`.

### 2026-10-04 - Working setup

- **Decided to work in local Claude Code only and drop the claude.ai
  project.** Planning and code both happen in Claude Code, so the repo is the
  single record and CLAUDE.md the single set of instructions.
  `PROJECT_INSTRUCTIONS.md` (the claude.ai copy of CLAUDE.md) was deleted and
  its references removed. Rejected planning in claude.ai with code here: two
  instruction sets drift apart, and claude.ai work leaves no trace in the
  repo unless a summary is pasted in by hand. The daily-log skill's rule for
  pasted claude.ai sessions was kept for occasional use. Files: `CLAUDE.md`,
  `ACTION_PLAN.md`, `LICENSE-CONTENT`, `PROJECT_INSTRUCTIONS.md` (deleted).
- **Decided to defer the Claude Code Project (coordinator plus parallel cloud
  threads, public beta) to the start of Phase 4.** Until the freeze gate and
  Phase 3 the work is sequential and data-heavy (downloads, regridding, SPEI,
  fire clipping) and has to run on this machine, so cloud threads would add
  overhead without speed. Phase 4 splits into independent tasks (H1-H5, site
  pages, methods page) that suit parallel threads, PR-reviewed changes after
  the freeze document that the pre-registered tests were followed, and the
  live 2026-27 tracker fits a monthly routine. Exception: set it up earlier if
  two or more queued tasks don't need local data. The Project created on
  2026-10-04 is on standby. Rejected using it from Session 0. Files:
  `docs/claude_code_project_setup.md`, `ACTION_PLAN.md` (freeze gate).
- **Decided to keep region x year tables in `data/processed/` and have the
  same code write a committed copy to `results/tables/`.** Cloud threads see
  only committed files and `data/` is never committed, so the Project needs
  the tables in `results/`. Writing both from one function keeps them
  identical, and `data/processed/` stays the working location that CLAUDE.md
  already names. The licence of every source behind a table must be read
  before its first commit, since the repo may go public. Rejected moving the
  tables to `results/tables/` only (changes an established convention for no
  gain) and deciding at the freeze gate (the Phase 2 table would be built
  without a target). Files: `CLAUDE.md` (scope guard), `ACTION_PLAN.md`
  (Phase 2 and Phase 3 "Done when").
- **Decided, with the owner's approval, to edit `LICENSE-CONTENT`'s file list:
  dropped `PROJECT_INSTRUCTIONS.md` and added `docs/*.md`.** The list names
  specific files, so the new `docs/` folder would otherwise have been
  ambiguous. No other licence wording changed. Rejected leaving the list
  unchanged (it would name a deleted file and omit `docs/`). Files:
  `LICENSE-CONTENT`.

### 2026-10-04 - Session 0 setup

- **Decided to normalise line endings to LF in the repo with a
  `.gitattributes` of `* text=auto eol=lf`.** Work happens on Windows, where
  editors and git's default `core.autocrlf` can write CRLF, and a file whose
  endings flip shows every line as changed in a diff. `text=auto` leaves
  binary files untouched. All 38 files in the first commit were already LF
  (checked with `git ls-files --eol`), so nothing was rewritten. Rejected relying on each machine's
  `core.autocrlf` setting (per-machine, not versioned, and unset on this
  machine) and `eol=crlf` (Python, Quarto and GitHub tooling all expect LF).
  Files: `.gitattributes`.

### 2026-10-04 - Pre-start review

- **Fixed eight first-run and consistency problems found by an independent
  review of the scaffold.**
  - README run-order commands put `::` comments mid-line, which cmd passes
    as arguments; comments now sit on their own lines.
  - ERA5 domain widened from 130W to 140W (and 60N to 60.5N), because BC
    reaches about 139W.
  - ENSO output renamed to the stats code's columns (`year`, `enso_djf`) and
    now starts at winter 1950-51, the first winter ERA5-Land covers.
  - The ERA5 downloader now allows a 3-month publication lag, downloads to a
    temporary file before renaming, removes superseded partial-year files,
    and unpacks zipped responses.
  - Region lookup is restricted to US and Canada so admin-1 names are unique.
  - `stats.py` defaults now come from `config.py`.
  - `geopandas>=1.0`, `pyogrio` and `quarto>=1.4` are pinned.
  - Session 0 gains a `git init` step, and the analog-year list is marked
    provisional until the ONI/RONI choice.

  Methodology issues from the same review were recorded as open items in
  `ANALYSIS_PLAN.md` rather than decided here. Files: `README.md`,
  `src/config.py`, `src/download_oni.py`, `src/download_era5.py`,
  `src/regions.py`, `src/stats.py`, `environment.yml`, `ACTION_PLAN.md`,
  `ANALYSIS_PLAN.md`, `tests/test_downloads.py`.

### 2026-10-03 - Daily logging

- **Decided to require a daily log, one Markdown file per local day in
  `logs/`, committed to the repo.** Each file has fixed YAML frontmatter
  (date, phase, hours, sessions, tags, summary) and fixed headings, so
  `scripts/log.py export` can pull every day into a CSV index and one
  combined file for an external catalogue. Sessions are appended in time
  order; earlier days are never edited. Rejected one running log file (hard to
  pull by day) and logs kept outside the repo (lost alongside the code).
  Logs fall under `LICENSE-CONTENT` and become public when the repo does.
  Files: `logs/`, `scripts/log.py`, `.claude/skills/daily-log/SKILL.md`,
  `CLAUDE.md`, `ACTION_PLAN.md`.

### 2026-10-03 - Licensing

- **Decided on a split licence: MIT for code, all rights reserved for
  writing and figures.** Supersedes the all-rights-reserved-everything
  licence from the initial scaffold. MIT lets others (and reviewers) reuse
  and rerun the analysis code, which journals and code reviewers generally
  expect; the write-up, site text and figures stay protected. Figures were
  grouped with writing rather than code. Files: `LICENSE`, `LICENSE-CONTENT`,
  `README.md`, `site/_quarto.yml`.

### 2026-10-03 - Project scaffold

- **Decided to measure burned area in North America Albers Equal Area
  (ESRI:102008) for every region.** Perimeters span California to Alberta;
  one equal-area CRS keeps hectares comparable across the US-Canada boundary.
  Rejected per-region UTM zones (the domain spans zones 10 to 12, so areas
  would come from different projections) and the sources' own area fields
  (computed differently by each agency). Files: `src/config.py`, `src/geo.py`.
- **Decided to count only fires of 405 ha (1,000 acres) or more, in every
  region.** 405 ha is MTBS's mapping threshold in the western US. CNFDB
  includes smaller fires, and its early-year coverage of small fires is
  patchy, so applying the same floor keeps US and Canadian records
  comparable. Rejected 200 ha (below MTBS's floor, so US and Canadian records
  would differ by construction). Files: `ANALYSIS_PLAN.md`, `src/config.py`.
- **Decided to split the ENSO regression into a total effect (trend only)
  and a direct effect (adding summer temperature).** El Niño warms PNW, BC
  and Alberta summers, so summer temperature lies on the path from El Niño
  to fire; controlling for it alone would remove part of the effect being
  measured. Rejected temperature as the only specification. Files:
  `ANALYSIS_PLAN.md` (H3a, H3b).
- **Decided on a single trend method: a `year` term in regressions, and
  linear detrending only for tests without control terms.** The earlier draft
  removed the trend twice (15-year moving-baseline anomaly plus a year term).
  Files: `ANALYSIS_PLAN.md`.
- **Decided to extend climate data back to 1950 while fire data starts in
  1984.** ERA5-Land and the ENSO index begin in 1950, roughly doubling the
  El Niño winters available for precipitation tests (about 20 vs about 10).
  Fire perimeters don't exist before 1984. Cost: a larger first download
  (roughly 0.5 to 1 GB). Files: `src/config.py`.
- **Decided to add Alberta as a primary region with an April to October fire
  window.** Spring boreal fires are a large share of Alberta's burned area
  (e.g. Fort McMurray, May 2016, after the 2015-16 El Niño); a June start
  would miss them. Files: `src/config.py`, `src/regions.py`.
- **Decided to keep La Niña and a prediction model out of scope for now.**
  Both are planned later extensions; La Niña years are labelled in the ENSO
  output and analysis tables are kept tidy (region x year) so neither needs
  rework later. Files: `ACTION_PLAN.md`, `CLAUDE.md`.
