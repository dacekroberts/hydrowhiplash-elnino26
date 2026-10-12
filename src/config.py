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
# Everything fetched or rebuilt after the registered runs (D73; src/later.py):
# downloads under LATER_RAW/<stamp>/, rebuilt tables under
# TRACKER_TABLES/<stamp>/ (set below, after RESULTS). Never a pinned path.
LATER_RAW = DATA_RAW / "later"
RESULTS = ROOT / "results"
TRACKER_TABLES = RESULTS / "tables" / "tracker"

# Coordinate reference systems
# Geographic, for storage and display only. Never measure area or distance in it.
CRS_GEOGRAPHIC = "EPSG:4326"
# Equal-area, for every burned-area calculation. One CRS for the whole domain
# (California to Alberta) keeps hectares comparable across regions.
CRS_EQUAL_AREA = "ESRI:102008"  # North America Albers Equal Area Conic
M2_PER_HA = 10_000

# ENSO classification. RONI chosen 2026-10-05 (owner; DECISIONS.md "ENSO
# index: RONI"); ONI is the robustness check, re-run for every registered test
# that uses the index (ANALYSIS_PLAN "Execution details", ONI robustness runs).
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
# Last fire season of the US regions' pre-registered fire tests, and the forecast year,
# never used in training (DECISIONS.md 2026-10-06 "Plan gaps closed"):
# CNFDB 2026 is not out before the analysis, WFIGS 2026 is provisional and
# California's 2026 season closes in February 2027.
FIRE_LAST_YEAR = 2025
FORECAST_YEAR = 2027
# CNFDB polygons end in 2024 (release files dated 28 Jan 2026; D56), so the
# Canadian regions' fire tests end at 2024 and the US regions' at 2025; the
# pooled H4 model uses the years every region has (owner, 2026-10-07, before
# any fire data; D57, frozen plan's deviations log). CNFDB 2025, when
# released, is reported beside the results, not substituted.
CNFDB_LAST_YEAR = 2024
FIRE_LAST_YEAR_BY_REGION = {
    "PNW": FIRE_LAST_YEAR, "BC": CNFDB_LAST_YEAR, "AB": CNFDB_LAST_YEAR,
    "AK": FIRE_LAST_YEAR, "YT": CNFDB_LAST_YEAR,
    "NorCal": FIRE_LAST_YEAR, "SoCal": FIRE_LAST_YEAR,
}
POOLED_LAST_YEAR = CNFDB_LAST_YEAR  # H4: 1984-2024 for all five regions

# Live 2026-27 tracker (ACTION_PLAN "Second goal"; D44, D46; dates from PR
# #19's table). Window: Oct-Mar precipitation (H5's months) through the
# April 1 snowpack. The freeze date is the analysis-plan-frozen commit
# (acf7a80, 2026-10-07 13:35 UTC-07:00). Verification dates follow
# FIRE_SEASON_MONTHS: after each region's last fire month of FORECAST_YEAR
# (California's season ends in January 2028). ERA5-Land monthly means
# arrive within about a week: a CDS probe on 2026-10-07 found September 2026
# published (D55), so a month's data is expected by TRACKER_DATA_DAY of the
# next month (October 2026 by 7 November; recheck at the first update).
# ERA5_LAG_MONTHS (3) is a margin, not the lag; it becomes 1 at the first
# tracker update (ACTION_PLAN Phase 5, hard-line item).
TRACKER_WINDOW = ("2026-10-01", "2027-04-30")
TRACKER_FREEZE_DATE = "2026-10-07"
TRACKER_DATA_DAY = 7

