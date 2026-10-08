"""Known-answer tests for the pre-results audit gate (ACTION_PLAN Phase 4, D51):
one-sided p, use_t and the small-sample correction, Driscoll-Kraay with
df = years - 1, the H4 contrast and F test, zero-fire indicators, the
expanding window and the trend-only skill score, the Holm/BH family runner,
detrending and z-scores. Each test plants a known answer on synthetic data
or rebuilds the number by hand; traps 1-11 of docs/session7_kickoff.md are
named where they are tested. No fire data.

Run from the repo root:  python -m pytest
"""
from math import comb

import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf
from scipy import stats as sps

from src import config, stats

YEARS = np.arange(1984, 2025)  # 41 seasons, as H4's pooled 1984-2024
H4_SLOPES = {"PNW": 0.8, "BC": 0.8, "AB": 0.8, "NorCal": 0.3, "SoCal": 0.0}


def panel(seed=0, slopes=H4_SLOPES, noise=0.5):
    """Five regions sharing one ENSO series, each with its own intercept,
    trend and ENSO slope (the H4 model's structure)."""
    rng = np.random.default_rng(seed)
    enso = rng.normal(0, 1, len(YEARS))
    frames = []
    for i, (region, slope) in enumerate(slopes.items()):
        frames.append(pd.DataFrame({
            "region": region, "year": YEARS, "enso_djf": enso,
            "temp_jja": rng.normal(0, 1, len(YEARS)),
            "log_burn": (10 + i) + slope * enso + 0.01 * i * (YEARS - 2000)
            + rng.normal(0, noise, len(YEARS))}))
    return pd.concat(frames, ignore_index=True)


def series(seed=0, n=42, beta=0.5, noise=0.5):
    rng = np.random.default_rng(seed)
    years = np.arange(1984, 1984 + n)
    enso = rng.normal(0, 1, n)
    return pd.DataFrame({"year": years, "enso_djf": enso, "temp_jja": rng.normal(0, 1, n),
                         "log_burn": 10 + beta * enso + 0.02 * (years - 2000)
                         + rng.normal(0, noise, n)})


def hand_hac(X, u, maxlags, groups=None):
    """Newey-West sandwich with Bartlett weights, summed (not averaged) as
    in statsmodels; with `groups` (time index per row) the scores are first
    summed within each time period (Driscoll-Kraay)."""
    scores = X * u[:, None]
    if groups is not None:
        scores = np.vstack([scores[groups == t].sum(axis=0) for t in np.unique(groups)])
    S = scores.T @ scores
    for lag in range(1, maxlags + 1):
        w = 1 - lag / (maxlags + 1)
        g = scores[lag:].T @ scores[:-lag]
        S += w * (g + g.T)
    bread = np.linalg.inv(X.T @ X)
    return bread @ S @ bread


# --- p-values -----------------------------------------------------------------

def test_t_pvalue_tails_by_hand():
    # Trap 5: one-sided p comes from the t statistic in the stated direction.
    assert stats.t_pvalue(2.0, 40, "greater") == pytest.approx(sps.t.sf(2.0, 40))
    assert stats.t_pvalue(2.0, 40, "less") == pytest.approx(1 - sps.t.sf(2.0, 40))
    assert stats.t_pvalue(2.0, 40, "two-sided") == pytest.approx(2 * sps.t.sf(2.0, 40))
    # opposite sign: p above 0.5, never half the two-sided p
    assert stats.t_pvalue(-2.0, 40, "greater") > 0.5
    assert stats.t_pvalue(-2.0, 40, "greater") == pytest.approx(1 - stats.t_pvalue(2.0, 40, "two-sided") / 2)
    with pytest.raises(ValueError, match="alternative"):
        stats.t_pvalue(1.0, 40, "larger")


def test_permutation_one_sided_tails():
    rng = np.random.default_rng(1)
    in_group = np.zeros(42, dtype=bool)
    in_group[:12] = True
    values = rng.normal(0, 1, 42) + 1.5 * in_group
    greater = stats.permutation_test(values, in_group, n_perm=2000, alternative="greater")
    less = stats.permutation_test(values, in_group, n_perm=2000, alternative="less")
    two = stats.permutation_test(values, in_group, n_perm=2000)
    assert greater["p"] < 0.01 and less["p"] > 0.99
    assert greater["p"] <= two["p"]
    # same seed, same draws: the two tails count every draw once (ties aside)
    assert greater["p"] + less["p"] == pytest.approx(1 + 2 / 2001, abs=1e-3)


