"""Single source of truth for every tunable value in the project.

Pipeline scripts, notebooks and the site import from here. Values that also
appear in ANALYSIS_PLAN.md must match it; once the plan is frozen, a change
here is a deviation and needs a row in its deviations log.
"""
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

# Coordinate reference systems
# Geographic, for storage and display only. Never measure area or distance in it.
CRS_GEOGRAPHIC = "EPSG:4326"
# Equal-area, for every burned-area calculation. One CRS for the whole domain
# (California to Alberta) keeps hectares comparable across regions.
CRS_EQUAL_AREA = "ESRI:102008"  # North America Albers Equal Area Conic
M2_PER_HA = 10_000

# ENSO classification. RONI chosen 2026-10-05 (owner; DECISIONS.md "ENSO
# index: RONI"); ONI is the robustness check, re-run for every headline test.
ENSO_INDEX = "RONI"  # "ONI" or "RONI"
ENSO_ROBUSTNESS_INDEX = "ONI"
ENSO_INDEX_URLS = {
    "ONI": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    # Same layout as the ONI table minus TOTAL; confirmed 2026-10-04. Official
    # ENSO index per NWS Public Information Statement 26-05.
    "RONI": "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt",
}
EL_NINO_THRESHOLD = 0.5   # deg C, DJF value at or above: El Nino winter
LA_NINA_THRESHOLD = -0.5  # deg C, DJF value at or below: La Nina winter
STRONG_THRESHOLD = 1.5    # deg C, strong El Nino

# Year ranges
CLIMATE_FIRST_YEAR = 1950  # ERA5-Land and ENSO index start
FIRE_FIRST_YEAR = 1984     # fire-perimeter records start (MTBS)

# Alaska is clipped at this longitude: west of it lie only the outer Aleutian
# and Bering Sea islands (1.1 Mha, 0.7% of the state, almost no fire), and the
# Near Islands cross the antimeridian.
ALASKA_WEST_LON = -169

# Climate download domains: name -> ([N, W, S, E], folder under data/raw).
# main: BC reaches about 139W at the Alaska panhandle and Haida Gwaii sits near
# 131-133W; Alberta's eastern border is 110W and both provinces end at 60N.
# Half a degree to a degree of buffer.
# north (added 2026-10-04): Alaska east of ALASKA_WEST_LON (51.2-71.4N) and
# Yukon (60-69.65N, 141-123.8W). Overlaps main south of 60.5N, where cells
# agree to float32 rounding (max relative difference 7e-7, measured 2026-10-04).
ERA5_DOMAINS = {
    "main": ([60.5, -140, 32, -109], "era5_land"),
    "north": ([71.5, ALASKA_WEST_LON, 51, -123.5], "era5_land_north"),
}
ERA5_DATASET = "reanalysis-era5-land-monthly-means"
# Changing this list after the download needs a full re-download: years already
# on disk are skipped. SWE added before the first download (DECISIONS.md,
# 2026-10-04 "ERA5-Land variables").
ERA5_VARIABLES = ["total_precipitation", "2m_temperature",
                  "snow_depth_water_equivalent"]
# Phase 2 additions, downloaded as a separate set so the core files stay
# untouched (ACTION_PLAN.md Phase 2; D13). Descriptive unless ANALYSIS_PLAN.md
# adds them before the freeze. Layers 1-2 cover 0-7 and 7-28 cm.
ERA5_SNOW_SOIL_VARIABLES = ["snowfall", "volumetric_soil_water_layer_1",
                            "volumetric_soil_water_layer_2"]
# Variable set name -> (variables, folder suffix). Each domain's set goes to
# its own folder: data/raw/<domain folder><suffix>.
ERA5_VARIABLE_SETS = {
    "core": (ERA5_VARIABLES, ""),
    "snow_soil": (ERA5_SNOW_SOIL_VARIABLES, "_snow_soil"),
}
ERA5_LAG_MONTHS = 3  # months behind real time before a month is safely published

