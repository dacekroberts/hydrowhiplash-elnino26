"""Tests for src/geo.py: equal-area measurement and latitude weighting."""
import geopandas as gpd
import numpy as np
import pytest
import xarray as xr
from shapely.geometry import box

from src import geo


def test_area_ha_known_square():
    # A 10 km x 10 km square in the equal-area CRS is exactly 10,000 ha.
    gdf = gpd.GeoDataFrame(geometry=[box(0, 0, 10_000, 10_000)], crs="ESRI:102008")
    assert geo.area_ha(gdf).iloc[0] == pytest.approx(10_000, rel=1e-6)


def test_area_ha_shrinks_with_latitude():
    # Same 1-degree box: much smaller at 60N than at 32N.
    gdf = gpd.GeoDataFrame(
        geometry=[box(-120, 32, -119, 33), box(-120, 60, -119, 61)], crs="EPSG:4326")
    south, north = geo.area_ha(gdf)
    assert north / south == pytest.approx(np.cos(np.deg2rad(60.5)) / np.cos(np.deg2rad(32.5)),
                                          rel=0.02)


def test_area_ha_requires_crs():
    with pytest.raises(ValueError):
        geo.area_ha(gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)]))


def test_regional_mean_weights_by_latitude():
    lat = np.array([0.0, 60.0])
    lon = np.array([0.0, 1.0])
    da = xr.DataArray([[1.0, 1.0], [3.0, 3.0]],
                      coords={"latitude": lat, "longitude": lon},
                      dims=["latitude", "longitude"])
    mask = xr.ones_like(da, dtype=bool)
    # cos(0) = 1, cos(60) = 0.5 -> weighted mean = (1*1 + 3*0.5) / 1.5
    assert float(geo.regional_mean(da, mask)) == pytest.approx(2.5 / 1.5)


def test_regional_mean_respects_mask():
    da = xr.DataArray([[1.0, 100.0]], coords={"latitude": [45.0], "longitude": [0.0, 1.0]},
                      dims=["latitude", "longitude"])
    mask = xr.DataArray([[True, False]], coords=da.coords, dims=da.dims)
    assert float(geo.regional_mean(da, mask)) == pytest.approx(1.0)


def test_regional_mean_skips_missing_cells_inside_the_mask():
    # Ocean or glacier cells inside a region are NaN; the mean must re-weight
    # over the cells that hold data, not count the NaN cells as zero.
    lat = np.array([0.0, 60.0])
    lon = np.array([0.0, 1.0])
    da = xr.DataArray([[1.0, np.nan], [3.0, 3.0]],
                      coords={"latitude": lat, "longitude": lon},
                      dims=["latitude", "longitude"])
    mask = xr.ones_like(da, dtype=bool)
    # weights 1 (one cell at 0N) and 0.5 + 0.5 (two cells at 60N)
    assert float(geo.regional_mean(da, mask)) == pytest.approx((1 * 1 + 3 * 1) / 2)
