"""Inferential statistics for small, autocorrelated climate samples.

Every function works on a tidy table with one row per year (single region) or
one row per region-year (pooled). Nothing here assumes normally distributed
data except the OLS prediction intervals, which are validated empirically by
leave-one-year-out and expanding-window coverage.

Headline methods (see ANALYSIS_PLAN.md):
  permutation_test       El Niño years vs the rest, no normality assumption
  bootstrap_ci_diff      confidence interval for that difference
  fit_ols_hac            regression with controls, Newey-West (HAC) errors
  fit_driscoll_kraay     pooled H4 model, Driscoll-Kraay errors, df = years - 1
  fit_pooled             the same model with year-clustered errors (alongside)
  h4_test                the H4 contrast and the joint F test of the interactions
  loyo_prediction        leave-one-year-out prediction intervals + coverage
  expanding_window       forward-chaining validation; forecast_skill against
                         the trend-only model
Supporting:
  coef_test              one coefficient: t, p in the stated direction, 95% CI
  t_pvalue               p from a t statistic, one- or two-sided
  block_bootstrap_ci     CI that respects year-to-year autocorrelation
  adjust_pvalues         Holm / Benjamini-Hochberg correction
  family_tests, run_family   the Holm/BH families of CORRECTION_FAMILIES
  detrend                residuals of value ~ year per region (burn_detr)
  zscore                 z against reference years, SD with ddof = 1
  with_zero_indicators   zero-fire sensitivity: one 0/1 column per zero year
Size checks (audit 2026-10-08 M1(b); added, reported beside the registered
p-values, not registered; scripts/stats_size_check.py measures them; kept
only where the measured size is near 5%):
  fit_ols_plain          the same model with ordinary standard errors; kept
                         for the per-region ENSO tests (H3a, H3b, C1, C2:
                         ENSO lag-1 autocorrelation -0.01, size 4-6%), not
                         for H5 and H6 (predictors up to AR 0.27: 7-9%) nor
                         the H4 contrast (0.7% with correlated regions, the
                         shared year shock cancels in a between-region
                         contrast; measured, not reported: D68)
  block_bootstrap_p      year-block bootstrap p; measured 6-9%, so dropped as
                         a check (kept to reproduce the measurement)
Other helpers (audit L6): strong_flags (near-threshold flip), center_year,
percent_change, lag1_autocorrelation, ols_prediction (the 2027 intervals).

Every fit made here carries `inference_df`, the t degrees of freedom its
tests use; coef_test, contrast_test and wald_f_test read it and take p from
scipy.stats, never from statsmodels' own t_test or wald_test, which use the
software's df count for the Driscoll-Kraay fit (trap 1, session 7 kickoff).
"""
from __future__ import annotations

from math import comb
from typing import Callable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats as sps
from statsmodels.stats.multitest import multipletests

from src.config import (ALPHA, BLOCK_LEN, CORRECTION_FAMILIES, ENSO_DECIMALS,
                        FORWARD_MIN_TRAIN_YEARS, STRONG_SENSITIVITY_BAND, STRONG_THRESHOLD,
                        H4_NORTH, H4_REFERENCE, H4_REGIONS, HAC_MAXLAGS, N_BOOTSTRAP,
                        N_PERMUTATIONS, POOLED_DF_YEARS_MINUS, PREDICTION_ALPHA,
                        RANDOM_SEED, ROBUST_SMALL_SAMPLE_CORRECTION, TEST_DIRECTIONS, USE_T)

DEFAULT_SEED = RANDOM_SEED
ALTERNATIVES = ("two-sided", "greater", "less")
# The H4 region term, written once so the formula and the coefficient names
# always agree; patsy names an interaction column
# "enso_djf:C(region, Treatment('SoCal'))[T.PNW]".
H4_REGION_TERM = f"C(region, Treatment('{H4_REFERENCE}'))"
H4_FORMULA = f"log_burn ~ enso_djf * {H4_REGION_TERM} + C(region):year"
H4_FORMULA_TEMP = f"log_burn ~ enso_djf * {H4_REGION_TERM} + temp_jja + C(region):year"


def _mean_diff(values: np.ndarray, in_group: np.ndarray) -> float:
    return values[in_group].mean() - values[~in_group].mean()


def _no_nan(values: np.ndarray, name: str) -> np.ndarray:
    """Raise on NaN: a NaN made permutation_test return p = 1/(n + 1), the
    smallest possible p, for a NaN difference (independent audit F3)."""
    if np.isnan(values).any():
        raise ValueError(f"{name} has {int(np.isnan(values).sum())} missing value(s); "
                         f"drop those years first.")
    return values


def _check_alternative(alternative: str) -> str:
    if alternative not in ALTERNATIVES:
        raise ValueError(f"alternative must be one of {ALTERNATIVES}, got {alternative!r}.")
    return alternative