# Rollout calendar (D87): src/rollout.py builds one dated list of every
# arrival the site waits on and writes it to
# results/tables/rollout_calendar.json; the tracker page's timetable and the
# scheduled reminders both read that file. Dates the settings above already
# fix (monthly data, the April 1 snowpack, the verification dates) are
# derived there, not repeated here. The windows below are expectations taken
# from each publisher's release record, not measurements; tighten one when
# its arrival is observed.
#   djf_index: CPC's first RONI release after February 2027, the forecast's
#     input (ANALYSIS_PLAN "Execution details"). CPC's posting day is not
#     measured; each monthly check records it.
#   cnfdb_2025, cnfdb_2026: the current release's files are dated 28 Jan 2026
#     and end in 2024 (D56); the frozen plan says "about January 2027".
#   canswe_v9, canswe_v10: one version a year since v5, published February
#     or March with data to the previous July (docs/alberta_swe_sources.md).
ROLLOUT_WINDOWS = {
    "djf_index": ("2027-03-01", "2027-03-14"),
    "cnfdb_2025": ("2027-01-01", "2027-02-28"),
    "canswe_v9": ("2027-02-01", "2027-03-31"),
    "cnfdb_2026": ("2028-01-01", "2028-02-29"),
    "canswe_v10": ("2028-02-01", "2028-03-31"),
    # D93: the provisional and the registered source for the 2027 season in
    # BC, AB and YT. NBAC v20260513 (files dated 22 May 2026) holds 2025;
    # CNFDB 2024 arrived in files dated 28 January 2026.
    "nbac_2027": ("2028-05-01", "2028-06-30"),
    "cnfdb_2027": ("2029-01-01", "2029-02-28"),
}
ROLLOUT_REMINDER_LEAD_DAYS = 3  # a reminder runs this many days before its date
# CPC may revise a RONI value for this many months after posting it
# (DATA_SOURCES.md, ONI/RONI row); revisions are reported, not substituted.
RONI_REVISION_MONTHS = 2

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
ERA5_LAG_MONTHS = 3  # download margin; months are published within about a week (D55; to 1 in Nov)

# Seasons. A season that crosses the new year is labelled by the year of its
# last month: (12, 1, 2) labelled Y is Dec of Y-1 plus Jan and Feb of Y.
WINTER_MONTHS = (12, 1, 2)  # DJF
SUMMER_MONTHS = (6, 7, 8)   # JJA

# SPEI and whiplash (DECISIONS.md 2026-10-04 "SPEI settings"; pre-freeze item)
PET_METHOD = "TW48"          # Thornthwaite (1948) as in R SPEI (src.whiplash.pet_thornthwaite)
SPEI_SCALE = 3               # months of P - PET amounts (mm) summed
SPEI_DIST = "fisk"           # log-logistic
SPEI_FIT_METHOD = "ML"       # maximum likelihood
SPEI_CAL_YEARS = (1951, 2020)  # calibration period, inclusive
# Clip per-cell SPEI to +-3.09 (probability 0.001 per tail): a fitted tail
# gave -8.21 in a 900-cell probe.
SPEI_CLIP = 3.09
# Thornthwaite heat index: climatological, from each cell's monthly mean
# temperatures over these years (Thornthwaite 1948), not recomputed per
# calendar year as in xclim's TW48 (DECISIONS.md 2026-10-06 "PET heat
# index"; D47). The N/30 month-length factor is included.
PET_HEAT_INDEX_YEARS = SPEI_CAL_YEARS
# Glacier and perennial-snow cells (the SWE glacier mask, src.snow) are left
# out of the per-cell SPEI fit and the regional SPEI means (2026-10-06).
GLACIER_SPEI_EXCLUDED = True

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
# The release of 2026-10-07 has no "Unknown"; its "Other" is the plan's
# Unknown (owner, 2026-10-07; D58), counted and reported separately.
MTBS_KEEP_TYPES = ("Wildfire", "Wildland Fire Use", "Other")
MTBS_UNKNOWN_TYPE = "Other"
# WFIGS attr_IncidentTypeCategory: WF wildfire kept, RX prescribed dropped.
WFIGS_KEEP_TYPES = ("WF",)
# CNFDB prescribed burns: CAUSE "H-PB" or PRESCRIBED "yes" (the two flag the
# same 309 polygons since 1984: Parks Canada 297, AB 7, Ontario 5; 306 fires
# after the dissolve), dropped.
CNFDB_PRESCRIBED_CAUSE = "H-PB"
# CNFDB polygons sharing agency, YEAR and FIRE_ID are one fire only where
# they touch or lie within this distance of another part, chained (owner,
# 2026-10-08, D67; audit round 2 H1: agencies reuse FIRE_ID within a year,
# parts a median 25 km apart). Counted merges: sound parts 0.5 km apart at
# most, separate fires 25 km or more, so any value between gives one table.
CNFDB_MERGE_KM = 1.0
# MTBS for fires ignited before this date, WFIGS from it (owner, 2026-10-07,
# D61; was 2025-01-01 earlier that day). A fire-by-fire match found MTBS
# missing 22-58% of each US region's 2024 WFIGS area and complete in
# 2021-2023 (0-4.2% missing).
MTBS_WFIGS_CUTOVER = "2024-01-01"
# Source-agreement rule (D60, re-run on 2023 by D61, fixed before it was
# computed): d = log(1 + union ha WFIGS) - log(1 + union ha MTBS) for
# fires ignited in SOURCE_CHECK_YEAR, in each US region's window. If |d|
# reaches the threshold in any US region, PNW, AK, NorCal and SoCal end at
# SOURCE_CHECK_YEAR; otherwise the frozen years stand. On 2024 (D60 as
# first computed) d was 0.23-0.90, from MTBS's unmapped 2024 fires.
SOURCE_CHECK_YEAR = 2023
# Calendar years over which MTBS and WFIGS are compared fire by fire for the
# methods page (scripts/source_pairs.py): the years both products hold before
# and at the cutover. Descriptive; no test reads it (D89).
SOURCE_PAIR_YEARS = (2021, 2024)
SOURCE_AGREEMENT_MAX_LOG_DIFF = 0.10
# Each region takes fires only from its own country's records, so a
# cross-border fire is never counted twice.
FIRE_COUNTRY = {"PNW": "US", "AK": "US", "NorCal": "US", "SoCal": "US",
                "BC": "CA", "AB": "CA", "YT": "CA"}
