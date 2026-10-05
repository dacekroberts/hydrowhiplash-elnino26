"""Tests for src/stats.py using synthetic data with known effects.

Run from the repo root:  python -m pytest
Each test plants an effect of known size and checks the method recovers it
(or, for null data, doesn't invent one).
"""
import numpy as np
import pandas as pd
import pytest

from src import stats

YEARS = np.arange(1984, 2026)
N = len(YEARS)


@pytest.fixture
def synthetic():
    rng = np.random.default_rng(0)
    enso = rng.normal(0, 1, N)
    temp = rng.normal(0, 1, N)
    log_burn = 0.5 * enso + 0.4 * temp + 0.02 * (YEARS - 2000) + rng.normal(0, 0.5, N)
    return pd.DataFrame({"year": YEARS, "enso_djf": enso,
                         "temp_jja": temp, "log_burn": log_burn})


def test_permutation_detects_large_difference():
    rng = np.random.default_rng(1)
    in_group = np.zeros(N, dtype=bool)
    in_group[:12] = True
    values = rng.normal(0, 1, N) + 2.0 * in_group
    result = stats.permutation_test(values, in_group, n_perm=2000)
    assert result["p"] < 0.01
    assert result["diff"] > 1.0


def test_permutation_null_is_not_significant():
    rng = np.random.default_rng(2)
    in_group = np.zeros(N, dtype=bool)
    in_group[:12] = True
    values = rng.normal(0, 1, N)
    assert stats.permutation_test(values, in_group, n_perm=2000)["p"] > 0.05


def test_bootstrap_ci_contains_true_difference():
    rng = np.random.default_rng(3)
    in_group = np.zeros(N, dtype=bool)
    in_group[:12] = True
    values = rng.normal(0, 1, N) + 1.0 * in_group
    ci = stats.bootstrap_ci_diff(values, in_group, n_boot=2000)
    assert ci["ci_low"] < 1.0 < ci["ci_high"]


def test_hac_regression_recovers_coefficient(synthetic):
    fit = stats.fit_ols_hac("log_burn ~ enso_djf + temp_jja + year", synthetic)
    lo, hi = fit.conf_int().loc["enso_djf"]
    assert lo < 0.5 < hi
    assert fit.pvalues["enso_djf"] < 0.05


def test_interaction_recovers_regional_difference():
    rng = np.random.default_rng(4)
    enso = rng.normal(0, 1, N)
    frames = []
    for region, effect in [("SoCal", 0.0), ("PNW", 0.8)]:
        frames.append(pd.DataFrame({
            "year": YEARS, "region": region, "enso_djf": enso,
            "log_burn": effect * enso + rng.normal(0, 0.5, N)}))
    panel = pd.concat(frames, ignore_index=True)
    fit = stats.fit_pooled(
        "log_burn ~ enso_djf * C(region, Treatment('SoCal')) + C(region):year",
        panel)
    term = next(t for t in fit.params.index if t.startswith("enso_djf:"))
    lo, hi = fit.conf_int().loc[term]
    assert lo < 0.8 < hi
    assert fit.pvalues[term] < 0.05


def test_block_bootstrap_ci_contains_estimate(synthetic):
    def coef(d):
        return stats.smf.ols("log_burn ~ enso_djf + year", d).fit().params["enso_djf"]
    ci = stats.block_bootstrap_ci(synthetic, coef, n_boot=300)
    assert ci["ci_low"] < ci["estimate"] < ci["ci_high"]


def test_adjust_pvalues_holm():
    adjusted = stats.adjust_pvalues([0.01, 0.04, 0.03, 0.2], method="holm")
    assert np.allclose(adjusted, [0.04, 0.09, 0.09, 0.2])


def test_loyo_coverage_close_to_nominal(synthetic):
    result = stats.loyo_prediction("log_burn ~ enso_djf + temp_jja + year",
                                   synthetic, alpha=0.2)
    assert len(result) == N
    assert 0.65 <= result["covered"].mean() <= 0.95


def test_loyo_missing_outcome_is_not_counted_as_uncovered(synthetic):
    # A region-year with no outcome, or a year still to come, keeps its
    # prediction but has no coverage verdict; coverage counts the rest only.
    gaps = synthetic.copy()
    gaps.loc[[3, 10], "log_burn"] = np.nan
    result = stats.loyo_prediction("log_burn ~ enso_djf + temp_jja + year", gaps, alpha=0.2)
    missing = result["year"].isin(gaps.loc[[3, 10], "year"])
    assert result.loc[missing, "covered"].isna().all()
    assert result.loc[missing, "predicted"].notna().all()
    checked = result.loc[~missing]
    assert result["covered"].mean() == checked["covered"].astype(bool).mean()


def test_block_bootstrap_rejects_unsorted_or_repeated_years(synthetic):
    def mean(d):
        return d["log_burn"].mean()
    with pytest.raises(ValueError, match="sorted"):
        stats.block_bootstrap_ci(synthetic.iloc[::-1], mean, n_boot=10)
    repeated = pd.concat([synthetic, synthetic]).sort_values("year")
    with pytest.raises(ValueError, match="one row per"):
        stats.block_bootstrap_ci(repeated, mean, n_boot=10)


def test_block_bootstrap_rejects_series_shorter_than_a_block(synthetic):
    with pytest.raises(ValueError, match="at least block_len"):
        stats.block_bootstrap_ci(synthetic.head(2), lambda d: d["log_burn"].mean(),
                                 block_len=3, n_boot=10)


def test_pooled_fit_drops_missing_rows_and_matches_complete_case():
    # A missing outcome used to fail with "The weights and list don't have the
    # same length"; the result must equal fitting the complete rows only.
    rng = np.random.default_rng(5)
    enso = rng.normal(0, 1, N)
    panel = pd.concat([pd.DataFrame({"year": YEARS, "region": r, "enso_djf": enso,
                                     "log_burn": rng.normal(0, 1, N)})
                       for r in ["SoCal", "PNW", "BC"]], ignore_index=True)
    panel.loc[[4, 50], "log_burn"] = np.nan
    formula = "log_burn ~ enso_djf * C(region, Treatment('SoCal'))"
    fit = stats.fit_pooled(formula, panel)
    complete = stats.fit_pooled(formula, panel.dropna().reset_index(drop=True))
    assert int(fit.nobs) == len(panel) - 2
    assert np.allclose(fit.params, complete.params)
    assert np.allclose(fit.bse, complete.bse)


def test_stats_defaults_come_from_config():
    import inspect
    from src import config
    sig = inspect.signature(stats.permutation_test)
    assert sig.parameters["n_perm"].default == config.N_PERMUTATIONS
    assert inspect.signature(stats.block_bootstrap_ci).parameters["n_boot"].default == config.N_BOOTSTRAP