def _contiguous_years(df: pd.DataFrame, model, year_col: str) -> None:
    """HAC weights neighbouring rows as neighbouring years, so the rows a fit
    uses must be one per year, sorted, with no gaps (independent audit F4:
    shuffled rows changed an HAC SE from 0.320 to 0.290; a dropped year was
    treated as adjacent)."""
    years = df.loc[model.data.row_labels, year_col].to_numpy()
    if len(years) and not (np.diff(years) == 1).all():
        raise ValueError(f"fit_ols_hac needs consecutive {year_col!r} values, sorted, one "
                         f"row each, in the rows the model uses (got {years.min()}-"
                         f"{years.max()}, {len(years)} rows); use a contiguous run.")


def _no_dropped_rows(df: pd.DataFrame, model, name: str) -> None:
    """The formula API drops a row with a missing value silently (41 rows to
    40 in the 2026-10-08 probe, trap 4); every fit here refuses instead, so a
    series cannot shorten and a panel cannot unbalance unnoticed."""
    used = len(model.data.row_labels)
    if used != len(df):
        raise ValueError(f"{name}: {len(df) - used} of {len(df)} rows have a missing value "
                         f"in the formula's variables; pass only complete rows.")


def t_pvalue(t: float, df: float, alternative: str = "two-sided") -> float:
    """p-value of a t statistic with `df` degrees of freedom.

    "greater" and "less" give the one tail in the stated direction, so an
    estimate of the opposite sign gives p above 0.5, never half the
    two-sided p (ANALYSIS_PLAN "Execution details", one-sided tests).
    """
    _check_alternative(alternative)
    if alternative == "greater":
        return float(sps.t.sf(t, df))
    if alternative == "less":
        return float(sps.t.cdf(t, df))
    return float(2 * sps.t.sf(abs(t), df))


def zscore(values, reference=None) -> np.ndarray:
    """(value - mean) / SD, with the mean and SD over the `reference` rows
    (boolean mask; all rows if None) and the SD with ddof = 1 (ANALYSIS_PLAN
    "Built variables"). numpy's std defaults to ddof 0 and pandas' to ddof 1
    (1.247 and 1.528 on [1, 2, 4]; trap 6), so the ddof is set here once."""
    values = np.asarray(values, dtype=float)
    ref = values if reference is None else values[np.asarray(reference, dtype=bool)]
    ref = _no_nan(ref, "reference values")
    if ref.size < 2:
        raise ValueError(f"zscore needs at least 2 reference values; got {ref.size}.")
    sd = ref.std(ddof=1)
    if sd == 0:
        raise ValueError("zscore reference values have SD 0.")
    return (values - ref.mean()) / sd


def detrend(df: pd.DataFrame, value: str, by: str = "region",
            year_col: str = "year") -> pd.Series:
    """Residuals of `value ~ year` by OLS within each `by` group, aligned to
    df's index (ANALYSIS_PLAN "Trend handling": burn_detr and the detrended
    climate variables in permutation and bootstrap tests). Raises on a
    missing value, so the caller chooses which years enter each group's
    trend (e.g. the zero-fire sensitivity re-detrends without them)."""
    out = pd.Series(np.nan, index=df.index, name=f"{value}_detr")
    for _, g in df.groupby(by, sort=False):
        y = _no_nan(g[value].to_numpy(dtype=float), value)
        x = g[year_col].to_numpy(dtype=float)
        if len(np.unique(x)) < 2:
            raise ValueError(f"detrend needs at least 2 distinct years per {by}.")
        slope, intercept = np.polyfit(x, y, 1)
        out.loc[g.index] = y - (intercept + slope * x)
    return out


def permutation_test(values, in_group, n_perm: int = N_PERMUTATIONS,
                     seed: int = DEFAULT_SEED, alternative: str = "two-sided") -> dict:
    """Permutation test for a difference in means, (group) - (rest).

    values       outcome per year (e.g. burned-area anomaly)
    in_group     boolean per year (e.g. year followed an El Niño winter)
    alternative  "two-sided" (|diff| at least as large), "greater" (permuted
                 differences at least as large as observed) or "less" (at
                 least as small); p = (count + 1) / (n_perm + 1), never 0.
    The permutation draws depend only on the seed and the number of years,
    so every region with the same years shares them (trap 11, a methods note).
    """
    _check_alternative(alternative)
    values = _no_nan(np.asarray(values, dtype=float), "values")
    in_group = np.asarray(in_group, dtype=bool)
    rng = np.random.default_rng(seed)
    observed = _mean_diff(values, in_group)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = _mean_diff(values, rng.permutation(in_group))
    if alternative == "greater":
        count = np.sum(null >= observed)
    elif alternative == "less":
        count = np.sum(null <= observed)
    else:
        count = np.sum(np.abs(null) >= abs(observed))
    # +1 in numerator and denominator so p is never exactly 0
    p = (count + 1) / (n_perm + 1)
    return {"diff": observed, "p": p, "alternative": alternative,
            "n_group": int(in_group.sum()), "n_rest": int((~in_group).sum())}


