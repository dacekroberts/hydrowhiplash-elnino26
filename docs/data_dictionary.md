# Data dictionary

Every kind of data the project works with: what it measures, how it is
measured, its units and the traps in using it. Raw sources first, then the
variables the pipeline derives from them, then the conventions shared by all
of them.

Tunable values (thresholds, years, months, CRS) live in `src/config.py`; this
file explains them but does not override them. Licences and attribution are
in `DATA_SOURCES.md`. Facts marked *confirm at download* come from the
source's documentation or general knowledge and still need checking against
the files themselves.

Status: **have** = downloaded; **planned** = in `ACTION_PLAN.md`.

| Data | Source | Phase | Status | Native units | Project units |
|---|---|---|---|---|---|
| ENSO index (ONI, RONI) | NOAA CPC | 0 | have (both; RONI used, ONI as check, 2026-10-05) | °C anomaly | °C anomaly |
| Precipitation | ERA5-Land | 0 | have | m/day | mm/month |
| 2 m air temperature | ERA5-Land | 0 | have | K | °C |
| Snow water equivalent (gridded) | ERA5-Land | 0 | have | m water equivalent | mm |
| Snowfall | ERA5-Land | 2 | have (2026-10-04) | m water equivalent/day | mm/month |
| Soil moisture, layers 1-2 | ERA5-Land | 2 | have (2026-10-04) | m³/m³ | m³/m³ |
| April 1 SWE (gridded snapshot) | ERA5-Land hourly | 2 | have (2026-10-04) | m water equivalent | mm |
| Glacier mask | derived from ERA5-Land `sd` (cap + perennial rule; the invariant field was not used, D27) | 2 | have | boolean | mask |
| Snow water equivalent (stations) | NRCS SNOTEL and snow courses (WA, OR, ID, AK), BC, Yukon, CanSWE (Alberta; BC and Yukon pillows) | 2 | have, cleaned (2026-10-05) | inches (NRCS; elevation in feet), mm (BC, Yukon), kg m-2 = mm (CanSWE) | mm; index in % of normal and SD |
| Snowfall fraction, summer soil moisture | derived from ERA5-Land `sf`, `tp`, `swvl1-2` | 2 | built (2026-10-05) | mm/month; m³/m³ | fraction 0-1; m³/m³ |
| PET, SPEI-3, whiplash | derived | 2 | built (2026-10-04) | mm/day; standardised | as native |
| Fire perimeters | MTBS, WFIGS/NIFC, CNFDB | 3 | have (2026-10-07, after the freeze) | polygons + dates (acres, ha fields not used) | ha (computed), days |
| Region boundaries | Natural Earth admin-1 | 1 | have | degrees (EPSG:4326) | polygons; ha in ESRI:102008 |

---

## 1. ENSO index (ONI and RONI)

**What it measures.** How much warmer or cooler than normal the sea surface
is in the Niño 3.4 box of the central-eastern tropical Pacific (5°N-5°S,
120°-170°W). Warm water there shifts tropical rainfall east, which bends the
Pacific jet stream: the classic El Niño winter is dry and mild in the PNW,
BC and Alberta and wet in southern California.

**How it is measured.** Sea surface temperature comes from NOAA's ERSST
(Extended Reconstructed SST) dataset, a monthly 2° global grid built from
ship, buoy and Argo float measurements, with statistical gap-filling in the
data-sparse early decades. CPC averages the Niño 3.4 box, subtracts a
climatology and smooths with a 3-month running mean.

- **ONI** (from ERSST v5, per the page name `ONI_v5`): the anomaly against a
  30-year base period. CPC uses centred base periods updated every 5 years,
  to limit drift from the warming trend (*confirm on the CPC ONI page*).
- **RONI** (from ERSST v6, per the CPC RONI page): the Niño 3.4 anomaly minus
  the average SST anomaly of the whole tropical belt (20°N-20°S), rescaled so
  its variance equals the original Niño 3.4 index. This removes the
  tropics-wide warming trend, leaving how much warmer Niño 3.4 is than the
  rest of the tropics, which is what drives the atmospheric response. RONI is
  NOAA's official ENSO index per NWS Public Information Statement 26-05.

**Units.** °C anomaly (a departure from normal, not a temperature).
Typical range about -2 to +2.6.

**Time.** Overlapping 3-month seasons labelled DJF, JFM, FMA ... NDJ. The
project uses the **DJF** value only. The DJF value labelled year Y is the
winter (Y-1)-Y, paired with fire season Y (see section 9).

**Project columns** (`data/processed/el_nino_winters.csv`): `year`,
`winter` (e.g. "1997-1998"), `enso_index` (the index named in
`ENSO_INDEX`; added 2026-10-06), `enso_djf` (°C), `phase` (`el_nino` if
≥ +0.5, `la_nina` if ≤ -0.5, else `neutral`), `strong` (≥ +1.5).

**Traps.**
- The project classifies on one DJF value. NOAA's official episode
  definition needs ≥ 0.5 for five consecutive overlapping seasons, so a few
  winters can differ from NOAA's own lists.
- Near-threshold winters flip with small changes (2009-10 is ONI 1.47,
  RONI 1.44; 1965-66 is RONI 1.53, strong only under RONI).
- The latest values are provisional: RONI values may change for up to two
  months after first posting.
- ONI and RONI disagree on 17 of 76 winters (`docs/plan_deviations.md` D15).
- RONI runs cooler than ONI in recent decades (mean difference -0.29 for
  2006-26) and so drifts down over the record (correlation with year -0.22,
  ONI -0.01): a regression with a `year` term separates the two.

**Index used.** RONI, chosen 2026-10-05 (`ENSO_INDEX`); every registered
test that uses the index (H1, H2, H3a, H3b, H4, C1, C2, strong-only) is
repeated with ONI (`ENSO_ROBUSTNESS_INDEX`), with ONI's own strong set and
near-threshold band. Every table carries
an `enso_index` column naming the index behind its `phase` labels.

## 2. ERA5-Land (gridded climate)

**What it is.** A reanalysis: a land-surface model (ECMWF's HTESSEL) run at
high resolution, driven by the weather of the ERA5 global reanalysis. ERA5
itself is a weather model continuously corrected by observations (stations,
satellites, balloons, aircraft). The result is a complete, physically
consistent estimate everywhere, including places with no stations. It is a
modelled best estimate, not a measurement; accuracy is lowest where
observations are sparse and terrain is complex (the BC Coast Mountains, the
Rockies).

**Grid.** Regular 0.1° latitude-longitude (about 9 km native). One cell is
11.1 km north-south everywhere, but east-west it shrinks with latitude: 9.4
km at 32°N and 5.6 km at 60°N. A cell at 60°N therefore covers about 62 km²
against about 104 km² at 32°N. An unweighted average over-counts northern
cells, which is why every regional mean goes through
`src.geo.regional_mean` with cos(latitude) weights. Two download domains
(`ERA5_DOMAINS`): main, 60.5°N to 32°N, 140°W to 109°W, 286 × 311 cells
(PNW, BC, AB, California); north, 71.5°N to 51°N, 169°W to 123.5°W (Alaska
and Yukon, added 2026-10-04), in `data/raw/era5_land_north/`. The two
overlap south of 60.5°N, where cells agree to float32 rounding (largest
relative difference 7e-7; SWE identical; land/ocean pattern identical), not
bit for bit: each request's GRIB packing depends on its area. Ocean cells are empty (NaN, 43.7% of
the domain): the dataset covers land only.

**Time.** Monthly means, 1950 to the last downloaded month. Months are
published within about a week (CDS probe 2026-10-07, D55); the download
stops `ERA5_LAG_MONTHS` (3, a margin, not the lag; 1 from the first
tracker update) before today, so the files end 2026-07. In the NetCDF
files the time dimension is `valid_time`, stamped on the first of each
month. Leftover GRIB coordinates `expver` and `number` are dropped before
combining years.

### 2a. Total precipitation (`tp`), have

- **Measures:** all liquid water reaching the ground as rain or snow
  (snow counted as its melted water). Comes from ERA5's precipitation,
  interpolated to the 0.1° grid without gauge correction (*confirm in the
  ERA5-Land documentation*).
- **Units:** in the monthly-means product, **metres per day**: the month's
  average daily total. The file's `units` attribute says "m", which is
  misleading. Convert with `mm/month = tp × 1000 × days_in_month`.
  Check: the wettest cell in February 1950 averaged 25.8 mm/day, about 720
  mm for the month, plausible for coastal BC.
- **Used for:** H1 (winter precipitation), SPEI (water supply), H5
  precipitation anomalies.

