"""Known-answer tests for src/climate_vars.py (temp_jja, temp_mam,
precip_anom; Phase 4 gate, D51). Synthetic grids only."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from src import climate_vars

TIME = "valid_time"


def grid(months=pd.date_range("1990-01-01", "1993-12-01", freq="MS")):
    """Two latitudes (0 and 60, so cos weights are 1 and 0.5) by two
    longitudes. t2m = month number + cell offset; tp = 10 mm/month in the
    southern row, 40 in the northern row."""
    lat = np.array([0.0, 60.0])
    lon = np.array([10.0, 11.0])
    m = months.month.to_numpy(dtype=float)
    offset = np.array([[0.0, 2.0], [4.0, 6.0]])
    t2m = m[:, None, None] + offset[None]
    tp = np.broadcast_to(np.array([[10.0, 10.0], [40.0, 40.0]])[None], t2m.shape).copy()
    ds = xr.Dataset({"t2m": ((TIME, "latitude", "longitude"), t2m),
                     "tp": ((TIME, "latitude", "longitude"), tp)},
                    coords={TIME: months, "latitude": lat, "longitude": lon})
    masks = xr.DataArray(np.ones((1, 2, 2), dtype=bool), dims=("region", "latitude", "longitude"),
                         coords={"region": ["R"], "latitude": lat, "longitude": lon})
    return ds, masks


def test_seasonal_temperature_and_octmar_total_by_hand():
    ds, masks = grid()
    out = climate_vars.climate_regional(ds, masks)
    # weights 1 (lat 0) and 0.5 (lat 60): cell offsets average to
    # (1 x (0 + 2) + 0.5 x (4 + 6)) / 3 = 7 / 3
    w_offset = 7 / 3
    assert np.allclose(out["temp_jja"].sel(region="R"), 7 + w_offset)  # mean of 6, 7, 8
    assert np.allclose(out["temp_mam"].sel(region="R"), 4 + w_offset)  # mean of 3, 4, 5
    # Oct-Mar: 6 months x (1 x 10 + 0.5 x 40) / 1.5 = 6 x 20 = 120 mm,
    # labelled by the March year; 1990's Oct-Mar is incomplete (no Oct-Dec 1989)
    octmar = out["precip_octmar_mm"].sel(region="R").dropna("year")
    assert list(octmar["year"].values) == [1991, 1992, 1993]
    assert np.allclose(octmar, 120.0)


def test_incomplete_summer_is_dropped():
    ds, masks = grid(pd.date_range("1990-01-01", "1991-07-01", freq="MS"))
    out = climate_vars.climate_regional(ds, masks)
    jja = out["temp_jja"].sel(region="R").dropna("year")
    assert list(jja["year"].values) == [1990]


def test_precip_anom_z_ddof1_and_lag1_by_year():
    years = np.arange(1988, 1996)
    table = pd.DataFrame({"region": "R", "year": years,
                          "precip_octmar_mm": [100.0, 120, 80, 110, 90, 130, 70, 100]})
    out = climate_vars.add_precip_anom(table, normal_years=(1989, 1993)).set_index("year")
    ref = np.array([120.0, 80, 110, 90])
    ref = np.append(ref, 130.0)  # 1989-1993 inclusive
    z94 = (70 - ref.mean()) / ref.std(ddof=1)
    assert out.loc[1994, "precip_anom_lag0"] == pytest.approx(z94)
    assert out.loc[1995, "precip_anom_lag1"] == pytest.approx(z94)
    assert np.isnan(out.loc[1988, "precip_anom_lag1"])
    # a missing year leaves the next lag1 empty instead of reaching back two winters
    gap = table[table["year"] != 1991]
    gapped = climate_vars.add_precip_anom(gap, normal_years=(1988, 1993)).set_index("year")
    assert np.isnan(gapped.loc[1992, "precip_anom_lag1"])


def test_precip_anom_per_region():
    table = pd.DataFrame({"region": ["A"] * 4 + ["B"] * 4, "year": list(range(1991, 1995)) * 2,
                          "precip_octmar_mm": [1.0, 2, 3, 4, 100, 200, 300, 400]})
    out = climate_vars.add_precip_anom(table, normal_years=(1991, 1994))
    a = out[out["region"] == "A"]["precip_anom_lag0"].to_numpy()
    b = out[out["region"] == "B"]["precip_anom_lag0"].to_numpy()
    assert np.allclose(a, b)  # same shape, different scale: same z
