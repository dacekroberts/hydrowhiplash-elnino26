# Read-only pre-freeze audit: changes bfbc802..97663e5 (2026-10-07)

Commit audited: `main` at `97663e5` (5 commits, 38 files since `bfbc802`).
Read-only: `git status` clean before and after; scripts in the session
scratchpad; no `src` module that writes files was run (only its functions
were imported); no fire data opened. Order: CLAUDE.md, data dictionary and
ANALYSIS_PLAN first; then code, data and recomputation; only then DECISIONS,
methods register, plan deviations and the audit documents.

## 1. What passed

| Check | Result |
|---|---|
| Tests | `pytest`: 209 passed (no cache files written). |
| ENSO | `enso_djf` = raw RONI DJF for all 76 winters; phase and strong 0 mismatches; 14 El Niño and 3 strong winters in 1984-2025. ONI vs RONI: 15 phase changes + 2 strong-only = D15's 17. RONI minus ONI 2006-26 mean -0.289; correlation with year RONI -0.222, ONI -0.013. Near-threshold band after rounding: 1965-66 (1.53), 1986-87 (1.46), 2009-10 (1.44); a bare float comparison drops 2009-10, as recorded. ENSO columns identical in all 6 region x year tables. |
| Committed tables | `results/tables/*` = `data/processed/*`, LF line endings; 532 rows, 1951-2026, 7 regions, no duplicate region-years; `whiplash_swe` = join of its inputs; whiplash = JJA - DJF exactly; re-standardised mean 0, SD 1.000000 over 1951-2020 (70 years). |
| Thornthwaite PET | own implementation (FAO-56 day length) vs `pet_thornthwaite` on 9 cells in both domains: median relative difference 0.2-0.9% (day-length formula only); N/30, climatological heat index and 0 at or below 0 °C all as documented. 2026 Jan-Feb PET no longer inflated. |
| Per-cell SPEI fits | a fresh xclim refit reproduces the cache (max 0.0003-0.0038); a 13-start optimiser finds no better likelihood than xclim's fit in 72 of 72 cell-months (6 cells): the cache is the ML optimum. |
| Glacier exclusion in SPEI | glacier mask grids = cache grids exactly; 0 SPEI values on the 752 + 2,250 glacier cells; every non-glacier land cell has SPEI in every calibration month (the remaining NaN cells are ocean inside the polygons). Fitted cells 33,867 main / 33,850 north. |
| Regional SPEI | rebuilt from the cache with own cos(lat) weights: max difference 2.6e-14. |
| Recorded refit numbers | calibration mean -0.0069 / -0.0076, SD 0.985; DJF 2026 SoCal -0.72, NorCal +0.17, PNW -0.26; SoCal 9.9% of cells at the clip in DJF 2026 (0% in 1998, 2015); BC El Niño minus neutral DJF -0.55, JJA +0.33. |
| Station table and index | dedupe rebuilt from raw via the `src.stations` cleaning functions: 71,759 to 71,183 rows, 24 pairs, 576 station-years (PNW 419, YT 123, AK 34), = committed table. Index rebuilt independently: z, %, counts identical; 932 stations with a normal. Contiguous station-z runs: PNW and BC 1951-2026, AB 1963-2025, AK 1960-2026, YT 1975-2026 (plan's claim holds); minimum 5 stations everywhere. |
| ERA5 SWE | `era5_swe_z` rebuilt exactly; SoCal empty (normal 0.06 mm); NorCal normal 60.8 mm, so H6 SWE NorCal is testable. Mean April 1 SWE excluded / all cells: AK 226 / 711, YT 167 / 475, BC 442 / 593, AB 67 / 69. |
| H6 predictor correlation | era5_swe_z vs spei3_djf: 0.49-0.68 over 1951-2026, 0.43-0.63 over 1984-2025 ("about 0.6" holds). |
| Config vs plan | thresholds, years (FIRE_LAST_YEAR 2025, FORECAST_YEAR 2027), Holm family sizes, directions, HAC lags, df rule, expanding window from 2004 (22 predictions) all match. |
| Notebooks | no hard-coded settings in code cells (display labels only). |

## 2. Findings, most severe first

### P1 (medium; plan cannot be run as written): zero-fire sensitivity vs contiguous HAC series
`ANALYSIS_PLAN.md:359-363`; `src/stats.py:46-55, 150-153`. The zero-fire
sensitivity "covers every burned-area test (H2, H3a, H3b, H4, H5, H6, C2)"
without the zero years, but "HAC series must be contiguous runs of years",
and `fit_ols_hac` raises on any gap. Dropping zero years from H3a, H3b, H5,
H6 or C2 leaves gaps, so the code stops and a stranger must choose: the
longest contiguous run, HAC treating gaps as adjacent, a gap-aware kernel,
or zero years kept with a flag. Not in any record (the kickoff lists
"zero-year scope" as closed). Owner's call.

### P2 (medium): the plan has no precedence rule for its stale passages
Contradicting text remains, resolved only in `docs/plan_deviations.md`
(D42, D43, D45, D48): Outcomes fire seasons (`ANALYSIS_PLAN.md:234-235`, no
D43 marker); hypotheses table directions H2 SoCal "higher", H5 "positive,
strongest in SoCal" (`:251-256`); H4 "errors clustered by year" (`:293-296`);
"Climate tests (... temperature, whiplash ...)" (`:215-216`); "roughly 10 to
13" El Niño years (`:4`; RONI gives 14). The plan never points to
`docs/plan_deviations.md`, and its own Deviations log (`:382-386`) is empty,
so a reader of the frozen plan meets two answers. Logged and left as the
owner's prose; a single sentence saying the dated decided notes and
"Execution details" govern would close it (owner's wording).

### P3 (medium-low): choices the plan text still leaves open
1. One-sided regression p "for the coefficient's sign" (`:345-347`) can be
   read as the observed sign's tail (half the two-sided p regardless of
   direction). Intended: the tail in the stated direction.
2. The 2027 forecast's 80% interval (`:297-298, 351-355`): full-fit OLS
   prediction interval, or LOYO-calibrated? LOYO gives coverage only.
3. Expanding window (`:199-202`): "prediction error" metric unnamed (RMSE,
   MAE, scale), and "the H6 models" still undefined (single-predictor
   models, combined, or all), the earlier audit's item 4.
4. H4 joint Wald test (`:349-350`): F(4, 41) or chi-square(4).
5. Glacier cells in `temp_jja`, `temp_mam`, `precip_anom` (`:366-368`): SPEI
   and SWE exclude them, H1's `precip_djf_mm` includes them; unstated.
6. Strong-only exploratory results (`:369-371`): which tests (H1, H2,
   regressions?).

### P4 (low): `dedupe_sites` counts agreement on bare ground as a shared record
`src/stations.py:372`; `src/config.py:346-349`. "80% of shared years within
2.6 mm" is met by two distinct low sites that are usually snow-free. 3 of the
24 merges are of that kind: `23G12`/`23G13:OR` (both ~0 every shared year),
`22F28`/`22F27:OR` (94% both ~0, the 2 snowy years disagree),
`945:OR:SNTL`/`21G04:OR` (80% both ~0, disagree when there is snow; a pillow
vs a course). The 3 km limit also misses copies with offset coordinates:
11 pairs 3-12 km apart with 83-100% identical values over 6-51 years, e.g.
`21A01:WA:SNOW`/`BCE-WA12` (51 years, 94%), `18A07:WA:SNOW`/`BCE-WA05`
(34, 97%), `22E01`/`22E02:OR` (28, 100%). Effect on the index today: none
(the stations involved have no 1991-2020 normal or SD 0). A rule asking for
agreement in years with snow would fix the first part.

### P5 (low): SPEI accumulates rates, not amounts
`src/whiplash.py:118-120` (xclim `rolling().mean()` of mm/day). Published
SPEI and `docs/data_dictionary.md:342` sum monthly P - PET in mm, so
February gets 28/31 of a month's weight there and equal weight here.
Fit-free test on 80 random cells: rank correlation >= 0.996; mean per-cell
|difference| 0.04 SD (February) and 0.01 (August); single-year maximum
0.1-0.25 typical, up to 0.97 at an extreme. Wording or method, owner's call.

### P6 (low): Thornthwaite constants vs the 1948 publication
- `src/whiplash.py:87` uses 0.01791 (xclim's value); Thornthwaite has
  1.792e-2. Effect at most 0.14% on PET. The hand-computation test copies
  the same constant, so it cannot catch this.
- Thornthwaite (1948) treats mean temperatures at or above 26.5 °C with a
  separate table; the code extends the power law. 60% of SoCal's area weight
  and 24% of NorCal's has at least one monthly normal above 26.5 °C. Rough
  scale: a SoCal desert cell at 33 °C gets about 267 mm/month (unadjusted)
  from the power law vs about 180 from the hot-range formula. It mainly
  affects JJA SPEI and whiplash (descriptive); DJF (H6) barely. The plan says
  "as published" (`ANALYSIS_PLAN.md:117-123`). Check against the original
  before acting (not consulted here).

### R (records vs code)
- `docs/data_dictionary.md:278`: 71,759 station-years, 2,180 stations; now
  71,183 and 2,166 after the dedupe.
- `docs/data_dictionary.md:367`: BC El Niño minus neutral summer SPEI-3
  +0.41; now +0.33 (DECISIONS records the change).
- `docs/data_dictionary.md:332`: `pet_thornthwaite` "now repeats xclim's
  TW48 steps" (no longer true); `:342` "summed over 3 months" (P5).
- `src/config.py:88`: comment "xclim Thornthwaite (1948)"; now its own form.
- `src/config.py:339`: "may be widened for AB and YT" vs the plan's frozen
  minimum of 5 (`ANALYSIS_PLAN.md:364-365`).
- `docs/methods_register.md` stale line references, e.g. rows at lines 35,
  37, 49, 51, 53, 54 (`era5.py:72` is now 76), 116 (`stats.py:126`, now
  139-153), 118 (`stats.py:144-150`, now 156-176), 121 (`stats.py:152`, now
  179).
- Everything else checked (DECISIONS 2026-10-06 entries, D47, D48, the
  methods register PET, glacier, dedupe and ENSO-join rows) matched.

### Info
- `tests/test_config.py` strong-band test checks a lambda inside the test;
  no `src` code applies `ENSO_DECIMALS` yet. None of the new plan settings
  (`FIRE_LAST_YEAR`, `USE_T`, `POOLED_*`, `TEST_DIRECTIONS`,
  `CORRECTION_FAMILIES`, `FORWARD_MIN_TRAIN_YEARS`) is read by code yet;
  `stats.py` has no one-sided, Driscoll-Kraay, `use_t` or expanding-window
  path (recorded as Phase 4).
- In 18 of 72 sampled cell-months the ML log-logistic shape runs to
  c = 1e7-1e8 (no finite optimum; effectively a logistic). Values are stable
  (<= 0.003 between optima); worth one methods sentence.

## 3. Could not check
Anything with fire data; `temp_jja`, `temp_mam`, `precip_anom` (not built);
ERA5-Land against observations; Thornthwaite's 1948 text and the R SPEI
source (no web access used); a full-grid SPEI refit (6 cells for the
likelihood check, 80 for the aggregation); DJF precipitation and snowfall
or soil tables (code unchanged except the ENSO join; checked by the bfbc802
audit); raw station values (the dedupe rebuild used the project's own
cleaning functions); notebooks and figures were not re-executed.
