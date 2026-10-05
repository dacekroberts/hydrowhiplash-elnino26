# Methods register

Every control, cap, filter, threshold, exclusion and data-handling rule the
pipeline applies, kept up to date as each one is added, so the Methods and
limitations section can be written from it. One row per control: its value,
where it lives, why it exists and its measured effect. Values live in
`src/config.py`; this file describes them and does not override them. The
reasoning for each judgment call is in `DECISIONS.md`; departures from the
plans are in `docs/plan_deviations.md`; units and traps per dataset are in
`docs/data_dictionary.md`.

**Status:** *applied* = in the pipeline now; *decided* = settled, not yet
built; *planned* = in the plans, not yet built; *pending* = waiting on a
decision (usually a pre-freeze item); *not handled* = a known issue with no
control yet.

Add a row when a control is introduced, and update its *measured effect*
when it is re-measured (keep the old number with its date). Started
2026-10-04 and back-filled the same day from the code, notebook 01,
`DECISIONS.md`, `docs/plan_deviations.md`, the data dictionary,
`ANALYSIS_PLAN.md` and the 2026-10-04 log. Where a source gives no
measurement the row says "not measured".

## Spatial

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| Area-weighted regional means | cos(latitude) weights | every regional climate mean | `src/geo.py` `regional_mean` | a 0.1° cell at 60N covers about 62 km², at 32N about 104 km² | not measured; an unweighted mean over-counts northern cells | applied | data dictionary s.2 |
| Region membership | a cell belongs to a region when its centre lies inside the polygon; `overlap=False`, error if a cell falls in two regions | every regional mean | `src/era5.py:102, 106` | simple, no partial cells | against fractional-overlap weighting (5 original regions; AK and YT not measured): mean difference -0.24% (AB) to +0.81% (NorCal), largest single-winter difference 1.40% (SoCal), correlation ≥ 0.99998 | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| Grid snapping | lat/lon rounded to 4 decimals | all ERA5-Land files | `src/era5.py` `snap_grid` | 35.5N is stored as 35.499999999999645, which would place the NorCal/SoCal boundary row by float noise | the 35.5N row is 58 cells; tested in `tests/test_era5.py` | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| California split | 35.5N (`CA_SPLIT_LAT`); clip boxes cut at 35.5N (130W to 110W) | NorCal, SoCal | `src/regions.py:54-55` | north-south precipitation seesaw | the 35.5N row goes to SoCal: SoCal DJF mean 110.9 mm with it, 110.8 without; NorCal would go 355.0 to 349.9 mm (-1.4%) if it took the row | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| Alaska west clip | 169W (`ALASKA_WEST_LON`); clip box 169W-129W, 50N-72N | AK | `src/regions.py:47` | outer Aleutian and Bering Sea islands, 1.1 Mha (0.7% of the state, almost no fire), cross the antimeridian | AK area 149.39 Mha | applied | DECISIONS "Alaska and Yukon added" |
| Admin-1 subset | USA and Canada only; error if region names are not unique | region polygons | `src/regions.py:39-42` | admin-1 names repeat across countries | not measured | applied | DECISIONS "Pre-start review" |
| Domain assignment | a region is read from the first `ERA5_DOMAINS` box that contains its whole bounding box | each region | `src/era5.py:156-168` | two download boxes overlap south of 60.5N | AK, YT read from north; the other five from main | applied | data dictionary s.2 |
| Domain overlap agreement | checked with rtol 1e-5 or atol 1e-3 (variable units); land/ocean NaN pattern must match exactly | `tp`, `t2m`, `sd` in the overlap | notebook 01, cell 5 | float32 GRIB packing differs per request area; atol because °C crosses 0 | 96 x 166 cells x 919 months: `tp` max difference 5.9e-5 mm/month (relative 7.5e-7; 9.4% of values differ), `t2m` max 2.4e-4 K, SWE identical, land/ocean pattern identical. Exact equality failed | applied | DECISIONS "Alaska and Yukon added" |
| Ocean cells | NaN in ERA5-Land, excluded from means; land cells taken from the first month | all ERA5-Land variables | `src/era5.py:195-198`; `regional_mean` | dataset covers land only | 43.7% of the main box is ocean. Mask cells (cells with data): PNW 7,361 (7,331), BC 13,395 (13,316), AB 9,461 (9,461), AK 27,711 (27,021), YT 8,753 (8,740), NorCal 2,820 (2,802), SoCal 1,312 (1,297) | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| Equal-area measurement | ESRI:102008 for every area; sources' own area fields never used | region areas; fire perimeters | `src/geo.py` `area_ha` | degrees are not a constant distance | region areas against official land / total area: CA -3.4% / +1.6%, PNW -2.1% / +1.2%, BC 0.1%, AB 0.3%, AK +0.9% (land), YT +0.4% | applied (regions); planned (fires) | DECISIONS "Phase 1 regions and ERA5 loading", "Alaska and Yukon added" |
| Region area rounding | nearest ha | `regions.geojson` `area_ha` | `src/regions.py:63` | display | none | applied | not recorded |

