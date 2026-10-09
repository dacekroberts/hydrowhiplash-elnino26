"""Tests for src/parks_gap.py and the parks_gap flag (D69); synthetic data."""
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from src.config import CRS_EQUAL_AREA
from src.fire import parks_gap
from src.parks_gap import park_pieces, start_month_outside, union_ha, whole_fire_area, with_park_area


def test_parks_gap_flags_only_the_configured_seasons():
    region = pd.Series(["AB", "AB", "AB", "BC", "AB"])
    year = pd.Series([2015, 2016, 2019, 2017, 2020])
    out = parks_gap(region, year, seasons={"AB": (2016, 2019)})
    assert out.tolist() == [False, True, True, False, False]


def nbac(rows):
    return gpd.GeoDataFrame(
        [{"GID": g, "ADMIN_NAME": a, "AG_SDATE": d, "HS_SDATE": None, "geometry": geom}
         for g, a, d, geom in rows], geometry="geometry", crs=CRS_EQUAL_AREA)


def test_park_pieces_floor_the_whole_fire_and_clip():
    # fire 1: 300 ha in the park + 300 ha in the province = 600 ha whole, kept;
    # fire 2: 300 ha in the park only, under the 405 ha floor, dropped.
    side = 1732.05  # metres; 300 ha square
    parts = whole_fire_area(nbac([
        ("2017_1", "PC", "2017-07-01", box(0, 0, side, side)),
        ("2017_1", "AB", "2017-07-01", box(side, 0, 2 * side, side)),
        ("2017_2", "PC", "2017-11-20", box(0, 5000, side, 5000 + side)),
    ]))
    assert parts.loc[0, "fire_ha"] == pytest.approx(600, rel=1e-4)
    region = gpd.GeoDataFrame({"region": ["AB"]},
                              geometry=[box(-1e5, -1e5, side / 2, 1e5)], crs=CRS_EQUAL_AREA)
    pieces = park_pieces(parts, region)
    assert pieces["GID"].tolist() == ["2017_1"]
    assert union_ha(pieces) == pytest.approx(150, rel=1e-4)   # clipped to the region
    late = park_pieces(parts, region, floor=0)
    assert start_month_outside(late, (4, 10)) == 1             # the November start


def test_with_park_area_adds_only_flagged_seasons():
    table = pd.DataFrame({"region": ["AB", "AB", "BC"], "year": [2017, 2020, 2017],
                          "burn_ha": [60000.0, 0.0, 1000.0], "log_burn": np.log1p([60000.0, 0, 1000]),
                          "zero_fire": [False, True, False], "enso_djf": [0.1, 0.2, 0.1]})
    parks = pd.DataFrame({"region": ["AB"], "year": [2017], "nbac_park_ha": [40000.0],
                          "n_nbac_park": [3]})
    out = with_park_area(table, parks)
    assert out["burn_ha"].tolist() == [100000.0, 0.0, 1000.0]
    assert out.loc[0, "log_burn"] == pytest.approx(np.log1p(100000))
    assert out["zero_fire"].tolist() == [False, True, False]
    assert out["n_nbac_park"].tolist() == [3, 0, 0]
    assert len(out) == len(table)
