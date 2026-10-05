"""Tests for src/stations.py on synthetic station records with known answers."""
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely.geometry import box

from src import stations
from src.config import FOOT_M, INCH_MM


def test_nearest_in_window_picks_closest_and_respects_window():
    df = pd.DataFrame({
        "key": ["a", "a", "a", "b", "c"],
        "year": [2000, 2000, 2000, 2000, 2001],
        "date": pd.to_datetime(["2000-03-25", "2000-03-31", "2000-04-03", "2000-04-20",
                                "2000-04-01"]),   # c: filed under 2001, dated 2000
    })
    out = stations.nearest_in_window(df, "key", "date", "year", window=10)
    assert list(out["key"]) == ["a"]
    assert out["date"].iloc[0] == pd.Timestamp("2000-03-31")


def test_nearest_in_window_tie_goes_to_later_date():
    df = pd.DataFrame({"key": ["a", "a"], "year": [2000, 2000],
                       "date": pd.to_datetime(["2000-03-29", "2000-04-04"])})
    out = stations.nearest_in_window(df, "key", "date", "year", window=10)
    assert out["date"].iloc[0] == pd.Timestamp("2000-04-04")


def test_join_flags_and_prefixed():
    qc = pd.Series(["V", "E", None])
    out = stations.join_flags(stations.prefixed(qc, "q:", skip=("", "V")),
                              pd.Series(["", "x", "y"]))
    assert list(out) == ["", "q:E;x", "y"]


# ---------------------------------------------------------------- NRCS

def nrcs_files(tmp_path):
    data_sntl = [{"stationTriplet": "1:WA:SNTL", "data": [{"stationElement": {}, "values": [
        {"month": 4, "year": 1975, "value": 30.0, "qcFlag": "B"},     # back-estimate: dropped
        {"month": 4, "year": 1990, "value": 20.0, "qcFlag": "V"},
        {"month": 4, "year": 1991, "value": 10.0, "qcFlag": "E"},     # kept, flagged
        {"month": 4, "year": 1992, "value": -1.0, "qcFlag": "S"},     # suspect: dropped
        {"month": 4, "year": 1993, "value": -0.5, "qcFlag": "V"},     # negative: dropped
        {"month": 3, "year": 1990, "value": 15.0, "qcFlag": "V"},     # not April
    ]}]}]
    data_snow = [{"stationTriplet": "2:WA:SNOW", "data": [{"stationElement": {}, "values": [
        {"month": 4, "monthPart": "1", "year": 1960, "collectionDate": "1960-03-28 00:00",
         "value": 40.0},
        {"month": 4, "monthPart": "1", "year": 1961, "collectionDate": "1961-07-01 00:00",
         "value": 35.0},                                              # placeholder date
        {"month": 4, "monthPart": "1", "year": 1962, "collectionDate": "1962-04-25 00:00",
         "value": 20.0},                                              # outside window
        {"month": 4, "monthPart": "2", "year": 1962, "collectionDate": "1962-04-15 00:00",
         "value": 25.0},                                              # mid-April survey
    ]}]}]
    meta = [{"stationTriplet": "1:WA:SNTL", "latitude": 47.0, "longitude": -121.0,
             "elevation": 1000.0},
            {"stationTriplet": "2:WA:SNOW", "latitude": 47.5, "longitude": -121.5,
             "elevation": 5000.0}]
    (tmp_path / "data_WA_SNTL_001.json").write_text(json.dumps(data_sntl))
    (tmp_path / "data_WA_SNOW_001.json").write_text(json.dumps(data_snow))
    (tmp_path / "stations_WA.json").write_text(json.dumps(meta))
    return tmp_path


def test_clean_nrcs_rules(tmp_path):
    table, counts = stations.clean_nrcs(*stations.read_nrcs(nrcs_files(tmp_path)))
    sntl = table[table["station_id"] == "1:WA:SNTL"].set_index("year")
    assert list(sntl.index) == [1990, 1991]
    assert sntl.loc[1990, "swe_apr1_mm"] == pytest.approx(20.0 * INCH_MM)
    assert sntl.loc[1990, "sample_date"] == pd.Timestamp("1990-04-01")
    assert sntl.loc[1991, "flags"] == "nrcs_qc:E"
    assert sntl.loc[1990, "elevation"] == pytest.approx(1000.0 * FOOT_M)
    assert set(sntl["method"]) == {"pillow"}
    snow = table[table["station_id"] == "2:WA:SNOW"].set_index("year")
    assert list(snow.index) == [1960, 1961]
    assert pd.isna(snow.loc[1961, "sample_date"])
    assert snow.loc[1961, "flags"] == "date_unknown"
    assert counts["qc B"] == 1 and counts["qc S"] == 1 and counts["negative"] == 1
    assert counts["outside window"] == 1 and counts["date_unknown (kept)"] == 1