### 2b. 2 m air temperature (`t2m`), have

- **Measures:** air temperature 2 m above the ground, the height of a
  standard weather station. ERA5's temperature is adjusted to ERA5-Land's
  finer terrain with a lapse rate (colder with height).
- **Units:** kelvin. `°C = K - 273.15`. 1950 domain range: 235 to 312 K
  (-38 to +39 °C).
- **Used for:** `temp_jja` (summer mean, H3b control), Thornthwaite PET.

### 2c. Snow water equivalent (`sd`), have

- **Measures:** the depth of water the snowpack would make if melted.
  It is the snow quantity that matters for water supply: 1 m of fluffy new
  snow and 30 cm of dense spring snow can hold the same water.
- **Units:** metres of water equivalent. `mm = sd × 1000`. The variable is
  long-named "Snow depth" in the file but is water equivalent, not depth.
- **Traps.**
  - Glaciers are held at a 10 m cap all year. In 1950, 325 land cells (0.65%)
    sat at the cap and raised the domain's April SWE from 233 to 283 mm, so
    glacier cells are excluded before any regional mean.
  - A second group of cells never reaches the cap but holds a steady ~5 m
    of SWE every April, 1950-2025, with no trend: ice, not seasonal snow.
    The exclusion mask (`src.snow.glacier_mask`) drops cells at the cap in
    any month and cells keeping more than 10 mm at the yearly minimum in at
    least 90% of 1950-2025: 752 main-domain cells (BC 336, AB 4) and 2,250
    north (AK 1,642, YT 269). Mean April 1 SWE 1951-2026, excluded / all
    cells: AK 226 / 711 mm, YT 167 / 475, BC 442 / 593, AB 67 / 69.
  - It's a monthly mean. "April SWE" is the average over April, centred
    mid-month after low-elevation melt has started, not the April 1 snapshot
    that snow surveys measure. The project takes April 1 from hourly
    ERA5-Land instead (section 2g). Tiny negative values (about -7e-25) are
    rounding noise; clip to 0.
- **Used for:** gridded snowpack next to the station surveys (Phase 2).

### 2d. Snowfall (`sf`), have

- **Measures:** precipitation falling as snow, as melted-water depth.
- **Units:** m water equivalent per day (monthly mean of daily totals), the
  same convention as `tp`: confirmed on the first file, where sf/tp is at
  most 0.9996 (median 0.41, main domain, 1950). `mm/month = sf × 1000 ×
  days_in_month` (`src.era5.convert_units`). Folders
  `data/raw/era5_land_snow_soil/` and `data/raw/era5_land_north_snow_soil/`.
- **Used for:** snowfall fraction = snowfall / total precipitation, to show
  how much of a warm El Niño winter fell as rain instead of snow.

### 2e. Soil moisture, layers 1-2 (`swvl1`, `swvl2`), have

- **Measures:** the fraction of a soil layer's volume that is water. Layer 1
  is 0-7 cm, layer 2 is 7-28 cm.
- **Units:** m³ of water per m³ of soil (0 = bone dry; typical values 0.1 to
  0.45, depending on soil type).
- **Traps:** values depend on soil texture, so compare anomalies, not raw
  values, across regions.
- **Used for:** summer fuel dryness, alongside SPEI (descriptive unless
  `ANALYSIS_PLAN.md` adds it).

### 2f. Glacier mask (invariant), not used