# Seasons. A season that crosses the new year is labelled by the year of its
# last month: (12, 1, 2) labelled Y is Dec of Y-1 plus Jan and Feb of Y.
WINTER_MONTHS = (12, 1, 2)  # DJF
SUMMER_MONTHS = (6, 7, 8)   # JJA

# SPEI and whiplash (DECISIONS.md 2026-10-04 "SPEI settings"; pre-freeze item)
PET_METHOD = "TW48"          # xclim Thornthwaite (1948); zero below 0 deg C
SPEI_SCALE = 3               # months summed in the water balance
SPEI_DIST = "fisk"           # log-logistic
SPEI_FIT_METHOD = "ML"       # maximum likelihood
SPEI_CAL_YEARS = (1951, 2020)  # calibration period, inclusive
# Clip per-cell SPEI to +-3.09 (probability 0.001 per tail): a fitted tail
# gave -8.21 in a 900-cell probe.
SPEI_CLIP = 3.09

# ERA5-Land SWE (DECISIONS.md 2026-10-04 "ERA5-Land SWE: glacier exclusion
# and April 1"). A cell is excluded from every SWE regional mean if it reaches
# the cap in any month, or keeps more than PERENNIAL_MIN_MM of snow at the
# yearly minimum in at least PERENNIAL_YEAR_FRACTION of GLACIER_MASK_YEARS.
SWE_CAP_MM = 9_990            # ERA5-Land holds glacier ice at 10 m (10,000 mm)
PERENNIAL_MIN_MM = 10
PERENNIAL_YEAR_FRACTION = 0.9
GLACIER_MASK_YEARS = (1950, 2025)  # complete years used to build the fixed mask
# April 1 SWE: 00:00 UTC on 1 April from hourly ERA5-Land.
ERA5_HOURLY_DATASET = "reanalysis-era5-land"
APRIL1_FOLDER_SUFFIX = "_april1"
# Hourly ERA5-Land publishes about 5 days behind real time; 7 leaves a margin.
ERA5_HOURLY_LAG_DAYS = 7

# Regions
NATURAL_EARTH_ADMIN1_URL = ("https://naciscdn.org/naturalearth/10m/cultural/"
                            "ne_10m_admin_1_states_provinces.zip")
PNW_STATES = ["Washington", "Oregon", "Idaho"]
CA_SPLIT_LAT = 35.5
# Roles: primary = the dry-winter whiplash regions; north = Alaska and Yukon
# (added 2026-10-04, own hypothesis family: El Nino acts there mainly through
# warm springs and early melt); contrast = California.
REGIONS = {  # name -> role, in display order
    "PNW": "primary",
    "BC": "primary",
    "AB": "primary",
    "AK": "north",
    "YT": "north",
    "NorCal": "contrast",
    "SoCal": "contrast",
}

# Fire data
MIN_FIRE_HA = 405  # 1,000 acres: MTBS western mapping threshold, applied everywhere
# First and last month of fire season Y, inclusive, by ignition date. A last
# month below the first wraps into the next calendar year: (6, 1) is June Y
# to January Y+1, so a January fire counts for the season before it.
# Decided 2026-10-05 (DECISIONS.md "Data rules"): California through January
# (wind-driven Oct-Jan fires), BC from April (northeast BC spring boreal
# fires), Alaska and Yukon the statutory season 1 Apr-30 Sep.
FIRE_SEASON_MONTHS = {
    "PNW": (6, 10),
    "BC": (4, 10),
    "AB": (4, 10),
    "AK": (4, 9),
    "YT": (4, 9),
    "NorCal": (6, 1),
    "SoCal": (6, 1),
}
# Fire record rules (ANALYSIS_PLAN.md "Fire record rules"). MTBS incident
# types kept; "Prescribed Fire" dropped. The MIN_FIRE_HA floor applies to the
# whole fire's area_ha before clipping to regions.
MTBS_KEEP_TYPES = ("Wildfire", "Wildland Fire Use", "Unknown")
# Zero-fire region-years: kept (log_burn = 0); excluded in a sensitivity run;
# no percent-change reporting where they exceed this share of seasons.
ZERO_YEAR_PCT_LIMIT = 0.10
# Strong-only results (exploratory): sensitivity run with the strong flag
# flipped for winters within this distance of STRONG_THRESHOLD (under RONI:
# 1965-66 1.53, 1986-87 1.46, 2009-10 1.44).
STRONG_SENSITIVITY_BAND = 0.06