def bootstrap_ci_diff(values, in_group, n_boot: int = N_BOOTSTRAP,
                      alpha: float = ALPHA, seed: int = DEFAULT_SEED) -> dict:
    """Percentile bootstrap CI for (mean of group) - (mean of rest).

    Resamples within each group so group sizes stay fixed. `n_distinct_group`
    is the number of distinct resamples of the group, C(2g - 1, g): 10 for
    the 3 strong winters of the fire record, so a strong-only CI is coarse
    (trap 9; report it beside such a CI).
    """
    values = _no_nan(np.asarray(values, dtype=float), "values")
    in_group = np.asarray(in_group, dtype=bool)
    rng = np.random.default_rng(seed)
    g, r = values[in_group], values[~in_group]
    diffs = (rng.choice(g, (n_boot, g.size)).mean(axis=1)
             - rng.choice(r, (n_boot, r.size)).mean(axis=1))
    lo, hi = np.quantile(diffs, [alpha / 2, 1 - alpha / 2])
    return {"diff": g.mean() - r.mean(), "ci_low": lo, "ci_high": hi,
            "level": 1 - alpha, "n_distinct_group": comb(2 * g.size - 1, g.size)}


def block_bootstrap_ci(df: pd.DataFrame, statistic: Callable[[pd.DataFrame], float],
                       block_len: int = BLOCK_LEN, n_boot: int = N_BOOTSTRAP,
                       alpha: float = ALPHA, seed: int = DEFAULT_SEED,
                       year_col: str = "year") -> dict:
    """Moving-block bootstrap CI for any statistic of a yearly time series.

    Resamples runs of `block_len` consecutive years, so short-range
    autocorrelation (one dry year following another) is preserved.
    `statistic` takes a DataFrame and returns a number (e.g. a regression
    coefficient).

    `df` must hold one row per year in increasing year order: blocks are
    runs of consecutive rows, so unsorted rows give a wrong answer with no
    error (a lag-1 autocorrelation of 0.84 came out as -0.08; DECISIONS.md
    2026-10-05 "Phase 1 audit"). Raises if `df[year_col]` is not strictly
    increasing, or if there are fewer rows than `block_len`.

    Blocks of a few years break up longer persistence, so statistics that
    depend on it (autocorrelation, trends in a random walk) are understated;
    use it for means and regression coefficients.
    """
    if year_col in df and not df[year_col].is_monotonic_increasing:
        raise ValueError(f"block_bootstrap_ci needs df sorted by {year_col!r}; sort it first.")
    if year_col in df and df[year_col].duplicated().any():
        raise ValueError(f"block_bootstrap_ci needs one row per {year_col!r} (a single "
                         f"region's series), but some {year_col} values repeat.")
    if len(df) < block_len:
        raise ValueError(f"block_bootstrap_ci needs at least block_len={block_len} rows; "
                         f"got {len(df)}.")
    rng = np.random.default_rng(seed)
    n = len(df)
    n_blocks = int(np.ceil(n / block_len))
    starts_max = n - block_len + 1
    stats = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, starts_max, n_blocks)
        idx = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n]
        stats[i] = statistic(df.iloc[idx].reset_index(drop=True))
    lo, hi = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return {"estimate": statistic(df), "ci_low": lo, "ci_high": hi,
            "level": 1 - alpha, "block_len": block_len}


def fit_ols_hac(formula: str, df: pd.DataFrame, maxlags: int = HAC_MAXLAGS,
                year_col: str = "year", use_t: bool = USE_T,
                use_correction: bool = ROBUST_SMALL_SAMPLE_CORRECTION):
    """OLS for one region's yearly series with Newey-West (HAC) errors.

    Example:
      fit_ols_hac("log_burn ~ enso_djf + year", region_df)          # H3a
      fit_ols_hac("log_burn ~ enso_djf + temp_jja + year", region_df)  # H3b
    The `year` term is the trend control; `temp_jja` the temperature control.
    t critical values with the residual df (n - k) when `use_t`; the
    covariance is scaled by n / (n - k) when `use_correction` (D65;
    statsmodels' own default is no correction). Raises unless every row
    is complete and the rows hold consecutive years in order (ANALYSIS_PLAN
    "Small-cluster corrections": HAC fits use contiguous runs), so a
    missing value at either end cannot shorten the series silently.
    """
    df = df.reset_index(drop=True)
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "fit_ols_hac")
    _contiguous_years(df, model, year_col)
    fit = model.fit(cov_type="HAC", use_t=use_t,
                    cov_kwds={"maxlags": maxlags, "use_correction": use_correction})
    fit.inference_df = float(fit.df_resid) if use_t else np.inf
    return fit


