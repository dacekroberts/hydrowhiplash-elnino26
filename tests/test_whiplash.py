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


def test_thornthwaite_has_values_in_polar_day_and_night():
    # North of the polar circle xclim's day length is NaN in polar day and
    # night; the infill gives 24 h and 0 h, so every month has a PET value.
    t = grid(seasonal_temperature(), lat=(70.0,))
    pet = whiplash.pet_thornthwaite(t).squeeze()
    assert pet.notnull().all()
    june = pet.sel({TIME: pet[TIME].dt.month == 6})
    assert (june > 0).all()
    december = pet.sel({TIME: pet[TIME].dt.month == 12})
    assert (december == 0).all()


def test_thornthwaite_matches_the_1948_formula_with_a_climatological_heat_index():
    # Hand computation: I from the 1951-1952 monthly means, then
    # PET = 16 (L/12) (N/30) (10 T / I)^a mm/month, divided by N.
    from xclim.indices.helpers import day_lengths

    t = grid(seasonal_temperature(), lat=(45.0,))
    pet = whiplash.pet_thornthwaite(t, normal_years=(1951, 1952)).squeeze()
    temps = seasonal_temperature()
    normal = np.clip(temps[12:].reshape(2, 12).mean(axis=0), 0, None)
    heat = ((normal / 5) ** 1.514).sum()
    a = 6.75e-7 * heat**3 - 7.71e-5 * heat**2 + 0.01791 * heat + 0.49239
    july = pd.Timestamp("1951-07-01")
    days = xr.DataArray(pd.date_range("1951-07-01", "1951-07-31"), dims="time", name="time")
    hours = float(day_lengths(days, xr.DataArray(45.0, attrs={"units": "degrees_north"})).mean())
    expected_month = 16 * (hours / 12) * (31 / 30) * (10 * temps[18] / heat) ** a
    assert float(pet.sel({TIME: july})) == pytest.approx(expected_month / 31, rel=1e-9)


def test_thornthwaite_month_does_not_change_when_later_months_are_missing():
    # The heat index comes from the normal period, not the calendar year, so an
    # incomplete final year gets the same PET as a complete one (2026 audit).
    full = grid(seasonal_temperature(4), lat=(45.0,))
    partial = full.isel({TIME: slice(0, 12 * 3 + 2)})  # last year Jan-Feb only
    a = whiplash.pet_thornthwaite(full).isel({TIME: slice(0, 12 * 3 + 2)})
    b = whiplash.pet_thornthwaite(partial)
    np.testing.assert_allclose(a.values, b.values, rtol=1e-12)


def test_thornthwaite_is_zero_not_nan_where_the_normal_never_thaws():
    t = grid(np.full(36, -5.0), lat=(62.0,))
    t[18] = 3.0  # one warm month in a year of an always-frozen normal
    pet = whiplash.pet_thornthwaite(t).squeeze()
    assert pet.notnull().all() and (pet == 0).all()


def test_thornthwaite_needs_every_month_of_the_normal_period():
    t = grid(seasonal_temperature(), lat=(45.0,))
    with pytest.raises(ValueError, match="every calendar month"):
        whiplash.pet_thornthwaite(t, normal_years=(1990, 2000))


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


def test_restandardise_sorts_unsorted_years():
    years = np.arange(1951, 2031)
    s = xr.DataArray(np.concatenate([np.tile([1.0, 3.0], 35), np.full(10, 10.0)]),
                     dims="year", coords={"year": years})
    shuffled = s.isel(year=np.random.default_rng(1).permutation(len(years)))
    z = whiplash.restandardise(shuffled, (1951, 2020))
    assert list(z["year"].values) == list(years)
    xr.testing.assert_allclose(z, whiplash.restandardise(s, (1951, 2020)))


def test_restandardise_needs_two_calibration_values():
    s = xr.DataArray([1.0, 2.0, 3.0], dims="year", coords={"year": [2019, 2021, 2022]})
    with pytest.raises(ValueError, match="Fewer than 2 values"):
        whiplash.restandardise(s, (2018, 2020))


def test_whiplash_table_raises_on_a_year_without_enso():
    years = [1951, 1952, 1953]
    ones = (("region", "year"), np.ones((1, 3)))
    regional = xr.Dataset({name: ones for name in (
        "spei3_djf", "spei3_jja", "whiplash", "spei3_djf_cellmean", "spei3_jja_cellmean")},
        coords={"region": ["R"], "year": years})
    winters = pd.DataFrame({"year": [1951, 1952], "winter": ["1950-1951", "1951-1952"],
                            "enso_index": "RONI", "enso_djf": 0.0, "phase": "neutral",
                            "strong": False})
    gap = winters.assign(year=[1951, 1953], winter=["1950-1951", "1952-1953"])
    with pytest.raises(ValueError, match=r"year\(s\) \[1952\]"):  # a gap inside the record
        whiplash.whiplash_table(regional, gap)
    pending = whiplash.whiplash_table(regional, winters)  # 1953 not yet published
    assert pending.loc[pending["year"] == 1953, "enso_djf"].isna().all()
    table = whiplash.whiplash_table(regional.sel(year=[1951, 1952]), winters)
    assert list(table.columns).count("enso_index") == 1 and len(table) == 2