## Climate variables

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| Precipitation unit conversion | mm/month = value × 1000 × days_in_month, each month's own length (29-day February in leap years) | `tp`, `sf` | `src/era5.py` `convert_units` | monthly-means product stores m/day despite the "m" units attribute | wettest cell Feb 1950: 25.8 mm/day, about 720 mm | applied | data dictionary s.2a, 2d |
| Snowfall units | m water equivalent per day, the `tp` convention | `sf` | `src/era5.py` `convert_units` | checked on the first file: sf/tp at most 0.9996, median 0.41 (main domain, 1950; cells with tp > 1e-4 m/day), 2026-10-04 | confirms the convention | applied | data dictionary s.2d |
| Temperature conversion | °C = K - 273.15 | `t2m` | `src/era5.py:72` | project units | 1950 range -38 to +39 °C | applied | data dictionary s.2b |
| SWE negative clip | clip at 0 | `sd` | `src/era5.py` `convert_units` | values near -7e-25 are rounding noise | none beyond noise | applied | data dictionary s.2c |
| GRIB coordinates dropped | `expver`, `number` | all files | `src/era5.py:39-46` | `expver` can differ for recent months | none | applied | data dictionary s.2 |
| Strict file joins | `join="exact"`; error on duplicate months | `open_era5` | `src/era5.py:87-90` | catch grid or time mismatches between yearly files | none so far | applied | not recorded |
| NaN propagation in seasonal sums | `skipna=False` | seasonal totals | `src/era5.py:123` | ocean cells stay NaN instead of summing to 0 | not measured | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| Incomplete seasons dropped | a season missing any month is dropped | seasonal totals | `src/era5.py:125` `winter_total` | first winter (1949-50) and the current one are partial | 76 winters, 1950-51 to 2025-26 | applied | data dictionary s.4d |
| 1997-98 map baseline | mean of all 76 winters (1997-98 included); per-cell % of normal; region labels = regional total ÷ regional mean | 1997-98 map only (not binding on H5) | notebook 01, cell 10 | full-record principle | AB 61, AK 86, BC 97, NorCal 170, PNW 97, SoCal 228, YT 94% | applied | DECISIONS "Phase 1 regions and ERA5 loading" |
| Map colour scale | log2(% / 100), clipped to -2..2 (25-400%) | 1997-98 map | `src/figures.py:135-137` | 50% and 200% sit equally far from 100% | values beyond the range saturate (not measured) | applied | same entry |
| Map extent | (-169, -109, 32, 71.5), hard-coded | 1997-98 map | `src/figures.py:116` | display | none; departs from the single-source rule (D28) | applied | D28 |
| Glacier exclusion: cap rule | cells at the 10 m cap (>= `SWE_CAP_MM`, 9,990 mm) in any month | SWE regional means | `src/snow.py` `glacier_mask` | ERA5-Land holds glacier ice at 10 m water equivalent | probe 2026-10-04, whole record: 358 main cells (BC 130), 1,104 north (AK 748, YT 221); PNW, AB, NorCal, SoCal none | applied | DECISIONS "ERA5-Land SWE: glacier exclusion and April 1"; D27 |
| Glacier exclusion: perennial snow | snow above `PERENNIAL_MIN_MM` (10 mm) at the yearly minimum in ≥ 90% of `GLACIER_MASK_YEARS` (1950-2025); one fixed mask with the cap rule | SWE regional means | `src/snow.py` `glacier_mask` | about 5 m of SWE every April with no trend (main domain 5,341 mm in 1950, 5,199 mm in 2025): ice, not seasonal snow; the cap rule misses it | probe 2026-10-04: 394 main cells not capped (BC 206, AB 4), 1,146 north (AK 894, YT 48). Mean April SWE 1950-2025, cap excluded / both excluded: AK 417 / 229, YT 203 / 170, BC 515 / 443, AB 51 / 49 mm; all cells (1950-2026): AK 715, YT 478, BC 595, AB 52 mm. Cap rule alone leaves AK 82% too high. Built mask (cap or perennial), 2026-10-04: 752 main cells (BC 336, AB 4), 2,250 north (AK 1,642, YT 269), matching the probe. Mean April 1 SWE 1951-2026, excluded / all cells: AK 226 / 711, YT 167 / 475, BC 442 / 593, AB 67 / 69 mm; PNW 136, NorCal 68 unchanged. Year-to-year SD barely changes (the excluded cells add depth, not variability), so El Niño differences in % of the mean shrink with glacier cells in (AK -0.8% vs -0.3%, YT -7.0% vs -2.4%) while differences in SD stay the same | applied | same entry; D27 |
| April 1 SWE | 00:00 UTC 1 April field of hourly ERA5-Land (`reanalysis-era5-land`) | SWE | `src/download_era5_april1.py`; `src/snow.py` `open_april1` | `sd` monthly mean is centred mid-month; the March/April mean is biased low where melt has begun, more so in warm springs | 1951-2026, glacier excluded: April 1 correlates 0.97-0.99 with the March/April mean and sits 2-10% above it (PNW 135.8 vs 129.5 mm, AB 67.1 vs 61.0, AK 225.8 vs 220.8) | applied | same entry |
| PET | Thornthwaite (xclim `TW48`); zero below 0 °C | SPEI | not built | temperature-only, no extra variables needed | probe block (47-50N, 122-119W): DJF 0.018 mm/day, JJA 3.35 mm/day; winter SPEI behaves like SPI in cold regions | decided | DECISIONS "SPEI settings" |
| SPEI fit | scale 3; log-logistic (`fisk`), maximum likelihood; calibration 1951-2020 | SPEI-3 per cell | not built | standard SPEI choice; fixed baseline | probe on 900 cells: calibrated mean -0.007, SD 0.988; 514 s | decided | DECISIONS "SPEI settings" |
| SPEI clip | ±3.09 per cell (probability 0.001 per tail) | SPEI-3 per cell | not built | fitted tails gave -8.21 in the probe | not yet measured on the full grid | decided | DECISIONS "SPEI settings" |
| SPEI regional aggregation | per-cell SPEI, cos(latitude) regional mean, re-standardised to mean 0, SD 1 over 1951-2020, per season | regional SPEI-3 | not built | every km² counts equally; regional values back in SD units | not yet measured | decided | DECISIONS "SPEI settings" |
| Whiplash index | SPEI-3(JJA) - SPEI-3(preceding DJF), every year | whiplash | not built | draft definition | not yet measured | pending (pre-freeze "Whiplash timing") | data dictionary s.4c |
| `precip_anom` (H5) | months, baseline and units not set | H5 | not built | pre-freeze item | none | pending | ANALYSIS_PLAN "H5 definitions" |

