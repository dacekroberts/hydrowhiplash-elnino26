"""Tests for src/prediction.py on synthetic region x year tables: no
committed table and no data/ is read."""
import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf

from src import prediction
from src.config import PRED_GROUPS, PRED_RIDGE_GRID, REGIONS

PREDICTORS = ("a", "b")
REGION_SET = ("N", "S", "W")


def synthetic(effect=(1.0, -0.5), noise=0.5, seed=0, years=range(1984, 2026),
              regions=REGION_SET) -> pd.DataFrame:
    """log_burn = region level + region trend + effect . predictors + noise;
    the predictors are correlated with each other."""
    rng = np.random.default_rng(seed)
    rows = []
    for i, region in enumerate(regions):
        for year in years:
            a = rng.normal()
            b = 0.6 * a + rng.normal()
            rows.append({"region": region, "year": year, "a": a, "b": b,
                         "log_burn": 8 + i + 0.02 * (i + 1) * (year - 2000)
                                     + effect[0] * a + effect[1] * b + rng.normal(0, noise)})
    return pd.DataFrame(rows)


def test_no_penalty_equals_ols_with_region_levels_and_trends():
    df = synthetic()
    train, new = df[df["year"] < 2020], df[df["year"] == 2020]
    fit = smf.ols("log_burn ~ C(region) + C(region):year + a_s + b_s", data=_std(train)).fit()
    expected = fit.predict(_std(train, new)).to_numpy()
    model = prediction.fit_pooled_ridge(train, PREDICTORS, penalty=0.0)
    assert np.allclose(prediction.predict(model, new), expected)
    assert np.allclose(model["beta"], [fit.params["a_s"], fit.params["b_s"]])


def _std(train, new=None):
    """`new` (default `train`) with a_s, b_s standardised on train per region."""
    out = (train if new is None else new).copy()
    stats = train.groupby("region")[list(PREDICTORS)].agg(["mean", "std"])
    for col in PREDICTORS:
        out[col + "_s"] = ((out[col] - out["region"].map(stats[(col, "mean")]))
                           / out["region"].map(stats[(col, "std")]))
    return out


def test_penalised_fit_equals_the_direct_solution():
    """Taking the level and trend out first equals solving the full design
    with the penalty on the predictor columns only."""
    train = synthetic(seed=1)
    penalty = 0.3
    s = _std(train)
    dummies = pd.get_dummies(s["region"]).to_numpy(dtype=float)
    design = np.column_stack([dummies, dummies * (s[["year"]].to_numpy() - 2000),
                              s[["a_s", "b_s"]].to_numpy()])
    weights = np.zeros(design.shape[1])
    weights[-2:] = penalty * len(s)
    direct = np.linalg.solve(design.T @ design + np.diag(weights), design.T @ s["log_burn"])
    model = prediction.fit_pooled_ridge(train, PREDICTORS, penalty=penalty)
    assert np.allclose(model["beta"], direct[-2:])


def test_infinite_penalty_is_the_per_region_trend():
    df = synthetic(seed=2)
    train, new = df[df["year"] < 2015], df[df["year"] == 2015]
    model = prediction.fit_pooled_ridge(train, PREDICTORS, penalty=np.inf)
    for (_, row), got in zip(new.iterrows(), prediction.predict(model, new)):
        fit = smf.ols("log_burn ~ year", data=train[train["region"] == row["region"]]).fit()
        assert got == pytest.approx(fit.predict(pd.DataFrame({"year": [2015]}))[0])
        assert model["spread"][row["region"]] == pytest.approx(np.sqrt(fit.mse_resid))


def test_largest_grid_penalty_is_close_to_the_trend():
    df = synthetic(seed=3)
    train, new = df[df["year"] < 2015], df[df["year"] == 2015]
    heavy = prediction.predict(prediction.fit_pooled_ridge(train, PREDICTORS,
                                                           max(PRED_RIDGE_GRID)), new)
    trend = prediction.predict(prediction.fit_pooled_ridge(train, PREDICTORS, np.inf), new)
    assert np.max(np.abs(heavy - trend)) < 0.01