def _balanced_panel(df: pd.DataFrame, unit_col: str, year_col: str) -> np.ndarray:
    """Every unit must hold the same consecutive years, once each (H4's
    balanced panel, POOLED_LAST_YEAR); returns the sorted years."""
    if df.duplicated([unit_col, year_col]).any():
        raise ValueError(f"Repeated {unit_col}-{year_col} rows in the panel.")
    years = np.sort(df[year_col].unique())
    if not (np.diff(years) == 1).all():
        raise ValueError(f"Panel years are not consecutive ({years.min()}-{years.max()}, "
                         f"{len(years)} distinct).")
    counts = df.groupby(unit_col)[year_col].nunique()
    if (counts != len(years)).any():
        short = counts[counts != len(years)].to_dict()
        raise ValueError(f"Unbalanced panel: {len(years)} years expected, got {short}.")
    return years


def fit_driscoll_kraay(formula: str, df: pd.DataFrame, maxlags: int = HAC_MAXLAGS,
                       year_col: str = "year", unit_col: str = "region",
                       use_correction: bool = ROBUST_SMALL_SAMPLE_CORRECTION):
    """Pooled regions with Driscoll-Kraay errors (H4's registered errors).

    Driscoll-Kraay sums the score over all regions in each year, then
    applies Newey-West weights over years, so it allows both correlation
    between regions in a year (a shared El Niño) and serial correlation
    over years. Its t df are set to number of years - POOLED_DF_YEARS_MINUS
    (`inference_df`, 40 for 1984-2024); statsmodels counts its own from row
    order and passes them to t_test and wald_test (trap 1), so test this
    fit only through coef_test, contrast_test, wald_f_test or h4_test. The
    covariance keeps statsmodels' cluster correction G / (G - 1) x
    (N - 1) / (N - K) when `use_correction` (D65). Raises on a missing
    value (trap 4) or an unbalanced or gapped panel.
    """
    df = df.reset_index(drop=True)
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "fit_driscoll_kraay")
    years = _balanced_panel(df, unit_col, year_col)
    time = (df[year_col] - years.min()).to_numpy(dtype=int)
    fit = model.fit(cov_type="hac-groupsum", use_t=True,
                    cov_kwds={"time": time, "maxlags": maxlags,
                              "use_correction": "cluster" if use_correction else False})
    fit.inference_df = float(len(years) - POOLED_DF_YEARS_MINUS)
    return fit


def fit_pooled(formula: str, df: pd.DataFrame, cluster: str = "year",
               use_correction: bool = ROBUST_SMALL_SAMPLE_CORRECTION):
    """Pooled regions with an interaction term, errors clustered by year
    (reported alongside the Driscoll-Kraay fit for H4).

    Example:
      fit_pooled(H4_FORMULA, panel_df)
    Clustering by year allows regions in the same year to be correlated
    (they share the same El Niño). The interaction coefficients answer
    "does El Niño affect region X differently from SoCal?"

    t critical values with clusters - 1 df (`inference_df`). Raises on a
    missing value in the formula's variables (trap 4: it used to drop such
    rows, which could unbalance H4's panel) or in the cluster column.
    """
    df = df.reset_index(drop=True)  # repeated labels (pd.concat) broke .loc (audit F8)
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "fit_pooled")
    groups = df[cluster]
    if groups.isna().any():
        raise ValueError(f"Cluster column {cluster!r} has missing values.")
    fit = model.fit(cov_type="cluster", use_t=True,
                    cov_kwds={"groups": groups, "use_correction": use_correction})
    fit.inference_df = float(groups.nunique() - 1)
    return fit


def fit_ols_plain(formula: str, df: pd.DataFrame):
    """The same model with ordinary (non-robust) standard errors and t with
    the residual df: one of the two size checks added beside the registered
    robust p-values (audit 2026-10-08 M1(b); added, reported, not
    registered). Raises on a missing value, as the registered fits do."""
    df = df.reset_index(drop=True)
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "fit_ols_plain")
    fit = model.fit()
    fit.inference_df = float(fit.df_resid)
    return fit