# ---------------------------------------------------------------- BC

def bc_raw():
    rows = [
        # course, date, swe, code, period
        ("1A01", "1990/03/30", "500", "", "01-Apr"),
        ("1A01", "1990/03/20", "480", "", "01-Apr"),        # repeat, farther from 1 April
        ("1A01", "1991/03/31", "300", "EST PILLOW", "01-Apr"),  # estimate: dropped
        ("1A01", "1992/03/29", "", "N", "01-Apr"),          # no SWE
        ("1A01", "1993/04/02", "450", "PROBLEM", "01-Apr"),  # kept, flagged
        ("1A01", "1993/05/01", "200", "", "01-May"),        # not the April 1 survey
        ("9Z99", "1990/03/30", "100", "", "01-Apr"),        # no coordinates
    ]
    return pd.DataFrame({"Number": [r[0] for r in rows], "Date of Survey": [r[1] for r in rows],
                         "Water Equiv. mm": [r[2] for r in rows],
                         "Survey Code": [r[3] or np.nan for r in rows],
                         "Survey Period": [r[4] for r in rows], "Elev. metres": 1500})


def test_clean_bc_rules():
    coords = pd.DataFrame({"station_id": ["BCE-1A01"], "lat": [52.9], "lon": [-118.5]})
    table, counts = stations.clean_bc(bc_raw(), coords)
    t = table.set_index("year")
    assert list(t.index) == [1990, 1993]
    assert t.loc[1990, "swe_apr1_mm"] == 500
    assert t.loc[1993, "flags"] == "bc:PROBLEM"
    assert (table["station_id"] == "BCE-1A01").all()
    assert counts["estimate codes"] == 1 and counts["no coordinates"] == 1


def test_read_bc_strips_headers_and_drops_repeats(tmp_path):
    header = "Snow Course Name, Number, Date of Survey, Water Equiv. mm, Survey Period\r\n"
    row = "X,1A01,2026/03/30,500,01-Apr\r\n"
    (tmp_path / "allmss_archive.csv").write_bytes((header + row).encode())
    (tmp_path / "allmss_current.csv").write_bytes((header + row).encode())
    df = stations.read_bc(tmp_path)
    assert len(df) == 1 and "Number" in df.columns


# ---------------------------------------------------------------- Yukon

def test_read_yukon_and_clean(tmp_path):
    text = ('"# comment"\n""\n'
            "location_code,location_name,parameter,units,sample_date,target_date,year,month,"
            "result,flag\n"
            "08AA-SC01,A,snow water equivalent,mm,1990-03-28,1990-04-01,1990,4,120,Actual\n"
            "08AA-SC01,A,snow depth,cm,1990-03-28,1990-04-01,1990,4,60,Actual\n"
            "08AA-SC01,A,snow water equivalent,mm,1991-03-27,1991-04-01,1991,4,90,Estimated SWE\n"
            "08AA-SC01,A,snow water equivalent,mm,1992-04-16,1992-04-01,1992,4,80,Actual\n"
            "08AA-SC01,A,snow water equivalent,mm,1992-05-01,1992-05-01,1992,5,10,Actual\n")
    p = tmp_path / "data.csv"
    p.write_text(text)
    meta = pd.DataFrame({"location_code": ["08AA-SC01"], "latitude": [61.1],
                         "longitude": [-137.0], "elevation_m": [1160]})
    table, counts = stations.clean_yukon(stations.read_yukon_csv(p), meta)
    t = table.set_index("year")
    assert list(t.index) == [1990, 1991]
    assert t.loc[1991, "flags"] == "yukon:estimated"
    assert t.loc[1990, "station_id"] == "YT-08AA-SC01"
    assert counts["outside window"] == 1


# ---------------------------------------------------------------- CanSWE