def test_grid_and_groups():
    assert len(PRED_RIDGE_GRID) == 13
    assert PRED_RIDGE_GRID[0] == pytest.approx(0.01)
    assert PRED_RIDGE_GRID[-1] == pytest.approx(1000)
    assert set(PRED_GROUPS["AK and YT"]) == {"AK", "YT"}
    assert set(PRED_GROUPS["AK and YT"]) | set(PRED_GROUPS["other five"]) == set(REGIONS)


def test_choose_penalty_light_with_signal_heavy_without():
    light, _ = prediction.choose_penalty(synthetic(effect=(1.5, -1.0), noise=0.3), PREDICTORS)
    heavy, mse = prediction.choose_penalty(synthetic(effect=(0, 0), noise=1.0, seed=5),
                                           PREDICTORS)
    assert light < 1 < heavy
    assert len(mse) == len(PRED_RIDGE_GRID)


def test_expanding_forecast_never_reads_the_predicted_year_or_later():
    df = synthetic(seed=4)
    pred, coefs = prediction.expanding_forecast(df, PREDICTORS)
    changed = df.copy()
    late = changed["year"] >= 2015
    changed.loc[late, "log_burn"] += 50
    changed.loc[late, ["a", "b"]] *= -3
    pred2, coefs2 = prediction.expanding_forecast(changed, PREDICTORS)
    early = pred["year"] < 2015
    cols = ["predicted", "pi_low", "pi_high", "cut", "p_yes", "predicted_trend", "penalty"]
    pd.testing.assert_frame_equal(pred.loc[early, cols], pred2.loc[early, cols])
    # the 2015 prediction reads 2015's predictors but not its outcome
    at = (pred["year"] == 2015).to_numpy()
    assert np.allclose(pred.loc[at, "predicted_trend"], pred2.loc[at, "predicted_trend"])
    assert coefs.loc[coefs["year"] <= 2015].equals(coefs2.loc[coefs2["year"] <= 2015])


def test_expanding_forecast_shape_and_first_year():
    df = synthetic(seed=6)
    df = df[~((df["region"] == "W") & (df["year"] == 2025))]  # one region ends a year early
    pred, coefs = prediction.expanding_forecast(df, PREDICTORS)
    assert pred["year"].min() == 2004 and (pred["n_train"] >= 20).all()
    assert len(pred) == 22 * 3 - 1
    assert list(coefs["year"]) == list(range(2004, 2026))
    assert not pred.duplicated(["region", "year"]).any()
    assert ((pred["p_yes"] >= 0) & (pred["p_yes"] <= 1)).all()
    assert (pred["actual_yes"] == (pred["actual"] > pred["cut"])).all()


def test_cut_is_the_training_quantile():
    df = synthetic(seed=7)
    pred, _ = prediction.expanding_forecast(df, PREDICTORS)
    row = pred[(pred["region"] == "S") & (pred["year"] == 2010)].iloc[0]
    train = df[(df["region"] == "S") & (df["year"] < 2010)]
    assert row["cut"] == pytest.approx(train["log_burn"].quantile(2 / 3))


def test_real_signal_gives_skill_and_honest_intervals():
    pred = pd.concat([prediction.expanding_forecast(synthetic(seed=s), PREDICTORS)[0]
                      for s in range(4)])
    scores = prediction.skill_scores(pred)
    assert scores["skill"] > 0.3
    assert 0.70 < scores["coverage"] < 0.90
    assert scores["bss_trend"] > 0 and scores["bss_base"] > 0
    assert scores["hits"] + scores["false_alarms"] == scores["n_called"]


def test_no_signal_gives_no_skill_and_fails_the_rule():
    df = synthetic(effect=(0, 0), noise=1.0, seed=8)
    pred, _ = prediction.expanding_forecast(df, PREDICTORS)
    table = prediction.skill_table(pred, groups={"all seven": REGION_SET}, n_boot=500)
    row = table.set_index("scope").loc["all seven"]
    assert abs(row["skill"]) < 0.05
    assert row["skill_low"] <= row["skill"] <= row["skill_high"]
    assert not prediction.beats_trend(table)
    assert list(table["scope"]) == ["all seven", *sorted(REGION_SET)]


