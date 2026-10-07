"""Tests for src/snow_soil.py on synthetic monthly grids with known answers."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from src import snow_soil
from src.era5 import LAT, LON, TIME


def grid(values_per_cell, start="2000-01-01", lats=(50.0, 60.0)):
    """Monthly field (time, lat, lon=1); `values_per_cell[i]` is a 1-D series."""
    data = np.stack(values_per_cell, axis=1)[:, :, None]
    time = pd.date_range(start, periods=data.shape[0], freq="MS")
    return xr.DataArray(data, dims=[TIME, LAT, LON],
                        coords={TIME: time, LAT: list(lats), LON: [-120.0]})


def mask_all(da):
    m = xr.ones_like(da.isel({TIME: 0}), dtype=bool).drop_vars(TIME)
    return m.expand_dims(region=["R"])


def test_snowfall_fraction_is_ratio_of_regional_totals_nov_to_mar():
    n = 24  # 2000-01 to 2001-12: one complete Nov-Mar season, labelled 2001
    months = np.tile(np.arange(1, 13), 2)
    cold = np.where(np.isin(months, [11, 12, 1, 2, 3]), 10.0, 0.0)    # all snow
    tp_cold = np.where(np.isin(months, [11, 12, 1, 2, 3]), 10.0, 5.0)
    wet = np.where(np.isin(months, [11, 12, 1, 2, 3]), 20.0, 0.0)      # snow 20 of 100
    tp_wet = np.where(np.isin(months, [11, 12, 1, 2, 3]), 100.0, 5.0)
    sf = grid([cold, wet])
    tp = grid([tp_cold, tp_wet])
    out = snow_soil.snowfall_fraction(sf, tp, mask_all(sf), months=(11, 12, 1, 2, 3))
    assert list(out["year"].values) == [2001]
    w = np.cos(np.deg2rad([50.0, 60.0]))
    sf_mean = (w[0] * 50 + w[1] * 100) / w.sum()
    tp_mean = (w[0] * 50 + w[1] * 500) / w.sum()
    frac = float(out["snowfall_frac"].sel(region="R", year=2001))
    assert frac == pytest.approx(sf_mean / tp_mean)
    # not the mean of per-cell fractions (1.0 and 0.2)
    assert frac != pytest.approx((w[0] * 1.0 + w[1] * 0.2) / w.sum())


def test_soil_moisture_depth_weighted_jja_mean():
    months = np.arange(1, 13)
    l1 = np.where(np.isin(months, [6, 7, 8]), 0.10, 0.40)
    l2 = np.where(np.isin(months, [6, 7, 8]), 0.30, 0.40)
    ds = xr.Dataset({"swvl1": grid([l1, l1]), "swvl2": grid([l2, l2])})
    out = snow_soil.soil_moisture(ds, mask_all(ds["swvl1"]), months=(6, 7, 8),
                                  weights={"swvl1": 0.25, "swvl2": 0.75})
    assert float(out.sel(region="R", year=2000)) == pytest.approx(0.25 * 0.10 + 0.75 * 0.30)


def test_soil_moisture_drops_incomplete_season():
    months = np.arange(1, 8)  # Jan-Jul only: no complete JJA
    ds = xr.Dataset({"swvl1": grid([np.full(7, 0.2)] * 2), "swvl2": grid([np.full(7, 0.2)] * 2)})
    out = snow_soil.soil_moisture(ds, mask_all(ds["swvl1"]), months=(6, 7, 8))
    assert out.sizes["year"] == 0


def test_snow_soil_table_left_join_raises_on_a_year_without_enso():
    cols = ("snowfall_frac", "sf_season_mm", "tp_season_mm", "soil_moisture")
    regional = xr.Dataset({c: (("region", "year"), np.ones((1, 4))) for c in cols},
                          coords={"region": ["R"], "year": [1950, 1951, 1952, 1953]})
    winters = pd.DataFrame({"year": [1951, 1952], "winter": ["1950-1951", "1951-1952"],
                            "enso_index": "RONI", "enso_djf": 0.0, "phase": "neutral",
                            "strong": False})
    gap = winters.assign(year=[1951, 1953], winter=["1950-1951", "1952-1953"])
    with pytest.raises(ValueError, match=r"year\(s\) \[1952\]"):  # a gap inside the record
        snow_soil.snow_soil_table(regional, gap)
    pending = snow_soil.snow_soil_table(regional, winters)  # 1953 not yet published
    assert pending.loc[pending["year"] == 1953, "phase"].isna().all()
    table = snow_soil.snow_soil_table(regional.sel(year=[1950, 1951, 1952]), winters)
    assert list(table["year"]) == [1951, 1952]              # 1950 precedes the first winter