def canswe_file(tmp_path):
    time = pd.date_range("1990-03-01", "1991-04-30", freq="D")
    ids = ["ALE-05AA801", "ALE-05AA801P", "HQ-1", "BCE-1A01"]
    snw = np.full((len(ids), len(time)), np.nan, dtype="float32")
    flag = np.full((len(ids), len(time)), b"", dtype="S1")
    t = {d: i for i, d in enumerate(time)}
    snw[0, t[pd.Timestamp("1990-03-27")]] = 150      # manual, nearest
    snw[0, t[pd.Timestamp("1990-03-15")]] = 140      # manual, outside window
    snw[0, t[pd.Timestamp("1991-04-05")]] = 160
    flag[0, t[pd.Timestamp("1991-04-05")]] = b"A"
    snw[1, t[pd.Timestamp("1990-03-31")]] = 99       # pillow, day before: not used
    snw[1, t[pd.Timestamp("1990-04-01")]] = 100      # pillow, 1 April
    snw[2, t[pd.Timestamp("1990-04-01")]] = 500      # Hydro-Quebec: never read
    snw[3, t[pd.Timestamp("1990-03-30")]] = 400
    ds = xr.Dataset(
        {"snw": (("station_id", "time"), snw), "data_flag_snw": (("station_id", "time"), flag),
         "lat": ("station_id", np.array([50.0, 50.0, 47.0, 52.9], dtype="float32")),
         "lon": ("station_id", np.array([-115.0, -115.0, -70.0, -118.5], dtype="float32")),
         "elevation": ("station_id", np.array([1500, 1500, 300, 1860], dtype="float32")),
         "type_mes": ("station_id", np.array([0, 2, 0, 0]))},
        coords={"station_id": ids, "time": time})
    path = tmp_path / "canswe.nc"
    ds.to_netcdf(path)
    return path


def test_read_and_clean_canswe(tmp_path):
    st, obs = stations.read_canswe(canswe_file(tmp_path), prefixes=("ALE", "BCE"))
    assert "HQ-1" not in set(st["station_id"]) and "HQ-1" not in set(obs["station_id"])
    table, _ = stations.clean_canswe(st, obs)
    t = table.set_index(["station_id", "year"])
    assert t.loc[("ALE-05AA801", 1990), "swe_apr1_mm"] == 150
    assert t.loc[("ALE-05AA801", 1991), "flags"] == "canswe:A"
    assert t.loc[("ALE-05AA801P", 1990), "swe_apr1_mm"] == 100
    assert t.loc[("ALE-05AA801P", 1990), "network"] == "Alberta pillow"
    assert t.loc[("ALE-05AA801", 1990), "network"] == "Alberta snow course"
    assert len(table) == 4


def test_combine_provincial_wins():
    def rows(source, swe, years):
        return pd.DataFrame({"station_id": "BCE-1A01", "source": source, "network": "n",
                             "method": "manual", "lat": 52.9, "lon": -118.5, "elevation": 1860,
                             "year": years, "swe_apr1_mm": swe, "sample_date": pd.NaT,
                             "flags": ""})
    out, counts = stations.combine(rows("bc", 500.0, [1990, 1991]),
                                   rows("canswe", 400.0, [1990, 1989]))
    assert out.set_index("year")["source"].to_dict() == {1989: "canswe", 1990: "bc", 1991: "bc"}
    assert counts == {"canswe rows replaced by provincial": 1, "canswe rows added": 1}


def test_assign_regions_drops_outside_and_yukon_network_abroad():
    regions = gpd.GeoDataFrame({"region": ["YT", "AK"]},
                               geometry=[box(-141, 60, -124, 69), box(-169, 51, -141, 71)],
                               crs="EPSG:4326")
    table = pd.DataFrame({"station_id": ["YT-a", "YT-b", "1:AK:SNTL", "X"],
                          "lat": [62.0, 64.0, 64.0, 40.0], "lon": [-135.0, -141.5, -150.0, -100.0],
                          "year": 2000})
    out, counts = stations.assign_regions(table, regions)
    assert out.set_index("station_id")["region"].to_dict() == {"YT-a": "YT", "1:AK:SNTL": "AK"}
    assert counts["stations in no region"] == 1
    assert counts["yukon network stations outside Yukon"] == 1


# ---------------------------------------------------------------- regional index

def station_rows(station_id, region, values, start=1991):
    return pd.DataFrame({"station_id": station_id, "region": region,
                         "year": range(start, start + len(values)), "swe_apr1_mm": values})


