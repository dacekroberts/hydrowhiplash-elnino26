# Independent pre-freeze audit: climate pipeline and committed tables (2026-10-06)

Session: "Climate data pipeline audit" (separate session, neutral prompt; the second audit planned in DECISIONS 2026-10-06 "Pre-freeze audit").
Commit audited: `main` at `bfbc802`. Read-only: no repo file changed (`git status` clean), scripts in that session's scratchpad, no `src` module that writes files was run, no fire data opened.
Order followed: CLAUDE.md, data dictionary and ANALYSIS_PLAN only; then code and data with independent recomputation from raw inputs; only then DECISIONS.md, methods register and the two earlier audits.

## 1. What passed (independent recomputation)

| Check | Result |
|---|---|
| ENSO | `enso_djf` = raw RONI DJF for all 76 winters; phase and strong 0 mismatches; 26 El Nino / 26 neutral / 24 La Nina / 7 strong; from 1984: 14 El Nino, 3 strong. ONI vs RONI: 15 phase differences, 17 phase-or-strong (matches the documented 17). ENSO columns identical in all six region x year tables; `enso_index.csv` = raw file. |
| DJF precipitation | rebuilt from raw NetCDF with own masks (shapely, cell centres), own cos(lat) weights, own month lengths: max relative difference 2e-8, 532/532 rows. Cell counts match the register (PNW 7,331 with data ... SoCal 1,297); the 35.5N row (58 cells) goes to SoCal. |
| SPEI fit | own scipy log-logistic ML fit per calendar month (1951-2020) reproduces the cached per-cell SPEI: r 0.999, median abs difference 0.0000, 99th percentile 0.13-0.15 (optimizer differences), on 1,412 main and 1,406 north sample cells. |
| Regional SPEI and whiplash | rebuilt from the cached cells (cos-lat mean, re-standardised 1951-2020): max difference 3e-15; whiplash = JJA - DJF to 3e-15. |
| Glacier mask | rebuilt from raw monthly `sd`: 752 main, 2,250 north, 0 cells differ; BC 336, AB 4, AK 1,642, YT 269. |
| April 1 SWE | rebuilt from the raw April 1 files: 0.0 mm difference, glacier-excluded and all-cells; means AK 225.8 / 711.4, YT 167.2 / 474.8, BC 442.0 / 592.8, AB 67.1 / 69.3 mm. All stamps 04-01 00:00. |
| Snowfall fraction, seasonal sf/tp, soil moisture | rebuilt from raw: max relative difference 8e-9; NaN only in 2026 soil moisture. sf never exceeds tp; NaN patterns of sf, swvl and tp identical. |
| Station index | rebuilt from `station_swe_apr1.csv`: z and % differences <= 4e-14, station counts and empty cells identical; 935 normals. `era5_swe_z` rebuilt: <= 4e-16; SoCal empty (normal 0.06 mm). |
| Station raw spot checks | 400 random NRCS rows vs the AWDB JSON: 0 mismatches; 300 random BC rows vs the BC CSVs: 0 mismatches. 71,759 rows, 2,180 stations, no duplicate station-years, offsets within +-10 days, 2,162 date_unknown. CanSWE times all midnight, daily. |
| Committed tables | `results/tables/*` = `data/processed/*` = HEAD, byte for byte. `whiplash_swe_region_year.csv` = join of its two inputs (<= 6e-14). |
| config vs plan | thresholds, SPEI settings, HAC lags 2, 10,000 permutations/bootstraps, 80% PIs, block 3, seed, directions, Holm family sizes (H1-H3b 5, H5 10, H6 9, north 2 each, C1/C2 3) all match. |
| Documented numbers | BC El Nino minus neutral SPEI-3 DJF -0.55 / JJA +0.41; PNW 2015 station % 3.3; SWE z vs winter SPEI correlation PNW 0.61, BC 0.67, AB 0.65 (all years); snowfall and soil means; ONI/RONI 17. |
| Tests | `pytest`: 182 passed. |

## 2. Findings, most severe first