# WFIGS discovery times are UTC; converted to the local date of the origin
# state before the season window is applied. Other states: Mountain time.
WFIGS_STATE_TZ = {"US-WA": "America/Los_Angeles", "US-OR": "America/Los_Angeles",
                  "US-CA": "America/Los_Angeles", "US-NV": "America/Los_Angeles",
                  "US-ID": "America/Boise", "US-AK": "America/Anchorage"}
WFIGS_DEFAULT_TZ = "America/Denver"
# Read only perimeters intersecting this lon/lat box (EPSG:4326 sources):
# every study region with a margin, so fires from neighbouring states that
# reach a region are kept.
FIRE_READ_BBOX = (-180.0, 30.0, -100.0, 72.0)
FIRE_EVENTS_TABLE = DATA_PROCESSED / "fire_events.csv"
FIRE_REGION_TABLE = DATA_PROCESSED / "fire_region_year.csv"
# Parks Canada gap (owner, 2026-10-08, D69; wording D71): CNFDB holds no
# Parks Canada polygon at or above 405 ha in BC, AB or YT for 2016-2021 (none
# at all for 2018-2020; Nahanni, NWT, only in 2016-2017; 2021 small fires
# only). NBAC park area (ADMIN_NAME "PC") puts the missing
# share of AB at 1.3% (2016), 39.1% (2017), 20.4% (2018), 14.3% (2019) and
# none in 2020-2021; BC 2017, 2018, 2023 and YT 2022, 2023 at most 0.9%
# (a stated limitation). These seasons are flagged `parks_gap` in the fire
# tables, and a reported sensitivity run uses FIRE_REGION_TABLE_PARKS, the
# main table with NBAC's park area added for them (src.parks_gap).
PARKS_GAP_SEASONS = {"AB": (2016, 2019)}
NBAC_PARK_ADMIN = "PC"
# NBAC also splits fires at Department of National Defence land (CFB
# Wainwright WW, Suffield SF in AB); no CNFDB polygon covers it in any year.
# A stated limitation, not added (owner, 2026-10-08, audit round 4 M2): cause
# undetermined, satellite-only, mostly undated, so not separable from range
# burning. Measured by `python -m src.parks_gap --measure`.
NBAC_DND_ADMIN = "DND"
# Per-fire split of the NBAC coverage measurement (audit 2026-10-08 round 5
# L6; scripts/nbac_coverage.py): an NBAC fire with more than this share of
# its area in a region under no same-YEAR CNFDB polygon counts as missing
# from CNFDB, the rest as rim disagreement. A measurement setting; no test
# reads it.
NBAC_MISSING_SHARE = 0.5
FIRE_REGION_TABLE_PARKS = DATA_PROCESSED / "fire_region_year_parks_nbac.csv"
# D62 frozen-rules variant: summed clipped area, MTBS "Other" dropped, CNFDB
# fires without a month dropped, the frozen years (src.fire.frozen_rules_table).
FIRE_REGION_TABLE_FROZEN = DATA_PROCESSED / "fire_region_year_frozen_rules.csv"
# Checksums of every input the tests read (trap 7, session 7 kickoff): the
# input tables in PINNED_RESULT_TABLES, the ENSO files, the fire downloads of
# 2026-10-07 and NBAC of 2026-10-08; no re-download until the results are in
# (src.pin_inputs).
INPUT_PINS_TABLE = RESULTS / "tables" / "input_pins.csv"
# Commit the tag analysis-plan-frozen points at (frozen 2026-10-07 13:35). The
# frozen-text check refuses a tag that points anywhere else, since a local
# tag can be moved (cold check 2026-10-11 M4; src.run_guard).
FROZEN_PLAN_COMMIT = "acf7a80232b2e1d6bc7c783162722db0b52e7cee"
# Offline copy of every pinned input (audit 2026-10-08 round 5 S1c; owner,
# 2026-10-11: a folder of its own inside the repository, never committed).
# Same relative paths as the originals; no builder or downloader writes here.
PINNED_COPY_DIR = ROOT / "pinned_inputs_copy"
# One row per re-pin: when, at which commit, why, and which files changed
# (audit 2026-10-08 round 5 S2; D73; docs/post_results_protocol.md).
INPUT_PINS_LOG = RESULTS / "tables" / "input_pins_log.csv"
# The committed input tables the tests read, pinned by name (audit 2026-10-08
# round 3 M1): the hypothesis runs write their own tables to results/tables/,
# which a folder rule would refuse or pin as inputs. Script outputs such as
# TEST_SIZE_TABLE are not inputs and are not pinned.
PINNED_RESULT_TABLES = ("climate_controls_region_year.csv", "fire_region_year.csv",
                        "fire_region_year_frozen_rules.csv", "fire_region_year_parks_nbac.csv",
                        "snow_soil_region_year.csv", "station_swe_region_year.csv",
                        "whiplash_swe_region_year.csv")