def test_permutation_one_sided_known_share():
    # one group member at the maximum of four values: a permuted difference
    # at least as large occurs when the 10 lands in the group, 1 in 4 draws.
    values = np.array([0.0, 0.0, 0.0, 10.0])
    group = np.array([False, False, False, True])
    p = stats.permutation_test(values, group, n_perm=8000, alternative="greater")["p"]
    assert p == pytest.approx(0.25, abs=0.015)


def test_bootstrap_reports_distinct_resamples_of_three_winters():
    # Trap 9: 3 strong winters have C(5, 3) = 10 distinct resamples.
    values = np.arange(20, dtype=float)
    group = np.zeros(20, dtype=bool)
    group[:3] = True
    out = stats.bootstrap_ci_diff(values, group, n_boot=500)
    assert out["n_distinct_group"] == 10 == comb(5, 3)


# --- per-region HAC ---------------------------------------------------------------

def test_hac_uses_t_and_matches_hand_newey_west():
    df = series()
    fit = stats.fit_ols_hac("log_burn ~ enso_djf + year", df, use_correction=False)
    assert fit.use_t and fit.inference_df == len(df) - 3
    X = fit.model.exog
    V = hand_hac(X, fit.resid.to_numpy(), config.HAC_MAXLAGS)
    assert np.allclose(fit.cov_params().to_numpy(), V)


def test_hac_small_sample_correction_scales_by_n_over_n_minus_k():
    # Trap 3, decided 2026-10-08 (D65): correction on.
    df = series()
    off = stats.fit_ols_hac("log_burn ~ enso_djf + year", df, use_correction=False)
    on = stats.fit_ols_hac("log_burn ~ enso_djf + year", df)
    assert config.ROBUST_SMALL_SAMPLE_CORRECTION is True
    assert np.allclose(on.bse / off.bse, np.sqrt(42 / 39))
    assert np.allclose(on.params, off.params)


def test_coef_test_one_sided_and_ci_by_hand():
    df = series(beta=0.5)
    fit = stats.fit_ols_hac("log_burn ~ enso_djf + year", df)
    out = stats.coef_test(fit, "enso_djf", "greater")
    t = fit.params["enso_djf"] / fit.bse["enso_djf"]
    assert out["t"] == pytest.approx(t)
    assert out["p"] == pytest.approx(sps.t.sf(t, 39))
    crit = sps.t.ppf(0.975, 39)
    assert out["ci_low"] == pytest.approx(fit.params["enso_djf"] - crit * fit.bse["enso_djf"])
    assert out["ci_low"] < 0.5 < out["ci_high"]
    # statsmodels' own two-sided p and CI agree for this fit (use_t, df 39)
    assert 2 * min(out["p"], 1 - out["p"]) == pytest.approx(fit.pvalues["enso_djf"])
    assert out["ci_low"] == pytest.approx(fit.conf_int().loc["enso_djf", 0])
    with pytest.raises(KeyError):
        stats.coef_test(fit, "enso", "greater")


# --- Driscoll-Kraay and H4 ------------------------------------------------------------

def test_driscoll_kraay_matches_hand_calculation_with_cluster_factor():
    df = panel()
    fit = stats.fit_driscoll_kraay(stats.H4_FORMULA, df)
    X, u = fit.model.exog, fit.resid.to_numpy()
    n, k, g = X.shape[0], X.shape[1], len(YEARS)
    V = hand_hac(X, u, config.HAC_MAXLAGS, groups=df["year"].to_numpy())
    V *= g / (g - 1) * (n - 1) / (n - k)
    assert np.allclose(fit.cov_params().to_numpy(), V)
    off = stats.fit_driscoll_kraay(stats.H4_FORMULA, df, use_correction=False)
    assert np.allclose(off.cov_params().to_numpy(), V / (g / (g - 1) * (n - 1) / (n - k)))


def test_driscoll_kraay_df_is_years_minus_one_whatever_the_row_order():
    # Trap 1: statsmodels' own t_test df depends on row order; ours is 40.
    df = panel()
    by_region = stats.fit_driscoll_kraay(stats.H4_FORMULA, df)
    by_year = stats.fit_driscoll_kraay(stats.H4_FORMULA, df.sort_values(["year", "region"]))
    shuffled = stats.fit_driscoll_kraay(stats.H4_FORMULA, df.sample(frac=1, random_state=3))
    for fit in (by_region, by_year, shuffled):
        assert fit.inference_df == len(YEARS) - 1 == 40
        assert np.allclose(fit.bse.sort_index(), by_region.bse.sort_index())
    term = stats.h4_interaction_name("PNW")
    sm_df = by_region.t_test(term).df_denom
    assert sm_df != 40  # the software's count, never used for a p-value


