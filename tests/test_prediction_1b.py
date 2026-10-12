"""Tests for src/prediction_1b.py on synthetic region x year tables: no
committed table and no data/ is read."""
import numpy as np
import pandas as pd
import pytest

from src import prediction, prediction_1b
from src.config import PRED_1B_GRID, PRED_1B_VARIANTS, PRED_PREDICTORS, REGIONS
from tests.test_prediction import _tables, synthetic

PREDICTORS = ("a", "b")
GRID = (0.01, 1.0, 1000.0)


def opposite(noise=0.5, seed=0, years=range(1984, 2026)) -> pd.DataFrame:
    """Predictor `a` raises log_burn in N and lowers it in S and W; region S
    swings ten times as widely as the others."""
    rng = np.random.default_rng(seed)
    rows = []
    for region, sign, size in (("N", 1.0, 1.0), ("S", -1.0, 10.0), ("W", -1.0, 1.0)):
        for year in years:
            a, b = rng.normal(size=2)
            rows.append({"region": region, "year": year, "a": a, "b": b,
                         "log_burn": 9 + 0.03 * (year - 2000)
                                     + size * (sign * a + rng.normal(0, noise))})
    return pd.DataFrame(rows)


def test_no_regional_departures_is_version_1():
    df = synthetic(seed=1)
    train, new = df[df["year"] < 2018], df[df["year"] == 2018]
    prep = prediction_1b._prepare(train, PREDICTORS, scaled=False)
    got = prediction_1b._predict(prep, prediction_1b._solve(prep, 0.3, np.inf), new)
    v1 = prediction.predict(prediction.fit_pooled_ridge(train, PREDICTORS, 0.3), new)
    assert np.allclose(got, v1)
    trend = prediction_1b._predict(prep, prediction_1b._solve(prep, np.inf, np.inf), new)
    assert np.allclose(trend, prediction.predict(
        prediction.fit_pooled_ridge(train, PREDICTORS, np.inf), new))


def test_partial_pooling_equals_the_direct_solution():
    """Minimise sum (y - x.(beta + delta_r))^2 + n*s*|beta|^2 + n*r*|delta|^2
    with scipy and compare."""
    from scipy.optimize import minimize
    train = opposite(seed=2, years=range(1984, 2010))
    prep = prediction_1b._prepare(train, PREDICTORS, scaled=False)
    shared, regional = 0.2, 0.05
    regions = list(prep["regions"])

    def loss(theta):
        beta, total = theta[:2], 0.0
        for k, region in enumerate(regions):
            rows = prep["regions"][region]["rows"]
            delta = theta[2 + 2 * k:4 + 2 * k]
            total += np.sum((prep["y"][rows] - prep["x"][rows] @ (beta + delta)) ** 2)
        n = len(prep["y"])
        return total + n * shared * beta @ beta + n * regional * theta[2:] @ theta[2:]

    best = minimize(loss, np.zeros(8), method="BFGS", options={"gtol": 1e-10}).x
    betas = prediction_1b._solve(prep, shared, regional)
    for k, region in enumerate(regions):
        assert np.allclose(betas[region], best[:2] + best[2 + 2 * k:4 + 2 * k], atol=1e-5)


def test_regional_coefficients_find_opposite_signs():
    train = opposite(seed=3)
    prep = prediction_1b._prepare(train, PREDICTORS, scaled=True)
    betas = prediction_1b._solve(prep, 1.0, 0.01)
    assert betas["N"][0] > 0.5 and betas["S"][0] < -0.5 and betas["W"][0] < -0.5
    shared_only = prediction_1b._solve(prep, 0.01, np.inf)
    assert shared_only["N"][0] == shared_only["S"][0]
    pair = prediction_1b.choose_penalties(train, PREDICTORS, True, True, GRID)
    assert np.isfinite(pair[1]) and pair[1] <= 1.0