def block_bootstrap_p(formula: str, df: pd.DataFrame, weights: dict[str, float],
                      alternative: str = "two-sided", block_len: int = BLOCK_LEN,
                      n_boot: int = N_BOOTSTRAP, alpha: float = ALPHA,
                      seed: int = DEFAULT_SEED, year_col: str = "year") -> dict:
    """Moving-block bootstrap of an OLS coefficient or contrast sum(w x b),
    with a p-value read from the bootstrap distribution: the other size
    check beside the registered robust p-values (audit 2026-10-08 M1(b);
    added, reported, not registered).

    Years are resampled in runs of `block_len` consecutive years; every row
    of a drawn year comes along, so in a panel the regions of one year stay
    together (their shared weather is kept) and in one region's series it
    is the registered block bootstrap. Each draw refits OLS by least
    squares on the formula's design matrix. p is the share of draws on the
    far side of 0 in the stated direction, as (count + 1) / (n_boot + 1)
    ("greater": draws <= 0; "less": draws >= 0; two-sided: twice the
    smaller tail, at most 1), so p < alpha (two-sided) exactly when the
    (1 - alpha) percentile CI excludes 0. Measured size 6-9% on synthetic
    null data like the project's (2026-10-08), no better than the robust
    tests, so not used as a check (owner's condition, M1(b)). Raises on a
    missing value, on a
    draw whose design is rank-deficient (e.g. a zero-fire indicator column
    with its year not drawn), or on non-consecutive years.
    """
    _check_alternative(alternative)
    df = df.reset_index(drop=True)
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "block_bootstrap_p")
    names = list(model.exog_names)
    missing = [n for n in weights if n not in names]
    if missing:
        raise KeyError(f"No coefficient(s) {missing}; the model has {names}.")
    w = np.zeros(len(names))
    for n, v in weights.items():
        w[names.index(n)] = v
    X, y = model.exog, model.endog
    years = np.sort(df[year_col].unique())
    if not (np.diff(years) == 1).all():
        raise ValueError(f"block_bootstrap_p needs consecutive {year_col!r} values.")
    rows_of = [np.flatnonzero(df[year_col].to_numpy() == yr) for yr in years]
    n_years = len(years)
    if n_years < block_len:
        raise ValueError(f"block_bootstrap_p needs at least block_len={block_len} years.")
    n_blocks = int(np.ceil(n_years / block_len))
    rng = np.random.default_rng(seed)
    k = X.shape[1]
    draws = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n_years - block_len + 1, n_blocks)
        picked = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n_years]
        idx = np.concatenate([rows_of[j] for j in picked])
        beta, _, rank, _ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
        if rank < k:
            raise ValueError("A bootstrap draw has a rank-deficient design; this check "
                             "does not cover such a model (e.g. zero-fire indicators).")
        draws[i] = w @ beta
    estimate = float(w @ np.linalg.lstsq(X, y, rcond=None)[0])
    low = (np.sum(draws <= 0) + 1) / (n_boot + 1)
    high = (np.sum(draws >= 0) + 1) / (n_boot + 1)
    p = {"greater": low, "less": high, "two-sided": min(1.0, 2 * min(low, high))}[alternative]
    lo, hi = np.quantile(draws, [alpha / 2, 1 - alpha / 2])
    return {"estimate": estimate, "p": float(p), "alternative": alternative,
            "ci_low": float(lo), "ci_high": float(hi), "n_boot": n_boot,
            "block_len": block_len}


def _inference_df(fit) -> float:
    if not hasattr(fit, "inference_df"):
        raise ValueError("Fit has no inference_df; fit it with fit_ols_hac, "
                         "fit_driscoll_kraay or fit_pooled.")
    return fit.inference_df


def _t_result(estimate: float, se: float, df: float, alternative: str,
              alpha: float) -> dict:
    t = estimate / se
    crit = sps.t.ppf(1 - alpha / 2, df)
    return {"estimate": float(estimate), "se": float(se), "t": float(t), "df": df,
            "p": t_pvalue(t, df, alternative), "alternative": alternative,
            "ci_low": float(estimate - crit * se), "ci_high": float(estimate + crit * se)}


def coef_test(fit, name: str, alternative: str = "two-sided", alpha: float = ALPHA) -> dict:
    """Estimate, SE, t, p in the stated direction and two-sided (1 - alpha)
    CI of one coefficient, with the fit's own `inference_df`. The CI is
    always two-sided (ANALYSIS_PLAN "Execution details")."""
    _check_alternative(alternative)
    if name not in fit.params.index:
        raise KeyError(f"No coefficient {name!r}; the fit has {list(fit.params.index)}.")
    return _t_result(fit.params[name], fit.bse[name], _inference_df(fit), alternative, alpha)


def contrast_test(fit, weights: dict[str, float], alternative: str = "two-sided",
                  alpha: float = ALPHA) -> dict:
    """t test of sum(w x coefficient) = 0 with the fit's robust covariance
    and `inference_df`; p from scipy.stats, not statsmodels' t_test."""
    _check_alternative(alternative)
    missing = [n for n in weights if n not in fit.params.index]
    if missing:
        raise KeyError(f"No coefficient(s) {missing}; the fit has {list(fit.params.index)}.")
    names = list(weights)
    w = np.array([weights[n] for n in names], dtype=float)
    estimate = float(w @ fit.params[names].to_numpy())
    se = float(np.sqrt(w @ fit.cov_params().loc[names, names].to_numpy() @ w))
    return _t_result(estimate, se, _inference_df(fit), alternative, alpha)