def test_driscoll_kraay_refuses_unbalanced_or_gapped_panel():
    df = panel()
    with pytest.raises(ValueError, match="Unbalanced"):
        stats.fit_driscoll_kraay(stats.H4_FORMULA, df.drop(index=5))
    gapped = df[df["year"] != 2000]
    with pytest.raises(ValueError, match="consecutive"):
        stats.fit_driscoll_kraay(stats.H4_FORMULA, gapped)


def test_h4_reference_is_socal_and_plain_region_term_is_refused():
    # Trap 2: plain C(region) takes AB as the reference.
    df = panel()
    fit = stats.fit_driscoll_kraay(stats.H4_FORMULA, df)
    for r in ("PNW", "BC", "AB", "NorCal"):
        assert stats.h4_interaction_name(r) in fit.params.index
    assert not any("[T.SoCal]" in n for n in fit.params.index)
    plain = stats.fit_driscoll_kraay("log_burn ~ enso_djf * C(region) + C(region):year", df)
    assert any("[T.SoCal]" in n for n in plain.params.index)  # AB is the reference
    with pytest.raises(KeyError, match="SoCal-reference"):
        stats.h4_test(plain)


def test_h4_contrast_equals_per_region_slopes_and_f_by_hand():
    df = panel(noise=0.4)
    fit = stats.fit_driscoll_kraay(stats.H4_FORMULA, df)
    # the fully interacted model's slopes equal separate per-region OLS slopes
    slope = {r: smf.ols("log_burn ~ enso_djf + year", g).fit().params["enso_djf"]
             for r, g in df.groupby("region")}
    out = stats.h4_test(fit)
    north_minus_socal = np.mean([slope[r] for r in ("PNW", "BC", "AB")]) - slope["SoCal"]
    c = out["contrast"]
    assert c["estimate"] == pytest.approx(north_minus_socal)
    assert c["df"] == 40 and c["alternative"] == "two-sided"
    assert c["ci_low"] < 0.8 < c["ci_high"]
    names = [stats.h4_interaction_name(r) for r in ("PNW", "BC", "AB")]
    L = np.zeros(len(fit.params))
    for n in names:
        L[list(fit.params.index).index(n)] = 1 / 3
    se = np.sqrt(L @ fit.cov_params().to_numpy() @ L)
    assert c["se"] == pytest.approx(se)
    assert c["p"] == pytest.approx(2 * sps.t.sf(abs(c["estimate"] / se), 40))
    joint = out["joint"]
    all4 = [stats.h4_interaction_name(r) for r in ("PNW", "BC", "AB", "NorCal")]
    b = fit.params[all4].to_numpy()
    V = fit.cov_params().loc[all4, all4].to_numpy()
    f = b @ np.linalg.inv(V) @ b / 4
    assert (joint["df_num"], joint["df_den"]) == (4, 40)
    assert joint["F"] == pytest.approx(f)
    assert joint["p"] == pytest.approx(sps.f.sf(f, 4, 40))
    # statsmodels' wald_test gives the same F but its own denominator df
    sm = fit.wald_test(np.eye(len(fit.params))[[list(fit.params.index).index(n) for n in all4]],
                       use_f=True, scalar=True)
    assert float(sm.statistic) == pytest.approx(f)
    assert sm.df_denom != 40


def test_h4_null_contrast_is_not_significant():
    # Only the registered contrast: the joint Driscoll-Kraay F test rejects a
    # true null in about 20% of synthetic panels at the 5% level (1,000 panels,
    # 2026-10-08; this seed gives p = 0.025), a size property of the method,
    # recorded in docs/methods_register.md "Statistics".
    df = panel(seed=7, slopes={r: 0.0 for r in H4_SLOPES})
    out = stats.h4_test(stats.fit_driscoll_kraay(stats.H4_FORMULA, df))
    assert out["contrast"]["p"] > 0.05