def test_scaled_fit_does_not_depend_on_a_regions_units():
    """Multiplying one region's detrended swings by 10 multiplies its own
    predicted moves by 10 and leaves the penalties and other regions alone."""
    df = opposite(seed=4)
    big = df.copy()
    is_n = big["region"] == "N"
    trend = 9 + 0.03 * (big["year"] - 2000)
    big.loc[is_n, "log_burn"] = trend[is_n] + 10 * (big.loc[is_n, "log_burn"] - trend[is_n])
    train, new = df[df["year"] < 2020], df[df["year"] == 2020]
    train_b, new_b = big[big["year"] < 2020], big[big["year"] == 2020]
    assert (prediction_1b.choose_penalties(train, PREDICTORS, True, True, GRID)
            == prediction_1b.choose_penalties(train_b, PREDICTORS, True, True, GRID))
    one, two = (prediction_1b._prepare(t, PREDICTORS, True) for t in (train, train_b))
    moves = []
    for prep, rows in ((one, new), (two, new_b)):
        full = prediction_1b._predict(prep, prediction_1b._solve(prep, 0.1, 0.1), rows)
        base = prediction_1b._predict(prep, prediction_1b._solve(prep, np.inf, np.inf), rows)
        moves.append(full - base)
    ratio = moves[1] / moves[0]
    assert ratio[(new["region"] == "N").to_numpy()] == pytest.approx(10)
    assert ratio[(new["region"] != "N").to_numpy()] == pytest.approx(1)


def test_penalty_pairs():
    assert len(PRED_1B_GRID) == 7
    assert (PRED_1B_GRID[0], PRED_1B_GRID[-1]) == pytest.approx((0.01, 1000))
    assert len(prediction_1b.penalty_pairs()) == 7 * 8
    assert all(np.isinf(r) for _, r in prediction_1b.penalty_pairs(by_region=False))


@pytest.fixture(scope="module")
def forecast():
    df = opposite(seed=5)
    raw, coefs = prediction_1b.expanding_forecast(df, PREDICTORS, True, True, GRID)
    return df, raw, coefs


def test_expanding_forecast_shape(forecast):
    df, raw, coefs = forecast
    assert raw["year"].min() == 2004 and len(raw) == 22 * 3
    assert len(coefs) == 22 * 3 * 2
    assert set(coefs["predictor"]) == set(PREDICTORS)
    row = raw[(raw["region"] == "S") & (raw["year"] == 2012)].iloc[0]
    train = df[(df["region"] == "S") & (df["year"] < 2012)]
    fit = np.polyfit(train["year"], train["log_burn"], 1)
    resid = train["log_burn"] - np.polyval(fit, train["year"])
    assert row["predicted_trend"] == pytest.approx(np.polyval(fit, 2012))
    assert row["scale"] == pytest.approx(np.sqrt(np.sum(resid ** 2) / (len(train) - 2)))
    assert row["cut_above_trend"] == pytest.approx(np.quantile(resid, 2 / 3))


def test_expanding_forecast_never_reads_later_years(forecast):
    df, raw, _ = forecast
    changed = df.copy()
    changed.loc[changed["year"] >= 2012, "log_burn"] += 40
    raw2, _ = prediction_1b.expanding_forecast(changed[changed["year"] <= 2013], PREDICTORS,
                                               True, True, GRID)
    cols = ["predicted", "predicted_trend", "scale", "train_spread", "cut_above_trend",
            "penalty_shared", "penalty_region"]
    early, early2 = raw[raw["year"] <= 2012], raw2[raw2["year"] <= 2012]
    pd.testing.assert_frame_equal(early[cols].reset_index(drop=True),
                                  early2[cols].reset_index(drop=True))


def test_real_regional_signal_gives_skill_in_both_figures(forecast):
    _, raw, _ = forecast
    table = prediction_1b.skill_table(prediction_1b.add_intervals(raw),
                                      groups={"all seven": ("N", "S", "W")}, n_boot=300)
    row = table.set_index("scope").loc["all seven"]
    assert row["skill"] > 0.3 and row["skill_scaled"] > 0.3
    assert row["skill_scaled_low"] <= row["skill_scaled"] <= row["skill_scaled_high"]
    assert 0.65 < row["coverage"] < 0.95


