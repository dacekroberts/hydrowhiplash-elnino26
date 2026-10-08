# Pre-results audit, round 1 (cold, read-only)

- **Commit audited:** 6e79757 (working tree at HEAD 0f188ae, which differs from 6e79757 only by `docs/session7_audit_prompt.md`; checked with `git diff --stat 6e79757 HEAD`).
- **Date:** 2026-10-08 (session 00:30 to 02:30 PDT).
- **Rules kept:** nothing inside the repository edited, created or deleted; no `src` main run; no hypothesis test on fire data; burned area never read, printed or summarised beside an ENSO column (fire tables read with the ENSO columns dropped; ENSO columns checked on their own against `el_nino_winters.csv`); nothing re-downloaded. Scratch scripts and outputs live in the session scratchpad (`check_tables.py`, `check_era5.py`, `check_fire_raw.py`, `check_more.py`, `check_oni.py`, `check_null_year.py`, `check_null_year2.py`, `check_daily.py`, `rebuild_regions.py`, `sim_stats.py`, `probe_stats.py`, `scale.py`).
- **Environment:** conda env `whiplash`, run via `conda.exe run -n whiplash --no-capture-output python ...` from the repo root. `python -m pytest`: 264 passed (81 s).

Severity: high = a registered result or a fire table would be wrong or not computable as registered; medium = a likely error, an untested path or a misleading record; low = clarity or hygiene.

**Headline:** nothing high. The climate controls and both fire tables reproduce exactly from the raw downloads by independent code. The one substantive problem is already known to the project and still open: the registered robust tests (Newey-West, Driscoll-Kraay, the H4 joint F) reject a true null well above 5% on data shaped like this project's, and with cross-region correlation, which the real regions have, the H4 contrast reaches 10%. Four medium findings follow, then eleven low ones.

## Findings

### M1 · Registered robust tests over-reject; the H4 contrast reaches 10% with correlated regions (medium)

- **Evidence.** `scripts/stats_size_check.py 1000` re-run: reproduces the register's "Test size (simulated)" row exactly (rho 0 / 0.3: DK contrast 0.062 / 0.081, DK joint F 0.175 / 0.192, clustered contrast 0.055 / 0.063, clustered joint F 0.111 / 0.136, HAC two-sided 0.075 / 0.092, HAC one-sided 0.061 / 0.078). My own simulations (`sim_stats.py`, different seeds and generator):

  | Test (null data, p < 0.05 share) | rho 0 | rho 0.3 | rho 0.5 |
  |---|---|---|---|
  | `fit_ols_hac` + `coef_test`, H3a shape, 42 years, two-sided (1,000 reps) | 0.082 | 0.078 | 0.077 |
  | plain OLS t on the same data | 0.056 | 0.044 | 0.040 |
  | permutation test, 14 of 42 years in group, two-sided (2,000 reps, 999 perms) | 0.045 | 0.050 | 0.048 |
  | permutation test, one-sided | 0.054 | 0.048 | 0.043 |

  H4 shape with errors correlated 0.5 across the five regions and AR(1) 0.3 over years, 41 years, 500 reps (Monte Carlo SE 0.01): DK contrast **0.100**, DK joint F **0.208**, year-clustered contrast 0.088, clustered joint F 0.142. The register's panel had independent regions; PNW, BC and AB share weather, so the correlated case is the realistic one. Holm within the H3a family (5 regions sharing one ENSO series, one-sided in the north) under the null: any test significant in **0.093** of families (1,000 reps; nominal at most 0.05), because each member test is oversized.