# Simulated size of each test shape (scripts/stats_size_check.py; D66, audit
# 2026-10-08 round 2 L1): the size labels printed beside robust p-values.
TEST_SIZE_TABLE = RESULTS / "tables" / "test_size.csv"

# NOAA NCEI Alaska climate divisions (Bieniek et al. 2012; DATA_SOURCES.md
# row "Alaska climate divisions"): boundary for the descriptive Interior
# Alaska check (owner, 2026-10-11; climate only, no registered test reads
# it; scripts/interior_alaska_check.py).
AK_DIVISIONS_URL = "https://www.ncei.noaa.gov/monitoring-content/data/us/climdiv/monthly/current/"
AK_DIVISIONS_FILES = ("AK_climate_divisions.zip",)
AK_DIVISIONS_RAW = DATA_RAW / "ak_climate_divisions"
# Interior = Central Interior (3), Northeast Interior (4) and Southeast
# Interior (5), the shapefile's FEATURE field (names checked at download).
AK_INTERIOR_DIVISIONS = (3, 4, 5)

# Fire perimeter downloads (Phase 3; DATA_SOURCES.md rows MTBS, WFIGS,
# CNFDB). Raw files as published; filtering happens in src/fire.py.
FIRE_RAW = DATA_RAW / "fire"
MTBS_RAW = FIRE_RAW / "mtbs"
WFIGS_RAW = FIRE_RAW / "wfigs"
CNFDB_RAW = FIRE_RAW / "cnfdb"
NBAC_RAW = FIRE_RAW / "nbac"
# The file behind "MTBS Burned Areas Boundaries Dataset 1984-2026" on the
# Direct Download page (checkbox name mtbs_perimeter_data, checked 2026-10-07).
MTBS_PERIMETER_URL = ("https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/"
                      "data/composite_data/burned_area_extent_shapefile/"
                      "mtbs_perimeter_data.zip")
