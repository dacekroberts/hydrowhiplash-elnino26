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
    "RONI": "",  # TODO: confirm on https://www.cpc.ncep.noaa.gov/data/indices/
}
EL_NINO_THRESHOLD = 0.5   # deg C, DJF value at or above: El Nino winter
LA_NINA_THRESHOLD = -0.5  # deg C, DJF value at or below: La Nina winter
STRONG_THRESHOLD = 1.5    # deg C, strong El Nino

# Year ranges
CLIMATE_FIRST_YEAR = 1950  # ERA5-Land and ENSO index start
FIRE_FIRST_YEAR = 1984     # fire-perimeter records start (MTBS)

# Climate download domain, [N, W, S, E]. BC reaches about 139W at the Alaska
# panhandle and Haida Gwaii sits near 131-133W; Alberta's eastern border is
# 110W and both provinces end at 60N. Half a degree to a degree of buffer.
ERA5_AREA = [60.5, -140, 32, -109]
ERA5_DATASET = "reanalysis-era5-land-monthly-means"
ERA5_VARIABLES = ["total_precipitation", "2m_temperature"]
ERA5_LAG_MONTHS = 3  # months behind real time before a month is safely published

# Regions
NATURAL_EARTH_ADMIN1_URL = ("https://naciscdn.org/naturalearth/10m/cultural/"
                            "ne_10m_admin_1_states_provinces.zip")
PNW_STATES = ["Washington", "Oregon", "Idaho"]
CA_SPLIT_LAT = 35.5
REGIONS = {  # name -> role
    "PNW": "primary",
    "BC": "primary",
    "AB": "primary",
    "NorCal": "contrast",
    "SoCal": "contrast",
}

# Fire data
MIN_FIRE_HA = 405  # 1,000 acres: MTBS western mapping threshold, applied everywhere
FIRE_SEASON_MONTHS = {  # first and last month, inclusive
    "PNW": (6, 10),
    "BC": (6, 10),
    "AB": (4, 10),
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