## ENSO classification

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| ENSO index | ONI now (`ENSO_INDEX`); ONI or RONI is a pre-freeze item | every phase label | `src/config.py` | RONI is NOAA's official index (PIS 26-05) | 17 of 76 winters change class (phase or strong flag). ONI: 25 El Niño (7 strong), 25 neutral, 26 La Niña; fire record 14 El Niño (4 strong). RONI: 26 El Niño (7 strong), 24 La Niña; fire record 14 (3 strong). Mean RONI minus ONI: +0.23 (1951-80), +0.11 (1981-2005), -0.29 (2006-26) | pending | D15 |
| Phase thresholds | neutral by default; El Niño ≥ +0.5, La Niña ≤ -0.5 °C; strong is a separate flag, ≥ +1.5; inclusive cuts; DJF value only | every phase label | `src/config.py:31-33`; `src/download_oni.py:65-68` | single-value rule, not NOAA's five-season episode rule | -0.50 (1954-55) is La Niña. Near a cut: 2009-10 (1.47), 1991-92 (1.54), 1972-73 (1.55) at the strong cut; 1951-52 (0.52) at the El Niño cut | applied | data dictionary s.1 |
| Index value used | the `ANOM` column as published (2 decimals), not `TOTAL` | `enso_djf` | `src/download_oni.py:51-54` | the anomaly is the index | none | applied | data dictionary s.1 |
| First winter | DJF year ≥ 1951 | `el_nino_winters.csv` | `src/download_oni.py:62` | ERA5-Land starts January 1950, so winter 1949-50 is incomplete | 76 winters | applied | DECISIONS "Pre-start review" |
| Year pairing | DJF value Y = winter (Y-1)-Y, paired with fire season Y | all tables | `WINTER_MONTHS` | season crossing the new year | none | applied | data dictionary s.9 |
| Printed rounding | `+.1f` | console output only | `src/download_oni.py:85` | display | 2009-10 (1.47) prints +1.5 but is not strong | applied | log 2026-10-04 |
| Cached index reuse | `load_winters(refresh=False)` by default | notebook ONI/RONI comparison | `src/download_oni.py:46` | exploration without re-downloading | stale values possible (not measured) | applied | not recorded |
| Provisional values | RONI revised for up to two months after posting | latest winters | none | | latest RONI (JAS 2026): +1.69 | not handled | data dictionary s.1, s.9; DATA_SOURCES |

