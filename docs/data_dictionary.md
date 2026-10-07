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
| Fire perimeters | MTBS, WFIGS/NIFC, CNFDB | 3 | planned (after freeze) | polygons + dates | ha, days |
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

**Index used.** RONI, chosen 2026-10-05 (`ENSO_INDEX`); every headline
test is repeated with ONI (`ENSO_ROBUSTNESS_INDEX`). Every table carries
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

**Time.** Monthly means, 1950 to about 3 months before today. In the NetCDF
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

- `temp_jja` (planned): June-August mean 2 m temperature per region, °C.
- `precip_anom_lag0`, `precip_anom_lag1` (planned; defined 2026-10-05):
  October-March total precipitation per region (`PRECIP_ANOM_MONTHS`;
  year Y = October Y-1 to March Y), as a z-score against the region's
  1991-2020 mean and SD (`PRECIP_ANOM_NORMAL_YEARS`). Unitless (SD).
  `lag0` = the Oct-Mar before fire season Y, `lag1` = the one before that.
  Longer than DJF so it catches California's autumn and March storms; it
  ends before every fire window opens (April at the earliest).
- `swe_z` in the tests = `era5_swe_z` (have): ERA5-Land April 1 SWE as a
  z-score against the region's own 1991-2020 mean and SD
  (`SWE_TEST_COLUMN`); the station index z (`station_swe_z`) is the
  check. Table: `results/tables/station_swe_region_year.csv`.
- `temp_mam` (planned; AK and YT, descriptive): March-May mean 2 m
  temperature per region, °C (`SPRING_MONTHS`), the spring warmth and
  early-melt path El Niño is thought to act through there.

- `snowfall_frac` (have, 2026-10-05): share of November-March
  precipitation that fell as snow, regional mean snowfall / regional mean
  precipitation over the season (`src.snow_soil`), 0 to 1. Year Y =
  November Y-1 to March Y. Also `sf_season_mm` and `tp_season_mm`, the two
  seasonal totals (mm). Table: `data/processed/snow_soil_region_year.csv`
  and `results/tables/`.
- `soil_moisture` (have, 2026-10-05): June-August mean volumetric soil water,
  0-28 cm (0.25 × layer 1 + 0.75 × layer 2, by thickness), m³/m³, regional
  mean. Year Y = summer Y. Same table.

## 5. Fire perimeters (after the freeze only), planned (Phase 3)

No fire data is downloaded, opened or summarised until `ANALYSIS_PLAN.md` is
frozen.

**What they are.** Polygons outlining the area each fire burned, with
attributes such as fire name, year, type and start date.

| Source | Coverage | How perimeters are mapped |
|---|---|---|
| MTBS (USGS / USDA Forest Service) | US, 1984 to about 2 years ago; fires ≥ 1,000 acres in the West | Landsat images before and after the fire; the burned area is mapped from the change in a burn index (dNBR), with analyst review. Includes prescribed burns, which the project removes |
| WFIGS / NIFC | US, recent years, filling MTBS's 2-year lag | Operational incident mapping: GPS walks, infrared flights, field sketches. Quality varies by incident |
| CNFDB (Natural Resources Canada) | Canada, decades back, by agency | Compiled from provincial, territorial and Parks Canada records; methods vary (aerial sketch, GPS, satellite). Some polygons lack dates; small and early fires patchy |

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

**Derived fire columns.**
- Burned area per region per season: sum of counted fires' clipped area, ha.
- `log_burn = ln(1 + ha)`: natural log, unitless. Large fire years span
  orders of magnitude, and logging tames that. A coefficient b on `log_burn`
  is reported as a percent change, `100 × (exp(b) - 1)`. A region-year with
  no counted fire gives 0, then jumps to about 6 for one 405 ha fire
  (pre-freeze item "Zero-fire years").
- `burn_detr`: residuals of `log_burn ~ year` per region, for tests without
  a trend term.
- Season length: days from the first to the last counted fire's start date.

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
- **Expanding-window validation:** fit on seasons 1984 to Y-1 only and
  predict Y, moving Y forward from 2004 (20 training seasons). Unlike
  leave-one-year-out, the model never sees years after the one predicted,
  as in the 2027 forecast.

## 9. Time conventions

- **Year label:** the DJF value labelled Y is the winter (Y-1)-Y, paired
  with fire season Y. The 1997-98 El Niño affects the **1998** fire season;
  the 2026-27 winter affects **2027**.
- **Seasons:** DJF = December-February (winter); JJA = June-August
  (summer); MAM = March-May.
- **Record lengths:** climate from winter 1950-51 (76 winters to 2025-26);
  fire from 1984.
- **Publication lags:** ERA5-Land about 3 months (`ERA5_LAG_MONTHS`);
  latest ENSO values revised for up to two months; MTBS about 2 years.