def test_year_clustered_fit_df_and_refusals():
    df = panel()
    fit = stats.fit_pooled(stats.H4_FORMULA, df)
    assert fit.inference_df == 40
    assert np.allclose(stats.h4_test(fit)["contrast"]["estimate"],
                       stats.h4_test(stats.fit_driscoll_kraay(stats.H4_FORMULA, df))["contrast"]["estimate"])


# --- zero-fire indicators -----------------------------------------------------------

def test_zero_indicators_match_a_fit_without_those_years():
    df = series(seed=4).assign(region="PNW")
    df["zero_fire"] = False
    df.loc[[7, 20], "zero_fire"] = True
    df.loc[[7, 20], "log_burn"] = 0.0
    formula, wide = stats.with_zero_indicators("log_burn ~ enso_djf + year", df)
    assert formula.count("zf_") == 2
    with_ind = stats.fit_ols_hac(formula, wide)
    dropped = smf.ols("log_burn ~ enso_djf + year", df[~df["zero_fire"]]).fit()
    for name in ("Intercept", "enso_djf", "year"):
        assert with_ind.params[name] == pytest.approx(dropped.params[name])
    assert with_ind.df_resid == dropped.df_resid


def test_zero_indicators_in_the_pooled_model_keep_df_and_coefficients():
    df = panel()
    df["zero_fire"] = False
    df.loc[(df["region"] == "SoCal") & (df["year"] == 2014), "zero_fire"] = True
    df.loc[df["zero_fire"], "log_burn"] = 0.0
    formula, wide = stats.with_zero_indicators(stats.H4_FORMULA, df)
    assert "zf_SoCal_2014" in formula
    fit = stats.fit_driscoll_kraay(formula, wide)
    assert fit.inference_df == 40
    dropped = smf.ols(stats.H4_FORMULA, df[~df["zero_fire"]]).fit()
    term = stats.h4_interaction_name("PNW")
    assert fit.params[term] == pytest.approx(dropped.params[term])
    assert fit.params["enso_djf"] == pytest.approx(dropped.params["enso_djf"])


# --- expanding window and skill ---------------------------------------------------------

def test_expanding_window_starts_in_2004_and_refits_on_earlier_years_only():
    df = series(n=42)  # 1984-2025
    out = stats.expanding_window("log_burn ~ enso_djf + year", df)
    assert out["year"].iloc[0] == 2004 and out["year"].iloc[-1] == 2025 and len(out) == 22
    assert (out["n_train"] == out["year"] - 1984).all()
    row = out[out["year"] == 2010].iloc[0]
    hand = smf.ols("log_burn ~ enso_djf + year", df[df["year"] < 2010]).fit()
    pred = hand.get_prediction(df[df["year"] == 2010]).summary_frame(alpha=0.2).iloc[0]
    assert row["predicted"] == pytest.approx(pred["mean"])
    assert row["pi_low"] == pytest.approx(pred["obs_ci_lower"])
    # Canada: 1984-2024 gives 21 predictions
    assert len(stats.expanding_window("log_burn ~ year", series(n=41))) == 21


def test_expanding_window_coverage_near_nominal_over_many_series():
    covered = [stats.expanding_window("log_burn ~ enso_djf + year", series(seed=s))["covered"]
               for s in range(40)]
    rate = pd.concat(covered).mean()
    assert 0.74 <= rate <= 0.86


def test_forecast_skill_known_answers():
    df = series(seed=2, beta=1.0, noise=0.3)
    model = stats.expanding_window("log_burn ~ enso_djf + year", df)
    trend = stats.expanding_window("log_burn ~ year", df)
    out = stats.forecast_skill(model, trend)
    assert out["n"] == 22 and out["skill"] > 0.5  # ENSO explains most of the variance
    same = stats.forecast_skill(trend, trend)
    assert same["skill"] == 0.0
    s = stats.validation_summary(model)
    assert s["rmse"] == pytest.approx(np.sqrt((model["error"] ** 2).mean()))
    assert s["mae"] == pytest.approx(model["error"].abs().mean())
    with pytest.raises(ValueError, match="different years"):
        stats.forecast_skill(model.iloc[1:], trend)


def test_expanding_window_refuses_missing_values():
    df = series()
    df.loc[30, "enso_djf"] = np.nan
    with pytest.raises(ValueError, match="missing value"):
        stats.expanding_window("log_burn ~ enso_djf + year", df)


# --- families -----------------------------------------------------------------

