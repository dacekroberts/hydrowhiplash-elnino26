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
| ENSO index (ONI, RONI) | NOAA CPC | 0 | have (ONI) | °C anomaly | °C anomaly |
| Precipitation | ERA5-Land | 0 | have | m/day | mm/month |
| 2 m air temperature | ERA5-Land | 0 | have | K | °C |
| Snow water equivalent (gridded) | ERA5-Land | 0 | have | m water equivalent | mm |
| Snowfall | ERA5-Land | 2 | planned | m water equivalent/day | mm/month |
| Soil moisture, layers 1-2 | ERA5-Land | 2 | planned | m³/m³ | m³/m³ |
| Glacier mask | ERA5-Land (invariant) | 2 | planned (option) | fraction 0-1 | mask |
| Snow water equivalent (stations) | SNOTEL, BC, Alberta | 2 | planned | inches (SNOTEL), mm (BC, AB) | mm |
| PET, SPEI-3, whiplash | derived | 2 | planned | mm/month; standardised | as native |
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
`winter` (e.g. "1997-1998"), `enso_djf` (°C), `phase` (`el_nino` if
≥ +0.5, `la_nina` if ≤ -0.5, else `neutral`), `strong` (≥ +1.5).

**Traps.**
- The project classifies on one DJF value. NOAA's official episode
  definition needs ≥ 0.5 for five consecutive overlapping seasons, so a few
  winters can differ from NOAA's own lists.
- Near-threshold winters flip with small changes (2009-10 is ONI 1.47).
- The latest values are provisional: RONI values may change for up to two
  months after first posting.
- ONI and RONI disagree on 17 of 76 winters (`docs/plan_deviations.md` D15).

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
  - It's a monthly mean. "April SWE" is the average over April, centred
    mid-month after low-elevation melt has started, not the April 1 snapshot
    that snow surveys measure. Tiny negative values (about -7e-25) are
    rounding noise; clip to 0.
- **Used for:** gridded snowpack next to the station surveys (Phase 2).

### 2d. Snowfall (`sf`), planned

- **Measures:** precipitation falling as snow, as melted-water depth.
- **Units:** m water equivalent per day (monthly mean of daily totals, the
  same convention as `tp`; *confirm at download*).
- **Used for:** snowfall fraction = snowfall / total precipitation, to show
  how much of a warm El Niño winter fell as rain instead of snow.

### 2e. Soil moisture, layers 1-2 (`swvl1`, `swvl2`), planned

- **Measures:** the fraction of a soil layer's volume that is water. Layer 1
  is 0-7 cm, layer 2 is 7-28 cm.
- **Units:** m³ of water per m³ of soil (0 = bone dry; typical values 0.1 to
  0.45, depending on soil type).
- **Traps:** values depend on soil texture, so compare anomalies, not raw
  values, across regions.
- **Used for:** summer fuel dryness, alongside SPEI (descriptive unless
  `ANALYSIS_PLAN.md` adds it).

### 2f. Glacier mask (invariant), planned option

- **Measures:** the fraction of each cell covered by glacier, one fixed
  field. It is the official alternative to flagging cells stuck at the 10 m
  SWE cap. Invariant fields are delivered for the whole globe, not cut to the
  domain.

## 3. Snowpack from stations (SNOTEL, BC, Alberta), planned

**What they measure.** April 1 snow water equivalent at fixed mountain
sites, the traditional measure of how much water the snowpack will release
in spring and summer.

**How.** Two methods, used by all three networks to differing degrees
(*confirm the details for each network at download*):
- **Manual snow courses:** surveyors push a calibrated tube through the
  snowpack, weigh the core and record depth and SWE at a marked transect on
  set dates, usually around the first of the month.
- **Automated stations (snow pillows):** a fluid-filled pillow on the ground
  weighs the snow above it and reports SWE continuously; SNOTEL sites are
  this type, often with a sonic depth sensor too.

**Units.** SNOTEL reports inches of water (`mm = in × 25.4`); BC and Alberta
report mm. Depth, where used, is cm or inches.

**Traps.** Sites sit at particular elevations, so a regional average reflects
where the stations are, not the whole region. Networks start in different
years and add or drop sites over time. Coverage is sparse in northern
Alberta. Point measurements and ERA5-Land's 9 km cells measure different
things, so expect level differences between them.

## 4. Derived climate variables, planned (Phase 2)

### 4a. Potential evapotranspiration (PET)

- **Measures:** how much water the air could draw from a fully wet
  surface: the atmosphere's demand for water.
- **Method:** Thornthwaite (draft), from monthly mean temperature and
  latitude (day length) only, via `xclim`. Simple, but temperature-only PET
  tends to overstate drying as temperatures rise. Penman-Monteith (humidity,
  radiation, wind) would need extra ERA5-Land variables.
- **Units:** mm/month.

### 4b. SPEI-3 (Standardised Precipitation-Evapotranspiration Index)

- **Measures:** whether a 3-month period was wetter or drier than usual,
  after accounting for both supply and demand. Monthly water balance
  D = P - PET is summed over 3 months, fitted to a probability distribution
  over a calibration period, and converted to a standard normal score.
- **Units:** dimensionless, in standard deviations. 0 = normal; -1 is
  moderately dry (drier than about 84% of the calibration years); -2 is
  extreme. Typical range -3 to +3.
- **Settings to fix before the freeze:** calibration period, distribution,
  PET method, scale 3.

### 4c. Whiplash index

- **Definition (draft):** SPEI-3(JJA) - SPEI-3(preceding DJF), every year.
- **Units:** standard deviations of SPEI.
- **Reading it:** negative = a swing from wetter-than-usual winter to
  drier-than-usual summer (e.g. winter +1, summer -1 gives -2). Positive =
  the reverse.
- **Open:** summer falls inside the fire season, so the index is a
  concurrent mechanism variable; a winter-to-spring version is the
  alternative (pre-freeze item "Whiplash timing").

### 4d. Other regional climate columns

- `precip_djf_mm` (have, Phase 1): winter (December-February,
  `WINTER_MONTHS`) precipitation total per region, mm, summed per cell
  from mm/month and then averaged with cos(latitude) weights. Table:
  `data/processed/djf_precip_region_year.csv` (`python -m src.era5`), 76
  winters x 7 regions with `enso_index`, `enso_djf`, `phase`, `strong`.
  Cells count for a region when their centre lies inside its polygon; the
  35.5N grid row sits exactly on the NorCal/SoCal split and goes to SoCal
  (`DECISIONS.md` 2026-10-04, "Phase 1 regions and ERA5 loading").

- `temp_jja`: June-August mean 2 m temperature per region, °C.
- `precip_anom_*`: winter precipitation anomaly per region; months,
  baseline and units (mm, % of normal or standardised) are fixed at the
  freeze (H5 definitions). `lag0` = preceding winter, `lag1` = the winter
  before.

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
- **Fire season:** June-October; Alberta April-October; Alaska and Yukon
  April-September (provisional)
  (`FIRE_SEASON_MONTHS`; California and BC windows are pre-freeze items).

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