- **Measures:** the fraction of each cell covered by glacier, one fixed
  field. It was the official alternative to flagging cells stuck at the 10 m
  SWE cap. Not used: the project derives its mask from `sd` itself (section
  2c; `DECISIONS.md` 2026-10-04 "ERA5-Land SWE: glacier exclusion and April
  1"; D27). Invariant fields are delivered for the whole globe, not cut to
  the domain.

### 2g. April 1 SWE from hourly ERA5-Land (`sd`), have

- **Measures:** snow water equivalent at 00:00 UTC on 1 April (late
  afternoon of 31 March local time), one field per year, 1950-2026. Same
  variable and grid as 2c, from the hourly dataset `reanalysis-era5-land`
  (DOI 10.24381/cds.e2161bac; ledger row in `DATA_SOURCES.md`).
- **Units:** metres of water equivalent; `mm = sd × 1000`, clipped at 0
  (`src.snow.open_april1`). Year label = the year of the April, i.e. winter
  (Y-1)-Y.
- **Check:** regional April 1 SWE correlates 0.97-0.99 with the mean of the
  March and April monthly means and sits 2-10% above it (1951-2026, glacier
  cells excluded), as a snapshot before mid-April melt should.
- **Files:** `data/raw/era5_land_april1/` and
  `data/raw/era5_land_north_april1/`, `era5_land_april1.nc` in each.

## 3. Snowpack from stations (NRCS, BC, Yukon, CanSWE for Alberta), have (cleaned 2026-10-05)

**What they measure.** April 1 snow water equivalent at fixed mountain
sites, the traditional measure of how much water the snowpack will release
in spring and summer.

**How.** Two methods, both in every network here (checked against the files,
2026-10-05):
- **Manual snow courses:** surveyors push a calibrated tube through the
  snowpack, weigh the core and record depth and SWE at a marked transect on
  set dates, usually around the first of the month.
- **Automated stations (snow pillows):** a fluid-filled pillow on the ground
  weighs the snow above it and reports SWE continuously; SNOTEL sites are
  this type, often with a sonic depth sensor too.

**Units.** NRCS (SNOTEL and snow courses) reports inches of water
(`mm = in × 25.4`) and station elevation in **feet** (`m = ft × 0.3048`); BC
and Yukon report mm and metres; CanSWE reports kg m⁻² (= mm) and metres.
Depth, where used, is cm or inches.

**Traps.** Sites sit at particular elevations, so a regional average reflects
where the stations are, not the whole region. Networks start in different
years and add or drop sites over time. Coverage is sparse in northern
Alberta. Point measurements and ERA5-Land's 9 km cells measure different
things, so expect level differences between them.

**What "April 1" means in each raw file** (downloaded 2026-10-05, raw and
unfiltered under `data/raw/stations/`; cleaned by `src.stations`, below):
- NRCS SNOTEL (`MONTHLY`, period reference START): month 4 is the midnight
  reading opening 1 April (the daily value dated 31 March).
- NRCS snow courses (`SEMIMONTHLY`, START): the April 1 survey is month 4,
  part 1, with its own collection date, usually late March.
- BC manual surveys: `Survey Period` = `01-Apr`, taken about 26 March to
  1 April.
- Yukon: `target_date` = 1 April (sample dates run 11 days early to 15
  days late).
- CanSWE: actual sampling dates on a daily axis; take the value nearest
  1 April within a window (pillows have daily values).

**Raw-data traps found at download** (to handle in cleaning):
- NRCS SNOTEL values before 1980 are almost all regression back-estimates
  (QC flag B: 932 of 976 April 1 values), not measurements.
- 2,163 NRCS snow-course April 1 values carry a placeholder collection date
  of 1 July (1950-2009); 89 negative SNOTEL values (lowest -108 in); 25
  listed NRCS stations return no data.
- BC: the archive already runs to June 2026, so 96 April 1 course-years are
  in both the archive and the current-season file; headers have leading
  spaces; CRLF line endings.
- Yukon: comment lines are quoted, so `comment="#"` does not skip them;
  6.5% of April 1 values are estimated from depth.
- CanSWE station prefixes: `ALE-` Alberta, `BCE-` BC, `YT-` Yukon, `HQ-`
  Hydro-Québec (excluded). April 1 ±15 days since 1950, stations with 30 or
  more years: ALE 124 (11 pillows), BCE 251 (32 pillows), YT 58.

**Fields and flags per source** (as read by `src/stations.py`):

| Source | Station id in the table | Date | Flags carried in `flags` |
|---|---|---|---|
| NRCS | triplet `id:state:network` (`SNTL` pillow, `SNOW` course) | SNTL: 1 April; courses: `collectionDate` | `nrcs_qc:` E (minor adjustment for sensor noise), K (estimate), C (different sensor equation), N (no validation profile), X (external estimate); `nrcs_qa:` P (provisional), A (approved), R (raw); `date_unknown` (1 July placeholder). B (back-estimate) and S (suspect) are dropped. V (validated) is not written. |
| BC | `BCE-<Number>` (CanSWE's id, so the two match) | `Date of Survey` | `bc:<Survey Code>` (PROBLEM, EARLY/LATE, TRACE, PRELIMINARY, UNSCHEDULED, ...; undefined in the files) |
| Yukon | `YT-<location_code>` | `sample_date` (the real day; `target_date` is 1 April) | `yukon:estimated` (depth measured, density from history) |
| CanSWE | its own `station_id` (`ALE-`, `BCE-`, `YT-`; pillows often end in `P`) | daily axis | `canswe:` A (sampling problems), B (outside nominal period), C (A and B), E (estimate), R (revised), T (trace) |

**Cleaned table** (`data/processed/station_swe_apr1.csv`, not committed;
built 2026-10-05): one row per station and year, columns `station_id`,
`source` (nrcs, bc, yukon, canswe), `network`, `method` (manual, pillow),
`lat`, `lon`, `elevation` (m), `year`, `swe_apr1_mm`, `sample_date` (empty
when unknown), `flags`, `region`. 71,250 station-years, 2,168 stations
after duplicate sites are counted once (71,759 and 2,180 before;
`dedupe_sites`), 1950-2026, five regions (no California stations). Rules and their counts:
`docs/methods_register.md` "Station snowpack".

**Regional station index** (`station_swe_region_year.csv`, also in
`results/tables/`):
- `station_swe_pct`: median across stations of SWE as % of each station's
  1991-2020 mean (stations with a normal of at least 10 mm). 100 = normal.
  Floors at 0, so in snow droughts with many bare stations the median
  collapses (PNW 2015: 3.3%).
- `station_swe_z`: mean across stations of (SWE - station mean) / station
  SD, in SD units. 0 = normal.
- `n_stations`, `n_stations_pct`: stations behind each value; the index is
  empty below 5.
- `era5_swe_apr1_mm`, `era5_swe_pct`, `era5_swe_z`: ERA5-Land April 1 SWE
  (glacier cells excluded) and the same two scales against its own
  1991-2020 regional mean.

**Traps found in cleaning:** the station network sits high (PNW median
station normal 3.1 times the ERA5-Land regional mean), so the station index
understates losses concentrated at low elevations (PNW strong El Niño
winters: low third of stations -42 points, high third +3). Comparing
stations and grid in mm is meaningless; compare % or z.

## 4. Derived climate variables, built (Phase 2) unless marked planned

### 4a. Potential evapotranspiration (PET)

- **Measures:** how much water the air could draw from a fully wet
  surface: the atmosphere's demand for water.
- **Method:** Thornthwaite (1948), from monthly mean temperature and
  latitude (day length) only: PET = 16 (L/12) (N/30) (10 T / I)^a mm per
  month, T the month's mean temperature (clipped at 0, so PET is 0 at or
  below 0 °C and cold winters' water balance is precipitation alone), L the
  mean day length in hours, N the days in the month, I the cell's **heat
  index** (how warm its climate is, from the 12 monthly normals: the sum of
  (Tm/5)^1.514 over 1951-2020 monthly means) and a a cubic in I
  (6.75e-7 I^3 - 7.71e-5 I^2 + 0.01792 I + 0.49239). As in the SPEI
  reference implementation (R package SPEI), the power law holds at every
  temperature: Thornthwaite's separate table for monthly means at or above
  26.5 °C is not used, which matters mostly in SoCal summers (pre-freeze
  audit 2026-10-07, P6; D49). Simple, but
  temperature-only PET tends to overstate drying as temperatures rise.
  Penman-Monteith (humidity, radiation, wind) would need extra ERA5-Land
  variables.
- **Units:** mm/day in `src.whiplash`.
- **Trap (fixed 2026-10-06):** xclim's TW48, followed until then, recomputes
  I from each calendar year. In an incomplete year (2026 to July) I is about
  half-size, so PET came out 1.5-2.1 times too high in January-April and
  SoCal's DJF 2026 SPEI-3 about 1 SD too dry; the 2027 forecast input
  (Jan-Feb only) would have been worse. In a year with no month above 0 °C,
  I = 0 and PET was 0/0 = NaN for the whole year (the icefield cells with no
  February SPEI). A per-year I also damps PET's response to warming, and
  xclim leaves out N/30. Now I is climatological, N/30 is in, and a cell
  whose normal never thaws has PET 0 (pre-freeze audits; D47).
- **Trap (fixed 2026-10-05):** day length is undefined in polar day and
  night, and xclim's TW48 returns NaN there, so north of about 68N every
  DJF and JJA SPEI-3 was missing and regional means silently skipped
  those cells (AK 15-17% of its area weight, YT 5-6%). `pet_thornthwaite`
  then repeated xclim's TW48 steps (its own Thornthwaite form since
  2026-10-06, above) with polar day lengths set to 24 h and 0 h; south of the polar circles PET is unchanged (largest difference
  3e-15 mm/day). Months partly in polar day (May, July far north) also
  change, by up to 0.42 mm/day, since xclim averaged only the non-polar
  days.

### 4b. SPEI-3 (Standardised Precipitation-Evapotranspiration Index)

- **Measures:** whether a 3-month period was wetter or drier than usual,
  after accounting for both supply and demand. Monthly water balance
  D = P - PET is summed over 3 months, fitted to a probability distribution
  over a calibration period, and converted to a standard normal score.
- **Units:** dimensionless, in standard deviations. 0 = normal; -1 is
  moderately dry (drier than about 84% of the calibration years); -2 is
  extreme. Typical range -3 to +3.
- **Settings (decided 2026-10-04, `DECISIONS.md` "SPEI settings"):**
  scale 3; log-logistic fitted by maximum likelihood per calendar month;
  calibration 1951-2020; D summed as monthly amounts in mm (until
  2026-10-07 daily rates were averaged, so February counted as a full
  month; pre-freeze audit P5, D49); per-cell values clipped to ±3.09;
  regional SPEI is
  the cos(latitude) mean of per-cell SPEI, re-standardised to mean 0 and
  SD 1 over 1951-2020 for each season. Per-cell SPEI is cached in
  `data/processed/spei3_cells_<domain>.nc`.

### 4c. Whiplash index

- **Definition:** SPEI-3(JJA) - SPEI-3(preceding DJF), every year,
  from the re-standardised regional values (`src.whiplash`). Table:
  `data/processed/whiplash_region_year.csv`; joined with April 1 SWE in
  `data/processed/whiplash_swe_region_year.csv` (`src.phase2`).
- **Units:** standard deviations of SPEI.
- **Reading it:** negative = a swing from wetter-than-usual winter to
  drier-than-usual summer (e.g. winter +1, summer -1 gives -2). Positive =
  the reverse.
- **Role (decided 2026-10-05):** a concurrent, descriptive mechanism
  variable, never tested; summer falls inside the fire season. In the
  north a positive value is two signals: a dry winter plus a wetter summer
  (El Niño minus neutral under RONI, BC winter SPEI-3 -0.54, summer +0.34;
  2026-10-07 refit),
  so it does not mean drier overall. Its forecastable parts, winter SPEI-3
  and April 1 SWE, are the H6 predictors.

### 4d. Other regional climate columns

- `precip_djf_mm` (have, Phase 1): winter (December-February,
  `WINTER_MONTHS`) precipitation total per region, mm, summed per cell
  from mm/month and then averaged with cos(latitude) weights. Table:
  `data/processed/djf_precip_region_year.csv` (`python -m src.era5`), 76
  winters x 7 regions with `enso_index`, `enso_djf`, `phase`, `strong`.
  Cells count for a region when their centre lies inside its polygon; the
  35.5N grid row sits exactly on the NorCal/SoCal split and goes to SoCal
  (`DECISIONS.md` 2026-10-04, "Phase 1 regions and ERA5 loading").

- **Climate controls table** (built 2026-10-08, session 7; `python -m
  src.climate_vars`): `data/processed/climate_controls_region_year.csv` and
  `results/tables/`, 532 rows (7 regions x 1951-2026) with the ENSO
  columns. Also holds `precip_djf_mm` (H1's input, identical to
  `djf_precip_region_year.csv`, added 2026-10-08 so it is committed and
  pinned; audit M4). Every land cell in the region counts, glacier cells included
  (only the SWE means and SPEI leave them out); cos(latitude) regional
  means via `src.geo.regional_mean`.
- `temp_jja` (have, 2026-10-08): June-August mean 2 m temperature per
  region, °C, the mean of the three monthly means (months not weighted by
  length). Year Y = summer Y; 2026 empty (no August yet). The H3b control.
  Means 1951-2025: SoCal 27.0 (deserts included), NorCal 21.7, PNW 18.0,
  AB 15.2, BC 11.4, YT 10.3, AK 10.3 °C.
- `precip_octmar_mm` and `precip_anom_lag0`, `precip_anom_lag1` (have,
  2026-10-08; defined 2026-10-05): October-March total precipitation per
  region (`PRECIP_ANOM_MONTHS`; year Y = October Y-1 to March Y), mm, and
  its z-score against the region's 1991-2020 mean and SD
  (`PRECIP_ANOM_NORMAL_YEARS`, SD with ddof 1). Unitless (SD). `lag0` =
  the Oct-Mar before fire season Y, `lag1` = the one before that (matched
  on year - 1; 1951 empty). Longer than DJF so it catches California's
  autumn and March storms; it ends before every fire window opens (April
  at the earliest). Correlation with DJF precipitation 0.75 (AK) to 0.91
  (SoCal). Trap: the 1991-2020 normal includes years after an
  expanding-window training cut (frozen; a stated limitation).
- `swe_z` in the tests = `era5_swe_z` (have): ERA5-Land April 1 SWE as a
  z-score against the region's own 1991-2020 mean and SD
  (`SWE_TEST_COLUMN`); the station index z (`station_swe_z`) is the
  check. Table: `results/tables/station_swe_region_year.csv`.
- `temp_mam` (have, 2026-10-08; AK and YT, descriptive): March-May mean
  2 m temperature per region, °C (`SPRING_MONTHS`), the spring warmth and
  early-melt path El Niño is thought to act through there. Built for all
  seven regions in the climate controls table, 1951-2026.

- `snowfall_frac` (have, 2026-10-05): share of November-March
  precipitation that fell as snow, regional mean snowfall / regional mean
  precipitation over the season (`src.snow_soil`), 0 to 1. Year Y =
  November Y-1 to March Y. Also `sf_season_mm` and `tp_season_mm`, the two
  seasonal totals (mm). Table: `data/processed/snow_soil_region_year.csv`
  and `results/tables/`.
- `soil_moisture` (have, 2026-10-05): June-August mean volumetric soil water,
  0-28 cm (0.25 × layer 1 + 0.75 × layer 2, by thickness), m³/m³, regional
  mean. Year Y = summer Y. Same table.

## 5. Fire perimeters, have (downloaded 2026-10-07, after the freeze)

**What they are.** Polygons outlining the area each fire burned, with
attributes such as fire name, year, type and start date. Downloads:
`python -m src.download_mtbs`, `src.download_wfigs`, `src.download_cnfdb`
(versions and sizes in `DATA_SOURCES.md`); processing `python -m src.fire`.

| Source | Coverage | How perimeters are mapped |
|---|---|---|
| MTBS (USGS / USDA Forest Service) | US, 1984 to about 2 years ago; fires ≥ 1,000 acres in the West | Landsat images before and after the fire; the burned area is mapped from the change in a burn index (dNBR), with analyst review. Includes prescribed burns, which the project removes |
| WFIGS / NIFC | US, recent years, filling MTBS's 2-year lag | Operational incident mapping: GPS walks, infrared flights, field sketches. Quality varies by incident |
| CNFDB (Natural Resources Canada) | Canada, decades back, by agency | Compiled from provincial, territorial and Parks Canada records; methods vary (aerial sketch, GPS, satellite). Some polygons lack dates; small and early fires patchy |

**MTBS file** (`mtbs_perims_DD.shp` in `mtbs_perimeter_data.zip`, release
of 2026-10-07): 30,932 polygons, EPSG:4269 (NAD83 geographic), one per
fire. Fields used: `event_id` (state code + location + ignition date),
`incid_name`, `incid_type`, `ig_date` (ignition date, YYYY-MM-DD). Types:
Wildfire 16,779, Prescribed Fire 9,639, Other 4,311, Wildland Fire Use 203.
There is no "Unknown" although the metadata documents one; "Other" is read
as the plan's Unknown (D58). Also `irwinid` (mostly empty for older fires),
`burnbndac` (acres from pixels, not used), `asmnt_type` (Initial, Extended,
"(SS)" = single scene), severity thresholds. Trap: boundaries include
unburned islands. Mapping lags: 2024 still lacks 114 WFIGS fires (22-58%
of each US region's area; McDonald AK, Lone Rock OR, Wapiti ID) and 2025
has 14 fires in the five states, so the project takes MTBS for ignitions
through 2023-12-31 and WFIGS after (`MTBS_WFIGS_CUTOVER`, D61). On fires
both hold, WFIGS/MTBS area is 0.96-0.99 (one-to-one pairs, 2021-2024).

**WFIGS file** (`wfigs_perimeters.geojson`, Hub export of 2026-10-07):
42,553 perimeters, EPSG:4326, coordinates with Z (73.5 M vertices; read in
2D). One perimeter per incident, the latest; a "Daily" perimeter can
predate containment. Share of counted WFIGS area from Daily perimeters in
the tested seasons (audit 2026-10-08 L4): NorCal 2024 84%, NorCal 2025
49%, SoCal 2024 42%, PNW 2025 23%, PNW 2024 19%, SoCal 2025 3%, AK 0%;
the 2023 source-agreement check covered this product mix (|d| at most
0.032). Fields used:
`attr_UniqueFireIdentifier` (YYYY-unit-number; unique among the rows the
build reads, discovered 2023 on; 50 pairs in 2020 share an id, a Final and
a Daily perimeter under different names, audit 2026-10-08 L2), `poly_IncidentName`,
`attr_IncidentTypeCategory` (WF 40,968, RX 1,585; no other values),
`attr_FireDiscoveryDateTime` (text "Sat, 19 Nov 2022 00:52:20 GMT", UTC;
converted to the origin state's local date, `WFIGS_STATE_TZ`),
`attr_POOState` ("US-WA"). Traps: `attr_IrwinID` is empty on 26,116 rows
(use the unique fire identifier); `poly_FeatureCategory` (Daily, Final,
Prescribed Fire) disagrees with the type field on 48 rows in the five
states, so the type field decides; complexes are stored as their child
fires only (110 children in the western states, no parent outline), so no
area is counted twice; the layer is live, so a snapshot date matters.

**CNFDB file** (`NFDB_poly.zip`, release NFDB_poly_20250630): two
shapefiles, 1972-2020 (41,210 polygons) and 2021-2024 (7,361), NAD83
Lambert conformal conic (metres). Fields used: `SRC_AGENCY` (BC, AB, YT,
PC = Parks Canada, and the other provinces), `FIRE_ID`, `FIRENAME`,
`YEAR`, `MONTH`, `DAY` (agency fire date; 0 or empty when unknown;
`DATE_TYPE` says whether it is a report, start, ignition or fire date),
`CAUSE` (N natural, H human, H-PB prescribed burn, U unknown, Re reburn),
`PRESCRIBED` ("yes" on the same 309 polygons as H-PB since 1984: Parks
Canada 297, AB 7, Ontario 5; 306 fires after the dissolve). Not used: `SIZE_HA`
(agency), `CALC_HA` (CFS, Canada Albers). Traps: Parks Canada sent no
polygons for 2018-2020 (update log; measured 2026-10-08: none at or above
405 ha in BC, AB or YT for 2016-2021, only Nahanni in 2016-2017 and small
fires in 2021; D71),
so fires inside national parks are missing in those years, and the
provinces did not map them (AB 2016-2019 flagged `parks_gap`, NBAC
sensitivity run, D69); fires on Department of National Defence land
(CFB Wainwright and Suffield, AB) are in no CNFDB polygon in any year:
109,773 ha over 1984-2024, 1% of AB's counted burned area, a stated
limitation (D71); agency minimum
sizes differ by decade (all far below 405 ha after 1984); Yukon 2022 has
97 large fires without month or day (D59). 104 polygons have no year at
all (`YEAR` = -9999, `CFS_NOTE1` "Fire year unknown, refer to decade";
YT 85, Parks Canada 19) and fall outside the read (`YEAR >= 1984`): they
cannot be given a season. Clipped to the study regions: AB 1980s 6
polygons, 10,835 ha (about 8% of AB's 1984-89 area), YT 1980s 6 polygons,
9,601 ha, and 1990s 21, 37,323 ha (about 2% of YT's 1984-99 area); a
stated limitation for AB and YT 1984-1999 (audit 2026-10-08 M2).

**Units and measurement rules.**
- **Area:** hectares, computed only by `src.geo.area_ha`, which projects to
  North America Albers Equal Area Conic (ESRI:102008) first. Never measured
  in EPSG:4326 (degrees aren't a constant distance), and never taken from a
  source's own area field. 1 ha = 10,000 m²; 1 acre = 0.4047 ha.
- **Fires counted:** ≥ 405 ha (`MIN_FIRE_HA`, = 1,000 acres) in every
  region, so US and Canadian records are comparable.
- **Fire season:** (decided 2026-10-05, `FIRE_SEASON_MONTHS`) PNW
  June-October; BC and Alberta April-October; Alaska and Yukon
  April-September; NorCal and SoCal June to January of the next year (a
  January Y+1 fire counts for season Y), by ignition date
  (`FIRE_SEASON_MONTHS`; decided 2026-10-05, D43).

**Derived fire columns** (built 2026-10-07; `results/tables/fire_region_year.csv`,
one row per region and season, 1984 to the region's last test year, 291
rows; every rule and count in `docs/methods_register.md` "Fire").
- `burn_ha`: burned area of the season's counted fires in the region, ha:
  each source's clipped pieces are unioned (overlap counted once, D61) and
  the sources summed. `double_ha`: the overlap left out (ha; rounded to
  1e-6 ha and clipped at 0, since audit round 4 L8 found floating-point
  noise of up to 4e-9 ha).
- `n_fires`: counted fire pieces in the region (a fire in two regions
  counts in each; 48 such fires, a fire being source, id and year). Pieces, not fires (audit 2026-10-08 L11): 13 slivers under
  1 ha of fires crossing an edge count in the neighbouring region (AB 5,
  BC 5, NorCal 1, PNW 1, YT 1), and WFIGS has 3 pairs sharing a name,
  region and season under different ids (Whiskey Mountain OR 2024, same
  unit, likely one fire; Mineral OR/ID and Horseshoe CA, different units),
  where the union keeps the area right but `n_fires` may count one fire
  twice; CNFDB fires in several polygons count once since 2026-10-08 where
  the parts lie within 1 km (D67).
  `n_undated`: CNFDB pieces without a
  month, counted for season YEAR (D59). `n_unknown_type`: MTBS "Other"
  pieces (the plan's Unknown, D58). `source`: MTBS, WFIGS, CNFDB, or
  "MTBS+WFIGS" (SoCal and NorCal seasons that span the 2024-01-01
  cutover), "none" for a zero-fire season.
- `log_burn = ln(1 + burn_ha)`: natural log, unitless. Large fire years span
  orders of magnitude, and logging tames that. A coefficient b on `log_burn`
  is reported as a percent change, `100 × (exp(b) - 1)`. A region-year with
  no counted fire gives 0, then jumps to about 6 for one 405 ha fire
  (pre-freeze item "Zero-fire years"). `parks_gap`: True for AB 2016-2019, where CNFDB holds no Parks Canada
  polygon and NBAC shows park area missing (`PARKS_GAP_SEASONS`, D69).
  `zero_fire`: True for such a season
  (1 of 291: SoCal 2014).
- `burn_detr`: residuals of `log_burn ~ year` per region (OLS over the
  region's test seasons), for the permutation and bootstrap tests, which
  have no trend term. Computed when a test runs by `src.stats.detrend`
  (built 2026-10-08), not stored in the table; the zero-fire sensitivity
  re-detrends without the zero seasons.
- `first_fire`, `last_fire`, `season_days`: first and last ignition date
  among counted fires with a full date, and the days between; empty with
  fewer than 2 such fires (9 region-seasons). Descriptive only.
- `winter`, `enso_index`, `enso_djf`, `phase`, `strong`: the ENSO columns of
  the winter before (year Y = winter (Y-1)-Y), from `el_nino_winters.csv`.
- `data/processed/fire_events.csv` (not committed): one row per fire-region
  piece (9,755 rows after the 1 km CNFDB dissolve of 2026-10-08, D67; 9,756
  after the round 1 dissolve, 9,758 per polygon; including 2026 WFIGS pieces
  outside the tests), with `fire_ha` (whole fire), `clipped_ha`, `season`,
  dates and flags; `cnfdb_year` (the agency YEAR, CNFDB only) and `n_parts`
  (CNFDB polygons merged into the fire: 1, or 2 for 10 counted fires; empty
  for MTBS and WFIGS). A CNFDB `fire_id` can name more than one fire in a
  year, since agencies reuse ids and parts over 1 km apart stay separate
  (e.g. BC 1994-K50087, two fires of 4,919 and 2,702 ha; audit round 3 L6).
- **Frozen-rules variant** (built 2026-10-08, D62; `python -m src.fire
  --frozen-rules`, from `fire_events.csv`):
  `results/tables/fire_region_year_frozen_rules.csv`, same columns and 291
  rows. `burn_ha` is the sum of clipped pieces (no union, `double_ha` 0),
  MTBS "Other" pieces and CNFDB pieces without a month left out, the frozen
  years. For the robustness run of every burned-area test only. Total
  burned area against the main table: AB 93.2%, YT 96.4%, AK 98.6%, NorCal
  99.5%, PNW 99.6%, SoCal 99.7%, BC 100.1% (summing counts CNFDB overlap
  twice); AB 1997 and YT 2022 (every fire undated; YT 2022 held 233,108 ha) become zero-fire seasons.

**Parks Canada sensitivity table** (D69; `python -m src.parks_gap`,
after `src.fire`): `results/tables/fire_region_year_parks_nbac.csv`, the
main table with `nbac_park_ha` (NBAC national-park burned area, ha; whole
fire floored at 405 ha by GID, park parts clipped and unioned, counted by
NBAC YEAR, since NBAC has no ignition date) added to `burn_ha` for the
`parks_gap` seasons, `log_burn` recomputed, `n_nbac_park` NBAC park fires;
0 elsewhere. For a reported sensitivity run only. In 7 seasons outside
the gap, `burn_ha` differs from the main table's in the last printed digit
(at most 4.7e-10 ha, `log_burn` at 5e-15) from the CSV round trip in
`with_park_area`; no value a test uses changes (audit round 5 L4, left as
is so the pinned table is not rebuilt).

**Later retrievals** (`data/raw/later/<stamp>/...`, never committed;
D73, D88): a download run with `--stamp` writes to the stamped twin of
its usual folder and closes it with `retrieval.json`: `stamp` (the
retrieval date), `source`, `note`, `recorded_utc`, and per file its
`bytes` and `sha256`. A closed folder is never rewritten. Tables rebuilt
from a retrieval go to `results/tables/tracker/<stamp>/` (committed),
beside the pinned tables, never over them. Trap: a stamped ERA5-Land
folder holds only the years that had no full-year file on disk, so it is
read on top of `data/raw`, not instead of it.

**Stamped rebuilds** (`results/tables/tracker/<stamp>/`, `python -m
src.<builder> --stamp <date>`; D88): the same table names as the pinned
ones, rebuilt from the files on disk plus the latest closed retrieval
not after the stamp. `rebuild.json`: per builder, `run_utc`, `commit`,
`retrievals_read` (each stamped folder read, with the sha256 of its
`retrieval.json`) and `tables`. `changed_cells.csv`: one row per cell
that differs from the pinned table of the same name: `table`, `region`,
`year`, `column`, `old`, `new`, `change` (changed, added, removed).
Floats are compared exactly. Traps: an added 2026 or 2027 row is
expected, a changed cell in an earlier year is not and needs
explaining; once a stamped index retrieval exists, the ENSO columns come
from it, and CPC's revisions show up here as changed cells.
Intermediate files (the SPEI cells, glacier masks, per-builder tables)
go to `data/processed/later/<stamp>/`, never committed.

**Input pins** (`results/tables/input_pins.csv`, `python -m
src.pin_inputs`, 2026-10-08): path, size, sha256 and modification time of
every input the tests read: the 7 committed input tables named in
`PINNED_RESULT_TABLES` (by name, so result tables written beside them are
not refused; audit round 3 M1), ENSO downloads, fire downloads (NBAC
included), `fire_events.csv`; `--verify` raises if any changed. RONI is
revised monthly and WFIGS is live, so the tests use these copies.
`pin_inputs.assert_pinned(path)` refuses any table outside the pins, for
the hypothesis loaders (audit round 4 L6).

**Measurement outputs, not committed, not pinned:**
`data/processed/parks_gap_measure.csv` (`MEASURE_TABLE`, `python -m
src.parks_gap --measure`): NBAC park and defence-land area and CNFDB Parks
Canada area per region and season, each a union per season as `burn_ha`,
behind the register's agreement figures (D71).
`data/processed/nbac_coverage.csv` (`python scripts/nbac_coverage.py`,
about 90 minutes): NBAC fire area at or above 405 ha with no CNFDB polygon
of the same calendar `YEAR` under it, per region, year and NBAC admin
label (audit round 4 F1). One number holds both whole fires CNFDB lacks
and outline disagreement at the rims of matched fires; the rims alone
were 0.3-1.2% of a season's NBAC area in the AB years probed (audit round
5 L6). For the session 8 decision on the NBAC re-run only.
`data/processed/nbac_coverage_fires.csv` (same run, from 2026-10-11): the
same areas per NBAC fire (`GID`), region, admin label and year (ha). The
script classes a fire within a region as "missing" where more than
`NBAC_MISSING_SHARE` (0.5) of its NBAC area there is uncovered, else
"rim".
`data/processed/interior_alaska_check.csv` (`python
scripts/interior_alaska_check.py`): `temp_jja`, `temp_mam` (deg C),
`precip_djf_mm`, `precip_octmar_mm` (mm) per year 1951-2026 for `AK` (the
study polygon, 27,711 ERA5-Land cells) and `AK_interior` (NOAA NCEI
climate divisions 3, 4 and 5, Central, Northeast and Southeast Interior,
clipped to the AK polygon: 11,772 cells, 41.8% of its area), built by
`src.climate_vars.climate_regional`, with the ENSO columns. Climate only;
no fire column; no registered test reads it. The boundary file
(`data/raw/ak_climate_divisions/`, `python -m src.download_ak_divisions`)
is 13 polygons in NAD83 longitude and latitude; its `FEATURE` field is the
division number and its area fields are not used.

## 6. Region boundaries, have (Phase 1)

- **Source:** Natural Earth admin-1 states and provinces, 1:10 million scale
  (`ne_10m_admin_1_states_provinces`), restricted to the US and Canada.
- **Regions:** PNW = Washington + Oregon + Idaho; BC; AB; AK = Alaska east
  of 169°W (`ALASKA_WEST_LON`); YT = Yukon; California split at 35.5°N
  (`CA_SPLIT_LAT`) into NorCal and SoCal. Roles: primary (PNW, BC, AB),
  north (AK, YT), contrast (NorCal, SoCal).
- **Areas (ha, ESRI:102008):** PNW 64.23 M, BC 94.56 M, AB 66.37 M, AK
  149.39 M, YT 48.45 M, NorCal 27.71 M, SoCal 13.26 M. Polygons include
  inland water but not sea, so they sit between official land and total
  areas (US totals include coastal water).
- **Units:** coordinates in degrees, EPSG:4326, for storage and display;
  region areas in ha via ESRI:102008.
- **Trap:** boundaries are generalised at 1:10 million, so coastlines and
  islands are simplified. Fine for masking 9 km climate cells and clipping
  fires; not a survey-grade boundary.

## 7. Coordinate systems

| CRS | Units | Used for |
|---|---|---|
| EPSG:4326 (WGS 84 latitude-longitude) | degrees | storage and display of all vector data; the ERA5-Land grid |
| ESRI:102008 (North America Albers Equal Area Conic) | metres | every area calculation, so a hectare means the same in California and Alberta |

## 8. Statistical quantities (Phase 4)

- **Effect size:** difference in means (El Niño minus other years), or a
  regression coefficient, reported first, with a 95% confidence interval.
- **Percent change:** `100 × (exp(b) - 1)` for coefficients on `log_burn`.
- **p-values:** after Holm correction within each hypothesis's family (BH
  alongside); significance at α = 0.05.
- **Prediction intervals:** 80% (`PREDICTION_ALPHA = 0.2`), with
  leave-one-year-out coverage reported.
- **One-sided and two-sided tests:** a one-sided test looks for an effect
  in one stated direction only (more power, but an effect the other way
  cannot count); two-sided looks both ways. Each test's direction per
  region is in `TEST_DIRECTIONS` (`greater`, `less`, `two-sided`, or
  None for descriptive), from `ANALYSIS_PLAN.md` "Directions and
  sidedness".
- **Interaction term:** `a:b` in a model formula lets the effect of `a`
  change with `b`. In C1 and C2, `enso_djf:year_c` asks whether El Niño's
  effect grows or shrinks over time; `year_c` is the year minus the mean
  year, so the `enso_djf` coefficient is the effect at mid-record.
- **Contrast:** a single combination of coefficients tested as one
  number. H4's is the mean ENSO slope of PNW, BC and AB minus SoCal's.
- **Holm correction:** within a family of m tests, sort the p-values; the
  smallest must be below α/m, the next below α/(m-1), and so on; at the
  first failure it and all larger ones are not significant. Controls the
  family-wise error rate, the chance of even one false positive in the
  family (5 tests at 0.05 uncorrected: about 23%).
- **Benjamini-Hochberg (BH):** controls the false discovery rate, the
  expected share of false positives among results called significant:
  the largest rank k with p ≤ (k/m)·α, and tests 1 to k pass. More
  lenient; a result passing BH but not Holm reads as suggestive.
- **t critical values (`use_t`):** with about 42 seasons, confidence
  intervals and p-values use the t distribution (n minus parameters
  degrees of freedom; for the Driscoll-Kraay H4 fit, number of years minus
  1, set explicitly because statsmodels counts it from row order) rather
  than the normal, a little wider.
- **Driscoll-Kraay errors:** standard errors for the pooled H4 model that
  allow regions in the same year to be correlated and each region to be
  correlated with itself over nearby years (statsmodels `hac-groupsum`,
  maxlags 2); year clustering allows only the first.
- **Small-sample correction (D65):** robust covariances are scaled up for
  the parameters the fit used: n/(n - k) for Newey-West, G/(G - 1) x
  (N - 1)/(N - K) for Driscoll-Kraay and year clustering
  (`ROBUST_SMALL_SAMPLE_CORRECTION`); SEs 4-5% wider.
- **F test:** a joint test that several coefficients are all 0. H4's
  joint test of the four interactions is F(4, years - 1) from the
  Driscoll-Kraay covariance. Size (simulated, 2026-10-08): it rejects a
  true null far more often than 5%; see `docs/methods_register.md`.
- **Test size:** the share of datasets with no true effect in which a test
  gives p < 0.05; a correct test gives about 5% (`scripts/stats_size_check.py`).
  `results/tables/test_size.csv` (audit round 2 L1): `shape`, `labels` (the
  registered tests whose p it labels), `method`, `sidedness`, `scenario`,
  `label_scenario` (True for the row the printed labels use: AR(1) 0.3
  errors with regions correlated 0.5 for the H4 panel shapes, "AR(1) 0.3,
  pooled" over 2,000 datasets for the per-region shapes; audit round 3 L4), `reps`, `rejection_rate`, `mc_se`,
  `measured`.
- **Lag-1 autocorrelation:** the sample autocorrelation at lag 1, one mean
  and the whole series' sum of squares (`stats.lag1_autocorrelation`, as
  statsmodels `acf`; round 2 L5).
- **Expanding-window validation:** fit on seasons 1984 to Y-1 only and
  predict Y, moving Y forward from 2004 (20 training seasons). Unlike
  leave-one-year-out, the model never sees years after the one predicted,
  as in the 2027 forecast.

### 8a. Result tables of the registered run (`results/tables/run1/`)

Written once by `src.run_hypotheses` on 2026-10-12 (tag
`registered-run1`); never edited (`docs/post_results_protocol.md`). Each
has a `.provenance.json` beside it (commit, input hashes, UTC time, seed,
package versions); `conda_list_explicit.txt` is the full environment.

- **`registered_tests.csv`** (52 rows): one row per registered test and
  region. **`reported_beside.csv`** (205 rows): the same columns for
  everything reported beside them, uncorrected. Columns:
  - `run_kind`: `registered`, or which side run: `oni_robustness` (ONI in
    place of RONI), `frozen_rules`, `parks_nbac`, `zero_fire` (SoCal's
    zero-fire season 2014 dropped from H2 and given its own 0/1 column
    in the regressions), `station_z` (station SWE in place of
    ERA5-Land), `strong_only` (strong El Niño winters against all other
    years, H1 and H2, once per index) and `strong_flip` (the same with
    every winter near the strong threshold switched to the other
    group; D52), `h4_secondary`,
    `h6_combined`, `block_bootstrap`, `h3_gap`, `lag1_autocorrelation`.
  - `enso_index`, `fire_table`: the index and fire table read
    (`fire_table` empty where no burned area is read: H1, C1).
  - `family`, `test`, `region`, `term`, `outcome`, `method`,
    `alternative`, `years`, `n`: the Holm family, the test, the
    coefficient or difference reported, the outcome, the method, the
    registered direction, the first and last year and the number of
    years (region-years for H4).
  - `n_group`: El Niño winters in the group (permutation tests only).
    `n_zero`: zero-fire seasons in the sample.
  - `estimate`, `ci_low`, `ci_high`, `ci_method`: the effect and its 95%
    interval. Units: mm of December to February precipitation for H1;
    log points of burned area for every `log_burn` row (per 1 unit of
    the predictor: 1 degree C of DJF index, 1 standard deviation of
    precipitation, SWE or SPEI); SWE standard deviations per index unit
    per year for C1; log points per index unit per year for C2. The
    interval is always two-sided, also where the test is one-sided.
  - `pct_change`, `pct_low`, `pct_high`: `100 × (exp(b) - 1)` for
    regression rows on `log_burn`; empty for H1, H2 and C1.
  - `se`, `statistic`, `df`, `p`: standard error, t (or F) statistic,
    degrees of freedom, and the p-value in the registered direction.
  - `p_holm`, `p_bh`, `significant`: Holm- and BH-adjusted p within the
    family, and the Holm verdict at 0.05; filled for registered rows
    only.
  - `size`, `size_shape`: the simulated rejection rate under no effect
    for this kind of test, and which row of `test_size.csv` it came
    from. `plain_ols_p`, `plain_ols_size`: the same test with ordinary
    standard errors, and its size (D66, D68).
  - `note`: the number of distinct permutations, or what a side row
    changed.
- **`validation.csv`** (39 rows): prediction checks per model and
  region. `method` is leave-one-year-out or expanding window;
  `coverage` is the share of years whose burned area fell inside the
  80% prediction interval (0.80 is the target); `rmse`, `mae` are the
  errors in log points; `rmse_trend`, `mae_trend` are the same for a
  model with the year trend only, over the same years; `skill` =
  1 - rmse / rmse_trend (above 0: the predictor beat the trend alone).

### 8b. Outputs for the site

- **`results/figures/burned_area_anomaly_series_roni.png`**
  (`python -m src.fire_figures`): per region, each fire season's
  `log_burn` minus the region's mean over its seasons with a counted
  fire, in log points; raw, not detrended. +2.3 is ten times the typical
  season (the right-hand axis), where "typical" is the geometric mean in
  the panel title. The zero-fire season is a marker, not a bar.
- **`results/figures/headline1_el_nino_vs_rest.png`**,
  **`headline2_enso_strength.png`**, **`headline3_north_vs_socal.png`**
  (`python -m src.results_figures`): one row per region and registered
  test of `run1`, the estimate as a dot on its two-sided 95% interval,
  a line at no effect. Units as in 8a: mm of December to February
  precipitation for H1, log points of burned area for H2, log points
  per 1 degree C of the winter index for H3a, H3b and H4. A filled
  green dot is significant after Holm, a hollow one is not. Trap:
  headline 3 sets the H4 contrast under four H3a slopes for context;
  the contrast comes from one pooled model ending at the pooled last
  year, so it is not the difference of the rows above it.
- **`results/figures/headline4_interval_coverage.png`** (same command):
  per region, the share of seasons whose burned area fell inside the
  H3a model's 80% prediction interval (`coverage` in
  `run1/validation.csv`), leave-one-year-out and expanding window; 80%
  is the target. Trap: 21 or 22 seasons stand behind each expanding
  window point, so one season moves it by about 5 points.
- **`results/figures/burned_area_season_history_roni.html`**
  (`python -m src.fire_figures`): the full-record view as an interactive
  chart, an HTML fragment the home page includes (plotly.js comes from
  its CDN, so the chart needs a network connection). Same values as the
  PNG: each season's `log_burn` minus the region's mean, shown on the
  axis as a multiple of the typical season; hover gives `burn_ha`. The
  dotted slot is `FORECAST_YEAR`, empty until it is verified.
- **Figure colours** (all figures above, D86): a bar is `fire`, `water`
  or `snow` by what it measures; an `enso-soft` band and a tick mark a
  season after an El Niño winter. The 1997-98 map runs `precip-dry-2`
  (25% of normal) to `precip-wet-2` (400%) on a log scale.
- **`results/tables/site_settings.json`** (`python -m src.site_settings`):
  the `src/config.py` values the site quotes in prose (thresholds, years,
  the fire floor, test settings, the freeze date and commit), since the
  site reads only `results/`. `tests/test_site_settings.py` fails if it
  no longer matches the config.
- **`results/tables/methods_numbers.csv`** (`python
  scripts/methods_numbers.py`; main checkout only, it reads four
  uncommitted measurement files): the measured numbers the methods page
  quotes. One row per number: `measure`, `group` (region, year, source
  or variable; "all" if none), `value`, `unit` (ha, percent, ratio,
  correlation, count), `n` (the fires, years, winters or pairs behind
  it), `basis` (the file it came from). Measures: the overlap that
  summing perimeters would count twice; winters the two indices class
  differently; NBAC area in fires missing from CNFDB, on provincial and
  territorial land; CNFDB national-park area by year; defence-land
  area and share; ERA5-Land against station snowpack (standardised and
  percent of normal); Interior Alaska against the statewide series;
  WFIGS over MTBS area on one-to-one fire pairs (`SOURCE_PAIR_YEARS`,
  `scripts/source_pairs.py`, D89). Descriptive; no test reads it.
  Traps: a ratio near 1 on matched pairs says nothing about fires only
  one product holds; the station correlation differs by measure.
- **`results/tables/rollout_calendar.json`** (`python -m src.rollout`;
  D87): the rollout calendar, one item per arrival the site waits on.
  Not data and not a result: dates and wording only. Per item: `id`;
  `kind` (record, data, index, release, season, verification); `start`
  and `end` (ISO dates; equal unless `precision` is "window");
  `precision` ("on" a day, "by" a day, "about" a day, "after" a day, or
  a "window"); `when` (the date as shown to readers); `title`;
  `site_change` (what changes on the site); `prepare` (the work behind
  it); `basis` (the setting or record the date comes from); `reader`
  (shown on the tracker page or not); `remind_on` (`start` minus
  `ROLLOUT_REMINDER_LEAD_DAYS`, or null where the item is checked at
  another item's reminder, listed in `checked_at`); `evidence` (a path
  under `results/`) and `done` (true only if that file exists);
  `forecast_stage` (first, final or null). `reminders` lists each
  reminder date with the items folded into it. Trap: a window is an
  expectation from a publisher's release record, not a measurement.
  `tests/test_rollout.py` fails if the file no longer matches the
  config.
- **`theme/tokens.json`** (the design tokens; D86): every colour (one
  value per theme, light and dark; the map ramps one value for both),
  typeface, spacing step, radius and stroke width, each with a usage
  note. Not data and not a result: presentation only. `src/theme.py`
  reads it; `python -m src.theme` writes **`site/theme/light.scss`**,
  **`dark.scss`** and **`fonts.html`** for the Quarto site, and
  `tests/test_theme.py` fails if they are stale. Colour families carry
  one meaning each: `fire` burned area, `water` precipitation, `snow`
  snowpack, `enso` a season after an El Niño winter, `evergreen` the
  frame and the Holm verdict.

**Map page and interactive charts (session 11; D98).** Three HTML
fragments in `results/figures/`, each included by a site page as is:

- `region_map.html` (`python -m src.map_page`): the seven regions as an
  inline SVG, the values as JSON and a short script. Per dataset, region
  and year it holds a class (0 to 4) and a text. Burned area: `burn_ha`
  over the region's typical season, which is `exp(mean log_burn) - 1`
  over seasons with a counted fire, the same baseline as the season
  history chart (a multiple, not a percent). Winter rain:
  `precip_octmar_mm` as a percent of the region's 1991-2020 mean (not the
  z-score the tests use). Snowpack: the committed `era5_swe_pct`, with
  `era5_swe_apr1_mm` as the raw value. Summer temperature: `temp_jja`
  minus the region's 1991-2020 mean, in °C. Trap: a class is relative to
  the region's own normal, so the same colour in two regions is not the
  same number of hectares or millimetres. A missing value has no entry.
  The outlines are simplified for display; never measure from them.
- `djf_precip_history_roni.html` (`python -m src.interactive`): December
  to February precipitation per region as a percent departure from the
  mean of the winters in the table (1951 on), raw, not detrended; the
  hover gives millimetres. Trap: the mean is over all winters shown, not
  the 1991-2020 normal the map uses.
- `burned_area_season_history_roni.html`: unchanged in its numbers; since
  session 11 drawn by the same builder, with year labels on every panel.

**Sea-surface temperature for the map (session 11; D99; display only).**
NOAA ERSST v6: a reconstruction of monthly sea-surface temperature from
ship, buoy and float measurements, filled in statistically so every ocean
cell has a value; 2° grid (about 220 km at the equator), cell centres at
even latitudes and longitudes, longitude in degrees east from 0 to 358.
`sst` is in °C; land and ice-covered cells are missing. No calculation in
this project reads it: it colours the map's ocean panels and nothing else.

- `src.ocean.winter_anomalies` returns two fields per winter (year Y is
  December Y-1 to February Y). `anomaly`: each month's value minus that
  cell's 1991-2020 mean for the month, averaged over the three months.
  `relative`: the same with the area-weighted mean anomaly of 20°S to
  20°N removed, which is what the relative index (RONI) does. The map
  shows `relative`.
- `results/tables/sst_nino34_check.csv`: per winter, the Niño 3.4 box
  mean (5°S to 5°N, 170°W to 120°W) of both fields beside the project's
  `enso_djf`. Trap: `sst_relative_nino34` is not RONI. RONI is rescaled
  at the end to the variance of the plain index, so it runs about a
  quarter larger in strong winters (1.69 against 2.13 in 1997-98).
- Traps: NOAA's own `ssta` variable in the files is not used; the last
  two months of the record are rewritten on each NOAA update, so a later
  download can differ for the latest winter; longitudes are east-positive,
  so 170°W is 190.

### 8c. Prediction model tables (`results/tables/prediction_v1/`; exploratory, D83)

Written by `python -m src.prediction` on 2026-10-12, after `run1` was
seen. Exploratory and uncorrected: reported apart from the registered
tests, never in place of one (`docs/prediction_model_spec.md`). One
sub-folder per run, same three tables in each, a `.provenance.json`
beside every table: `forecast/` (predictors known in spring),
`hindsight/` (June to August temperature added; cannot forecast),
`no_zero_fire/` (the forecast run without SoCal 2014). Column `run`
repeats the label.

- **`predictions.csv`**: one row per region and unseen season (2004 to
  the region's last test year). `n_train`: the region's seasons before
  that year. `penalty`: the ridge penalty chosen inside the training
  seasons, per training row (dimensionless; larger means the predictors
  count for less). `actual`, `predicted`, `pi_low`, `pi_high`: `log_burn`
  in log points, and the 80% interval (prediction plus or minus 1.28
  times the region's training residual spread). `covered`: whether the
  interval held the actual value. `cut`: the two-thirds quantile of the
  region's training `log_burn`; `actual_yes`: `actual` above `cut`;
  `p_yes`: the model's probability of that, 0 to 1. Columns ending
  `_trend` are the same for the trend-only baseline (`log_burn ~ year`
  per region).
- **`skill.csv`**: one row per `scope` (all seven, AK and YT, other five,
  then each region). `rmse`, `mae` in log points, with `_trend` for the
  baseline; `skill` = 1 - rmse / rmse_trend (above 0: the predictors
  beat the trend). `coverage`: share of seasons inside the 80% interval
  (0.80 is the target). `brier`, `brier_trend`, `brier_base`: mean
  squared gap between the probability and the 0 or 1 outcome, for the
  model, the trend-only model and a constant one in three (lower is
  better). `bss_base`, `bss_trend` = 1 - brier / the reference's.
  `n_yes`: seasons above the cut; `n_called`: seasons with `p_yes` of 0.5
  or more; `hits`, `false_alarms`: called seasons that were, or were not,
  above the cut. `*_low`, `*_high`: 95% interval from resampling the
  unseen years (whole years, 10,000 draws, seed 2026); descriptive, not
  a test.
- **`coefficients.csv`**: one row per predicted year: `n_train_rows`,
  `penalty`, and each predictor's coefficient in log points of burned
  area per 1 standard deviation of the predictor (standardised within
  region on the training seasons).
- **Traps:** the yes or no cut comes from earlier seasons, and burned
  area trends up, so more than a third of unseen seasons are "yes" (83
  of 151 in the forecast run): `bss_base` credits the trend, `bss_trend`
  does not. `swe_z` is 0 for SoCal ("no information"). Only the fit is
  forward-looking: `swe_z` and `spei3_djf` are built on fixed reference
  periods that contain later years (as in `stats.expanding_window`).

### 8d. Prediction model version 1b (`results/tables/prediction_v1b/`; exploratory, D83)

Written by `python -m src.prediction_1b` on 2026-10-12, after version 1's
results were seen (`docs/prediction_model_spec.md` section 8). One
sub-folder per variant (`regions`, `scaled`, `regions_scaled`,
`spring_inputs`, `june_update`, `hindsight`; the last cannot forecast),
each with the three tables of 8c, and `variants.csv` at the top. Columns
as in 8c except:

- **New inputs:** `precip_anom_lag1` (the previous winter's October to
  March precipitation, in standard deviations from the 1991-2020 normal;
  section 4);
  `snowfall_frac` (snowfall over total precipitation, November to March,
  0 to 1); `temp_mam` (March to May mean temperature, degrees C; known
  by 1 June).
- **`predictions.csv`:** `penalty_shared`, `penalty_region`: the two
  ridge penalties chosen (`inf` in the second: no regional departures).
  `scale`: the region's training spread around its trend, log points;
  the divisor behind `skill_scaled`. `train_spread`: the model's
  training residual spread, log points. `cut_above_trend`: the
  two-thirds quantile of the training seasons' distances above the
  trend, log points. `actual_yes`: `actual` more than `cut_above_trend`
  above `predicted_trend` (a different bar from 8c's `cut`; the two
  yes or no outcomes are not comparable). `spread`, `spread_trend`: the
  spread behind the 80% interval and `p_yes`; `spread_from` says whether
  it came from the region's earlier unseen-year errors ("past errors",
  once 8 exist) or the training spread ("training").
- **`skill.csv`:** adds `skill_scaled` with its interval: skill with
  every error divided by its region's `scale` first, so regions count
  about equally in a pooled row.
- **`coefficients.csv`:** long: one row per predicted year, region and
  predictor; `coefficient` is the region's own (shared plus departure),
  in log points per standard deviation of the predictor.
- **`variants.csv`:** the three group rows of every variant's
  `skill.csv`, with version 1's forecast and hindsight runs (`v1`,
  `v1_hindsight`) rescored with 1b's intervals and yes or no bar.
- **Traps:** the variants share the same 22 unseen years, so the best of
  them flatters itself; read the whole table. `actual_yes` rates differ
  by region (AB 14%, BC 62%) because a straight trend runs ahead of AB
  and behind BC. For the first 8 unseen years of each region the
  interval still comes from the training spread.

### 8e. Prediction model version 1c (`results/tables/prediction_v1c/`; exploratory, D83)

Written by `python -m src.prediction_1c` on 2026-10-12, after version
1b's results were seen (`docs/prediction_model_spec.md` section 9). Two
sub-folders, `last_burn` and `ceiling` (the second cannot forecast),
each with the three tables of 8d, and `variants.csv`: 1b's rows with the
two new variants below them. Columns as in 8d except:

- **`burn_lag1`** (input of `last_burn`; built in memory, not stored):
  the region's `log_burn` of the season before, in log points. The first
  season (1984) takes the mean of the region's values for 1985 to 2003.
- **`spei3_jja`**, **`soil_moisture`** (inputs of `ceiling`, with
  `temp_jja`): summer SPEI-3 in standard deviations and June to August
  soil moisture, 0 to 28 cm, in m3/m3 (section 4). Known only after the
  summer.
- **Traps:** `ceiling` is not a forecast: it shows how much of the
  trend-only error the summer's seasonal means account for (pooled
  0.126; BC 0.483, AK 0.345, NorCal 0.257, YT 0.221; AB, PNW and SoCal
  near zero). Soil moisture in June to August is measured while the
  season is under way. For a real spring forecast, `burn_lag1` needs
  last season's fires already counted, and CNFDB polygons arrive late.

## 9. Time conventions

- **Year label:** the DJF value labelled Y is the winter (Y-1)-Y, paired
  with fire season Y. The 1997-98 El Niño affects the **1998** fire season;
  the 2026-27 winter affects **2027**.
- **Seasons:** DJF = December-February (winter); JJA = June-August
  (summer); MAM = March-May.
- **Record lengths:** climate from winter 1950-51 (76 winters to 2025-26);
  fire from 1984.
- **Publication lags:** ERA5-Land monthly means about a week (D55;
  `ERA5_LAG_MONTHS` 3 is a download margin, 1 from the first tracker update);
  latest ENSO values revised for up to two months; MTBS about 2 years.
