"""Tests for src/fire.py on synthetic fires: type filters, cutover, the
whole-fire floor before clipping, season windows, country assignment,
undated CNFDB fires and the region x year table."""
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from src import fire
from src.config import CRS_EQUAL_AREA, FIRE_FIRST_YEAR

KM = 1_000


def square_ha(x0, y0, ha):
    side = (ha * 10_000) ** 0.5
    return box(x0, y0, x0 + side, y0 + side)


def fires_frame(rows, crs=CRS_EQUAL_AREA):
    df = pd.DataFrame(rows)
    df["ignition"] = pd.to_datetime(df["ignition"])
    for col, default in (("month_known", True), ("date_known", True), ("name", "x")):
        if col not in df:
            df[col] = default
    return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)


@pytest.fixture
def regions():
    # Two US regions side by side (PNW west of x=0, NorCal east) and BC to the north.
    return gpd.GeoDataFrame(
        {"region": ["PNW", "NorCal", "BC"]},
        geometry=[box(-100 * KM, 0, 0, 100 * KM), box(0, 0, 100 * KM, 100 * KM),
                  box(-100 * KM, 100 * KM, 100 * KM, 200 * KM)],
        crs=CRS_EQUAL_AREA)


def test_season_year_plain_window():
    s = fire.season_year(pd.to_datetime(pd.Series(["2020-05-31", "2020-06-01", "2020-10-31",
                                                   "2020-11-01"])), (6, 10))
    assert s.tolist() == [pd.NA, 2020, 2020, pd.NA]


def test_season_year_wraps_january_into_previous_season():
    s = fire.season_year(pd.to_datetime(pd.Series(["2025-01-07", "2024-12-31", "2024-06-01",
                                                   "2025-02-01", "2024-05-31"])), (6, 1))
    assert s.tolist() == [2024, 2024, 2024, pd.NA, pd.NA]


