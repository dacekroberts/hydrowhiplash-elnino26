"""Tests for src/whiplash.py on synthetic data with known answers."""
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from src import whiplash
from src.config import SPEI_CLIP
from src.era5 import LAT, LON, TIME


def grid(values, start="1950-01-01", lat=(45.0,), lon=(-120.0,)):
    """Monthly DataArray (valid_time, latitude, longitude); values (time,) or (time, lat, lon)."""
    values = np.asarray(values, dtype="float64")
    time = pd.date_range(start, periods=values.shape[0], freq="MS")
    if values.ndim == 1:
        values = np.broadcast_to(values[:, None, None],
                                 (len(time), len(lat), len(lon))).copy()
    return xr.DataArray(values, dims=[TIME, LAT, LON],
                        coords={TIME: time, LAT: list(lat), LON: list(lon)})


def seasonal_temperature(n_years=3):
    months = np.tile(np.arange(1, 13), n_years)
    return 5 - 15 * np.cos(2 * np.pi * (months - 1) / 12)  # -10 in Jan, +20 in Jul


def test_thornthwaite_zero_below_freezing_positive_in_summer():
    t = grid(seasonal_temperature(), lat=(50.0,))
    pet = whiplash.pet_thornthwaite(t).squeeze()
    cold = t.squeeze() <= 0
    assert (pet.where(cold, drop=True) == 0).all()
    jja = pet.sel({TIME: pet[TIME].dt.month.isin([6, 7, 8])})
    assert (jja > 1).all() and (jja < 8).all()  # mm/day, plausible at 50N
    assert pet.attrs["units"] == "mm/d"


def test_water_balance_converts_precip_back_to_mm_per_day():
    tp = grid([31.0, 28.0, 31.0])           # mm/month: 1 mm/day in Jan-Mar 1950
    pet = grid([0.25, 0.25, 0.25])
    wb = whiplash.water_balance(tp, pet).squeeze().values
    assert wb == pytest.approx([0.75, 0.75, 0.75])


@pytest.fixture(scope="module")
def synthetic_spei():
    """SPEI for 3 cells, 60 years of random water balance, calibrated on
    1951-2010 via a patched calibration window."""
    rng = np.random.default_rng(1)
    n = 60 * 12
    vals = rng.gamma(2.0, 1.0, size=(n, 1, 3)) - 1.5   # mm/day, some negative
    vals[5, 0, 0] = -40.0                                # one extreme month
    wb = grid(vals, start="1951-01-01", lon=(-121.0, -120.0, -119.0))
    keep = xr.ones_like(wb.isel({TIME: 0}, drop=True), dtype=bool)
    keep[0, 2] = False                                   # third cell not fitted
    mp = pytest.MonkeyPatch()
    mp.setattr(whiplash, "SPEI_CAL_YEARS", (1951, 2010))
    try:
        serial = whiplash.spei_cells(wb, keep=keep, workers=1, n_blocks=2)
    finally:
        mp.undo()
    return wb, keep, serial


def test_spei_is_standardised_and_clipped(synthetic_spei):
    _, _, spei = synthetic_spei
    fitted = spei.isel({LON: [0, 1]}).sel({TIME: slice("1951-03", None)})
    assert abs(float(fitted.mean())) < 0.1
    assert 0.85 < float(fitted.std()) < 1.15
    assert float(np.abs(fitted).max()) <= SPEI_CLIP
    assert np.isfinite(fitted.values).all()
    assert spei.dims == (TIME, LAT, LON) and spei.dtype == np.float32


def test_spei_skips_cells_not_kept(synthetic_spei):
    _, _, spei = synthetic_spei
    assert spei.isel({LON: 2}).isnull().all()


def test_spei_parallel_matches_serial(synthetic_spei):
    # Worker processes import the module afresh, so both runs use the default
    # calibration window rather than the fixture's patched one.
    wb, keep, _ = synthetic_spei
    a = whiplash.spei_cells(wb, keep=keep, workers=1, n_blocks=3)
    b = whiplash.spei_cells(wb, keep=keep, workers=2, n_blocks=3)
    xr.testing.assert_allclose(a, b)


def test_season_spei_labels_by_last_month():
    time = pd.date_range("1950-01-01", "1952-12-01", freq="MS")
    spei = grid(time.year * 100 + time.month)
    djf = whiplash.season_spei(spei, (12, 1, 2)).squeeze()
    jja = whiplash.season_spei(spei, (6, 7, 8)).squeeze()
    assert djf.sel(year=1951).item() == 195102   # winter 1950-51 ends Feb 1951
    assert jja.sel(year=1951).item() == 195108
    with pytest.raises(ValueError):
        whiplash.season_spei(spei, (12, 1))


def test_restandardise_uses_calibration_years_only():
    years = np.arange(1951, 2031)
    s = xr.DataArray(np.concatenate([np.tile([1.0, 3.0], 35), np.full(10, 10.0)]),
                     dims="year", coords={"year": years})
    z = whiplash.restandardise(s, (1951, 2020))
    cal = z.sel(year=slice(1951, 2020))
    assert float(cal.mean()) == pytest.approx(0, abs=1e-12)
    assert float(cal.std(ddof=1)) == pytest.approx(1)
    sd = np.std(np.tile([1.0, 3.0], 35), ddof=1)
    assert float(z.sel(year=2025)) == pytest.approx((10 - 2) / sd)


def test_whiplash_is_summer_minus_winter():
    # Wet winter (+1) to dry summer (-1) gives -2 after re-standardising
    # identical series; built so the cell mean equals the input.
    years = np.arange(1951, 2021)
    rng = np.random.default_rng(0)
    base = rng.normal(size=years.size)
    time = pd.date_range("1950-01-01", "2020-12-01", freq="MS")
    vals = np.full(time.size, np.nan)
    for i, y in enumerate(years):
        vals[(time.year == y) & (time.month == 2)] = base[i]
        vals[(time.year == y) & (time.month == 8)] = -base[i]
    spei = grid(vals)
    masks = xr.ones_like(spei.isel({TIME: 0}, drop=True), dtype=bool).expand_dims(
        region=["R"])
    out = whiplash.regional_spei(spei, masks).sel(region="R")
    z = (base - base.mean()) / base.std(ddof=1)
    assert out["spei3_djf"].sel(year=years).values == pytest.approx(z)
    assert out["whiplash"].sel(year=years).values == pytest.approx(-2 * z)