# Statistics (values mirror ANALYSIS_PLAN.md)
ALPHA = 0.05
N_PERMUTATIONS = 10_000
N_BOOTSTRAP = 10_000
HAC_MAXLAGS = 2
BLOCK_LEN = 3
PREDICTION_ALPHA = 0.2  # 80% prediction intervals
RANDOM_SEED = 2026
# Secondary compounding tests C1 (SWE) and C2 (burned area): enso_djf x
# centred year, per region below (ANALYSIS_PLAN.md "Secondary tests:
# compounding"; DECISIONS.md 2026-10-05 "Trend and climate change").
COMPOUNDING_REGIONS = ("PNW", "BC", "AB")

# H5 precip_anom (DECISIONS.md 2026-10-05 "Hypotheses"): Oct-Mar total,
# labelled by the March year, as a z-score against the region's normal over
# PRECIP_ANOM_NORMAL_YEARS. lag0 = the preceding Oct-Mar, lag1 = the one before.
PRECIP_ANOM_MONTHS = (10, 11, 12, 1, 2, 3)
PRECIP_ANOM_NORMAL_YEARS = (1991, 2020)
# AK and YT descriptive spring mechanism variable: mean 2 m temperature.
SPRING_MONTHS = (3, 4, 5)  # MAM

# Test directions (ANALYSIS_PLAN.md "Directions and sidedness"), as the
# alternative of each test per region: "greater", "less", "two-sided", or None
# where the region is descriptive only or the test does not apply. H4 is one
# north-vs-SoCal contrast. The tests in src/stats.py are two-sided today; a
# one-sided p-value needs the sign of the estimate (Phase 4).
_NORTH = ("PNW", "BC", "AB")


def _directions(north, norcal, socal, ak_yt):
    out = {r: north for r in _NORTH}
    out.update({"NorCal": norcal, "SoCal": socal, "AK": ak_yt, "YT": ak_yt})
    return out


TEST_DIRECTIONS = {
    "H1": _directions("two-sided", "two-sided", "two-sided", None),  # a check
    "H2": _directions("greater", "two-sided", "two-sided", "two-sided"),
    "H3a": _directions("greater", "two-sided", "two-sided", "two-sided"),
    "H3b": _directions("greater", "two-sided", "two-sided", "two-sided"),
    "H4": "two-sided",
    "H5_lag0": _directions("less", "two-sided", "two-sided", None),
    "H5_lag1": _directions("two-sided", "two-sided", "greater", None),
    "H6_swe": _directions("less", "two-sided", None, None),
    "H6_spei": _directions("less", "two-sided", "two-sided", None),
    "C1": {r: "less" for r in COMPOUNDING_REGIONS},
    "C2": {r: "two-sided" for r in COMPOUNDING_REGIONS},
}

# Small-cluster corrections (decided 2026-10-05; DECISIONS.md "Inference"):
# t critical values in every HAC and pooled fit; the pooled H4 model uses
# Driscoll-Kraay errors (statsmodels cov_type "hac-groupsum") with
# HAC_MAXLAGS, year-clustered errors reported alongside. src/stats.py does
# not apply these yet (Phase 4).
USE_T = True
POOLED_COV_TYPE = "hac-groupsum"
# Expanding-window validation: fit on seasons FIRE_FIRST_YEAR..Y-1, predict Y,
# once this many training seasons exist (first prediction 2004).
FORWARD_MIN_TRAIN_YEARS = 20
# Holm families (BH alongside): family -> tests in it. Region lists for each
# test come from TEST_DIRECTIONS (None = not tested). ONI and station-z
# robustness runs are not corrected.
_MAIN = ("PNW", "BC", "AB", "NorCal", "SoCal")
_AK_YT = ("AK", "YT")
CORRECTION_FAMILIES = {
    "H1": [("H1", _MAIN)],
    "H2": [("H2", _MAIN)],
    "H3a": [("H3a", _MAIN)],
    "H3b": [("H3b", _MAIN)],
    "H5": [("H5_lag0", _MAIN), ("H5_lag1", _MAIN)],
    "H6": [("H6_swe", _MAIN), ("H6_spei", _MAIN)],
    "north_H2": [("H2", _AK_YT)],
    "north_H3a": [("H3a", _AK_YT)],
    "north_H3b": [("H3b", _AK_YT)],
    "C1": [("C1", COMPOUNDING_REGIONS)],
    "C2": [("C2", COMPOUNDING_REGIONS)],
}