def test_intervals_use_earlier_errors_only():
    years = range(2004, 2020)
    pred = pd.DataFrame({"region": "N", "year": list(years), "n_train": 20, "actual": 0.0,
                         "predicted": [float(k % 3) for k in range(16)],
                         "predicted_trend": 1.0, "scale": 5.0, "train_spread": 7.0,
                         "cut_above_trend": 0.5})
    out = prediction_1b.add_intervals(pred, min_past=4)
    assert list(out["spread_from"][:4]) == ["training"] * 4
    assert (out["spread"][:4] == 7.0).all() and (out["spread_trend"][:4] == 5.0).all()
    errors = -out["predicted"].to_numpy()
    assert out["spread"][4] == pytest.approx(np.sqrt(np.mean(errors[:4] ** 2)))
    assert out["spread"][10] == pytest.approx(np.sqrt(np.mean(errors[:10] ** 2)))
    assert out["spread_trend"][9] == pytest.approx(1.0)
    later = pred.copy()
    later.loc[12:, "actual"] = 99.0
    out2 = prediction_1b.add_intervals(later, min_past=4)
    assert out["spread"][:13].equals(out2["spread"][:13])
    assert not out["actual_yes"].any() and out2["actual_yes"][12:].all()
    assert ((out["p_yes"] > 0) & (out["p_yes"] < 1)).all()


def test_yes_rate_is_near_a_third_under_a_trend():
    """Version 1's bar sat under most later seasons when the outcome rises;
    a bar measured from the trend does not."""
    rates = []
    for seed in range(3):
        df = synthetic(effect=(0, 0), noise=1.0, seed=seed)
        df["log_burn"] += 0.15 * (df["year"] - 2000)
        raw, _ = prediction_1b.expanding_forecast(df, PREDICTORS, False, True, (1.0,))
        rates.append(prediction_1b.add_intervals(raw)["actual_yes"].mean())
    assert 0.2 < np.mean(rates) < 0.47


def test_rescore_v1_matches_and_refuses_a_different_trend():
    df = synthetic(seed=6)
    v1, _ = prediction.expanding_forecast(df, PREDICTORS, grid=(1.0,))
    raw, _ = prediction_1b.expanding_forecast(df, PREDICTORS, False, False, (1.0,))
    reference = prediction_1b.add_intervals(raw)
    rescored = prediction_1b.rescore_v1(v1, reference)
    assert np.allclose(rescored["predicted"], reference["predicted"])
    assert np.allclose(rescored["spread"], reference["spread"])
    assert (rescored["actual_yes"] == reference["actual_yes"]).all()
    wrong = reference.assign(predicted_trend=reference["predicted_trend"] + 1)
    with pytest.raises(ValueError, match="trend-only"):
        prediction_1b.rescore_v1(v1, wrong)


def test_variants_are_fixed_and_only_hindsight_reads_summer():
    assert list(PRED_1B_VARIANTS) == ["regions", "scaled", "regions_scaled", "spring_inputs",
                                      "june_update", "hindsight"]
    for name, (predictors, _, _) in PRED_1B_VARIANTS.items():
        assert ("temp_jja" in predictors) == (name == "hindsight")
        assert ("temp_mam" in predictors) == (name in ("june_update", "hindsight"))
        assert set(PRED_PREDICTORS) <= set(predictors)
    assert PRED_1B_VARIANTS["scaled"][1:] == (False, True)
    assert PRED_1B_VARIANTS["regions"][1:] == (True, False)


def test_frame_1b_adds_the_spring_inputs_and_refuses_gaps():
    fire, controls, swe, spei = _tables()
    controls = controls.assign(temp_mam=5.0)
    snow = controls[["region", "year"]].assign(snowfall_frac=0.4)
    frame = prediction_1b.frame_1b(fire, controls, swe, spei, snow)
    assert {"precip_anom_lag1", "temp_mam", "snowfall_frac", "swe_z"} <= set(frame.columns)
    assert len(frame) == 2 * len(REGIONS)
    with pytest.raises(ValueError, match="snowfall_frac"):
        prediction_1b.frame_1b(fire, controls, swe, spei, snow.iloc[1:])


def test_variants_table_keeps_every_variant():
    skill = pd.DataFrame({"scope": ["all seven", "AB"], "skill": [0.1, 0.2]})
    out = prediction_1b.variants_table({"one": skill, "two": skill})
    assert list(out["variant"]) == ["one", "two"] and list(out.columns)[0] == "variant"