# WFIGS Interagency Fire Perimeters, all years (ArcGIS Online item). The layer
# is live (refreshed about every 5 minutes), so the whole layer is taken from
# the Hub export, one consistent snapshot, not paged through the query API.
WFIGS_ITEM_ID = "5e72b1699bf74eefb3f3aff6f4ba5511"
WFIGS_ITEM_URL = "https://www.arcgis.com/sharing/rest/content/items/" + WFIGS_ITEM_ID
WFIGS_LAYER_URL = ("https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
                   "WFIGS_Interagency_Perimeters/FeatureServer/0")
WFIGS_EXPORT_URL = ("https://hub.arcgis.com/api/download/v1/items/" + WFIGS_ITEM_ID
                    + "/geojson")
WFIGS_EXPORT_WAIT_S = 900  # give up if the Hub export is not ready by then
# CNFDB agency fire polygons, current release (files dated 28 Jan 2026). The
# whole-record zip, not NFDB_poly_large_fires.zip: that subset is cut on the
# agency's own area field, and the project's floor is on computed area.
CNFDB_URL = "https://cwfis.cfs.nrcan.gc.ca/downloads/nfdb/fire_poly/current_version/"
CNFDB_FILES = ["NFDB_poly.zip", "NFDB_documentation_EN.pdf", "NFDB_poly_update_log.txt",
               "NFDB_poly_shapefile_metadata.pdf", "NFDB_Poly_metadata_NAP_ISO_19115_2003.xml"]
# NBAC (National Burned Area Composite), release v20260513, years 1972-2025
# (DATA_SOURCES.md NBAC row; docs/nbac_probe.md). Used for the Parks Canada
# sensitivity run (D69, src.parks_gap; pinned) and the exploratory NBAC vs
# CNFDB comparison (owner, 2026-10-08); not an input to any registered test.
NBAC_URL = "https://cwfis.cfs.nrcan.gc.ca/downloads/nbac/"
NBAC_RELEASE = "20260513"
NBAC_FILES = [f"NBAC_1972to2025_{NBAC_RELEASE}_shp.zip",
              f"NBAC_1972to2025_{NBAC_RELEASE}_shp_metadata.pdf"]
# Zero-fire region-years: kept (log_burn = 0); a sensitivity run leaves them
# out (permutation tests drop them, regressions give each its own 0/1
# indicator; ANALYSIS_PLAN "Execution details"); no percent-change reporting
# where they exceed this share of seasons.
ZERO_YEAR_PCT_LIMIT = 0.10
# Strong-only results (exploratory): one sensitivity run with the strong flag
# flipped together for every winter within this distance of STRONG_THRESHOLD,
# on the index in use (RONI: 1965-66 1.53, 1986-87 1.46, 2009-10 1.44; ONI:
# 1972-73 1.55, 1991-92 1.54, 2009-10 1.47).
STRONG_SENSITIVITY_BAND = 0.06
# Index values are published to 2 decimals; distances to a threshold are
# rounded to this many decimals before comparing, or abs(1.44 - 1.5) =
# 0.06000000000000005 would drop 2009-10 from the band (independent audit F7).
ENSO_DECIMALS = 2

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
# H1 (a check) compares DJF totals instead, as in Phase 1 (WINTER_MONTHS).
H1_VALUE = "precip_djf_mm"
PRECIP_ANOM_NORMAL_YEARS = (1991, 2020)
# AK and YT descriptive spring mechanism variable: mean 2 m temperature.
SPRING_MONTHS = (3, 4, 5)  # MAM
# temp_jja (H3b control), temp_mam (descriptive), precip_octmar_mm and
# precip_anom_lag0/lag1 (H5) per region and year (src.climate_vars).
CLIMATE_CONTROLS_TABLE = DATA_PROCESSED / "climate_controls_region_year.csv"

