# Pre-results audit, round 3 (cold, read-only)

- **Commit audited:** 309de6a (working tree at HEAD 0939cf9, which differs from 309de6a only by `docs/session7_audit_prompt.md`; `git diff --stat 309de6a..0939cf9`).
- **Date:** 2026-10-08 (session about 14:35 to 15:50 PDT).
- **Model:** Claude Fable 5.1 (claude-fable-5-1), Claude Code desktop app, cold session (no part in writing the code or in rounds 1 and 2).
- **Rules kept:** nothing inside the repository edited, created or deleted (`git status` clean before and after; `PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider`; the pre-existing `.pytest_cache` files are dated 13:39 and 14:15, before this session); no `src` main run (`scripts/stats_size_check.py` was imported and its `main` called with `TEST_SIZE_TABLE` redirected to the scratchpad; `src.download_nbac` was imported only); no hypothesis test on fire data; burned area never read, printed or summarised beside an ENSO column (fire tables read with `usecols` lists that leave the ENSO columns out; `fire_events.csv` has none; the RONI series was read on its own from `el_nino_winters.csv` and used only as a regressor on synthetic null outcomes); nothing re-downloaded; `data/raw/fire/nbac/` not opened. Scratch scripts and outputs in the session scratchpad: `r3_cnfdb.py` (independent rebuild), `r3_thresholds.py`, `r3_merged_attrs.py`, `r3_invalid.py`, `r3_tables.py`, `r3_more.py`, `r3_sim.py`, `r3_size_repro.py` and their `.out` files, `r3_groups.csv`, `r3_own_table_*.csv`, `test_size_repro.csv`, copies of the committed tables at the three commits.
- **Environment:** conda env `whiplash` via `conda.exe run -n whiplash --no-capture-output python ...` from the repo root. `python -m pytest -p no:cacheprovider`: 283 passed (138 s). `scripts/check_no_em_dashes.py`: clean.

Severity: high = a registered result or a fire table would be wrong or not computable as registered; medium = a likely error, an untested path or a misleading record; low = clarity or hygiene.

**Headline:** nothing high. The round 2 fix does what D67, D68 and DECISIONS "Audit round 2 settled" say. An independent rebuild of the Canadian seasons from the raw CNFDB download by my own code (own grouping, own connected components, own floor, clip, windows and unions) reproduces the committed tables at 6e79757, 32e8d42 and 309de6a under their three rules, main and frozen-rules, with no mismatch; the register's before-and-after numbers, group counts (136 groups, 344 polygons, 58 merged fires from 121 polygons, 79 ids still naming several fires, 10 counted merges) and the claim that any distance from 0.5 to 25 km gives the same tables all hold; the 1 km components are identical whether the distance is measured in ESRI:102008 or in a conformal CRS. The size script reproduces `results/tables/test_size.csv` to the last digit from its seed, and my own generator agrees with every row within Monte Carlo error; the shapes are fair stand-ins (H5's two-lag model and the real RONI regressor included). One medium finding: the pin check pins the whole `results/tables/` folder, so it will refuse the moment the first hypothesis run writes a table there. Seven low findings, mostly records.

## Findings

### M1 · `pin_inputs --verify` will fail as soon as a results table is written (medium, untested path)