## Statistics (Phase 4; defaults in `src/config.py` and `src/stats.py`)

| Control | Value | Code | Why | Status | Record |
|---|---|---|---|---|---|
| Significance | α = 0.05 after correction | `config.py:109` | | applied (default) | ANALYSIS_PLAN "Reporting rules" |
| Permutation test | 10,000 permutations; two-sided; p = (count + 1) / (n + 1) | `config.py:110`; `stats.py:53` | | applied | ANALYSIS_PLAN "Headline methods" 1 |
| Bootstrap CI | 10,000 resamples; 95% percentile; resampled within each group | `config.py:111`; `stats.py:68-70` | | applied | same |
| HAC errors | Newey-West, maxlags 2; `use_t` not set | `config.py:112`; `stats.py:107` | | applied; `use_t=True` pending | ANALYSIS_PLAN "Small-cluster corrections" |
| Block bootstrap | moving blocks of 3; ceil(n/3) blocks, truncated to n | `config.py:113`; `stats.py:87-92` | autocorrelation check on HAC | applied | ANALYSIS_PLAN "Supporting methods" |
| Pooled-model errors | clustered by year | `stats.py:122` | | applied; Driscoll-Kraay pending | same |
| Prediction intervals | 80% (α 0.2), leave-one-year-out, plain OLS (not HAC) | `config.py:114`; `stats.py:144` | | applied; forward validation pending | ANALYSIS_PLAN "Headline methods" 4 |
| Random seed | 2026, the same stream re-seeded in every call | `config.py:115`; `stats.py:30` | reproducibility | applied | not recorded |
| Multiple comparisons | Holm by default, BH alongside; families not yet defined | `stats.py:125` | | families pending | ANALYSIS_PLAN "Correction families" |
| Trend handling | `year` term in regressions; `burn_detr` in permutation and bootstrap tests | | one method only | planned | ANALYSIS_PLAN "Outcomes" |
| Outcome transform | `log_burn = log(1 + ha)`; coefficients reported as 100 × (exp(b) - 1) | | burned area spans orders of magnitude | planned | ANALYSIS_PLAN "Outcomes"; data dictionary s.5 |
| Strong-only results | labelled exploratory | | about 5 strong winters | planned | ANALYSIS_PLAN "Reporting rules" |
| Descriptive summaries | SD with ddof = 1; % relative to the all-winter mean; "below median" uses strict < | `describe.py:25-42` | | applied | not recorded |