# Test directions (ANALYSIS_PLAN.md "Directions and sidedness"), as the
# alternative of each test per region: "greater", "less", "two-sided", or None
# where the region is descriptive only or the test does not apply. H4 is one
# north-vs-SoCal contrast. Passed as `alternative` to src.stats
# permutation_test, coef_test and contrast_test (one tail in the stated
# direction; built 2026-10-08).
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
# HAC_MAXLAGS, year-clustered errors reported alongside (src.stats
# fit_ols_hac, fit_driscoll_kraay, fit_pooled; applied 2026-10-08).
USE_T = True
POOLED_COV_TYPE = "hac-groupsum"
# t degrees of freedom for the Driscoll-Kraay fit: number of years minus
# this. statsmodels 0.15 counts them from the row order of the time groups
# (df 0, 4 or 100 for the same data sorted three ways; code audit 2026-10-05),
# and its t_test and wald_test use that count too (F(4, 4) and t df 4 on a
# 5-region, 41-year panel; probe 2026-10-08), so src/stats.py takes every
# p-value from scipy with this df instead.
POOLED_DF_YEARS_MINUS = 1
# Small-sample correction of the robust covariances (owner, 2026-10-08,
# before any result; D65, frozen plan's deviations log). True: Newey-West
# gets n / (n - k) (statsmodels' HAC default is no correction); Driscoll-Kraay
# and year-clustered errors keep statsmodels' cluster factor
# G / (G - 1) x (N - 1) / (N - K) (their default). SEs about 3.8% wider for
# H3a (n 42, k 3), 5.1% for H3b, 4.9% for the H4 Driscoll-Kraay fit.
ROBUST_SMALL_SAMPLE_CORRECTION = True
# H4 pooled model (ANALYSIS_PLAN "Headline methods" 3, "H4's actual test"):
# the five main regions, SoCal the reference level (patsy would take AB,
# the first alphabetically), and the contrast's north regions.
H4_REGIONS = ("PNW", "BC", "AB", "NorCal", "SoCal")
H4_REFERENCE = "SoCal"
H4_NORTH = _NORTH
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
STATION_MIN_PER_REGION_YEAR = 5   # frozen at 5 for every region (ANALYSIS_PLAN "Execution details")
STATION_INDEX_TABLE = DATA_PROCESSED / "station_swe_region_year.csv"
# One site under two station IDs (another network's copy or a renamed
# course; pre-freeze audits 2026-10-06): within SITE_DUP_MAX_KM and at least
# SITE_DUP_MIN_SHARE of at least SITE_DUP_MIN_YEARS shared years within
# SITE_DUP_TOL_MM (0.1 inch, NRCS's reporting step). The lower-priority copy
# loses the shared years (src.stations.dedupe_sites).
SITE_DUP_MAX_KM = 3
SITE_DUP_TOL_MM = 2.6
SITE_DUP_MIN_SHARE = 0.8
SITE_DUP_MIN_YEARS = 3
SITE_SOURCE_PRIORITY = {"nrcs": 0, "bc": 1, "yukon": 1, "canswe": 2}
# SWE in the tests (owner, 2026-10-05; DECISIONS.md "SWE source for the
# tests"): ERA5-Land April 1 SWE as a z-score against its own regional
# STATION_NORMAL_YEARS normal is the predictor; the station index z is the
# robustness check where it exists. Both columns are in STATION_INDEX_TABLE.
SWE_TEST_COLUMN = "era5_swe_z"
SWE_CHECK_COLUMN = "station_swe_z"
# ERA5-Land SWE % and z are left empty for a region whose normal is under
# this (SoCal: 0.06 mm, z reached 4.7 and % 1,787; pre-freeze data audit,
# 2026-10-05), the same floor as STATION_PCT_MIN_NORMAL_MM.
ERA5_SWE_MIN_NORMAL_MM = 10

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