- **Why.** With 41-42 periods and Bartlett weights to lag 2, the HAC and Driscoll-Kraay variances are biased down and the t(n - k) or t(years - 1) reference does not absorb that; the 4 x 4 interaction covariance for the joint F is estimated from 41 yearly score sums. Note that plain OLS keeps close to nominal size here because the ENSO regressor is nearly white year to year, so the HAC protects against little in this design while costing size.
- **Suggested fix** (the methods are frozen; the owner's decision is pending per the register). Options, any of which keeps the registered estimates and CIs: (a) print the measured null rejection rate beside every HAC, Driscoll-Kraay and joint-F p-value and read "significant" with that calibration; (b) report a calibrated p from the already registered moving-block bootstrap (blocks of 3) for the H3a and H3b coefficients, and the plain OLS p alongside, as the check the plan allows; (c) demote the joint F to descriptive (it is secondary already) and keep the contrast as the H4 test, with its ~10% size stated. Whatever is chosen, add the correlated-regions row to the register's "Test size" entry.

### M2 · CNFDB polygons with an unknown year are dropped silently and recorded nowhere (medium)

- **Evidence.** `src/fire.py:148` reads CNFDB with `where="YEAR >= 1984"`. The 1972-2020 shapefile holds 104 polygons with `YEAR = -9999` and `CFS_NOTE1` "Fire year unknown, refer to decade" (`check_null_year2.py`): YT 85 (56,320 ha CFS area), Parks Canada 19 (92,764 ha, Wood Buffalo). 43 of them have `CALC_HA >= 405` (YT 31, PC 12; 141,892 ha), decades 1970s 6, 1980s 16, 1990s 21; no month, day, report date or polygon date. Clipped to the study regions (`check_daily.py`, equal-area CRS): AB 1980s 6 polygons 10,835 ha (plus 2 of the 1970s, 2,928 ha); YT 1980s 6 polygons 9,601 ha, 1990s 21 polygons 37,323 ha. For scale, the main table holds AB 1984-1989 131,487 ha and YT 1984-1999 2,368,599 ha, so up to about 8% of AB's 1984-89 area and 2% of YT's 1984-99 area burned in fires the record cannot date. D59, the register's "Undated CNFDB fires" row and data dictionary section 5 cover fires without a month only; the plan's "CNFDB date completeness" report counts months.
- **Why it matters.** Not a computable rule change (a fire with no year has no season), but it is an exclusion the records do not state, in the early part of two Canadian series, and the frozen-rules variant (D62) shares it.
- **Suggested fix.** Record it: data dictionary section 5 (CNFDB traps), the register's undated row (count, area, regions and decades as above), and the methods limitation for AB and YT 1984-1999. No rule change.

### M3 · The 405 ha floor is applied per polygon, not per fire, for CNFDB (medium, measured effect small)

- **Evidence.** `whole_fire_floor` (`src/fire.py:185`) measures each row. CNFDB stores some fires as several polygons under one (`SRC_AGENCY`, `YEAR`, `FIRE_ID`): 136 such groups nationwide since 1984 (`check_fire_raw.py`). Inside the study agencies: 3 BC fires whose polygons are each under 405 ha but sum above it are dropped (1998 N40187: 349 + 207 = 556 ha; 1998 N40188: 283 + 176 = 459 ha; 2003 N40570: 393 + 251 = 645 ha; 1,660 ha in total), and 5 fires with two polygons each at or above 405 ha count twice in `n_fires` (BC 1994 K50087 and 2004 N70493; NT VQ030-90 and EV008-95 inside YT; NT FS015-12 inside AB; 10 pieces, `check_more.py`). The plan's rule: "The 405 ha floor applies to each fire's whole `area_ha`". MTBS and WFIGS have no repeated ids among the rows used; WFIGS has 3 pairs of pieces sharing name, region and season under different ids (Whiskey Mountain OR 2024, two ids with the same discovery date; Mineral; Horseshoe), where the union keeps the area right but `n_fires` may count one fire twice.
- **Suggested fix.** Either dissolve CNFDB polygons by (`SRC_AGENCY`, `YEAR`, `FIRE_ID`) where `FIRE_ID` is non-empty before the floor (D62's firm line allows a defect fix found by a check, with before-and-after numbers: BC 1998 + 1,015 ha, BC 2003 + 645 ha, 5 fewer `n_fires`), or record the per-polygon rule and its measured effect in the register and leave the table. Both tables are affected the same way.

### M4 · H1's input table is neither committed nor pinned (medium)

- **Evidence.** `H1_VALUE = "precip_djf_mm"` (`src/config.py:291`) lives only in `data/processed/djf_precip_region_year.csv` (532 rows, 1951-2026, no missing values; `check_tables.py`). `results/tables/` has no copy, and `results/tables/input_pins.csv` (25 files) holds no file with that column. The register's pinned-inputs row says the pins cover "the 25 files the tests read" and `--verify` runs before every test run; H1 would read an unpinned file. The climate controls table has `precip_octmar_mm` (H5) but not the DJF total.
- **Suggested fix.** Write a committed copy (`src.era5` main, or add `precip_djf_mm` to the climate controls table) and re-pin, with a log note; until then H1 runs outside the pin.

### L1 · Register's "332 pieces" needs its tolerance (low)

`docs/methods_register.md` "Country assignment": "332 pieces are part of a fire that crosses a region or country edge". From `fire_events.csv`: pieces whose clipped area is below the whole fire by more than 1 ha, over all events including 2026 = 332; with any difference = 351 (345 in the tested seasons); 249 of those are in fires that touch one region only (cut by an outer or country edge). State the tolerance and the year range, or recount.

### L2 · Data dictionary: WFIGS `attr_UniqueFireIdentifier` is not unique (low)

Section 5 says "(YYYY-unit-number, unique)". 100 rows of the layer share an id with another row (50 pairs, all 2020, a Final and a Daily perimeter with different incident names, e.g. 2020-CASHF-000910 "FLAT" / "Ridge"); 4 in the five states; none among the rows the build uses (UTC year 2023 on). Reword to "unique among the rows used".

### L3 · ERA5-Land lag wording stale after D55 (low)

Data dictionary section 2 "Monthly means, 1950 to about 3 months before today" and section 9 "Publication lags: ERA5-Land about 3 months (`ERA5_LAG_MONTHS`)": D55 found the lag about a week and the 3 months a download margin. The register's lag row was updated; the dictionary was not.

### L4 · Share of counted WFIGS area from "Daily" perimeters (low, record)

Of the counted WFIGS area in the tested seasons with a feature category (`check_daily.py`): NorCal 2024 84% (211,266 of 250,176 ha), NorCal 2025 49%, SoCal 2024 42%, PNW 2025 23%, PNW 2024 19%, SoCal 2025 3%, AK 0%; 30 of 469 counted pieces have no category. A daily perimeter can predate containment. The 2023 source-agreement check already covered this product mix (|d| at most 0.032), so no action; worth a sentence in section 5 beside "One perimeter per incident, the latest".

### L5 · `loyo_prediction` has no one-row-per-year guard (low)

`src/stats.py:480`: passed a two-region table with no region term it fits one pooled model per held-out year and returns 84 rows (probe 3 in `probe_stats.py`); `expanding_window` refuses a repeated year. Add the same check.

### L6 · Plan steps with no helper, each a place where a known trap can recur (low)

Not built in `src/stats.py`: the near-threshold strong flip (the rounding to `ENSO_DECIMALS` that fixed audit F7 exists only as a config comment); `year_c` centred on each model's own years (C1 1951-2026, C2 each region's fire years; probe 4: the interaction coefficient is the same under either centring, the `enso_djf` main effect is not); percent change `100 * (exp(b) - 1)`; lag-1 autocorrelation of each outcome series; the 2027 OLS prediction interval (probe 2: `get_prediction` on the HAC fit gives [10.477, 11.691] against [10.479, 11.690] from a plain OLS fit on the same synthetic series, close but mixing the robust covariance into the mean part; the plan says OLS intervals, so use a plain fit as `expanding_window` does). Small functions with known-answer tests would close these before the hypothesis runs.

### L7 · Zero-indicator SE correction is a little larger than a dropped-year fit's (low, number for the register)

With indicators the D65 factor is sqrt(42 / (39 - z)) instead of sqrt((42 - z) / (39 - z)): SEs 1.2% (1 zero year) to 3.8% (3) wider than a dropped-year fit's, on top of the lag-sum difference D52 accepts (`sim_stats.py`, 300 reps each). Conservative direction; one line in the register's zero-fire row.

### L8 · Significance uses strict `<` (low)

`run_family` (`src/stats.py:476`): `significant = p_holm < alpha`; a Holm-adjusted p of exactly 0.05 is not significant (probe 10). The plan says "α = 0.05 after correction". Either is defensible; state it.

### L9 · Idaho's WFIGS zone is Mountain time (low)

`WFIGS_STATE_TZ["US-ID"] = "America/Boise"`; the panhandle is Pacific. Affects only a discovery between 23:00 and 24:00 Pacific on a window edge (31 May, 31 October). Not measured; none of the 2023-plus rows changes calendar year between UTC and local date (`check_fire_raw.py`).

### L10 · Test suite gaps (low)

`test_h4_null_contrast_is_not_significant` checks one seed; `test_stats_defaults_come_from_config` does not cover `HAC_MAXLAGS`, `BLOCK_LEN` or `ALPHA` defaults; no test of `contrast_test` with a one-sided alternative or of `wald_f_test` outside `h4_test`; `hand_hac` re-implements statsmodels' own formula, so the known-answer tests confirm the code calls the estimator as intended but say nothing about the estimator's small-sample behaviour, which is where the actual problem is (M1). The size script is the right tool for that and is not part of the suite.

### L11 · `n_fires` counts pieces, including a fire stored under two ids or two polygons (low)

Documented for cross-region fires (47) only; the M3 cases add 5 CNFDB fires and up to 3 WFIGS fires counted twice. One sentence in data dictionary section 5.

## Checked and passed

**Statistics code (scope 1).**
- Every registered test and robustness run can be computed with these functions as the plan states: H1/H2 and strong-only via `detrend` + `permutation_test(alternative=...)` + `bootstrap_ci_diff`; H3a/H3b/H5/H6/C1/C2 via `fit_ols_hac` + `coef_test` with `TEST_DIRECTIONS`; H4 via `fit_driscoll_kraay` + `h4_test` (contrast = mean of the PNW, BC, AB interaction coefficients, two-sided; joint F(4, 40)) and `fit_pooled` alongside; the H3a minus H3b gap via `block_bootstrap_ci` with an OLS-difference statistic (probe 1 works; a HAC statistic inside the bootstrap raises on non-consecutive years, as it should); zero-fire sensitivity via `with_zero_indicators` (coefficients and residual df equal a dropped fit; H4 df stays 40); expanding window from 2004 (22 or 21 predictions), `validation_summary`, `forecast_skill`; Holm/BH via `run_family` with family sizes H1 5, H2 5, H3a 5, H3b 5, H5 10, H6 9, north 2 each, C1 3, C2 3. Formula terms, reference level (SoCal; plain `C(region)` refused), year alignment (fire Y, DJF Y, JJA Y, Oct-Mar ending March Y, April 1 Y, lag1 = Y-1), sidedness (greater, less, tail in the stated direction; p(greater) + p(less) = 1 + 2/(n+1) up to ties), seeds (2026 everywhere), sorting and gap refusals, missing-value refusals, and the correction families all agree with the plan and `config.py`.
- statsmodels 0.15.0 behaviour as described: HAC default no correction, `hac-groupsum` and cluster default the cluster factor; the Driscoll-Kraay fit's own `df_resid_inference` is 4 on a region-sorted 5 x 41 panel while `inference_df` is 40; `time` is 0-based so `np.bincount` orders the yearly score sums chronologically whatever the row order (SEs identical for three orderings).
- Permutation test size is nominal (0.043-0.054) even with AR(1) 0.5 outcomes when the El Niño years sit at random positions, so trap 10 is mild for this design. Bootstrap percentile CI coverage 0.944 (rho 0) and 0.932 (rho 0.3) for 14 vs 28 years.
- `python -m pytest`: 264 passed. `scripts/stats_size_check.py` reproduced to three decimals.

**Built variables (scope 2).** `temp_jja`, `temp_mam` and `precip_octmar_mm` recomputed from the raw yearly NetCDF files (`era5_land_*.nc`, both domains) with my own regionmask mask, cos(latitude) weights, K to deg C and m/day x 1000 x days-in-month, for PNW, SoCal, YT and AK in 1951, 1984, 2000, 2016 and 2025: all 60 values agree to the printed 4 decimals (`check_era5.py`). `precip_anom_lag0` equals the z-score against each region's 1991-2020 mean and SD (ddof 1, 30 reference values) and `lag1` equals `lag0` of year - 1 in every region; `temp_jja` empty only for 2026, `lag1` only for 1951; 532 rows; ENSO columns equal `el_nino_winters.csv`; the dictionary's means and the 0.75-0.91 correlation with DJF precipitation reproduce.

**Fire build (scope 3).**
- Independent rebuild from the raw downloads (`rebuild_regions.py`: own reading, prescribed filter, make_valid, equal-area floor, intersection with the region polygons, own season logic including the January wrap, union per season): BC, AB and YT 1984-2024 and PNW, NorCal and SoCal 1984-2022 (MTBS years) agree with `fire_region_year.csv` in every season on `n_fires`, `n_undated` and union `burn_ha` (differences under 1 ha; totals ratio 1.000000).
- From `fire_events.csv`: `n_fires`, `n_undated`, `n_unknown_type`, `first_fire`, `last_fire`, `season_days`, `source`, `zero_fire` and `log_burn = log1p(burn_ha)` reproduce; sum of clipped area = `burn_ha` + `double_ha` in all 291 rows; union never above the sum; the frozen-rules table reproduces column for column from an independent sum (summed area, Other dropped, undated dropped, 291 rows, `double_ha` 0, zero seasons AB 1997, YT 2022, SoCal 2014, ratios AB 0.932 to BC 1.001); dated pieces' seasons agree with the windows; no MTBS piece on or after the cutover, no WFIGS piece before it; the Jan 1984 Modjeska fire falls in season 1983 and stays out of the table, as the rule says.
- Register "Fire" counts reproduce: MTBS types in the read box (12,249 / 1,021 / 520 / 190; 30,932 in the file), CNFDB causes and 309 prescribed, Other pieces (PNW 45, NorCal 39, SoCal 10, AK 9), undated (YT 104, AB 60, BC 6), 47 cross-region fires, 1 zero-fire season, 9 empty season lengths, `double_ha` by region, month share by decade and region, the frozen-variant ratios, 291 rows (4 x 42 + 3 x 41), YT 102 / AB 39 / BC 0 undated large fires by agency (CFS area). MTBS: no null ignition date, no duplicate `event_id`, ignition years 1984-2026. WFIGS: no null discovery time, no null state, the GeoJSON carries an integer `id` member so the fid-based chunked read is consistent; 2023-plus rows never change calendar year between UTC and local date. ONI classification from the pinned file gives the plan's strong set (1958, 1973, 1983, 1992, 1998, 2016, 2024) and band (1972-73 1.55, 1991-92 1.54, 2009-10 1.47); RONI gives 14 El Niño and 3 strong winters in 1984-2025 and the band 1965-66, 1986-87, 2009-10. Download manifests match the ledger (MTBS Last-Modified 2026-10-07 05:07 GMT, 389,974,748 bytes; WFIGS 42,553 features, 2026-10-07 22:51 UTC; CNFDB files dated 28 Jan 2026).

**Records (scope 4).** `config.py` agrees with the plan on thresholds, years, windows, directions, families, H4 regions and reference, HAC lags, block length, permutation and bootstrap counts, the D65 correction, the cutover and the source check; the 2026-10-08 DECISIONS entry's "tests 232 to 264" and the register's statistics rows match the code and the measurements here; the data dictionary's 9,758 events rows, 532 climate rows and `temp_jja` means match. Stale passages already logged (D9, D41-D43, D45, D48, D54, D56) were not re-listed.

## Not checked

- WFIGS geometry was not rebuilt independently (the US 2023-2025 seasons and the MTBS+WFIGS seasons rest on the main build and the events file); AK was not rebuilt (its MTBS years were not in my MTBS box); the 266 out-of-window pieces (450,411 ha) are dropped before `fire_events.csv` is written and cannot be recounted from it.
- Any statistic on real fire data, by the rules of this session; the station index, SPEI and SWE inputs (outside scope); the Parks Canada 2018-2020 gap; licence text.
- Whether a "Daily" WFIGS perimeter is the fire's final extent (L4).

## Verification output

Before (start of session):

```
$ python -m src.pin_inputs --verify
all inputs match C:\Users\dacek\Documents\Portfolio\hydrowhiplash-elnino26\results\tables\input_pins.csv

$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

After (end of session, HEAD 0f188ae):

```
$ python -m src.pin_inputs --verify
all inputs match C:\Users\dacek\Documents\Portfolio\hydrowhiplash-elnino26\results\tables\input_pins.csv

$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```