def test_family_sizes_match_the_plan():
    sizes = {f: len(stats.family_tests(f)) for f in config.CORRECTION_FAMILIES}
    assert sizes == {"H1": 5, "H2": 5, "H3a": 5, "H3b": 5, "H5": 10, "H6": 9,
                     "north_H2": 2, "north_H3a": 2, "north_H3b": 2, "C1": 3, "C2": 3}
    assert ("H6_swe", "SoCal") not in stats.family_tests("H6")


def test_run_family_holm_and_bh_by_hand():
    tests = stats.family_tests("H2")
    p = dict(zip(tests, [0.01, 0.04, 0.03, 0.2, 0.002]))
    out = stats.run_family("H2", p).set_index("region")
    # Holm by hand: sorted 0.002, 0.01, 0.03, 0.04, 0.2 x 5, 4, 3, 2, 1, running max
    assert out.loc["SoCal", "p_holm"] == pytest.approx(0.01)
    assert out.loc["PNW", "p_holm"] == pytest.approx(0.04)
    assert out.loc["AB", "p_holm"] == pytest.approx(0.09)
    assert out.loc["BC", "p_holm"] == pytest.approx(0.09)
    assert out.loc["NorCal", "p_holm"] == pytest.approx(0.2)
    # BH by hand: 0.2, 0.05, 0.05, 0.05, 0.01
    assert out.loc["BC", "p_bh"] == pytest.approx(0.05)
    assert out.loc["SoCal", "p_bh"] == pytest.approx(0.01)
    assert list(out["significant"]) == [True, False, False, False, True]


def test_run_family_refuses_missing_or_extra_tests():
    tests = stats.family_tests("C1")
    with pytest.raises(ValueError, match="needs exactly"):
        stats.run_family("C1", {tests[0]: 0.1, tests[1]: 0.2})
    extra = {t: 0.1 for t in tests} | {("C1", "SoCal"): 0.3}
    with pytest.raises(ValueError, match="needs exactly"):
        stats.run_family("C1", extra)


# --- detrend and z-scores ---------------------------------------------------------------

def test_detrend_per_region_removes_each_regions_own_line():
    years = np.arange(1984, 2026)
    rng = np.random.default_rng(9)
    noise = rng.normal(0, 1, (2, years.size))
    df = pd.concat([pd.DataFrame({"region": "A", "year": years,
                                  "log_burn": 5 + 0.1 * (years - 1984) + noise[0]}),
                    pd.DataFrame({"region": "B", "year": years,
                                  "log_burn": 9 - 0.3 * (years - 1984) + noise[1]})],
                   ignore_index=True)
    detr = stats.detrend(df, "log_burn")
    for r, g in df.assign(d=detr).groupby("region"):
        assert abs(g["d"].mean()) < 1e-9
        assert abs(np.corrcoef(g["year"], g["d"])[0, 1]) < 1e-9
        own = g["log_burn"] - np.polyval(np.polyfit(g["year"], g["log_burn"], 1), g["year"])
        assert np.allclose(g["d"], own)
    exact = pd.DataFrame({"region": "A", "year": years, "v": 2 + 0.5 * years})
    assert np.allclose(stats.detrend(exact, "v"), 0)
    with pytest.raises(ValueError, match="missing"):
        stats.detrend(df.assign(log_burn=df["log_burn"].where(df.index != 3)), "log_burn")


def test_zscore_uses_ddof_one():
    # Trap 6: pandas std is ddof 1 (1.528), numpy's ddof 0 (1.247).
    z = stats.zscore([1.0, 2.0, 4.0])
    assert z[2] == pytest.approx((4 - 7 / 3) / np.std([1, 2, 4], ddof=1))
    ref = np.array([True, True, False, False])
    z = stats.zscore([1.0, 3.0, 2.0, 10.0], reference=ref)
    assert z[3] == pytest.approx((10 - 2) / np.std([1, 3], ddof=1))
    with pytest.raises(ValueError, match="at least 2"):
        stats.zscore([1.0, 2.0], reference=[True, False])


# --- size checks (audit 2026-10-08 M1(b)) -------------------------------------------

def test_plain_ols_p_matches_statsmodels_ols():
    df = series()
    fit = stats.fit_ols_plain("log_burn ~ enso_djf + year", df)
    ref = smf.ols("log_burn ~ enso_djf + year", df).fit()
    out = stats.coef_test(fit, "enso_djf")
    assert fit.inference_df == 39
    assert out["p"] == pytest.approx(ref.pvalues["enso_djf"])
    assert out["ci_low"] == pytest.approx(ref.conf_int().loc["enso_djf", 0])
    gap = df.copy()
    gap.loc[3, "enso_djf"] = np.nan
    with pytest.raises(ValueError, match="missing value"):
        stats.fit_ols_plain("log_burn ~ enso_djf + year", gap)


