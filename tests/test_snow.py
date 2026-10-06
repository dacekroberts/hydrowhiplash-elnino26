"""Tests for src/snow.py on synthetic SWE with known answers."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from src import snow
from src.era5 import LAT, LON, TIME


def monthly_cells(columns, start="1950-01-01"):
    """Monthly SWE (mm) for cells along longitude; `columns` is a list of 1-D series."""
    data = np.stack(columns, axis=1)[:, None, :]
    time = pd.date_range(start, periods=data.shape[0], freq="MS")
    return xr.DataArray(data, dims=[TIME, LAT, LON],
                        coords={TIME: time, LAT: [60.0],
                                LON: [-140.0 + i for i in range(len(columns))]})


def seasonal(n_years, peak=300.0, leftover=None):
    """Snow Nov-May, none Jun-Oct; `leftover[y]` mm left in summer of year y."""
    out = []
    for y in range(n_years):
        year = np.where(np.isin(np.arange(1, 13), [11, 12, 1, 2, 3, 4, 5]), peak, 0.0)
        if leftover is not None:
            year[5:10] = leftover[y]
        out.append(year)
    return np.concatenate(out)


def test_glacier_mask_flags_cap_and_perennial_cells():
    n = 10
    capped_once = seasonal(n)
    capped_once[3] = 10_000.0                               # one month at the cap
    cells = [
        np.full(12 * n, 10_000.0),                          # glacier at the cap
        np.full(12 * n, 5_000.0),                           # steady ~5 m, never capped
        seasonal(n),                                        # seasonal snow
        seasonal(n, leftover=[50.0] * 8 + [0.0] * 2),       # snow left in 8 of 10 years
        seasonal(n, leftover=[50.0] * 9 + [0.0]),           # snow left in 9 of 10 years
        capped_once,
        np.full(12 * n, np.nan),                            # ocean
    ]
    mask = snow.glacier_mask(monthly_cells(cells), years=(1950, 1959)).squeeze()
    assert mask.values.tolist() == [True, True, False, False, True, True, False]


def test_glacier_mask_uses_only_the_mask_years():
    late_glacier = np.concatenate([seasonal(10), np.full(24, 10_000.0)])  # capped after 1959
    mask = snow.glacier_mask(monthly_cells([late_glacier]), years=(1950, 1959))
    assert not mask.item()


def write_april1(tmp_path, values_m, years=(1950, 1951)):
    time = pd.to_datetime([f"{y}-04-01" for y in years])
    da = xr.DataArray(np.asarray(values_m, dtype="float32").reshape(len(years), 1, -1),
                      dims=[TIME, LAT, LON],
                      coords={TIME: time, LAT: [59.99999999999],
                              LON: [-140.0 + i for i in range(len(values_m[0]))]})
    ds = da.rename("sd").to_dataset().assign_coords(number=0)
    ds.to_netcdf(tmp_path / snow.APRIL1_FILE)


def test_open_april1_units_years_and_grid(tmp_path):
    write_april1(tmp_path, [[0.25, -1e-20], [0.5, 10.0]])
    sd = snow.open_april1(tmp_path)
    assert list(sd["year"].values) == [1950, 1951]
    assert sd[LAT].item() == 60.0                           # snapped
    assert sd.sel(year=1950).values.ravel() == pytest.approx([250.0, 0.0])
    assert sd.attrs["units"] == "mm" and "number" not in sd.coords


def test_open_april1_rejects_other_dates(tmp_path):
    da = xr.DataArray(np.zeros((1, 1, 1)), dims=[TIME, LAT, LON],
                      coords={TIME: pd.to_datetime(["1950-04-15"]), LAT: [60.0], LON: [-140.0]})
    da.rename("sd").to_dataset().to_netcdf(tmp_path / snow.APRIL1_FILE)
    with pytest.raises(ValueError):
        snow.open_april1(tmp_path)


def test_april1_regional_excludes_glacier_cells(tmp_path):
    write_april1(tmp_path, [[0.2, 10.0, 0.4], [0.1, 10.0, 0.3]])
    sd = snow.open_april1(tmp_path)
    masks = xr.ones_like(sd.isel(year=0, drop=True), dtype=bool).expand_dims(region=["R"])
    glacier = xr.DataArray([[False, True, False]], dims=[LAT, LON],
                           coords={LAT: sd[LAT], LON: sd[LON]})
    out = snow.april1_regional(sd, masks, glacier).sel(region="R")
    # Same latitude, so equal weights: mean of the two non-glacier cells.
    assert out["swe_apr1_mm"].values == pytest.approx([300.0, 200.0])
    assert out["swe_apr1_mm_all_cells"].values == pytest.approx([3533.33, 3466.67], rel=1e-4)
    assert snow.excluded_cells(masks, glacier).loc["R"] == 1


def test_glacier_mask_ignores_a_partial_year():
    # Nine complete years with snow left in 8 (8/9 is below the 0.9 rule), then
    # Jan-May of a tenth year: its minimum (300 mm) would make 9/10 if counted.
    nine = seasonal(9, leftover=[50.0] * 8 + [0.0])
    partial = np.full(5, 300.0)
    mask = snow.glacier_mask(monthly_cells([np.concatenate([nine, partial])]),
                             years=(1950, 1959))
    assert not mask.item()


def test_glacier_mask_needs_a_complete_year():
    with pytest.raises(ValueError, match="No complete year"):
        snow.glacier_mask(monthly_cells([np.full(5, 300.0)]), years=(1950, 1950))


def winters_table(years, index="RONI"):
    return pd.DataFrame({"year": years, "winter": [f"{y - 1}-{y}" for y in years],
                         "enso_index": index, "enso_djf": 0.0, "phase": "neutral",
                         "strong": False})


def april1_ds(years):
    return xr.Dataset({"swe_apr1_mm": (("region", "year"), np.ones((1, len(years)))),
                       "swe_apr1_mm_all_cells": (("region", "year"), np.ones((1, len(years))))},
                      coords={"region": ["R"], "year": list(years)})


def test_april1_table_drops_1950_and_keeps_one_enso_index():
    # April 1 1950 has no winter before it in ERA5-Land; ENSO winters start 1951.
    table = snow.april1_table(april1_ds([1950, 1951, 1952]), winters_table([1951, 1952]))
    assert list(table["year"]) == [1951, 1952]
    assert list(table.columns).count("enso_index") == 1
    assert set(table["enso_index"]) == {"RONI"}


def test_april1_table_raises_on_a_year_without_enso():
    with pytest.raises(ValueError, match=r"No RONI DJF value for year\(s\) \[1953\]"):
        snow.april1_table(april1_ds([1951, 1952, 1953]), winters_table([1951, 1952]))