## Fire (Phase 3, after the freeze)

| Control | Value | Code | Why | Status | Record |
|---|---|---|---|---|---|
| No fire data before the freeze | rule | | pre-registration | applied | data dictionary s.5 |
| Fire record start | 1984 (`FIRE_FIRST_YEAR`, `config.py:37`); D8 notes "1985+" wording elsewhere | | MTBS start | planned | D8 |
| Minimum fire size | 405 ha (`MIN_FIRE_HA`), on computed area | | MTBS western mapping floor; applied to Canada for comparability | planned | ANALYSIS_PLAN "Outcomes" |
| Fire-season windows | `FIRE_SEASON_MONTHS`: Jun-Oct; AB Apr-Oct; AK, YT Apr-Sep provisional | | California and BC windows are pre-freeze items | planned | ANALYSIS_PLAN "Fire windows" |
| Wildfires only | prescribed burns removed | | MTBS includes prescribed burns | pending | ANALYSIS_PLAN "Fire record rules" |
| Boundary-crossing fires | clipped area; dated by ignition date | | | pending | same |
| MTBS to WFIGS cutover | about a 2-year MTBS lag | | | pending | same; data dictionary s.9 |
| Season length | first to last counted fire's start date; CNFDB date completeness to check | | | planned / pending | data dictionary s.5 |
| Zero-fire years | 0 jumps to about 6 for one 405 ha fire; handling not set | | | pending | ANALYSIS_PLAN "Zero-fire years" |

## Time and data handling

| Control | Value | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|
| ERA5-Land publication lag | 3 months (`ERA5_LAG_MONTHS`) | `config.py`; `download_era5.py` `months_available` | unpublished months | first version gave June for October, fixed to July; data ends 2026-07 | applied | DECISIONS "Pre-start review"; log 2026-10-04 |
| Hourly ERA5-Land lag | 7 days (`ERA5_HOURLY_LAG_DAYS`) | `download_era5_april1.py` `april1_years` | hourly data publishes about 5 days behind | none | applied | DECISIONS "ERA5-Land SWE: glacier exclusion and April 1" |
| Partial-year files | `_partial.nc`, re-requested every run, deleted once the full year exists; read by the `era5_land_*.nc` glob | `download_era5.py:113-124`; `era5.py:82` | | 919 months loaded | applied | same |
| Atomic downloads | write to `.tmp`, then rename | `download_era5.py:87`; `download_era5_april1.py` | no truncated files that later runs would skip | none | applied | same |
| Zipped responses | unpacked to a folder, which `open_era5`'s non-recursive glob does not read | `download_era5.py:89-97` | mixed variable types can arrive zipped | none so far: snowfall and soil moisture arrived as plain NetCDF (1950-1952 checked) | applied | same |
| Access-error stop | stop at the first 401/403; skip the year on other errors | `download_era5.py:80, 125-131` | an unaccepted licence fails every year | 77 x 403 before the fix | applied | D6 |
| ENSO merge | left merge on `year`, validated many-to-one | `era5.py:146` | every winter kept, whatever its phase | 532 rows (7 regions x 76 winters) | applied | not recorded |