def test_block_bootstrap_p_on_one_series_is_the_registered_block_bootstrap():
    # Same seed and blocks as block_bootstrap_ci: identical draws, so the CIs agree.
    df = series(beta=0.5)
    out = stats.block_bootstrap_p("log_burn ~ enso_djf + year", df, {"enso_djf": 1.0},
                                  alternative="greater", n_boot=500)

    def coef(d):
        return smf.ols("log_burn ~ enso_djf + year", d).fit().params["enso_djf"]
    ref = stats.block_bootstrap_ci(df, coef, n_boot=500)
    assert out["ci_low"] == pytest.approx(ref["ci_low"])
    assert out["ci_high"] == pytest.approx(ref["ci_high"])
    assert out["estimate"] == pytest.approx(ref["estimate"])
    assert out["p"] < 0.01  # planted 0.5 with noise 0.5


def test_block_bootstrap_p_tails_and_ci_agree():
    df = series(seed=11, beta=0.0)
    two = stats.block_bootstrap_p("log_burn ~ enso_djf + year", df, {"enso_djf": 1.0},
                                  n_boot=999)
    greater = stats.block_bootstrap_p("log_burn ~ enso_djf + year", df, {"enso_djf": 1.0},
                                      alternative="greater", n_boot=999)
    less = stats.block_bootstrap_p("log_burn ~ enso_djf + year", df, {"enso_djf": 1.0},
                                   alternative="less", n_boot=999)
    assert two["p"] == pytest.approx(min(1.0, 2 * min(greater["p"], less["p"])))
    assert (two["p"] < 0.05) == (two["ci_low"] > 0 or two["ci_high"] < 0)


def test_block_bootstrap_p_panel_contrast_estimate_and_refusals():
    df = panel()
    weights = {stats.h4_interaction_name(r): 1 / 3 for r in ("PNW", "BC", "AB")}
    out = stats.block_bootstrap_p(stats.H4_FORMULA, df, weights, n_boot=300)
    ols = smf.ols(stats.H4_FORMULA, df).fit()
    assert out["estimate"] == pytest.approx(sum(ols.params[n] * w for n, w in weights.items()))
    assert out["ci_low"] < 0.8 < out["ci_high"] and out["p"] < 0.05
    df["zero_fire"] = False
    df.loc[(df["region"] == "SoCal") & (df["year"] == 2014), "zero_fire"] = True
    formula, wide = stats.with_zero_indicators(stats.H4_FORMULA, df)
    with pytest.raises(ValueError, match="rank-deficient"):
        stats.block_bootstrap_p(formula, wide, weights, n_boot=300)
    with pytest.raises(KeyError):
        stats.block_bootstrap_p(stats.H4_FORMULA, panel(), {"nope": 1.0}, n_boot=10)


# --- audit round 1 low findings (L5, L6, L10) ---------------------------------------

def test_loyo_refuses_repeated_years():
    df = pd.concat([series(seed=1), series(seed=2)], ignore_index=True)
    with pytest.raises(ValueError, match="one row per"):
        stats.loyo_prediction("log_burn ~ enso_djf + year", df)


def test_strong_flags_and_the_near_threshold_flip():
    # RONI band winters: 1965-66 1.53, 1986-87 1.46, 2009-10 1.44 (1.44 needs the rounding)
    enso = np.array([1.53, 1.46, 1.44, 1.43, 1.57, 2.40, 0.8, 1.50])
    assert list(stats.strong_flags(enso)) == [True, False, False, False, True, True, False, True]
    flipped = stats.strong_flags(enso, flip_band=True)
    assert list(flipped) == [False, True, True, False, True, True, False, False]
    assert abs(1.44 - 1.5) > 0.06  # the floating-point trap the rounding avoids


def test_center_year_uses_the_rows_given():
    df = pd.DataFrame({"year": np.arange(1984, 2025)})
    assert stats.center_year(df).mean() == pytest.approx(0)
    assert stats.center_year(df).iloc[0] == -20
    assert stats.center_year(df[df["year"] >= 2000]).iloc[0] == -12