def wald_f_test(fit, names: list[str]) -> dict:
    """Joint test that every coefficient in `names` is 0, as an F test with
    (q, inference_df) degrees of freedom: F = b' (V)^-1 b / q with the fit's
    robust covariance V (ANALYSIS_PLAN "Execution details": F(4, years - 1)
    for H4); p from scipy.stats, not statsmodels' wald_test."""
    missing = [n for n in names if n not in fit.params.index]
    if missing:
        raise KeyError(f"No coefficient(s) {missing}; the fit has {list(fit.params.index)}.")
    b = fit.params[names].to_numpy()
    cov = fit.cov_params().loc[names, names].to_numpy()
    q, df_den = len(names), _inference_df(fit)
    f = float(b @ np.linalg.solve(cov, b) / q)
    return {"F": f, "df_num": q, "df_den": df_den, "p": float(sps.f.sf(f, q, df_den))}


def h4_interaction_name(region: str) -> str:
    return f"enso_djf:{H4_REGION_TERM}[T.{region}]"


def h4_test(fit, north=H4_NORTH, regions=H4_REGIONS, reference: str = H4_REFERENCE) -> dict:
    """H4's registered contrast and its secondary joint test.

    With SoCal as the reference level, `enso_djf` is SoCal's slope and each
    interaction coefficient is a region's slope minus SoCal's, so the mean
    of the PNW, BC and AB interactions is the mean north slope minus
    SoCal's (two-sided). The joint F test covers every interaction (four).
    Raises if the coefficient names are not those of a SoCal-reference fit
    (trap 2: plain C(region) takes AB as the reference).
    """
    others = [r for r in regions if r != reference]
    names = [h4_interaction_name(r) for r in others]
    missing = [n for n in names if n not in fit.params.index]
    if missing or any(f"[T.{reference}]" in n for n in fit.params.index):
        raise KeyError(f"Not a {reference}-reference H4 fit: missing {missing}; "
                       f"fit has {list(fit.params.index)}.")
    contrast = contrast_test(fit, {h4_interaction_name(r): 1 / len(north) for r in north},
                             alternative=TEST_DIRECTIONS["H4"])
    return {"contrast": contrast, "joint": wald_f_test(fit, names)}


def with_zero_indicators(formula: str, df: pd.DataFrame, flag: str = "zero_fire",
                         region_col: str = "region",
                         year_col: str = "year") -> tuple[str, pd.DataFrame]:
    """Zero-fire sensitivity for regressions (ANALYSIS_PLAN "Execution
    details"): every zero region-year gets its own 0/1 column (zf_<region>_
    <year>), added to the formula. The other coefficients and the residual
    df then equal those of a fit without those rows, while the series stays
    contiguous for the HAC and Driscoll-Kraay lags (their SEs differ
    slightly: the zero residuals still enter the lag sums; D52)."""
    df = df.reset_index(drop=True).copy()
    zero = df[flag].astype(bool)
    terms = []
    for i in df.index[zero]:
        col = f"zf_{df.at[i, region_col]}_{int(df.at[i, year_col])}"
        df[col] = 0.0
        df.loc[i, col] = 1.0
        terms.append(col)
    return (formula + "".join(f" + {t}" for t in terms)), df


def adjust_pvalues(pvalues, method: str = "holm") -> np.ndarray:
    """Multiple-comparison correction. method: 'holm' or 'fdr_bh'. Raises on a
    missing p-value, which would otherwise count in the family size."""
    pvalues = _no_nan(np.asarray(pvalues, dtype=float), "pvalues")
    return multipletests(pvalues, method=method)[1]


def family_tests(family: str) -> list[tuple[str, str]]:
    """(test, region) pairs of a Holm family in CORRECTION_FAMILIES; regions
    with no direction in TEST_DIRECTIONS (descriptive or not applicable,
    e.g. SoCal SWE) are not tested. Sizes: H1, H2, H3a, H3b 5; H5 10; H6 9;
    north H2, H3a, H3b 2 each; C1, C2 3."""
    out = []
    for test, regions in CORRECTION_FAMILIES[family]:
        out += [(test, r) for r in regions if TEST_DIRECTIONS[test][r] is not None]
    return out