# Station snowpack (Phase 2; DATA_SOURCES.md rows NRCS, BC, Yukon)
# Raw downloads; cleaning and the April 1 extraction in src/stations.py (below).
STATIONS_RAW = DATA_RAW / "stations"
NRCS_SNOW_RAW = STATIONS_RAW / "nrcs"
BC_SNOW_RAW = STATIONS_RAW / "bc"
YUKON_SNOW_RAW = STATIONS_RAW / "yukon"
# NRCS AWDB REST API, no key. Parameter names checked against the OpenAPI
# spec at https://wcc.sc.egov.usda.gov/awdbRestApi/v3/api-docs (2026-10-05).
NRCS_AWDB_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/"
NRCS_STATES = ["WA", "OR", "ID", "AK"]
NRCS_ELEMENT = "WTEQ"  # snow water equivalent, inches
# Network -> (duration, periodRef). SNTL: snow pillows, MONTHLY with START is
# the midnight reading opening the month (equals the DAILY value dated the
# last day of the previous month). SNOW: manual snow courses, SEMIMONTHLY
# keeps the collection date (their MONTHLY is derived); with START the
# April 1 survey is month 4, monthPart "1" (END labels it month 3, part "2").
NRCS_NETWORKS = {
    "SNTL": ("MONTHLY", "START"),
    "SNOW": ("SEMIMONTHLY", "START"),
}
NRCS_BATCH_SIZE = 40     # station triplets per data request
NRCS_PAUSE_S = 1.0       # seconds between requests
# HTTP settings shared by the station downloads. Retries cover 5xx, 429 and
# timeouts; the wait doubles each time from HTTP_BACKOFF_S.
HTTP_TIMEOUT_S = 300
HTTP_RETRIES = 4
HTTP_BACKOFF_S = 5.0
# BC manual snow surveys (BC River Forecast Centre), saved as published.
BC_SNOW_URLS = {
    "allmss_archive.csv": ("https://www.env.gov.bc.ca/wsd/data_searches/snow/"
                           "asws/data/allmss_archive.csv"),
    "allmss_current.csv": ("https://www.env.gov.bc.ca/wsd/data_searches/snow/"
                           "asws/data/allmss_current.csv"),
}
# Yukon snow survey network (Yukon Water Data API v2), saved as published.
YUKON_SNOW_URLS = {
    "snow_survey_data.csv": "https://service.yukon.ca/water-data/api/v2/snow-survey/data",
    "snow_survey_metadata.csv": ("https://service.yukon.ca/water-data/api/v2/"
                                 "snow-survey/metadata"),
}
# CanSWE v8 (Vionnet et al.; Open Government Licence - Canada), from Zenodo.
# Version DOI 10.5281/zenodo.19075529, concept DOI 10.5281/zenodo.4734371.
# The CSV zip in the record holds the same data as the NetCDF; not downloaded.
CANSWE_RAW = STATIONS_RAW / "canswe"
CANSWE_RECORD_URL = "https://zenodo.org/api/records/19075529"
CANSWE_FILES = ["CanSWE-CanEEN_1928-2025_v8.nc", "ReadMe_CanSWE_v8.pdf"]