def test_percent_change_by_hand():
    assert stats.percent_change(0.0) == 0.0
    assert stats.percent_change(np.log(2)) == pytest.approx(100.0)
    assert np.allclose(stats.percent_change([-np.log(2), np.log(1.5)]), [-50.0, 50.0])


def test_lag1_autocorrelation_known_answers_and_refusals():
    years = np.arange(1984, 2026)
    alternating = pd.DataFrame({"year": years, "v": np.tile([1.0, -1.0], 21)})
    assert stats.lag1_autocorrelation(alternating, "v") == pytest.approx(-1.0)
    rng = np.random.default_rng(3)
    x = np.empty(4000)
    x[0] = 0
    for i in range(1, 4000):
        x[i] = 0.6 * x[i - 1] + rng.normal()
    long = pd.DataFrame({"year": np.arange(4000), "v": x})
    assert stats.lag1_autocorrelation(long, "v") == pytest.approx(0.6, abs=0.03)
    with pytest.raises(ValueError, match="consecutive"):
        stats.lag1_autocorrelation(alternating.drop(index=5), "v")


def test_ols_prediction_is_a_plain_ols_interval():
    df = series()
    train, new = df.iloc[:-1], df.iloc[[-1]]
    out = stats.ols_prediction("log_burn ~ enso_djf + year", train, new)
    ref = smf.ols("log_burn ~ enso_djf + year", train).fit().get_prediction(new).summary_frame(alpha=0.2)
    assert out["pi_low"].iloc[0] == pytest.approx(ref["obs_ci_lower"].iloc[0])
    assert out["predicted"].iloc[0] == pytest.approx(ref["mean"].iloc[0])


def test_h4_null_contrast_rejection_rate_over_seeds():
    # L10: more than one seed; 60 null panels, the registered contrast should
    # not reject far more than the measured ~8% (binomial 60 x 0.08 = 4.8).
    hits = sum(stats.h4_test(stats.fit_driscoll_kraay(
        stats.H4_FORMULA, panel(seed=100 + s, slopes={r: 0.0 for r in H4_SLOPES})))
        ["contrast"]["p"] < 0.05 for s in range(60))
    assert hits <= 12


def test_contrast_one_sided_and_wald_f_on_its_own():
    df = series(beta=0.5)
    fit = stats.fit_ols_hac("log_burn ~ enso_djf + temp_jja + year", df)
    c = stats.contrast_test(fit, {"enso_djf": 1.0}, alternative="greater")
    single = stats.coef_test(fit, "enso_djf", "greater")
    assert c["p"] == pytest.approx(single["p"]) and c["estimate"] == pytest.approx(single["estimate"])
    less = stats.contrast_test(fit, {"enso_djf": 1.0}, alternative="less")
    assert less["p"] == pytest.approx(1 - c["p"])
    # one-coefficient F equals t squared, same p as two-sided t
    f = stats.wald_f_test(fit, ["enso_djf"])
    t2 = stats.coef_test(fit, "enso_djf")
    assert f["F"] == pytest.approx(t2["t"] ** 2)
    assert f["p"] == pytest.approx(t2["p"])
    assert (f["df_num"], f["df_den"]) == (1, 38)


def test_all_stats_defaults_come_from_config():
    import inspect
    sig = {name: inspect.signature(getattr(stats, name)).parameters
           for name in ("fit_ols_hac", "fit_driscoll_kraay", "block_bootstrap_ci",
                        "bootstrap_ci_diff", "coef_test", "expanding_window", "run_family")}
    assert sig["fit_ols_hac"]["maxlags"].default == config.HAC_MAXLAGS
    assert sig["fit_ols_hac"]["use_t"].default == config.USE_T
    assert sig["fit_ols_hac"]["use_correction"].default == config.ROBUST_SMALL_SAMPLE_CORRECTION
    assert sig["fit_driscoll_kraay"]["maxlags"].default == config.HAC_MAXLAGS
    assert sig["block_bootstrap_ci"]["block_len"].default == config.BLOCK_LEN
    assert sig["bootstrap_ci_diff"]["alpha"].default == config.ALPHA
    assert sig["coef_test"]["alpha"].default == config.ALPHA
    assert sig["expanding_window"]["min_train"].default == config.FORWARD_MIN_TRAIN_YEARS
    assert sig["expanding_window"]["alpha"].default == config.PREDICTION_ALPHA
    assert sig["run_family"]["alpha"].default == config.ALPHA
