"""Tests for src/era5.py on small synthetic grids with known answers."""
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely.geometry import box

from src import era5


def monthly(values, start="1950-01-01", lat=(45.0,), lon=(-120.0,), name="tp"):
    """Monthly DataArray (valid_time, latitude, longitude) from a 1-D series."""
    values = np.asarray(values, dtype="float64")
    time = pd.date_range(start, periods=len(values), freq="MS")
    data = np.broadcast_to(values[:, None, None], (len(values), len(lat), len(lon))).copy()
    return xr.DataArray(data, name=name, dims=[era5.TIME, era5.LAT, era5.LON],
                        coords={era5.TIME: time, era5.LAT: list(lat), era5.LON: list(lon)})


def test_precip_m_per_day_to_mm_per_month_with_leap_years():
    # 1 mm/day (0.001 m/day) for Jan-Mar of 2000 (leap) and 2001.
    tp = monthly([0.001] * 15, start="2000-01-01")
    mm = era5.convert_units(tp.to_dataset())["tp"].sel(latitude=45, longitude=-120)
    assert mm.sel(valid_time="2000-01-01").item() == pytest.approx(31)
    assert mm.sel(valid_time="2000-02-01").item() == pytest.approx(29)
    assert mm.sel(valid_time="2001-02-01").item() == pytest.approx(28)
    assert mm.sel(valid_time="2000-04-01").item() == pytest.approx(30)
    assert mm.attrs["units"] == "mm/month"


def test_temperature_and_swe_units():
    ds = xr.Dataset({"t2m": monthly([273.15, 300.0]), "sd": monthly([-7e-25, 0.25])})
    out = era5.convert_units(ds)
    assert out["t2m"].values.ravel() == pytest.approx([0.0, 26.85])
    # Tiny negative SWE is rounding noise, clipped to 0; 0.25 m -> 250 mm.
    assert out["sd"].values.ravel() == pytest.approx([0.0, 250.0])


def test_drop_grib_coords_and_snap_grid():
    da = monthly([1.0], lat=(35.499999999999645,), lon=(-120.00000000001,))
    ds = da.to_dataset().assign_coords(expver=(era5.TIME, ["0001"]), number=0)
    out = era5.snap_grid(era5.drop_grib_coords(ds))
    assert "expver" not in out.variables and "number" not in out.variables
    assert out[era5.LAT].item() == 35.5 and out[era5.LON].item() == -120.0
    # Files without the leftovers pass through unchanged.
    assert set(era5.drop_grib_coords(da.to_dataset()).variables) == set(da.to_dataset().variables)


def test_winter_total_pairs_december_with_following_year():
    # Value = year * 100 + month, Jan 1950 to Dec 1952, so each sum is traceable.
    time = pd.date_range("1950-01-01", "1952-12-01", freq="MS")
    tp = monthly(time.year * 100 + time.month)
    total = era5.winter_total(tp, months=(12, 1, 2))
    # Winter 1950 lacks Dec 1949 and winter 1953 lacks Jan/Feb 1953: both dropped.
    assert list(total["year"].values) == [1951, 1952]
    assert total.sel(year=1951).item() == 195012 + 195101 + 195102
    assert total.sel(year=1952).item() == 195112 + 195201 + 195202


def test_winter_total_other_seasons():
    time = pd.date_range("1950-01-01", "1951-12-01", freq="MS")
    tp = monthly(np.ones(len(time)))
    # Oct-Mar crosses the new year: only 1951 (Oct 1950 to Mar 1951) is complete.
    ondjfm = era5.winter_total(tp, months=(10, 11, 12, 1, 2, 3))
    assert list(ondjfm["year"].values) == [1951]
    assert ondjfm.item() == 6
    # JJA does not cross the year: both summers complete.
    jja = era5.winter_total(tp, months=(6, 7, 8))
    assert list(jja["year"].values) == [1950, 1951]


def test_winter_total_keeps_ocean_nan():
    time = pd.date_range("1950-01-01", "1951-12-01", freq="MS")
    tp = monthly(np.ones(len(time)), lon=(-125.0, -120.0))
    tp[:, :, 0] = np.nan  # ocean cell
    total = era5.winter_total(tp, months=(12, 1, 2))
    assert np.isnan(total.sel(longitude=-125.0).item())
    assert total.sel(longitude=-120.0).item() == 3


def grid(lat, lon):
    return xr.Dataset(coords={era5.LAT: lat, era5.LON: lon})