def test_rule_passes_with_signal():
    pred, _ = prediction.expanding_forecast(synthetic(seed=9), PREDICTORS)
    assert prediction.beats_trend(
        prediction.skill_table(pred, groups={"all seven": REGION_SET}, n_boot=500))


def test_skill_scores_by_hand():
    pred = pd.DataFrame({"year": [1, 2], "actual": [1.0, 3.0], "predicted": [1.0, 2.0],
                         "predicted_trend": [3.0, 3.0], "covered": [True, False],
                         "covered_trend": [True, True], "actual_yes": [False, True],
                         "p_yes": [0.2, 0.9], "p_yes_trend": [0.5, 0.5]})
    s = prediction.skill_scores(pred, top_share=1 / 3)
    assert s["rmse"] == pytest.approx(np.sqrt(0.5))
    assert s["rmse_trend"] == pytest.approx(np.sqrt(2.0))
    assert s["skill"] == pytest.approx(0.5)
    assert s["brier"] == pytest.approx((0.04 + 0.01) / 2)
    assert s["brier_base"] == pytest.approx((1 / 9 + 4 / 9) / 2)
    assert s["bss_trend"] == pytest.approx(1 - 0.025 / 0.25)
    assert (s["n_yes"], s["n_called"], s["hits"], s["false_alarms"]) == (1, 1, 1, 0)
    assert s["coverage"] == 0.5


def test_bootstrap_is_seeded_and_resamples_whole_years():
    pred, _ = prediction.expanding_forecast(synthetic(seed=10), PREDICTORS)
    one = prediction.bootstrap_skill(pred, n_boot=300, seed=1)
    assert one == prediction.bootstrap_skill(pred, n_boot=300, seed=1)
    assert one != prediction.bootstrap_skill(pred, n_boot=300, seed=2)
    single = pred[pred["year"] == 2010]  # one year: every draw is the same year
    flat = prediction.bootstrap_skill(single, n_boot=50)
    assert flat["skill_low"] == pytest.approx(flat["skill_high"])
    assert flat["skill_low"] == pytest.approx(prediction.skill_scores(single)["skill"])


def _tables(swe_socal=np.nan):
    rows = [{"region": r, "year": y} for r in REGIONS for y in (1984, 1985)]
    base = pd.DataFrame(rows)
    fire = base.assign(log_burn=10.0, zero_fire=False, enso_djf=0.1, phase="neutral")
    controls = base.assign(temp_jja=15.0, precip_anom_lag0=0.0, precip_anom_lag1=0.0,
                           precip_octmar_mm=500.0)
    swe = base.assign(era5_swe_z=0.3, station_swe_z=0.2)
    swe.loc[swe["region"] == "SoCal", "era5_swe_z"] = swe_socal
    spei = base.assign(spei3_djf=-0.2)
    return fire, controls, swe, spei


def test_prediction_frame_sets_no_snow_region_to_zero():
    frame = prediction.prediction_frame(*_tables())
    assert (frame.loc[frame["region"] == "SoCal", "swe_z"] == 0).all()
    assert (frame.loc[frame["region"] != "SoCal", "swe_z"] == 0.3).all()
    assert len(frame) == 14 and not frame.isna().any().any()


def test_prediction_frame_refuses_surprises():
    with pytest.raises(ValueError, match="no-snow"):
        prediction.prediction_frame(*_tables(swe_socal=1.0))
    fire, controls, swe, spei = _tables()
    spei.loc[0, "spei3_djf"] = np.nan
    with pytest.raises(ValueError, match="spei3_djf"):
        prediction.prediction_frame(fire, controls, swe, spei)


def test_runs_are_labelled_and_the_forecast_run_has_no_summer_predictor():
    frame = prediction.prediction_frame(*_tables())
    frame.loc[0, "zero_fire"] = True
    runs = prediction.runs(frame)
    assert set(runs) == {"", "hindsight", "no_zero_fire"}
    assert "temp_jja" not in runs[""][1] and "temp_jja" not in runs["no_zero_fire"][1]
    assert "temp_jja" in runs["hindsight"][1]
    assert len(runs["no_zero_fire"][0]) == len(frame) - 1
