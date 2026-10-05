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

# ENSO classification (see ANALYSIS_PLAN.md: "Decisions to make before freezing")
ENSO_INDEX = "ONI"  # "ONI" or "RONI"
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
FIRE_SEASON_MONTHS = {  # first and last month, inclusive
    "PNW": (6, 10),
    "BC": (6, 10),
    "AB": (4, 10),
    "AK": (4, 9),  # provisional: Alaska and Yukon statutory season, 1 Apr-30 Sep
    "YT": (4, 9),
    "NorCal": (6, 10),
    "SoCal": (6, 10),
}

# Statistics (values mirror ANALYSIS_PLAN.md)
ALPHA = 0.05
N_PERMUTATIONS = 10_000
N_BOOTSTRAP = 10_000
HAC_MAXLAGS = 2
BLOCK_LEN = 3
PREDICTION_ALPHA = 0.2  # 80% prediction intervals
RANDOM_SEED = 2026