def run_family(family: str, pvalues: dict[tuple[str, str], float],
               alpha: float = ALPHA) -> pd.DataFrame:
    """Holm and BH within one family. `pvalues` maps (test, region) to the
    p-value in the stated direction and must hold exactly the family's
    tests; significance at alpha is decided by Holm (D50), BH alongside."""
    expected = family_tests(family)
    if set(pvalues) != set(expected) or len(pvalues) != len(expected):
        raise ValueError(f"Family {family} needs exactly {expected}; got missing "
                         f"{sorted(set(expected) - set(pvalues))}, extra "
                         f"{sorted(set(pvalues) - set(expected))}.")
    p = np.array([pvalues[k] for k in expected], dtype=float)
    out = pd.DataFrame(expected, columns=["test", "region"])
    out["family"] = family
    out["p"] = p
    out["p_holm"] = adjust_pvalues(p, "holm")
    out["p_bh"] = adjust_pvalues(p, "fdr_bh")
    out["significant"] = out["p_holm"] < alpha
    return out[["family", "test", "region", "p", "p_holm", "p_bh", "significant"]]


def loyo_prediction(formula: str, df: pd.DataFrame, alpha: float = PREDICTION_ALPHA,
                    year_col: str = "year") -> pd.DataFrame:
    """Leave-one-year-out prediction intervals and their coverage.

    For each year: fit on all other years, predict the held-out year with a
    (1 - alpha) prediction interval, and record whether the actual value
    fell inside. Mean of `covered` is the empirical coverage, which should
    be close to 1 - alpha if the intervals are honest.

    A held-out row with no actual value (a region-year with a missing
    outcome, or a year still to come) keeps its prediction and interval but
    has `covered` missing (pandas nullable boolean), so `covered.mean()`
    counts only years that can be checked (DECISIONS.md 2026-10-05
    "Phase 1 audit").
    """
    if df[year_col].duplicated().any():  # audit 2026-10-08 L5
        raise ValueError(f"loyo_prediction needs one row per {year_col!r} (one region's "
                         f"series); some {year_col} values repeat.")
    response = formula.split("~")[0].strip()
    rows = []
    for year in df[year_col].unique():
        train = df[df[year_col] != year]
        test = df[df[year_col] == year]
        fit = smf.ols(formula, data=train).fit()
        pred = fit.get_prediction(test).summary_frame(alpha=alpha)
        for (_, t), (_, p) in zip(test.iterrows(), pred.iterrows()):
            actual = t[response]
            covered = (pd.NA if pd.isna(actual)
                       else bool(p["obs_ci_lower"] <= actual <= p["obs_ci_upper"]))
            rows.append({
                year_col: year, "actual": actual, "predicted": p["mean"],
                "pi_low": p["obs_ci_lower"], "pi_high": p["obs_ci_upper"],
                "covered": covered,
            })
    out = pd.DataFrame(rows)
    out["covered"] = out["covered"].astype("boolean")
    return out


def expanding_window(formula: str, df: pd.DataFrame,
                     min_train: int = FORWARD_MIN_TRAIN_YEARS,
                     alpha: float = PREDICTION_ALPHA, year_col: str = "year") -> pd.DataFrame:
    """Forward-chaining validation for one region's series (ANALYSIS_PLAN
    "Forward validation"): for each year Y with at least `min_train` earlier
    seasons, fit plain OLS on every season before Y, predict Y with a
    (1 - alpha) prediction interval, and record the error. With seasons
    from 1984 the first prediction is 2004.

    Only the fit is forward-looking: inputs built with fixed reference
    periods (the 1991-2020 normals of precip_anom and the SWE z, the
    1951-2020 SPEI calibration) contain later years (trap 8; a stated
    limitation, frozen). Raises on a missing value or a repeated year.
    """
    df = df.sort_values(year_col).reset_index(drop=True)
    if df[year_col].duplicated().any():
        raise ValueError(f"expanding_window needs one row per {year_col!r}.")
    model = smf.ols(formula, data=df)
    _no_dropped_rows(df, model, "expanding_window")
    response = formula.split("~")[0].strip()
    years = df[year_col].to_numpy()
    rows = []
    for i, year in enumerate(years):
        if i < min_train:
            continue
        fit = smf.ols(formula, data=df.iloc[:i]).fit()
        p = fit.get_prediction(df.iloc[[i]]).summary_frame(alpha=alpha).iloc[0]
        actual = df.at[i, response]
        rows.append({year_col: int(year), "n_train": i, "actual": actual,
                     "predicted": p["mean"], "pi_low": p["obs_ci_lower"],
                     "pi_high": p["obs_ci_upper"],
                     "covered": bool(p["obs_ci_lower"] <= actual <= p["obs_ci_upper"]),
                     "error": actual - p["mean"]})
    return pd.DataFrame(rows)