# Station April 1 SWE cleaning (src/stations.py; DECISIONS.md 2026-10-05
# "Station snowpack cleaning rules"; measured effects in
# docs/methods_register.md "Station snowpack").
INCH_MM = 25.4
FOOT_M = 0.3048            # NRCS station elevations are in feet
# NRCS QC flags dropped: B = regression back-estimate homogenising pillow and
# snow course records (not a measurement; would double-count the course),
# S = suspect (holds all 8 negative April values). Kept: V, E (minor
# adjustment for sensor noise), K (estimate), C, N, X.
NRCS_DROP_QC = ("B", "S")
# Snow-course collection date used as a placeholder (2,163 April 1 surveys,
# 1950-2009); the value is kept and flagged date_unknown.
NRCS_PLACEHOLDER_DATE = (7, 1)  # (month, day)
# Manual surveys: the sample nearest 1 April within +-STATION_WINDOW_DAYS.
# Share of surveys inside +-10 days: NRCS 98.3%, BC 99.99%, Yukon 99.8%,
# Alberta (CanSWE) 98.8% (profile 2026-10-05).
STATION_WINDOW_DAYS = 10
# BC survey codes that mark an estimate rather than a survey; dropped. Every
# other code is kept and carried in `flags`.
BC_DROP_CODES = ("EST AREAL AVG", "EST PILLOW")
# CanSWE: station prefixes used and the role of each. Alberta comes only from
# CanSWE (D30); BC and Yukon manual courses come from the provincial files,
# which win wherever both hold the same station-year.
CANSWE_PREFIXES = ("ALE", "BCE", "YT")
CANSWE_PILLOW_TYPE = 2      # type_mes: snow pillow or snow scale
# Yukon network sites outside Yukon (3 in Alaska, 4 in BC, 2 in NWT) are
# dropped: lowest licence risk (DATA_SOURCES.md Yukon row).
YUKON_NETWORK_REGION = "YT"
STATION_TABLE = DATA_PROCESSED / "station_swe_apr1.csv"
# Regional station index (src.stations.station_index). Each station's normal
# is its mean (and SD) of April 1 SWE over STATION_NORMAL_YEARS, from at least
# STATION_NORMAL_MIN_YEARS values (2/3 of the period). swe_pct = median across
# stations of SWE / normal x 100, leaving out stations whose normal is under
# STATION_PCT_MIN_NORMAL_MM (percentages explode there); swe_z = mean of
# (SWE - mean) / SD. A region-year needs STATION_MIN_PER_REGION_YEAR stations.
STATION_NORMAL_YEARS = (1991, 2020)
STATION_NORMAL_MIN_YEARS = 20
STATION_PCT_MIN_NORMAL_MM = 10
STATION_MIN_PER_REGION_YEAR = 5   # owner: may be widened for AB and YT if too short
STATION_INDEX_TABLE = DATA_PROCESSED / "station_swe_region_year.csv"
# SWE in the tests (owner, 2026-10-05; DECISIONS.md "SWE source for the
# tests"): ERA5-Land April 1 SWE as a z-score against its own regional
# STATION_NORMAL_YEARS normal is the predictor; the station index z is the
# robustness check where it exists. Both columns are in STATION_INDEX_TABLE.
SWE_TEST_COLUMN = "era5_swe_z"
SWE_CHECK_COLUMN = "station_swe_z"

# Snowfall fraction and soil moisture (src/snow_soil.py; descriptive unless
# ANALYSIS_PLAN.md adds them; DECISIONS.md 2026-10-05 "Snowfall fraction and
# soil moisture columns"). Snowfall fraction = regional mean snowfall /
# regional mean total precipitation over SNOWFALL_MONTHS (the accumulation
# season behind April 1 SWE; labelled by the March year). Soil moisture = the
# JJA mean of the depth-weighted 0-28 cm layer (layer 1 is 0-7 cm, layer 2
# 7-28 cm, so weights 7/28 and 21/28).
SNOWFALL_MONTHS = (11, 12, 1, 2, 3)  # Nov-Mar
SOIL_MONTHS = SUMMER_MONTHS          # JJA
SOIL_LAYER_WEIGHTS = {"swvl1": 0.25, "swvl2": 0.75}
SNOW_SOIL_TABLE = DATA_PROCESSED / "snow_soil_region_year.csv"