- **Evidence.** `src/pin_inputs.py:33` pins `RESULTS / "tables"` as a folder and `pinned_files()` takes every file in it; `verify()` (`src/pin_inputs.py:62-70`) raises `not pinned: ...` for any file in a pinned folder that is absent from `input_pins.csv`. `CLAUDE.md` ("code writes figures and tables to `results/`") and the plan's reporting put the hypothesis outputs in `results/tables/`; the register's "Pinned inputs" row says `--verify` runs "before every test run". So the second test run after the first table is written will refuse to start, and the only ways through are re-pinning (which turns outputs into "inputs" and defeats the trap 7 purpose) or writing results elsewhere. `test_size.csv`, itself a script output, is already pinned this way (its `measured` column is today's date, so any re-run changes its hash). The "not pinned" refusal is tested and intended for a stray input (`tests/test_pin_inputs.py:33-44`); what no test or record covers is that the same folder is where the outputs go.
- **Suggested fix.** Pin a named list of input tables (the seven in `results/tables/` today) instead of the folder, or exclude a results subfolder; keep the folder rule for the three download folders. One line in the register row.

### L1 · The build logs in `data/processed/` are from the round 1 build; the 1 km build's output was not saved (low, record)

`data/processed/fire_run.log` (11:43) and `fire_frozen_rules_run.log` (11:44) predate the 14:08 rebuild of `fire_events.csv` and both tables; the log holds the round 1 counts (prescribed 304, wildfires 40,665, at floor 10,751, pieces 10,022, CNFDB 1,169/1,163 fires for BC) while the register's "Fire" header says "Counts below are from that build (`data/processed/fire_run.log`)" and its rows carry the 1 km counts (306, 40,808, 10,754, 10,021). `logs/2026-10-08.md` holds only the 00:40 session. The counts themselves are right (my rebuild: wildfires 40,808, at floor 10,754, prescribed 306 after the dissolve, 309 polygons; see "Checked and passed"), but nothing in the repository records where they came from. Suggest re-running `python -m src.fire` with the output captured (the tables will be byte-identical) or stating in the register that the 1 km counts come from the 14:08 session output.

### L2 · Data dictionary section 5 still says 304 prescribed polygons (low, record)

`docs/data_dictionary.md:496`: "`PRESCRIBED` ("yes" on the same 304 polygons as H-PB)". Raw count since 1984: 309 (Parks Canada 297, AB 7, Ontario 5), as `src/config.py:192` and the register now say; 304 was the round 1 post-dissolve count.

### L3 · D68's "3.8-5.6% in the second run" does not match the table (low, record)

`docs/plan_deviations.md` D68: "Kept for H3a, H3b, C1, C2 (3.8-5.6% in the second run)". In `test_size.csv` the plain OLS rows for those four shapes run 0.038 to 0.061 (H3a plain OLS, independent errors, 0.061); under the label scenario alone 0.043 to 0.054. Write 3.8-6.1% (or 4.3-5.4% for the label scenario).

### L4 · The per-region size labels rest on one 1,000-dataset draw labelled by an irrelevant scenario (low)

`scripts/stats_size_check.py:38` sets `LABEL_SCENARIO = "AR(1) 0.3, regions r 0.5"`; for the per-region shapes (H3a, H3b, persistent predictor, C1, C2) the region correlation does nothing, so the "label" rows are a second independent AR(1) 0.3 draw, and the two draws differ by up to 0.019 (H3b one-sided 0.081 vs 0.062, H3a two-sided 0.061 vs 0.069, C1 0.064 vs 0.077, persistent two-sided 0.095 vs 0.098), as the Monte Carlo SE 0.007 predicts. The printed label beside a p-value therefore carries about plus or minus 0.014. Suggest pooling the two AR(1) 0.3 scenarios for the per-region shapes (2,000 datasets) or raising `reps` for them, and printing `mc_se` beside the label.

### L5 · The largest per-region overshoot, C2 at 10%, sits outside the "6-9%" the records quote for the robust tests (low, record)

`ANALYSIS_PLAN.md` deviations log row 8 (D66) and `docs/plan_deviations.md` D66 say "the registered robust tests reject a true null in 6-9% of synthetic datasets like the project's (joint F about 20%)". The round 2 fix added the C2 interaction shape: Newey-West two-sided 0.100-0.104 (`test_size.csv`; own generator 0.115, with the real RONI regressor 0.099). DECISIONS "Audit round 2 settled" records it; the two D66 rows do not. One clause.

### L6 · Split id groups keep one `fire_id`; `fire_events.csv` now holds two fires under one (id, year) (low, record)

Round 2 suggested leaving far-apart parts "as separate fires with the id suffixed"; the fix keeps the id. Among counted pieces one key names two fires: `BC:1994-K50087`, 1994, two rows with `n_parts` 1 and different `fire_ha` (4,919 and 2,702 ha), one region. Nothing in the build keys on (id, year) after the dissolve (`n_fires` counts pieces; the cross-region count of 48 is unaffected: none of the 25 CNFDB keys in two regions is a split group), but the data dictionary's `n_parts` sentence should say that a `fire_id` can now name more than one fire.

### L7 · Merged-fire attribute disagreements are no longer recorded (low, record)

The round 1 docstring counted groups disagreeing on month, day and cause; the 1 km docstring and register row dropped the counts. Of the 58 merged fires, 3 disagree on month (BC 2003-N40570 and BC 2006-G80343 among the counted ten; QC 2023-20231080535), 11 on day, 0 on cause, 0 mix prescribed and wildfire parts, 3 have every part undated (so stay undated), none has some parts dated and some not. The register row could carry these (the two counted merges take the earlier month's date, as the rule says).

## Checked and passed

**The fixes (scope 1).**
- **`merge_components` and `dissolve_cnfdb`** (`src/fire.py:163-211`): union-find over pairs with `distance <= max_km * 1000` after `make_valid` and `to_crs(CRS_EQUAL_AREA)`, so touching parts (distance 0) and parts within 1 km merge and merges chain; singleton components keep their own row and attributes (`n_parts` 1); a merged fire takes the earliest month-known part's date, flags and `fire_type` and the union of the parts; blank ids never enter. `read_cnfdb` calls it with the config default (`CNFDB_MERGE_KM` 1.0). Among the 344 grouped polygons 14 are invalid; after `make_valid` all are Polygon or MultiPolygon (no GeometryCollection, no line parts that could shorten a distance). The 1 km components computed in ESRI:102008 and in EPSG:3347 (conformal) are identical for all 136 groups, so the equal-area ruler changes nothing. No merged fire has a tie on the earliest ignition date between parts with different cause or date flag, so `sort_values("ignition")` (unstable sort) cannot pick differently from run to run.
- **Independent rebuild** (`r3_cnfdb.py`: own pyogrio read of both shapefiles with `YEAR >= 1984`, 41,177 polygons; own grouping, own connected components via scipy, own union, floor in ESRI:102008, overlay with `regions.geojson`, own windows including the undated-by-YEAR rule, own union per season): for BC, AB and YT 1984-2024 (123 region-seasons) under each rule, `n_fires`, `n_undated`, `burn_ha` and `double_ha` equal the committed main table of the matching commit in every row (max absolute difference 0.0000 ha), and `n_fires` and summed `burn_ha` of the frozen-rules table likewise: per polygon against 6e79757 (41,177 fires, 309 prescribed, 40,868 wildfires, 10,774 at the floor, no merged fire counted), full id merge against 32e8d42 (40,969 fires, 304 prescribed, 40,665 wildfires, 10,751 at the floor, 13 merged fires counted including BC 1994-K50087, 1998-N40187 and N40188) and the 1 km rule against 309de6a (41,114 fires, 306 prescribed, 40,808 wildfires with N 24,309, H 11,716, U 4,776, Re 7, 10,754 at the floor, the 10 merged fires of the register). So the register's "Wildfire types", "Minimum fire size" and "CNFDB fires in several polygons" counts are right even though their stated source log is stale (L1).
- **Group statistics** reproduce the register row: 136 groups (344 polygons; sizes 2 x 99, 3 x 19, 4 x 4, 5 x 11, 6 x 3); 58 merged fires from 121 polygons (2 parts 55, 3 parts 2, 5 parts 1); 57 groups fully merged, 79 ids still naming more than one fire; no group mixes prescribed and wildfire parts; largest nearest-neighbour gap within a group 0.2 km at the 25th percentile, 25.5 km at the median, 327 km at the 75th, 1,109 km at most; prescribed polygons 309 (PC 297, AB 7, ON 5), 306 fires after the dissolve; CAUSE N 24,353, H 11,729, U 4,779, Re 7 before, N 24,309, H 11,716, U 4,776, Re 7 after; blank ids MB 625, SK 45, PC 9; no month-known date fails to parse.
- **Merge distance** (`r3_thresholds.py`, Canadian region-season contributions of the 344 grouped polygons): thresholds 0.5, 2, 5, 10, 20 and 24 km give exactly the 1 km result; 26 km re-merges BC 1998 (+1,014.9 ha, 2 fires); 50 km and "merge all" also re-merge BC 1994-K50087 (2 fires to 1); touching-only (0 km) would lose BC 2003-N40570 (+644.7 ha), split BC 2004-N70493 (1 to 2 fires) and drop 32.9 ha from BC 2006. So "any distance from 0.5 to 25 km gives the same tables" holds, and three of the ten sound merges do not touch (within 0.5 km).
- **Committed tables across the three commits** (`r3_tables.py`, ENSO columns never read): 6e79757 to 32e8d42 changed 8 Canadian seasons (BC 1994 11 to 10 fires; BC 1998 22 to 24, +1,014.9 ha, +0.0167 in `log_burn`; BC 2003 +644.7 ha; BC 2004 43 to 42; BC 2006 +32.9 ha; AB 2012 46 to 45, +40.4 ha union, +236.0 `double_ha`; YT 1990 19 to 18; YT 1995 28 to 27 and `n_undated` 2 to 1); 32e8d42 to 309de6a changed exactly BC 1994 (back to 11) and BC 1998 (back to 22 fires, 60,120.5 ha); net 6e79757 to 309de6a is the register's 6 seasons; no US row changed in any step. Frozen-rules table: 7, 2 and 5 rows (YT 1995 absent, its merged fire undated); AB 2012 +276.4 ha summed. Both 309de6a tables: 291 rows, `log_burn` = log1p(`burn_ha`), `zero_fire` consistent (SoCal 2014; frozen also AB 1997, YT 2022), frozen `double_ha` all 0, frozen/main area ratios AB 0.932 to BC 1.001 as recorded.
- **Events file at 309de6a:** 9,755 rows; `n_parts` 1 for 3,028 CNFDB pieces, 2 for 10, empty for 6,717 MTBS and WFIGS pieces; the 10 merged counted fires are exactly the register's list (BC 2003-N40570, 2004-N70493, 2006-G60430, G60490, G80343; NT VQ030-90, EV008-95, SS003-12, FS015-12; PC 2012WB16); no piece under 405 ha whole, none clipped above its whole area; `n_fires`, `n_undated`, `n_unknown_type` of all 291 main rows and `n_fires`, `burn_ha` of all 291 frozen rows reproduce from the events file (sum = `burn_ha` + `double_ha` to 5e-10 ha); undated YT 103, AB 60, BC 6; 48 fires in more than one region by (source, id, year).
- **Size table:** `scripts/stats_size_check.py` run from its seed with the output path redirected reproduces `results/tables/test_size.csv` exactly (51 rows, every `rejection_rate`, label, method, sidedness, `label_scenario`, `reps`, `mc_se` identical). The shapes match the registered models: H3a `log_burn ~ enso_djf + year`, H3b with a control at AR 0.5 correlated 0.4 with ENSO, persistent predictor at AR 0.27 (the largest real lag-1; recomputed below), C2 and C1 interaction formulas with `year_c` centred, 42 and 76 periods, sidedness per `TEST_DIRECTIONS` (C1 `less`, north one-sided), H4 panel 5 x 41 with the registered formula, Driscoll-Kraay df 40, clustered and plain fits. Own generator and seeds (`r3_sim.py`, 1,000 null datasets each, errors AR(1) 0.3, regions correlated 0.5 for H4; MC SE 0.007) against the table's label rows: H3a Newey-West one-sided 0.057 (table 0.063), two-sided 0.074 (0.069), plain OLS 0.043 (0.044); H3b 0.068 / 0.066 / 0.035 (0.062 / 0.081 / 0.043); persistent predictor 0.079 / 0.099 (0.076 / 0.098); C2 Newey-West 0.115 (0.100), plain OLS 0.048 (0.052); C1 one-sided 0.070 (0.077), plain OLS 0.056 (0.054); H4 Driscoll-Kraay contrast 0.085 (0.078), joint F 0.224 (0.195), year-clustered contrast 0.073 (0.053), joint F 0.150 (0.137), plain OLS contrast 0.010 (0.007). Shapes the table does not hold: H5's actual two-lag model (`log_burn ~ x + x_lag + year`, lag1 the same AR 0.27 series shifted) gives lag0 one-sided 0.086 and lag1 two-sided 0.086, one-sided 0.060, so the single-predictor rows are a fair stand-in; with the real RONI DJF values as the regressor (skew 0.46, lag-1 -0.008) and synthetic null outcomes the sizes are lower (H3a Newey-West one-sided 0.053, two-sided 0.057; C2 0.099; C1 one-sided 0.056; H4 Driscoll-Kraay contrast 0.057, joint F 0.157), so the white-Gaussian ENSO stand-in labels are, if anything, conservative.
- **`lag1_autocorrelation`** (`src/stats.py:703-716`): equals statsmodels `acf(nlags=1)` to 3e-16 over 200 AR(1) series with rho in (-0.8, 0.8); -41/42 on the alternating series. Real predictors recomputed from the climate tables only, 1984-2025: `enso_djf` -0.008, `enso_djf x year_c` 0.005, `precip_anom_lag0` -0.048 to 0.267, `spei3_djf` -0.187 to 0.150, April 1 SWE -0.180 to 0.224 (a z-score has the same value), `temp_jja` 0.027 to 0.476: the register's "-0.01, 0.00, -0.05 to 0.27, -0.19 to 0.15, -0.18 to 0.22, 0.03 to 0.48".
- **Strengthened tests:** the H4 multi-seed bound is as described (Binomial(200, 0.08): P(X > 26) about 0.6%; at 16%, P(X <= 26) about 14%, so a doubling is caught 86% of the time); the bootstrap agreement test runs five seeds with betas 0, 0, 0.15, 0.3, 0.5 and checks p against the CI each time; the new dissolve test covers a 25 km pair, a 3-part chain with 0.6 km gaps and the exact 1 km edge, and `merge_components` at 0.5 km splits the chain. `python -m pytest`: 283 passed.

**The rest of the gate (scope 2).** `src/stats.py` and `src/pin_inputs.py` changed only in `lag1_autocorrelation` (used by nothing else: grep) and in `input_pins.csv` gaining `test_size.csv`; `--verify` passes before and after. `src/download_nbac.py` imports cleanly and writes under `NBAC_RAW`, which is outside the pinned folders. The size script's `ar1` is unit-variance stationary from its first value; `null_series` builds `temp_jja` with correlation 0.4 to ENSO and unit variance as its docstring says. `check_no_em_dashes.py`: clean.

**Records (scope 3).** DECISIONS "Audit round 2 settled", D67, D68, the plan's deviations log rows 9 and 10, the register rows "CNFDB fires in several polygons", "Wildfire types", "Minimum fire size", "Country assignment", "Fire-season windows", "Undated CNFDB fires", "Union area", "Test size (simulated)", "Pinned inputs", data dictionary sections 5 and 8 (`n_parts`, `cnfdb_year`, 9,755 rows, 26 pins, `test_size.csv` columns, the lag-1 definition), `src/config.py` comments (`CNFDB_MERGE_KM`, the 309 prescribed polygons) and the ACTION_PLAN progress line agree with the code, the tables and my numbers, except as in L1-L3 and L5-L7. The D66 row's "H4 contrast" in the plain OLS list is superseded by the D68 row, as a log should be.

## Not checked

- US seasons were not rebuilt from MTBS and WFIGS geometry this round (they are byte-identical across the three commits, which is what the fix claims; round 1 rebuilt the MTBS seasons).
- Any statistic on real fire data, by the rules of this session; the station index, SPEI and SWE inputs; the Parks Canada gap; NBAC (not opened); licence text.
- The stdout of the 14:08 rebuild (L1): its counts were checked against my own rebuild instead.
- Whether BC 2003-N40570's two parts (months differ, within 1 km) are one fire in BC's records; the rule treats them as one, as the register says.

## Verification output

Before (start of session, HEAD 0939cf9):

```
$ python -m src.pin_inputs --verify
all inputs match C:\Users\dacek\Documents\Portfolio\hydrowhiplash-elnino26\results\tables\input_pins.csv

$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

After (end of session, HEAD 0939cf9):

```
$ python -m src.pin_inputs --verify
all inputs match C:\Users\dacek\Documents\Portfolio\hydrowhiplash-elnino26\results\tables\input_pins.csv

$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

(`.pytest_cache/v/cache/lastfailed` and `nodeids` are dated 13:39:18 and 14:15:26, before this session; nothing was written there.)
