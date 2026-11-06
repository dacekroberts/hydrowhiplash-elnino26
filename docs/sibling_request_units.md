<!-- Copy of climate-whiplash-prediction docs/parent_request_units.md at its commit 98a2468, taken 2026-11-06 for D113. Not edited; the sibling holds the master. -->

# Request to the parent: burned area by unit

**Ready, 2026-11-06 (session 15), the unit layer updated to `units_b` the same day; not sent.** Route R1 was approved on
2026-11-06 (`DECISIONS.md` "Stage 6 calls 4 to 9"). The owner carries
this file and the unit layer to a session in the parent.

**The unit layer:** `data/processed/units_b.geojson` in this repository
(EPSG:4326, 129 units, 20,126,824 bytes, sha256
`9818cdbb4213649cf545a49e35fe8eed7d52bf2a2f4909e8745aa68e6ac970cb`),
built at 04e4e03 from EPA Level III ecoregions (US regions) and the
Ecological Framework of Canada's ecoregions (BC, AB, YT); its table is
`results/tables/units_b/units.csv`. It replaces the 131-unit
`units.geojson` of aa99cfd, where glacier cells counted toward the
30-cell floor (`DECISIONS.md` 2026-11-06 "Units rebuilt"); the earlier
layer is not to be used. Columns: `unit` (e.g. `PNW-01`), `region`,
`sources`, `area_km2`, `n_cells` (non-glacier land cells), `undersized`,
`geojson_sha256`. The units of a
region tile it; project to ESRI:102008 before clipping, as for the
regions. Boundary terms: EPA, no use constraints; Canada, Open
Government Licence - Canada.

Nothing in the parent is written from this repository: this file
is the specification a session in the parent works from, carried there
by the owner, as `docs/parent_request_after_date.md` was.

## What is asked for

Two tables, built from the parent's own MTBS, WFIGS and CNFDB files by
the builder of its `fire_region_year.csv`, with the unit layer this
repository hands over (`units_b.geojson`, the output of `src/units.py`,
with its checksum):

1. `fire_unit_year.csv`: one row per unit and season, for the same
   region-seasons as the pinned `fire_region_year.csv` (to 2025 for PNW,
   AK, NorCal and SoCal; to 2024 for BC, AB and YT). Columns: `unit`,
   `region`, `year`, `burn_ha`, `n_fires`, `n_undated`. Zero seasons
   kept: every unit appears in every season of its region.
2. `fire_after_issue_date_unit_year.csv`: the same split as
   `fire_after_issue_date_region_year.csv`, per unit: `unit`, `region`,
   `year`, `issue_date`, `after_ha`, `before_ha`, `undated_ha`,
   `n_after`, `n_before`, `n_undated`, `burn_ha`.

**Every rule as in `fire_region_year.csv`:** fires of 405 ha or more by
whole-fire area before any clipping, each region's season window, the
same start dates, prescribed burns out, CNFDB parts within 1 km merged,
area in ESRI:102008. The one change: each kept fire is clipped to the
units of its region instead of to the region, and each source's pieces
are unioned within a unit and the sources summed, as they are now
within a region. A fire that crosses a unit border counts once in each
unit it reaches (`n_fires`).

## Checks the tables must pass, on the parent's side and again here

- Units summed to their region equal the pinned `burn_ha` of every
  region-season to 1e-6 ha (the units tile each region, so the union
  per unit summed is the union per region). Same for each split column
  against the pinned split table.
- The unit and season set is exactly the layer's units times their
  region's seasons.
- No row for a held-back region-season or a later season.
- `src/unit_fire_check.py` runs these checks on arrival; the table is
  pinned only if it passes.

## The held-back seasons

Nothing for a held-back season is built for this request
(`docs/held_back_seasons.md` section 2). On each scoring day, the
parent's region numbers for the arriving season come with the unit
numbers for the same season, built by the same rules, in one approved
read.

## How it arrives

As the split table did: the owner carries the two files over, the read
is approved once, recorded in `results/tables/parent_handoff.json` with
checksums, and pinned in `BUILT_INPUT_TABLES`.

## Limits to state with the tables

- Clipping to units splits a fire's area across units, but the 405 ha
  floor is on the whole fire, so a unit can hold a piece of a few
  hectares.
- A unit's season window is its region's.
- Values derived from MTBS, WFIGS and CNFDB keep those sources' terms
  (`DATA_SOURCES.md`).