### F1 (high; critical for the 2027 forecast): heat index summed over a partial year
`src/whiplash.py:79-80`. Thornthwaite scales each month's PET against an annual heat index, the sum over the year's 12 monthly temperatures. The code sums whatever months the file holds. For 2026 (file ends July) the index is about 0.55 of a full year, so 2026 PET is too high: Jan x1.97, Feb x1.78, Mar x1.35, Apr x1.40, May x1.22, Jun x1.15, Jul x1.09 (median ratio to PET with 2025's full-year index, main-domain sample).

Effect on the committed 2026 DJF SPEI-3 (sample estimates; "complete year" = 2026 temperatures padded with Aug-Dec 2025):

| Region | Table | Complete-year index | Run on 1 March (Jan-Feb only) |
|---|---|---|---|
| SoCal | -1.37 | about -0.34 (-0.52 in a second estimate) | -2.45 (Jan-Feb PET x3.6) |
| NorCal | -0.02 | +0.23 to +0.27 | -1.39 (x4.8) |
| PNW | -0.32 | -0.20 | -2.58 (x21) |
| BC, AB, AK, YT | unchanged (winter PET is 0) | | |

Evidence it is an artefact: SoCal 2026 DJF precipitation z +0.16 (20th wettest of 76) but SPEI-3 69th of 76, when the two correlate 0.90 over 1951-2025; 32.6% of SoCal cells sit at the -3.09 clip, the highest share of any region-year 1951-2026. The plan's H6 winter SPEI predictor is "known by 1 March", which is the Jan-Feb-only column: the 2027 forecast input for PNW, NorCal and SoCal would be badly biased dry. Also: every rebuild silently changes the last year's values as months arrive, and JJA SPEI of an unfinished year is affected the same way. Not recorded in any project document.
Possible fixes (owner's call): a fixed climatological heat index (also resolves F2), or compute the index only from complete years.

### F2 (medium): PET differs from the published Thornthwaite (1948) formula
`src/whiplash.py:79-83` (identical to xclim TW48: own reimplementation matched the project to a median ratio 1.0000).
- The month-length factor N/30 is missing (PET in mm/month is computed for a 30-day month, then divided by the real month length): February +7.1%, 31-day months -3.2%, April exact.
- The heat index is recomputed for each year; Thornthwaite and, to my knowledge, the SPEI reference implementation (R `SPEI::thornthwaite`) use one index from the climatology (verify against the R source). A per-year index partly cancels warming: JJA PET temperature sensitivity 0.14 vs 0.22 mm/day per degC (main sample), 0.10 vs 0.25 (north); JJA PET interannual CV 0.050 vs 0.069 (main), 0.035 vs 0.072 (north).
- Measured effect on regional SPEI-3 (1/25-cell sample), project vs textbook formula: DJF r >= 0.999 except SoCal 0.989 (max difference 0.62); JJA r PNW 0.996, BC 0.967, AB 0.988, NorCal 0.995, SoCal 0.997, AK 0.946, YT 0.953 (max differences 0.2-0.8 SD). El Nino minus neutral: DJF unchanged (SoCal 0.92 vs 0.88); JJA shrinks by 0.02-0.08 SD (AB 0.48 to 0.44, BC 0.40 to 0.32, AK -0.11 to -0.19).
- `ANALYSIS_PLAN.md` "SPEI settings" says "Thornthwaite (1948) PET"; the methods register says "xclim TW48 steps" (accurate). A disclosure or wording question for the freeze; H6 (DJF) is barely affected.

### F3 (medium, latent Phase 4): `permutation_test` returns a "significant" p for NaN input
`src/stats.py:50-53`. One NaN in `values` gives diff = NaN but p = 1/(n_perm + 1) (0.0050 at 200 permutations, 0.0001 at 10,000), because `abs(null) >= abs(nan)` is always False. NaNs exist today in candidate inputs (SoCal `era5_swe_z`, AB station z gaps, 2026 summer columns). `bootstrap_ci_diff` returns NaN (loud enough). Suggested: raise on NaN.

### F4 (medium, latent): `fit_ols_hac` depends on row order and ignores gaps
`src/stats.py:118-127`. Newey-West weights adjacent rows: shuffling the rows of one synthetic series changed the HAC SE of `enso_djf` from 0.320 to 0.290; dropped years are treated as adjacent with no warning. `block_bootstrap_ci` got a sort guard in the Phase 1 audit; this function has none. `use_t` not yet applied (known, config comment).

### F5 (low): NaN PET when a cell stays at or below 0 C all year
`src/whiplash.py:82`. Heat index 0 gives 0/0, so PET is NaN for the whole year instead of 0, and SPEI is missing for that year (and the next Jan-Feb). Cells drop out of regional means only in cold years: weighted NaN share up to 2.7% (YT), 0.9% (AK), 0.1% (BC). Cells affected: BC up to 14 in a year (51 years), AK up to 226 (20 every year), YT up to 211 (62 every year).
**This is the open cause in the previous audit:** all 46 north cells with no February value are frozen in 62-75 of their 77 years (Jan and Feb SPEI 100% NaN, other months 91%). Audit finding 17's BC glacier cells have the same cause.

### F6 (low): station series counted twice under different IDs
`src/stations.py:284-311` (`combine`, `assign_regions`). Site pairs within 3 km with >= 3 shared years and >= 80% values within 2.6 mm: 24 pairs, about 602 station-years (PNW 18, YT 5, AK 1). Examples: `19A01:WA:SNOW` = `BCE-WA07` (51 years, all identical), `20A01:WA:SNOW` = `BCE-WA11` (51), `17A01:WA:SNOW` = `BCE-WA01` (46), `YT-09BA-SC02` = `YT-09BA-SC02A` (45, all identical), `YT-09AB-SC02` = `-SC02A` (58), `33J03:AK:SNOW` = `BCE-AK03` (34), `18A08:WA:SNOW` = `BCE-WA06` (21, 1 m apart); also NRCS course pairs (`23G12`/`23G13:OR`) and SNOTEL/course co-located pairs (`1069:WA:SNTL` / `21B50:WA:SNOW`). At least 8 of the 15 BC-run WA/ID courses duplicate NRCS courses. Affects only the station index (robustness check), slightly overweighting the north Cascades.

### F7 (low): float comparison drops 2009-10 from the strong-sensitivity band
`src/config.py:150`. `abs(1.44 - 1.5)` = 0.06000000000000005, so a literal `<= STRONG_SENSITIVITY_BAND` selects 1965-66 and 1986-87 only; the plan, DECISIONS and the register list 2009-10 too. Rounding first (e.g. to 6 decimals) gives all three.

### F8 (low): `fit_pooled` crashes on duplicate index labels
`src/stats.py:145`. A panel from `pd.concat` of per-region frames (repeated index) raises "The weights and list don't have the same length" because `df.loc[row_labels]` returns extra rows. Loud; fix with positional selection or reset_index.

### F9 (very low): `adjust_pvalues` with NaN counts the NaN in the family size
`[0.01, nan, 0.04]` -> Holm `[0.03, nan, 0.08]` (m = 3). Worth a guard alongside F3.

## 3. Can a stranger execute ANALYSIS_PLAN.md without own choices?
Not yet. Contradictions resolved only in `docs/plan_deviations.md` (logged, left as owner's prose): "Outcomes" fire windows, line 227-228 (D43); H4 "errors clustered by year", line 287 (D45); H5 "positive lag coefficient" and H2 SoCal "higher" in the hypotheses table (D42); season length listed as an outcome (D42). Open choices:
1. Last fire season in the analysis; whether 2026 (California closes Feb 2027) is in the training data.
2. How one-sided p-values are computed (permutation: one tail of the null; HAC: halved two-sided p with sign check?) and the CI level reported for one-sided tests.
3. Which H4 fit is the registered test: with or without `temp_jja`.
4. Which "H6 models" get expanding-window validation (each single-predictor model, the combined one, or all).
5. Handling of missing years in HAC series (station z gaps; see F4).
6. Whether the 0.06 band is inclusive after rounding (F7).
7. PET formula wording (F2) and the partial-year handling for the forecast (F1).
8. Build details for `temp_jja`, `temp_mam`, `precip_anom` (SD ddof; masks and weights presumably via `src.geo`) not stated in the plan.

## 4. Records vs code (step 3)
- `DECISIONS.md:591-594` (SPEI settings): "months added later ... are scored against an unchanged normal" and "recent summers read drier as Thornthwaite PET rises with temperature". With a per-year heat index (F1, F2) the PET side is neither fixed nor fully temperature-responsive.
- `docs/audit_2026-10-05_phase2.md:87-92`, `docs/methods_register.md:61`, `DECISIONS.md:40-41`: "46 north cells ... cause open": cause is F5. Audit finding 17 same cause. The audit's "SPEI fit ... as decided" pass did not cover the partial-year heat index (F1).
- `docs/methods_register.md:66`: `precip_anom` row still "pending / not set", while row 126 says decided. Fire rows 143-147 "pending" duplicate the decided rows 141-142. Line references stale (e.g. Significance `config.py:109`, now line 153; `era5.py:156-168`, now 181-193).
- `docs/methods_register.md:80`: CanSWE pillows 2,776 (BC 2,198, AB 467, YT 111) are counted by station prefix; the table by region has 2,771 (BC 2,208, AB 454, YT 109). Not wrong; worth one clause.
- `docs/methods_register.md:86`, `DECISIONS.md:437-438`: "15 BC-run courses in WA and ID count for PNW" is true, but at least 8 duplicate NRCS courses (F6).
- `docs/data_dictionary.md:237`: "cleaning not yet built" is stale.
- `ANALYSIS_PLAN.md` "SPEI settings": "Thornthwaite (1948) PET" vs the xclim TW48 formula (F2).
- Everything else tested matched the records (section 1).

## 5. Could not check
ERA5-Land against independent observations; later revisions of the 2026 ERA5-Land months; RONI against CPC's live page (downloaded file used); a full-grid textbook-Thornthwaite SPEI (1/25-cell sample only); the R SPEI package source (F2 relies on its documented method); CanSWE and Yukon raw values (NRCS and BC spot-checked); the NRCS QC-flag choices themselves; `temp_jja`, `temp_mam`, `precip_anom` (not built); anything involving fire data.
