# Read-only review of ee9503d..b9153a4 and the whole analysis plan (2026-10-07)

Commit reviewed: `main` at `b9153a4` (1 commit, 7 files since `ee9503d`).
Read-only: `git status` clean before and after; scripts in the session
scratchpad outside the repo; no `src` module that writes files was run (only
its functions were imported); pytest with no cache provider and no bytecode
(`.pytest_cache` still dated 2026-10-04); no fire data opened. Order:
CLAUDE.md, data dictionary and ANALYSIS_PLAN first; then the diff, code,
data and recomputation; only then DECISIONS (2026-10-07), plan_deviations
D49-D52, the methods register and the two saved audits.

## 1. What passed

| Check | Result |
|---|---|
| Tests | 213 passed (34 in `test_stations.py` and `test_config.py` alone) |
| Station table | Rebuilt in memory from the raw files with the `src.stations` functions: 71,759 rows and 2,180 stations before the duplicate-site rule, 71,250 and 2,168 after, 18 pairs, 509 rows dropped (PNW 352, YT 123, AK 34); identical to `data/processed/station_swe_apr1.csv` in every id, year, value, source and region; 0 duplicate (station, year) rows; 58 mixed-source ids before the rule, 57 after |
| New priority rule | Replaying the pair loop with diagnostics: exactly one of the 18 pairs is decided by the shared-row rank (09CA-SC04 keeps its 7 years, SC05 loses the 7 CanSWE copies, 85.7% agreement, 0.00 km); 0 pairs where the shared ranks tie and the whole-id rank chose the keeper; no id keeps in one pair and loses in another |
| Station index | Recomputed from the rebuilt table: z, %, counts and `era5_swe_z` identical (max difference 3e-14); `results/tables/station_swe_region_year.csv` = `data/processed` and byte-identical to `ee9503d` (DECISIONS' "byte-identical" claim holds); 933 normals (PNW 405, BC 205, AK 159, AB 110, YT 54; at least 24 years 363, 181, 139, 107, 51); correlation with ERA5-Land 0.78-0.95, level ratio 3.10 (PNW) to 0.68 (AK); z runs contiguous with 5 or more stations: PNW and BC 1951-2026, AK 1960-2026, AB 1963-2025, YT 1975-2026 |
| F3 corrections | 22F05:OR:SNOW / 710:OR:SNTL: 10 shared years, 1 snowy, agrees in it (dropped for fewer than 3); the other five un-merged pairs have 0-3 snowy years and agree in none; 23G10/23G12 is 21 shared, 3 snowy, 0 agreeing (the new test's pattern, 86% over all years); near-identical pairs 3-12 km apart under the snowy rule: 5 (17A06/BCE-WA02 3.0 km, 18A07/BCE-WA05 3.7, 21A01/BCE-WA12 5.3, 21F11/21F23 6.6, 33J01/BCE-AK02 3.3) |
| New tests | Each tests what it claims: the snowy-years test is the real 23G10/23G12 pattern; the shared-rows test fails under the old first-row rule (twin has 7 values to 6); the SC04/SC05 test fails under a best-row-of-the-id rule (SC05 would rank Yukon and keep the copies) |
| Dedupe edge cases | Chain of three ids (no year lost), mixed id plus a CanSWE twin, float `year`, a NaN value, an unknown source string (ranked last): all behave; duplicate rows inside one id are averaged by the pivot and so never match (none exist in the data) |
| ENSO | `enso_djf` = raw RONI DJF for all 76 winters, phase and strong flags 0 mismatches; 26 El Niño and 7 strong winters; band after rounding 1965-66 1.53, 1986-87 1.46, 2009-10 1.44; fire record 1984-2025: 14 El Niño, 3 strong; ONI vs RONI 15 phase changes + 2 strong-flag changes = 17; RONI minus ONI 2006-26 mean -0.289; correlation with year RONI -0.222, ONI -0.013 |
| Plan claims in the diff | `permutation_test` counts (count + 1) / (n + 1) (`src/stats.py:74`; two-sided today, one-sided is Phase 4 as `config.py:196` says); `pet_thornthwaite` has 0.01792, N/30, clip at 0 and the 1951-2020 heat index (code read, not re-run); H6 predictors correlate 0.62-0.68 over 1951-2026 and 0.47-0.62 over 1984-2025 ("about 0.6" holds) |
| Config vs plan | Thresholds, years, fire windows, `TEST_DIRECTIONS` against the sidedness table (every cell), `CORRECTION_FAMILIES` (H6 = 4 + 5, H5 = 10, north families of 2, C1 and C2 of 3), compounding regions, HAC lags, block length, permutations, prediction alpha, df rule, expanding window from 2004 (22 seasons), station minimum 5, band 0.06 and 2 decimals, SPEI settings: all match |
| Dry runs replayed | The same pre-dedupe table run through four variants of the pair loop: the 2026-10-06 all-years rule gives 24 pairs, 576 rows (PNW 419, YT 123, AK 34), 71,183 rows, 2,166 stations, 932 normals, and its index differs from the committed one by at most 0.016 in PNW z (28 region-years' counts) and 0 elsewhere; the ee9503d first-row rule with snowy years gives the committed table exactly; the rejected best-row rule gives 2,167 stations (SC04 gone, SC05 keeps the 7 copies) and moves the YT index (z up to 0.098, % up to 3.0, 7 region-years' counts); the current rule equals the committed table and index. The six pairs the old rule merged and the current one does not are exactly the six the register names |
| Records | DECISIONS 2026-10-07 "Fix review findings settled" (every number, including the three dry-run figures above), D52, the register's station-normal and duplicate-site rows and the fix-review audit all match the code and data, except finding 5 and the wording under section 2b |
| Em dashes | `scripts/check_no_em_dashes.py`: none |

## 2. Findings, most severe first (nothing high)

### 1 (medium-low, plan leaves a choice open): the ONI run of the near-threshold flip
`ANALYSIS_PLAN.md:417-425`; `src/config.py:161-168`. The flip is defined by
RONI's band (1965-66, 1986-87, 2009-10) and the ONI bullet repeats "the
strong-only results" with ONI in place of RONI. Under ONI those winters are
1.24, 1.18 and 1.47, and ONI's own band is 1972-73 (1.55), 1991-92 (1.54)
and 2009-10 (1.47); ONI's strong set also differs (2023-24 at 1.84 in, 1965-66
out). A stranger must choose between flipping the three RONI winters, ONI's
own band, or not flipping under ONI. One clause closes it.

### 2 (low, two dated notes disagree): zero-fire sensitivity
`ANALYSIS_PLAN.md:189-190` (decided 2026-10-05: "a sensitivity analysis
excludes them") against `:396-405` (2026-10-07: regressions keep every row
with per-year indicators; only the permutation tests drop the years). The
precedence sentence (`:11`) covers original text against a dated note, not
two dated notes, and the later one does not say it supersedes the earlier.
`src/config.py:158-159` also still says "excluded in a sensitivity run".

### 3 (low, code vs docstring, latent): tie-break order in `dedupe_sites`
`src/stations.py:345-347` says priority is read from the shared years, "then
more values, then station_id". When the shared-year ranks tie, the code
(`:360-363`) orders by the id's best rank over all its rows first, then
values, then id. Probe: id A with a single NRCS row outside the shared years
beats id B, which has more values, although both hold CanSWE rows in the
shared years. No pair in the data is decided this way today.

### 4 (low, latent): site coordinates come from an id's first row
`src/stations.py:361`. SC05 is found only because its CanSWE rows (1978-84)
carry SC04's coordinates (61.1167, -138.8833) and sort first; Yukon's SC05
sits at 61.25, -138.98, about 16 km away. With the Yukon rows first the pair
is missed (probe: 1 pair to 0). Works today; worth a sentence in the
docstring, or testing every distinct coordinate an id carries.

### 5 (low, record vs data): stale count in the register
`docs/methods_register.md:91` "(with 3 stations: AK 1960, AB 1951, YT 1965)":
the index table has 2 YT stations in 1965-67 and 3 first in 1968 (2 again in
1970, 1972, 1974). Stale since the duplicate-site rule.

## 2b. Records and plan wording not caught up with D52, and secondary choices still open (all low)

### 6 (record vs plan): the register does not record the D52 flip and ONI decisions
`docs/methods_register.md:135` (strong-only sensitivity) says nothing about
the flip being one joint run of the three winters, or about the strong-only
results being repeated under ONI, and the row still reads "decided (Phase
4)". CLAUDE.md asks for every re-measured control to be in the register.