def test_station_normals_needs_enough_years_in_period():
    table = pd.concat([station_rows("a", "R", [100.0] * 25),
                       station_rows("b", "R", [100.0] * 25, start=1950),  # mostly before
                       station_rows("c", "R", [50.0, 150.0] * 10)])
    normals = stations.station_normals(table, years=(1991, 2020), min_years=20)
    assert list(normals["station_id"]) == ["a", "c"]
    assert normals.set_index("station_id").loc["c", "normal_mm"] == pytest.approx(100.0)


def test_station_index_median_pct_mean_z_and_minimum_count():
    table = pd.concat([station_rows("a", "R", [100.0, 200.0]),
                       station_rows("b", "R", [5.0, 10.0]),      # normal under 10 mm
                       station_rows("c", "R", [300.0, 100.0]),
                       station_rows("d", "Q", [1.0, 3.0])])
    normals = stations.station_normals(table, years=(1991, 1992), min_years=2)
    idx = stations.station_index(table, normals, min_stations=2, min_normal_mm=10)
    r = idx[idx["region"] == "R"].set_index("year")
    # % of normal: a 100/150, c 300/200 -> median of 66.7 and 150 (b excluded)
    assert r.loc[1991, "station_swe_pct"] == pytest.approx((100 / 150 * 100 + 150) / 2)
    assert r.loc[1991, "n_stations_pct"] == 2 and r.loc[1991, "n_stations"] == 3
    # z: each station's first year is one SD below or above its mean
    sd = np.std([100, 200], ddof=1)
    expected = np.mean([(100 - 150) / sd, (5 - 7.5) / np.std([5, 10], ddof=1),
                        (300 - 200) / np.std([300, 100], ddof=1)])
    assert r.loc[1991, "station_swe_z"] == pytest.approx(expected)
    q = idx[idx["region"] == "Q"].set_index("year")
    assert q["station_swe_z"].isna().all() and q["station_swe_pct"].isna().all()


def test_anomalies_against_normal_years():
    years = pd.Series([1990, 1991, 1992])
    pct, z = stations.anomalies(pd.Series([50.0, 100.0, 300.0]), years, normal_years=(1991, 1992))
    assert list(pct.round(6)) == [25.0, 50.0, 150.0]
    assert z.iloc[2] == pytest.approx((300 - 200) / np.std([100, 300], ddof=1))


def test_compare_era5_keeps_every_era5_year():
    era5 = pd.DataFrame({"region": "R", "year": [1991, 1992, 1993], "winter": "w",
                         "swe_apr1_mm": [100.0, 200.0, 300.0], "enso_index": "ONI",
                         "enso_djf": 0.0, "phase": "neutral", "strong": False})
    index = pd.DataFrame({"region": ["R"], "year": [1992], "n_stations": [5],
                          "station_swe_z": [0.1], "n_stations_pct": [5],
                          "station_swe_pct": [90.0]})
    out = stations.compare_era5(index, era5)
    assert list(out["year"]) == [1991, 1992, 1993]
    assert list(out["n_stations"]) == [0, 5, 0]
    assert out["station_swe_pct"].isna().sum() == 2


def test_effects_by_group_splits_stations_and_measures_differences():
    years = [2000, 2001, 2002, 2003]
    enso = pd.DataFrame({"year": years, "phase": ["el_nino", "neutral", "neutral", "el_nino"],
                         "strong": [True, False, False, False]})
    low = [station_rows(f"l{i}", "R", [50.0, 100.0, 100.0, 150.0], start=2000) for i in range(2)]
    high = [station_rows(f"h{i}", "R", [100.0] * 4, start=2000) for i in range(2)]
    table = pd.concat(low + high)
    table["elevation"] = table["station_id"].map({"l0": 500, "l1": 600, "h0": 2000, "h1": 2100})
    normals = stations.station_normals(table, years=(2000, 2003), min_years=4)
    out = stations.effects_by_group(table, normals, enso, groups=2).set_index("group")
    # low: % = 50, 100, 100, 150; El Nino mean 100, neutral 100; strong 50 - mean 100
    assert out.loc[1, "nino_minus_neutral"] == pytest.approx(0.0)
    assert out.loc[1, "strong_minus_all"] == pytest.approx(-50.0)
    assert out.loc[2, "strong_minus_all"] == pytest.approx(0.0)
    assert list(out["stations"]) == [2, 2]