# Seasonal-outlook prediction model, version 1 (exploratory; planned after
# run1 was seen; D83; docs/prediction_model_spec.md; settings agreed by the
# owner 2026-10-12). Column names as in run_hypotheses.fire_frame, with
# precip_octmar_mm added. Scoring reuses FORWARD_MIN_TRAIN_YEARS,
# PREDICTION_ALPHA, N_BOOTSTRAP and RANDOM_SEED.
PRED_PREDICTORS = ("enso_djf", "precip_octmar_mm", "swe_z", "spei3_djf")
# hindsight run only: not known in spring, never a forecasting predictor
PRED_HINDSIGHT_PREDICTORS = (*PRED_PREDICTORS, "temp_jja")
# Ridge penalties tried at each step, per training row on predictors
# standardised within region: 13 values, 0.01 (almost none) to 1000 (the
# predictors switched off, leaving the trend-only baseline).
PRED_RIDGE_GRID = tuple(10 ** (-2 + 5 * k / 12) for k in range(13))
PRED_TOP_SHARE = 1 / 3        # yes or no outcome: top third of the region's training seasons
PRED_YES_PROBABILITY = 0.5    # a "yes" call in the hits and false alarms count
PRED_SKILL_CI = 0.95          # interval on skill, unseen years resampled
# regions with no snowpack predictor (ERA5_SWE_MIN_NORMAL_MM leaves swe_z
# empty): the value is set to 0, "no information", so the region stays pooled
PRED_NO_SNOW_REGIONS = ("SoCal",)
# skill is reported for these groups beside each region
PRED_GROUPS = {"all seven": tuple(REGIONS),
               "AK and YT": tuple(r for r, role in REGIONS.items() if role == "north"),
               "other five": tuple(r for r, role in REGIONS.items() if role != "north")}
PRED_RUN = "prediction_v1"    # results/tables/<PRED_RUN>/<label>/

# Version 1b (agreed 2026-10-12, after version 1 was seen; spec section 8;
# D91). The variants are fixed before any is run and all are reported.
PRED_1B_SPRING = (*PRED_PREDICTORS, "precip_anom_lag1", "snowfall_frac")
# temp_mam is known by 1 June: before the season in PNW, NorCal and SoCal,
# two months into it in BC, AB, AK and YT (FIRE_SEASON_MONTHS)
PRED_1B_JUNE = (*PRED_1B_SPRING, "temp_mam")
# variant -> (predictors, regional coefficients, per-region scale)
PRED_1B_VARIANTS = {
    "regions": (PRED_PREDICTORS, True, False),
    "scaled": (PRED_PREDICTORS, False, True),
    "regions_scaled": (PRED_PREDICTORS, True, True),
    "spring_inputs": (PRED_1B_SPRING, True, True),
    "june_update": (PRED_1B_JUNE, True, True),
    "hindsight": ((*PRED_1B_JUNE, "temp_jja"), True, True),  # cannot forecast
}
PRED_1B_GRID = PRED_RIDGE_GRID[::2]  # 7 values, 0.01 to 1000, for each penalty
PRED_1B_MIN_PAST_ERRORS = 8          # unseen-year errors needed before they set the interval
PRED_1B_RUN = "prediction_v1b"

# Version 1c (agreed 2026-10-12, after version 1b was seen; spec section 9;
# D92). Two variants, fixed before either is run, both in spring_inputs'
# design. burn_lag1 is the region's log_burn of the season before.
PRED_1C_VARIANTS = {
    "last_burn": ((*PRED_1B_SPRING, "burn_lag1"), True, True),
    # cannot forecast: the summer's mean temperature, SPEI-3 and soil moisture
    "ceiling": ((*PRED_1B_JUNE, "temp_jja", "spei3_jja", "soil_moisture"), True, True),
}
PRED_1C_RUN = "prediction_v1c"

