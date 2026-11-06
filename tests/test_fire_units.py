"""Tests for src/fire_units.py on synthetic fires and units: clipping to units
matches clipping to regions when the units tile them, zero seasons kept,
a fire crossing a unit border counted in each unit, held-back seasons dropped
and refused, the unit layer's checksum, and each check failing on a gap."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from src import fire, fire_after_date as fad, fire_units as fu
from src.config import CRS_EQUAL_AREA, REGIONS

KM = 1_000
SIDE = (1_000 * 10_000) ** 0.5  # side of a 1,000 ha square, m
LAST = {r: 2025 if r in ("PNW", "AK", "NorCal", "SoCal") else 2024 for r in REGIONS}
SEASONS = [("PNW", 2020), ("PNW", 2021), ("BC", 2020)]


@pytest.fixture
def regions():
    return gpd.GeoDataFrame(
        {"region": ["PNW", "BC"]},
        geometry=[box(-100 * KM, 0, 100 * KM, 100 * KM), box(-100 * KM, 100 * KM, 100 * KM, 200 * KM)],
        crs=CRS_EQUAL_AREA)


@pytest.fixture
def units():
    # PNW split at x=0 into two units; BC one unit
    return gpd.GeoDataFrame(
        {"unit": ["PNW-01", "PNW-02", "BC-01"], "region": ["PNW", "PNW", "BC"]},
        geometry=[box(-100 * KM, 0, 0, 100 * KM), box(0, 0, 100 * KM, 100 * KM),
                  box(-100 * KM, 100 * KM, 100 * KM, 200 * KM)],
        crs=CRS_EQUAL_AREA)


def fires():
    rows = [
        # crosses the PNW unit border; overlaps the next fire (same source)
        {"source": "WFIGS", "ignition": "2020-07-10", "geometry": box(-SIDE / 2, 10 * KM, SIDE / 2, 10 * KM + SIDE)},
        {"source": "WFIGS", "ignition": "2020-08-10", "geometry": box(0, 10 * KM, SIDE, 10 * KM + SIDE)},
        # the other source on the same ground: sources are summed, not unioned
        {"source": "MTBS", "ignition": "2015-07-01", "geometry": box(-50 * KM, 50 * KM, -50 * KM + SIDE, 50 * KM + SIDE)},
        # held-back seasons: PNW 2026 and BC 2025
        {"source": "WFIGS", "ignition": "2026-07-10", "geometry": box(-50 * KM, 20 * KM, -50 * KM + SIDE, 20 * KM + SIDE)},
        {"source": "CNFDB", "ignition": "2025-07-10", "cnfdb_year": 2025, "geometry": box(0, 150 * KM, SIDE, 150 * KM + SIDE)},
        {"source": "CNFDB", "ignition": "2020-06-10", "cnfdb_year": 2020, "geometry": box(0, 150 * KM, SIDE, 150 * KM + SIDE)},
        # undated CNFDB fire
        {"source": "CNFDB", "ignition": "2020-07-15", "cnfdb_year": 2020, "month_known": False,
         "date_known": False, "geometry": box(-50 * KM, 150 * KM, -50 * KM + SIDE, 150 * KM + SIDE)},
    ]
    df = pd.DataFrame(rows)
    df["ignition"] = pd.to_datetime(df["ignition"])
    for col, default in (("month_known", True), ("date_known", True), ("name", "x"),
                         ("fire_type", "WF")):
        df[col] = df[col].fillna(default) if col in df else default
    return fire.whole_fire_floor(gpd.GeoDataFrame(df, geometry="geometry", crs=CRS_EQUAL_AREA))


def region_rows(regions, seasons=SEASONS):
    pieces = fad.select_pieces(fire.clip_to_regions(fires(), regions), seasons)
    areas = fire.union_areas(pieces)
    table = fire.region_year_table(pieces, last_year=LAST, areas=areas)
    keys = pd.MultiIndex.from_frame(table[["region", "year"]])
    return table[keys.isin(pd.MultiIndex.from_tuples(seasons))].reset_index(drop=True)


def test_units_tiling_a_region_sum_to_it(regions, units):
    pieces = fu.clip_to_units(fires(), units)
    table = fu.unit_table(pieces, units, SEASONS, LAST)
    split = fu.unit_split_table(pieces, units, SEASONS, last_year=LAST)
    pinned = region_rows(regions)
    pinned_split = fad.split_table(fire.clip_to_regions(fires(), regions), SEASONS, last_year=LAST)
    checks = fu.check_tables(table, split, pinned, pinned_split, units, SEASONS, last_year=LAST)
    assert all(c["ok"] for c in checks.values()), checks
    # zero seasons kept: every unit in every season of its region
    assert len(table) == 2 * 2 + 1 and len(split) == 3 * len(table)
    assert table.set_index(["unit", "year"]).loc[("PNW-01", 2021), "burn_ha"] == 0
    # the border-crossing fire is a piece in both units
    n = table.set_index(["unit", "year"])["n_fires"]
    assert n[("PNW-01", 2020)] == 1 and n[("PNW-02", 2020)] == 2
    assert n.sum() > pinned["n_fires"].sum()


def test_held_back_never_built(units):
    pieces = fu.clip_to_units(fires(), units)
    table = fu.unit_table(pieces, units, last_year=LAST)
    assert table["year"].max() <= 2025
    assert not ((table["region"] == "BC") & (table["year"] > 2024)).any()
    with pytest.raises(fad.HeldBackSeasonError):
        fu.unit_table(pieces, units, [("PNW", 2026)], LAST)
    with pytest.raises(fad.HeldBackSeasonError):
        fu.unit_split_table(pieces, units, [("BC", 2025)], last_year=LAST)


def test_gap_between_units_fails_the_sum_check(regions, units):
    # shrink PNW-02 so part of the crossing fires falls outside every unit
    short = units.copy()
    short.loc[1, "geometry"] = box(0.5 * SIDE, 0, 100 * KM, 100 * KM)
    pieces = fu.clip_to_units(fires(), short)
    table = fu.unit_table(pieces, short, SEASONS, LAST)
    split = fu.unit_split_table(pieces, short, SEASONS, last_year=LAST)
    pinned = region_rows(regions)
    pinned_split = fad.split_table(fire.clip_to_regions(fires(), regions), SEASONS, last_year=LAST)
    checks = fu.check_tables(table, split, pinned, pinned_split, short, SEASONS, last_year=LAST)
    sums = checks["3 units sum to the pinned region burn_ha"]
    assert not sums["ok"]
    assert sums["gaps"]["burn_ha"]["at"] == "PNW 2020"
    assert sums["gaps"]["burn_ha"]["max_gap_ha"] == pytest.approx(0.5 * SIDE * SIDE / 1e4, rel=1e-6)
    assert not checks["4 each split column sums to the pinned split table"]["ok"]
    assert checks["1 unit table: the unit and season set is exact"]["ok"]


def test_set_check_catches_missing_and_extra_rows(regions, units):
    pieces = fu.clip_to_units(fires(), units)
    table = fu.unit_table(pieces, units, SEASONS, LAST)
    split = fu.unit_split_table(pieces, units, SEASONS, last_year=LAST)
    pinned = region_rows(regions)
    pinned_split = fad.split_table(fire.clip_to_regions(fires(), regions), SEASONS, last_year=LAST)
    late = pd.concat([table.iloc[1:], table.iloc[[0]].assign(year=2026)], ignore_index=True)
    checks = fu.check_tables(late, split, pinned, pinned_split, units, SEASONS, last_year=LAST)
    assert not checks["1 unit table: the unit and season set is exact"]["ok"]
    assert not checks["2 no held-back or later season"]["ok"]


def test_unit_layer_checksum_and_repair(tmp_path, units):
    path = tmp_path / "units.geojson"
    units.to_crs("EPSG:4326").to_file(path, driver="GeoJSON")
    with pytest.raises(fu.UnitsLayerError):
        fu.load_units(path, expected_sha256="0" * 64)
    from src.pin_inputs import sha256
    assert len(fu.load_units(path, expected_sha256=sha256(path))) == 3
    # a bow-tie polygon is repaired to polygons only
    from shapely.geometry import Polygon
    bad = units.copy()
    bad.loc[0, "geometry"] = Polygon([(0, 0), (10, 10), (10, 0), (0, 10)])
    fixed = fu.prepare_units(bad)
    assert fixed.is_valid.all() and fixed.geom_type.isin(["Polygon", "MultiPolygon"]).all()
    with pytest.raises(fu.UnitsLayerError):
        fu.prepare_units(pd.concat([units, units.iloc[[0]]]).pipe(gpd.GeoDataFrame, crs=CRS_EQUAL_AREA))


def test_scoring_day_path_on_made_up_pieces(regions, units):
    # made-up fires only: PNW 2026 and BC 2025 stand in for scored seasons
    scored = [("PNW", 2026), ("BC", 2025)]
    pieces = fu.clip_to_units(fires(), units)
    table = fu.unit_table(pieces, units, scored, LAST, scoring_day_seasons=scored)
    split = fu.unit_split_table(pieces, units, scored, last_year=LAST, scoring_day_seasons=scored)
    assert sorted(set(zip(table["region"], table["year"]))) == sorted(scored)
    assert len(table) == 2 + 1 and len(split) == 3 * len(table)
    # that day's outcome tables, by the region rules on the same made-up fires
    region_pieces = fad.select_pieces(fire.clip_to_regions(fires(), regions), scored)
    areas = fire.union_areas(region_pieces).groupby(["region", "season"])["union_ha"].sum()
    outcome = pd.DataFrame([{"region": r, "year": y, "burn_ha": float(areas.get((r, y), 0.0))}
                            for r, y in scored])
    outcome_split = fad.split_table(fire.clip_to_regions(fires(), regions), scored,
                                    last_year=LAST, scoring_day_seasons=scored)
    checks = fu.check_tables(table, split, outcome, outcome_split, units, scored,
                             last_year=LAST, scoring_day_seasons=scored)
    assert all(c["ok"] for c in checks.values()), checks
    assert table["burn_ha"].sum() > 0
    # without the scoring-day names the same rows fail check 2
    checks = fu.check_tables(table, split, outcome, outcome_split, units, scored, last_year=LAST)
    assert not checks["2 no held-back or later season"]["ok"]


def test_scoring_day_names_must_match_the_seasons_asked(units):
    pieces = fu.clip_to_units(fires(), units)
    with pytest.raises(fad.HeldBackSeasonError):
        fu.unit_table(pieces, units, [("PNW", 2026)], LAST,
                      scoring_day_seasons=[("PNW", 2026), ("BC", 2025)])
    with pytest.raises(fad.HeldBackSeasonError):
        fu.unit_split_table(pieces, units, [("PNW", 2026), ("BC", 2025)], last_year=LAST,
                            scoring_day_seasons=[("PNW", 2026)])
    # a development build never carries a held-back piece
    dev = fu.unit_table(pieces, units, last_year=LAST)
    assert not (dev["year"] > dev["region"].map(LAST)).any()