def test_keep_wildfires_per_source():
    f = fires_frame([
        {"source": "MTBS", "fire_type": "Wildfire", "ignition": "2000-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "MTBS", "fire_type": "Prescribed Fire", "ignition": "2000-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "MTBS", "fire_type": "Other", "ignition": "2000-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "WFIGS", "fire_type": "RX", "ignition": "2025-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "WFIGS", "fire_type": "WF", "ignition": "2025-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "CNFDB", "fire_type": "prescribed", "ignition": "2000-07-01", "geometry": box(0, 0, 1, 1)},
        {"source": "CNFDB", "fire_type": None, "ignition": "2000-07-01", "geometry": box(0, 0, 1, 1)},
    ])
    kept, counts = fire.keep_wildfires(f)
    assert kept["fire_type"].fillna("na").tolist() == ["Wildfire", "Other", "WF", "na"]
    assert counts["n"].sum() == len(f)


def test_splice_us_by_ignition_date():
    f = fires_frame([
        {"source": "MTBS", "fire_type": "Wildfire", "ignition": "2024-12-31", "geometry": box(0, 0, 1, 1)},
        {"source": "MTBS", "fire_type": "Wildfire", "ignition": "2025-01-07", "geometry": box(0, 0, 1, 1)},
        {"source": "WFIGS", "fire_type": "WF", "ignition": "2024-12-31", "geometry": box(0, 0, 1, 1)},
        {"source": "WFIGS", "fire_type": "WF", "ignition": "2025-01-07", "geometry": box(0, 0, 1, 1)},
        {"source": "CNFDB", "fire_type": "N", "ignition": "2025-01-07", "geometry": box(0, 0, 1, 1)},
    ])
    out = fire.splice_us(f, "2025-01-01")
    assert list(zip(out["source"], out["ignition"].dt.year)) == [
        ("MTBS", 2024), ("WFIGS", 2025), ("CNFDB", 2025)]


def test_floor_applies_to_whole_fire_before_clipping(regions):
    # 600 ha straddling PNW and NorCal: kept whole, each region gets about 300 ha.
    side = (600 * 10_000) ** 0.5
    f = fires_frame([
        {"source": "MTBS", "fire_id": "a", "fire_type": "Wildfire", "ignition": "2000-07-01",
         "geometry": box(-side / 2, 10 * KM, side / 2, 10 * KM + side)},
        {"source": "MTBS", "fire_id": "b", "fire_type": "Wildfire", "ignition": "2000-07-01",
         "geometry": square_ha(-50 * KM, 50 * KM, 400)},
    ])
    floored = fire.whole_fire_floor(f)
    assert floored["fire_id"].tolist() == ["a"]
    pieces = fire.clip_to_regions(floored, regions)
    by_region = pieces.set_index("region")["clipped_ha"]
    assert by_region["PNW"] == pytest.approx(300, rel=1e-6)
    assert by_region["NorCal"] == pytest.approx(300, rel=1e-6)


def test_each_region_takes_its_own_countrys_fires(regions):
    # One MTBS and one CNFDB fire, each crossing the PNW-BC line.
    f = fires_frame([
        {"source": "MTBS", "fire_id": "us", "fire_type": "Wildfire", "ignition": "2000-07-01",
         "geometry": box(-60 * KM, 95 * KM, -50 * KM, 105 * KM)},
        {"source": "CNFDB", "fire_id": "ca", "fire_type": "N", "ignition": "2000-07-01",
         "geometry": box(-40 * KM, 95 * KM, -30 * KM, 105 * KM)},
    ])
    f["cnfdb_year"] = [np.nan, 2000]
    pieces = fire.clip_to_regions(f, regions)
    assert sorted(zip(pieces["fire_id"], pieces["region"])) == [("ca", "BC"), ("us", "PNW")]
    assert pieces["clipped_ha"].tolist() == pytest.approx([5_000, 5_000], rel=1e-6)


def test_region_windows_differ_for_one_fire(regions):
    # A 15 April fire crossing PNW (Jun-Oct) and BC (Apr-Oct): only BC counts it,
    # and only from CNFDB; the MTBS copy counts nowhere.
    f = fires_frame([
        {"source": "CNFDB", "fire_id": "ca", "fire_type": "N", "ignition": "2000-04-15",
         "geometry": box(-40 * KM, 95 * KM, -30 * KM, 105 * KM)},
        {"source": "MTBS", "fire_id": "us", "fire_type": "Wildfire", "ignition": "2000-04-15",
         "geometry": box(-40 * KM, 95 * KM, -30 * KM, 105 * KM)},
    ])
    f["cnfdb_year"] = [2000, np.nan]
    pieces = fire.clip_to_regions(f, regions)
    seasons = dict(zip(pieces["region"], pieces["season"]))
    assert seasons["BC"] == 2000 and pd.isna(seasons["PNW"])


def test_cnfdb_dates_and_undated_fires_count_by_year(regions):
    d = fire.cnfdb_dates(pd.Series([2022, 2022, 2022]), pd.Series([7, 0, 8]),
                         pd.Series([3, 0, np.nan]))
    assert d["month_known"].tolist() == [True, False, True]
    assert d["date_known"].tolist() == [True, False, False]
    f = fires_frame([
        {"source": "CNFDB", "fire_id": "u", "fire_type": "N", "ignition": d["ignition"][1],
         "month_known": False, "date_known": False,
         "geometry": square_ha(0, 150 * KM, 500)}])
    f["cnfdb_year"] = [2022]
    pieces = fire.clip_to_regions(f, regions)
    assert pieces["season"].tolist() == [2022] and pieces["undated"].tolist() == [True]


def test_region_year_table_zero_years_and_season_days():
    pieces = pd.DataFrame({
        "region": ["PNW", "PNW", "PNW"], "season": [1985, 1985, 1986],
        "clipped_ha": [500.0, 1500.0, 700.0], "source": ["MTBS"] * 3,
        "fire_type": ["Wildfire", "Other", "Wildfire"], "undated": [False] * 3,
        "date_known": [True, True, True],
        "ignition": pd.to_datetime(["1985-06-10", "1985-08-19", "1986-07-01"])})
    last = {r: FIRE_FIRST_YEAR + 3 for r in fire.REGIONS}
    t = fire.region_year_table(pieces, last).set_index(["region", "year"])
    assert t.loc[("PNW", 1984), "zero_fire"] and t.loc[("PNW", 1984), "log_burn"] == 0
    assert t.loc[("PNW", 1985), "burn_ha"] == 2000
    assert t.loc[("PNW", 1985), "log_burn"] == pytest.approx(np.log(2001))
    assert t.loc[("PNW", 1985), "season_days"] == 70
    assert t.loc[("PNW", 1985), "n_unknown_type"] == 1
    assert np.isnan(t.loc[("PNW", 1986), "season_days"])  # one fire: undefined
    assert len(t) == 4 * len(fire.REGIONS)


def test_union_areas_count_overlap_once_and_feed_the_table(regions):
    # Two 1,000 ha squares in one PNW season overlapping by half: union 1,500 ha.
    side = (1_000 * 10_000) ** 0.5
    f = fires_frame([
        {"source": "WFIGS", "fire_id": "a", "fire_type": "WF", "ignition": "2024-07-01",
         "geometry": box(-80 * KM, 10 * KM, -80 * KM + side, 10 * KM + side)},
        {"source": "WFIGS", "fire_id": "b", "fire_type": "WF", "ignition": "2024-08-01",
         "geometry": box(-80 * KM + side / 2, 10 * KM, -80 * KM + 1.5 * side, 10 * KM + side)},
    ])
    pieces = fire.clip_to_regions(f, regions)
    areas = fire.union_areas(pieces)
    row = areas.iloc[0]
    assert row["sum_ha"] == pytest.approx(2_000, rel=1e-6)
    assert row["union_ha"] == pytest.approx(1_500, rel=1e-6)
    assert row["double_ha"] == pytest.approx(500, rel=1e-6)
    last = {r: 2024 for r in fire.REGIONS}
    t = fire.region_year_table(pieces, last, areas=areas).set_index(["region", "year"])
    assert t.loc[("PNW", 2024), "burn_ha"] == pytest.approx(1_500, rel=1e-6)
    assert t.loc[("PNW", 2024), "n_fires"] == 2


def test_local_dates_shift_late_evening_utc():
    utc = pd.to_datetime(pd.Series(["2024-11-01 05:00", "2024-11-01 05:00"]), utc=True)
    out = fire.local_dates(utc, pd.Series(["US-WA", "US-AK"]))
    assert out.dt.strftime("%Y-%m-%d").tolist() == ["2024-10-31", "2024-10-31"]


def test_frozen_rules_table_sums_drops_other_and_undated():
    # D62: summed clipped area (no union), MTBS "Other" dropped, CNFDB fires
    # without a month dropped; every other piece kept as in the main table.
    from src.fire import frozen_rules_pieces, frozen_rules_table, region_year_table

    def piece(source, region, ha, fire_type="Wildfire", undated=False, season=1990):
        return {"source": source, "fire_id": f"{source}{ha}", "region": region,
                "clipped_ha": float(ha), "fire_type": fire_type, "undated": undated,
                "season": season, "ignition": pd.Timestamp(f"{season}-07-01"),
                "date_known": not undated, "month_known": not undated}

    pieces = pd.DataFrame([
        piece("MTBS", "PNW", 500), piece("MTBS", "PNW", 600),       # overlap: summed here
        piece("MTBS", "PNW", 700, fire_type="Other"),               # dropped
        piece("CNFDB", "YT", 800, fire_type="N"),
        piece("CNFDB", "YT", 900, fire_type="N", undated=True),     # dropped
        piece("WFIGS", "SoCal", 1000, fire_type="WF", season=2024),
    ])
    pieces["season"] = pieces["season"].astype("Int64")
    kept = frozen_rules_pieces(pieces)
    assert sorted(kept["clipped_ha"]) == [500, 600, 800, 1000]
    last = {r: 2025 for r in ("PNW", "AK", "NorCal", "SoCal")} | {r: 2024 for r in ("BC", "AB", "YT")}
    table = frozen_rules_table(pieces, last_year=last).set_index(["region", "year"])
    assert table.loc[("PNW", 1990), "burn_ha"] == 1100
    assert table.loc[("PNW", 1990), "n_unknown_type"] == 0
    assert table.loc[("YT", 1990), "burn_ha"] == 800 and table.loc[("YT", 1990), "n_undated"] == 0
    assert table.loc[("SoCal", 2024), "burn_ha"] == 1000
    assert table.loc[("PNW", 1991), "zero_fire"]
    assert len(table) == 4 * 42 + 3 * 41
    # the main table on the same pieces keeps Other and the undated fire
    main = region_year_table(pieces, last_year=last).set_index(["region", "year"])
    assert main.loc[("PNW", 1990), "burn_ha"] == 1800
    assert main.loc[("YT", 1990), "burn_ha"] == 1700


def test_dissolve_cnfdb_merges_parts_of_one_fire_before_the_floor():
    # Audit 2026-10-08 M3: BC 1998-N40187 was two polygons of 349 and 207 ha,
    # each under the floor, together 556 ha.
    import geopandas as gpd
    from shapely.geometry import box
    from src.fire import dissolve_cnfdb

    def row(fire_id, year, geom, month_known=True, ignition="1998-08-05", key=True,
            fire_type="N"):
        return {"source": "CNFDB", "fire_id": fire_id, "name": None, "fire_type": fire_type,
                "ignition": pd.Timestamp(ignition), "month_known": month_known,
                "date_known": month_known, "cnfdb_year": year, "fire_key": key,
                "geometry": geom}

    fires = gpd.GeoDataFrame([
        row("BC:A", 1998, box(0, 0, 1, 1), ignition="1998-08-05"),
        row("BC:A", 1998, box(2, 0, 3, 1), ignition="1998-05-16", fire_type="H"),
        row("BC:A", 1999, box(5, 0, 6, 1)),                       # same id, other year
        row("MB:", 1998, box(7, 0, 8, 1), key=False),             # blank ids never merge
        row("MB:", 1998, box(9, 0, 10, 1), key=False),
        row("NT:B", 1995, box(0, 5, 1, 6), month_known=False, ignition="1995-07-15"),
        row("NT:B", 1995, box(1, 5, 2, 6), month_known=False, ignition="1995-07-15"),
        row("NT:C", 1996, box(0, 8, 1, 9), month_known=False, ignition="1996-07-15"),
        row("NT:C", 1996, box(1, 8, 2, 9), ignition="1996-08-02"),
    ], geometry="geometry", crs="EPSG:3347")
    out = dissolve_cnfdb(fires)
    assert len(out) == 6
    a = out[(out["fire_id"] == "BC:A") & (out["cnfdb_year"] == 1998)].iloc[0]
    assert a["n_parts"] == 2 and a.geometry.area == pytest.approx(2.0)
    assert a["ignition"] == pd.Timestamp("1998-05-16") and a["fire_type"] == "H"
    assert (out["fire_id"] == "MB:").sum() == 2
    b = out[out["fire_id"] == "NT:B"].iloc[0]
    assert not b["month_known"] and b["n_parts"] == 2
    c = out[out["fire_id"] == "NT:C"].iloc[0]
    assert c["month_known"] and c["ignition"] == pd.Timestamp("1996-08-02")
    assert "fire_key" not in out


def test_dissolve_cnfdb_keeps_far_apart_parts_separate_and_chains_near_ones():
    # Audit 2026-10-08 round 2 H1 (D67): agencies reuse FIRE_ID within a year;
    # BC 1998-N40187 was two fires 25 km apart. Built in CRS_EQUAL_AREA (metres)
    # so the distances are exact.
    import geopandas as gpd
    from shapely.geometry import box
    from src.config import CRS_EQUAL_AREA
    from src.fire import dissolve_cnfdb, merge_components

    def row(fire_id, geom, ignition="1998-08-05", fire_type="N"):
        return {"source": "CNFDB", "fire_id": fire_id, "name": None, "fire_type": fire_type,
                "ignition": pd.Timestamp(ignition), "month_known": True, "date_known": True,
                "cnfdb_year": 1998, "fire_key": True, "geometry": geom}

    far = [row("BC:F", box(0, 0, 1000, 1000), ignition="1998-05-16", fire_type="H"),
           row("BC:F", box(26000, 0, 27000, 1000))]                      # 25 km gap
    chain = [row("BC:G", box(0, 50000, 1000, 51000)),
             row("BC:G", box(1600, 50000, 2600, 51000)),                 # 0.6 km from the first
             row("BC:G", box(3200, 50000, 4200, 51000))]                 # 0.6 km from the second
    edge = [row("BC:H", box(0, 90000, 1000, 91000)),
            row("BC:H", box(2000, 90000, 3000, 91000))]                  # exactly 1 km: merged
    fires = gpd.GeoDataFrame(far + chain + edge, geometry="geometry", crs=CRS_EQUAL_AREA)
    out = dissolve_cnfdb(fires, max_km=1.0)
    f = out[out["fire_id"] == "BC:F"].sort_values("ignition")
    assert len(f) == 2 and (f["n_parts"] == 1).all()
    assert list(f["fire_type"]) == ["H", "N"]            # each part keeps its own attributes
    assert f.geometry.area.tolist() == pytest.approx([1e6, 1e6])
    g = out[out["fire_id"] == "BC:G"]
    assert len(g) == 1 and g["n_parts"].iloc[0] == 3     # chained, though first and last are 2.2 km apart
    assert g.geometry.area.iloc[0] == pytest.approx(3e6)
    assert (out["fire_id"] == "BC:H").sum() == 1
    # a smaller distance splits the chain
    assert len(set(merge_components(fires.geometry.iloc[2:5], max_km=0.5))) == 3