# Map page (ACTION_PLAN "Second goal"; D85, D98). Display settings only: no
# test reads them. One entry per selectable dataset:
# (committed table, value column, measure, class edges, colour tokens, detail
# column shown as the raw value). Measures: "ratio" = the season over the
# region's typical season (back-transformed mean log burned area of seasons
# with a counted fire, as in the season history chart); "pct" = percent of
# the region's mean over MAP_NORMAL_YEARS; "diff" = difference from that
# mean; "as_is" = the column already is a percent of normal. Five classes
# per layer, cut at the four edges (a value on an edge goes to the class
# above). Edges chosen by eye for a readable spread, not from a test.
MAP_NORMAL_YEARS = PRECIP_ANOM_NORMAL_YEARS
MAP_LAYERS = {
    "fire": ("fire_region_year.csv", "burn_ha", "ratio", (0.1, 0.5, 2.0, 10.0),
             ("fire-1", "fire-2", "fire-3", "fire-4", "fire-5"), "burn_ha"),
    "rain": ("climate_controls_region_year.csv", "precip_octmar_mm", "pct", (60, 85, 115, 140),
             ("precip-dry-2", "precip-dry-1", "precip-mid", "precip-wet-1", "precip-wet-2"),
             "precip_octmar_mm"),
    "snow": ("station_swe_region_year.csv", "era5_swe_pct", "as_is", (50, 80, 120, 150),
             ("snow-1", "snow-2", "snow-3", "snow-4", "snow-5"), "era5_swe_apr1_mm"),
    "temp": ("climate_controls_region_year.csv", "temp_jja", "diff", (-1.0, -0.3, 0.3, 1.0),
             ("temp-cold-2", "temp-cold-1", "temp-mid", "temp-warm-1", "temp-warm-2"),
             "temp_jja"),
}
MAP_START_LAYER = "fire"
# The outlines are drawn in an Albers projection centred on the study area
# (display only; areas are measured in CRS_EQUAL_AREA), with islands and
# other parts under MAP_MIN_PART_KM2 left out and outlines simplified.
MAP_DISPLAY_CRS = "+proj=aea +lat_1=38 +lat_2=64 +lat_0=50 +lon_0=-132 +datum=WGS84 +units=m"
MAP_SIMPLIFY_KM = 6
MAP_MIN_PART_KM2 = 800
MAP_WIDTH = 640

# Sea-surface temperature for the map page's ocean panels (D99). Display
# only: no test, reported run or forecast reads it, and the files are not
# pinned inputs. ERSST v6 is the version NOAA CPC builds ONI and RONI from.
ERSST_URL = "https://www.ncei.noaa.gov/data/sea-surface-temperature-extended-reconstructed/v6/access/"
ERSST_RAW = DATA_RAW / "ersst_v6"
ERSST_LAST_WINTER = 2026           # winter 2025-26, the last one in the climate tables
SST_MONTHS = (12, 1, 2)            # December of Y-1 with January and February of Y
SST_NORMAL_YEARS = (1991, 2020)    # winters; the base period of ONI and RONI
SST_TROPICS_LAT = (-20, 20)        # the tropical mean RONI subtracts, every longitude
NINO34_BOX = ((-5, 5), (190, 240))  # 5S-5N, 170W-120W, as (lat, lon east) ranges
# The two panels, as (lat, lon east) ranges of cell centres: the whole tropical
# Pacific, and the ocean beside the seven regions.
SST_PANELS = {"tropics": ((-30, 30), (120, 290)), "coast": ((24, 62), (170, 246))}
# Five classes of the relative anomaly in degrees Celsius, cut at these edges
# (by eye, as MAP_LAYERS), coloured with the temperature ramp.
SST_EDGES = (-1.0, -0.4, 0.4, 1.0)
SST_TOKENS = ("temp-cold-2", "temp-cold-1", "temp-mid", "temp-warm-1", "temp-warm-2")
