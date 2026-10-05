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