def test_region_masks_cell_centres_and_shared_edge():
    # Two boxes split at 35.5, where a row of cell centres sits exactly on the
    # shared edge (as with CA_SPLIT_LAT on the ERA5 grid).
    regions = gpd.GeoDataFrame(
        {"region": ["North", "South"]},
        geometry=[box(-121, 35.5, -119, 37), box(-121, 34, -119, 35.5)], crs="EPSG:4326")
    lat = np.round(np.arange(37.5, 33.45, -0.1), 4)
    lon = np.round(np.arange(-121.5, -118.45, 0.1), 4)
    mask = era5.region_masks(regions, grid(lat, lon))
    assert list(mask["region"].values) == ["North", "South"]
    edge = mask.sel(latitude=35.5, longitude=-120.0)
    assert int(edge.sum()) == 1  # in exactly one region, never both or neither
    assert bool(mask.sel(region="North", latitude=36.0, longitude=-120.0))
    assert bool(mask.sel(region="South", latitude=35.0, longitude=-120.0))
    assert not bool(mask.sel(latitude=36.0, longitude=-121.5).any())  # outside both


def test_regional_series_weights_by_latitude():
    regions = gpd.GeoDataFrame({"region": ["R"]}, geometry=[box(-1, -1, 1, 61)],
                               crs="EPSG:4326")
    da = xr.DataArray([[1.0], [3.0]], dims=[era5.LAT, era5.LON],
                      coords={era5.LAT: [0.0, 60.0], era5.LON: [0.0]})
    masks = era5.region_masks(regions, da)
    out = era5.regional_series(da, masks)
    # cos(0) = 1, cos(60) = 0.5 -> (1 * 1 + 3 * 0.5) / 1.5
    assert out.sel(region="R").item() == pytest.approx(2.5 / 1.5)


def test_winter_precip_table_is_tidy_with_every_phase():
    time = pd.date_range("1950-01-01", "1952-12-01", freq="MS")
    # 1 mm/day everywhere: DJF 1951 = 31 + 31 + 28 = 90 mm; DJF 1952 (leap) = 91 mm.
    ds = xr.Dataset({"tp": monthly(np.ones(len(time)), lat=(36.0, 34.0))})
    ds = era5.convert_units(xr.Dataset({"tp": ds["tp"] * 0.001}))
    regions = gpd.GeoDataFrame({"region": ["North", "South"]},
                               geometry=[box(-121, 35, -119, 37), box(-121, 33, -119, 35)],
                               crs="EPSG:4326")
    winters = pd.DataFrame({"year": [1951, 1952], "winter": ["1950-1951", "1951-1952"],
                            "enso_djf": [-0.66, 0.52], "phase": ["la_nina", "el_nino"],
                            "strong": [False, False]})
    table = era5.winter_precip_table(ds, era5.region_masks(regions, ds), winters)
    assert len(table) == 4
    assert set(table["phase"]) == {"la_nina", "el_nino"}
    north = table[table["region"] == "North"].set_index("year")["precip_djf_mm"]
    assert north[1951] == pytest.approx(90) and north[1952] == pytest.approx(91)


def test_open_era5_combines_files(tmp_path):
    for year, expver in [(1950, "0001"), (1951, "0005")]:
        da = monthly(np.full(12, 0.001), start=f"{year}-01-01",
                     lat=(45.000000000001, 44.9), lon=(-120.0, -119.9))
        ds = da.to_dataset().assign_coords(expver=(era5.TIME, [expver] * 12), number=0)
        ds.to_netcdf(tmp_path / f"era5_land_{year}.nc")
    ds = era5.open_era5(tmp_path)
    assert ds.sizes[era5.TIME] == 24
    assert "expver" not in ds.variables
    assert 45.0 in ds[era5.LAT].values
    assert ds["tp"].sel(valid_time="1951-02-01").values.ravel() == pytest.approx(28)


def test_assign_domains_picks_containing_box():
    regions = gpd.GeoDataFrame(
        {"region": ["South", "North", "Edge", "Outside"]},
        geometry=[box(-120, 40, -115, 45), box(-150, 62, -140, 65),
                  box(-169, 55, -160, 60), box(-175, 55, -160, 60)], crs="EPSG:4326")
    with pytest.raises(ValueError, match="Outside"):
        era5.assign_domains(regions)
    domains = era5.assign_domains(regions.iloc[:3])
    assert domains.to_dict() == {"South": "main", "North": "north", "Edge": "north"}