def validation_summary(predictions: pd.DataFrame) -> dict:
    """n, RMSE and MAE of the prediction errors, and interval coverage."""
    err = _no_nan(predictions["error"].to_numpy(dtype=float), "error")
    return {"n": int(err.size), "rmse": float(np.sqrt(np.mean(err ** 2))),
            "mae": float(np.mean(np.abs(err))),
            "coverage": float(predictions["covered"].astype(bool).mean())}


def forecast_skill(model: pd.DataFrame, trend: pd.DataFrame, year_col: str = "year") -> dict:
    """Skill of a validated model against the trend-only model
    (`log_burn ~ year`) over the same held-out years: 1 - RMSE(model) /
    RMSE(trend) (0 = no gain over the trend; descriptive, not tested; D50).
    Raises unless both cover the same years."""
    if list(model[year_col]) != list(trend[year_col]):
        raise ValueError("Model and trend-only predictions cover different years.")
    m, t = validation_summary(model), validation_summary(trend)
    return {"n": m["n"], "rmse_model": m["rmse"], "rmse_trend": t["rmse"],
            "mae_model": m["mae"], "mae_trend": t["mae"],
            "skill": 1 - m["rmse"] / t["rmse"]}


# Helpers for plan steps with no function before audit round 1 (L6) -----------

def strong_flags(enso, flip_band: bool = False, threshold: float = STRONG_THRESHOLD,
                 band: float = STRONG_SENSITIVITY_BAND, decimals: int = ENSO_DECIMALS) -> np.ndarray:
    """Strong El Niño flag per winter (index at or above `threshold`). With
    `flip_band`, every winter whose distance to the threshold, rounded to
    the index's published decimals, is at most `band` has its flag flipped,
    all together (ANALYSIS_PLAN "Execution details", strong-only results;
    D52). Rounding first keeps 2009-10 (RONI 1.44): abs(1.44 - 1.5) is
    0.06000000000000005 in floating point (independent audit F7)."""
    enso = _no_nan(np.asarray(enso, dtype=float), "enso")
    strong = enso >= threshold
    if flip_band:
        near = np.round(np.abs(enso - threshold), decimals) <= band
        strong = np.where(near, ~strong, strong)
    return strong


def center_year(df: pd.DataFrame, year_col: str = "year") -> pd.Series:
    """year_c for C1 and C2: the year minus the mean year of the rows the
    model uses, so pass exactly those rows (C1 winters 1951-2026, C2 the
    region's fire seasons); the enso_djf coefficient is then the effect at
    that model's mid-record (the interaction does not depend on the centre)."""
    return (df[year_col] - df[year_col].mean()).rename("year_c")


def percent_change(b):
    """Coefficient on log_burn as a percent change, 100 x (exp(b) - 1)
    (ANALYSIS_PLAN "Reporting rules"); apply to the estimate and to each CI
    end separately (the result is not symmetric)."""
    return 100 * (np.exp(np.asarray(b, dtype=float)) - 1)


def lag1_autocorrelation(df: pd.DataFrame, value: str, year_col: str = "year") -> float:
    """Sample lag-1 autocorrelation of one region's series of consecutive
    years in order (ANALYSIS_PLAN "Supporting methods", autocorrelation):
    the textbook estimator, one mean and the whole series' sum of squares
    in the denominator, as statsmodels `acf` (audit 2026-10-08 round 2 L5;
    was the Pearson correlation of adjacent pairs, 0.203 against 0.197 on
    the audit's synthetic series)."""
    years = df[year_col].to_numpy()
    if len(years) < 3 or not (np.diff(years) == 1).all():
        raise ValueError(f"lag1_autocorrelation needs at least 3 consecutive, sorted {year_col!r} values.")
    x = _no_nan(df[value].to_numpy(dtype=float), value)
    d = x - x.mean()
    return float((d[:-1] * d[1:]).sum() / (d * d).sum())


def ols_prediction(formula: str, train: pd.DataFrame, new: pd.DataFrame,
                   alpha: float = PREDICTION_ALPHA) -> pd.DataFrame:
    """(1 - alpha) OLS prediction intervals for `new` rows from a plain OLS
    fit on `train` (t with the fit's residual df), as the 2027 forecast
    needs (ANALYSIS_PLAN "Execution details"). A plain fit, not the HAC
    fit: get_prediction on a HAC fit mixes the robust covariance into the
    interval (audit 2026-10-08 L6). Raises on a missing value in `train`."""
    train = train.reset_index(drop=True)
    model = smf.ols(formula, data=train)
    _no_dropped_rows(train, model, "ols_prediction")
    pred = model.fit().get_prediction(new).summary_frame(alpha=alpha)
    return pd.DataFrame({"predicted": pred["mean"].to_numpy(),
                         "pi_low": pred["obs_ci_lower"].to_numpy(),
                         "pi_high": pred["obs_ci_upper"].to_numpy()}, index=new.index)
