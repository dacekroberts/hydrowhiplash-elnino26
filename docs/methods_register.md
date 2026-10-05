# Methods register

Every control, cap, filter, threshold and exclusion the pipeline applies,
kept up to date as each one is added, so the Methods and limitations section
can be written from it. One row per control: its value, where it lives, why it
exists and its measured effect. Values live in `src/config.py`; this file
describes them and does not override them. The reasoning for each judgment
call is in `DECISIONS.md`; departures from the plans are in
`docs/plan_deviations.md`; units and traps per dataset are in
`docs/data_dictionary.md`.

**Status:** *applied* = in the pipeline now; *planned* = in the plans, not
yet built; *pending* = waiting on a decision (usually a pre-freeze item).

Add a row when a control is introduced, and update its *measured effect*
when it is re-measured (keep the old number with its date).

## Spatial

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| Area-weighted regional means | cos(latitude) weights | every regional climate mean | `src.geo.regional_mean` | a 0.1° cell at 60N covers about 62 km², at 32N about 104 km² | not re-measured; an unweighted mean over-counts northern cells | applied | data dictionary s.2 |
| Region membership | a cell belongs to a region when its centre lies inside the polygon | every regional mean | `src.era5.region_masks` | simple, no partial cells | fractional-overlap weighting changes regional series by at most 1.4% (correlation ≥ 0.99998), 2026-10-04 | applied | DECISIONS 2026-10-04 "Phase 1 regions and ERA5 loading" |
| Grid snapping | lat/lon rounded to 4 decimals | all ERA5-Land files | `src.era5.snap_grid` | 35.5N is stored as 35.499999999999645, which would place the NorCal/SoCal boundary row by float noise | the 35.5N row goes to SoCal by rule, not by accident | applied | DECISIONS 2026-10-04 "Phase 1 regions and ERA5 loading" |
| California split | 35.5N (`CA_SPLIT_LAT`) | NorCal, SoCal | `src/regions.py` | north-south precipitation seesaw | the 35.5N grid row goes to SoCal | applied | data dictionary s.6 |
| Alaska west clip | 169W (`ALASKA_WEST_LON`) | AK | `src/regions.py` | outer Aleutian and Bering Sea islands, 1.1 Mha (0.7% of the state, almost no fire), cross the antimeridian | AK area 149.39 Mha | applied | DECISIONS 2026-10-04 "Alaska and Yukon added" |
| Domain assignment | each region read from the first `ERA5_DOMAINS` box containing it | all regions | `src.era5.assign_domains` | two download boxes overlap south of 60.5N | overlap cells agree to float32 rounding (max relative difference 7e-7) | applied | data dictionary s.2 |
| Ocean cells | NaN in ERA5-Land; excluded from means | all ERA5-Land variables | `regional_mean` (NaN-aware weights) | dataset covers land only | 43.7% of the main box is ocean | applied | data dictionary s.2 |
| Equal-area measurement | ESRI:102008 for every area | fire perimeters, region areas | `src.geo.area_ha` | degrees are not a constant distance | region areas within about 2% of official figures | applied (regions); planned (fires) | data dictionary s.7 |

## Climate variables

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| Precipitation unit conversion | mm/month = tp × 1000 × days_in_month | `tp`, `sf` | `src.era5.convert_units` | monthly-means product stores m/day despite the "m" units attribute | wettest cell Feb 1950: 25.8 mm/day, about 720 mm | applied (`tp`); planned (`sf`) | data dictionary s.2a, 2d |
| Snowfall units | m water equivalent per day, same as `tp` | `sf` | (to add to `convert_units`) | confirmed on the first file: sf/tp ≤ 0.9996, median 0.41 (main domain, 1950) | 2026-10-04 | planned | data dictionary s.2d |
| SWE negative clip | clip at 0 | `sd` | `src.era5.convert_units` | values near -7e-25 are rounding noise | none beyond noise | applied | data dictionary s.2c |
| Incomplete seasons dropped | a season missing any month is dropped | seasonal totals | `src.era5.winter_total` | first winter (1949-50) and the current one are partial | 76 winters, 1950-51 to 2025-26 | applied | data dictionary s.4d |
| Glacier exclusion, cap rule | cells at the 10 m SWE cap (≥ 9,990 mm) in any month | SWE | not built | ERA5-Land holds glacier ice at 10 m water equivalent | whole record: 358 main cells (BC 130), 1,104 north cells (AK 748, YT 221). Mean April SWE, 1950-2025, all cells vs cap excluded: BC 595 → 516 mm, AK 715 → 417 mm, YT 478 → 204 mm; PNW, AB, NorCal, SoCal have none (2026-10-04) | pending | ACTION_PLAN Phase 2 |
| Perennial snow cells | snow left at the annual minimum (> 10 mm) in ≥ 90% of years, 1950-2025 | SWE | not built | about 5 m of SWE every April with no trend (main 5,341 mm in 1950, 5,199 in 2025), so ice or model artefact, not seasonal snow; the cap rule misses them | not capped: 394 main (BC 206, AB 4), 1,146 north (AK 894, YT 48). Excluding them too: BC 515 → 443 mm, AK 417 → 229 mm, YT 203 → 170 mm, AB 51 → 49 mm (2026-10-04) | pending | to be logged with the glacier decision |
| April 1 SWE | approximation method to be chosen | SWE | not built | `sd` is a monthly mean centred mid-month | | pending | ACTION_PLAN Phase 2 |
| SPEI settings | PET method, distribution, calibration period, scale 3, per cell or regional | SPEI-3, whiplash | not built | pre-freeze item | | pending | ANALYSIS_PLAN "SPEI settings" |

## ENSO classification

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| ENSO index | ONI now; ONI vs RONI is a pre-freeze item | every phase label | `ENSO_INDEX` | RONI is NOAA's official index (PIS 26-05) | 17 of 76 winters change class between the two | pending | D15 |
| Phase thresholds | El Niño ≥ +0.5, La Niña ≤ -0.5, strong ≥ +1.5 °C, on the DJF value only | every phase label | `src.download_oni` | single-value rule, not NOAA's five-season episode rule | a few winters differ from NOAA lists; 2009-10 (1.47), 1991-92 (1.54), 1972-73 (1.55) sit at the strong cut | applied | data dictionary s.1 |
| Year pairing | DJF value Y = winter (Y-1)-Y, paired with fire season Y | all tables | `WINTER_MONTHS` | season crossing the new year | | applied | data dictionary s.9 |

## Fire (Phase 3, after the freeze)

| Control | Value | Applies to | Code | Why | Measured effect | Status | Record |
|---|---|---|---|---|---|---|---|
| Minimum fire size | 405 ha (`MIN_FIRE_HA`), on computed area | every region | not built | MTBS western mapping floor; applied to Canada for comparability | | planned | ANALYSIS_PLAN "Outcomes" |
| Fire-season windows | `FIRE_SEASON_MONTHS` (Jun-Oct; AB Apr-Oct; AK, YT Apr-Sep provisional) | every region | not built | California and BC windows are pre-freeze items | | planned | ANALYSIS_PLAN "Fire windows" |