### 7 (record wording): "every headline test" survives in three places
`docs/methods_register.md:100`, `docs/data_dictionary.md:83` and
`src/config.py:24` still say ONI is re-run "for every headline test". D52
redefined that phrase in the plan to mean every registered test that uses
the index (H1, H2, H3a, H3b, H4, C1, C2, strong-only), so the three are not
wrong under the plan, but a reader of the register or the dictionary alone
takes the narrow meaning the owner rejected.

### 8 (plan, exploratory): strong-only results name no regions and no sidedness
`ANALYSIS_PLAN.md:417-422`. "Compare strong El Niño winters with all other
years, for H1 and H2" does not say whether AK and YT are included for H2,
nor whether the H2 one-sided directions (PNW, BC, AB "greater") carry over
or every strong-only test is two-sided. Exploratory, so low cost either way.

### 9 (plan, secondary): coverage for the secondary H6 forecasts
`ANALYSIS_PLAN.md:377-384` and headline method 4 (`:314-315`) give
leave-one-year-out coverage for the H3a intervals only; the H6
single-predictor forecasts are "secondary" with no statement of whether
their intervals get the same leave-one-year-out report. The expanding-window
coverage does cover them (`:385-392`), so only the leave-one-year-out part
is open.

### Info
- `DECISIONS.md` fix-review entry: "the four headline methods only (would
  leave C1, C2 and H4's contrast without the index check)". H4 is headline
  method 3, so only C1 and C2 would have been left out.
- `src/config.py:326` counts the Yukon file's sites outside Yukon (3 AK, 4
  BC, 2 NWT: confirmed); the code drops 8 stations with a region (one more
  CanSWE `YT-` site), as the register's row says.
- `ANALYSIS_PLAN.md:250` "days from the first to the last counted fire"
  does not say by ignition date; the data dictionary does. Descriptive only.
- Already recorded stale wording left as the owner's prose (D9, D41-D43,
  D45, D48) is still as the deviations log describes it.

## 3. Could not check
Fire data; the R SPEI source and the per-cell SPEI refit (code outside this
range, read only); notebooks and figures (not re-executed); `temp_jja`,
`temp_mam`, `precip_anom` (unbuilt); whether
`docs/audit_2026-10-07_fixreview.md` is the review session's file
"unchanged but for line endings" (the original was outside the repo).
