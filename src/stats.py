"""Inferential statistics for small, autocorrelated climate samples.

Every function works on a tidy table with one row per year (single region) or
one row per region-year (pooled). Nothing here assumes normally distributed
data except the OLS prediction intervals, which are validated empirically by
leave-one-year-out coverage.

Headline methods (see ANALYSIS_PLAN.md):
  permutation_test       El Niño years vs the rest, no normality assumption
  bootstrap_ci_diff      confidence interval for that difference
  fit_ols_hac            regression with controls, Newey-West (HAC) errors
  fit_pooled             pooled regions with ENSO index x region interaction
  loyo_prediction        leave-one-year-out prediction intervals + coverage
Supporting:
  block_bootstrap_ci     CI that respects year-to-year autocorrelation
  adjust_pvalues         Holm / Benjamini-Hochberg correction
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from src.config import (ALPHA, BLOCK_LEN, HAC_MAXLAGS, N_BOOTSTRAP,
                        N_PERMUTATIONS, PREDICTION_ALPHA, RANDOM_SEED)

DEFAULT_SEED = RANDOM_SEED


def _mean_diff(values: np.ndarray, in_group: np.ndarray) -> float:
    return values[in_group].mean() - values[~in_group].mean()


def _no_nan(values: np.ndarray, name: str) -> np.ndarray:
    """Raise on NaN: a NaN made permutation_test return p = 1/(n + 1), the
    smallest possible p, for a NaN difference (independent audit F3)."""
    if np.isnan(values).any():
        raise ValueError(f"{name} has {int(np.isnan(values).sum())} missing value(s); "
                         f"drop those years first.")
    return values


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


def permutation_test(values, in_group, n_perm: int = N_PERMUTATIONS,
                     seed: int = DEFAULT_SEED) -> dict:
    """Two-sided permutation test for a difference in means.

    values    outcome per year (e.g. burned-area anomaly)
    in_group  boolean per year (e.g. year followed an El Niño winter)
    Returns the observed difference and the permutation p-value.
    """
    values = _no_nan(np.asarray(values, dtype=float), "values")
    in_group = np.asarray(in_group, dtype=bool)
    rng = np.random.default_rng(seed)
    observed = _mean_diff(values, in_group)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = _mean_diff(values, rng.permutation(in_group))
    # +1 in numerator and denominator so p is never exactly 0
    p = (np.sum(np.abs(null) >= abs(observed)) + 1) / (n_perm + 1)
    return {"diff": observed, "p": p, "n_group": int(in_group.sum()),
            "n_rest": int((~in_group).sum())}


def bootstrap_ci_diff(values, in_group, n_boot: int = N_BOOTSTRAP,
                      alpha: float = ALPHA, seed: int = DEFAULT_SEED) -> dict:
    """Percentile bootstrap CI for (mean of group) - (mean of rest).

    Resamples within each group so group sizes stay fixed.
    """
    values = _no_nan(np.asarray(values, dtype=float), "values")
    in_group = np.asarray(in_group, dtype=bool)
    rng = np.random.default_rng(seed)
    g, r = values[in_group], values[~in_group]
    diffs = (rng.choice(g, (n_boot, g.size)).mean(axis=1)
             - rng.choice(r, (n_boot, r.size)).mean(axis=1))
    lo, hi = np.quantile(diffs, [alpha / 2, 1 - alpha / 2])
    return {"diff": g.mean() - r.mean(), "ci_low": lo, "ci_high": hi,
            "level": 1 - alpha}


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
                year_col: str = "year"):
    """OLS for one region's yearly series with Newey-West (HAC) errors.

    Example:
      fit_ols_hac("log_burn ~ enso_djf + year", region_df)          # H3a
      fit_ols_hac("log_burn ~ enso_djf + temp_jja + year", region_df)  # H3b
    The `year` term is the trend control; `temp_jja` the temperature control.
    Raises unless the rows used hold consecutive years in order (ANALYSIS_PLAN
    "Small-cluster corrections": HAC fits use contiguous runs).
    """
    df = df.reset_index(drop=True)
    model = smf.ols(formula, data=df)
    _contiguous_years(df, model, year_col)
    return model.fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})


def fit_pooled(formula: str, df: pd.DataFrame, cluster: str = "year"):
    """Pooled regions with an interaction term, errors clustered by year.

    Example:
      fit_pooled("log_burn ~ enso_djf * C(region, Treatment('SoCal'))"
                 " + C(region):year", panel_df)
    Clustering by year allows regions in the same year to be correlated
    (they share the same El Niño). The interaction coefficients answer
    "does El Niño affect region X differently from SoCal?"

    Rows with a missing value in the formula's variables are dropped, as in
    plain OLS (`fit.nobs` gives the rows used); the cluster groups are taken
    from those same rows (DECISIONS.md 2026-10-05 "Phase 1 audit").
    """
    df = df.reset_index(drop=True)  # repeated labels (pd.concat) broke .loc (audit F8)
    model = smf.ols(formula, data=df)
    groups = df.loc[model.data.row_labels, cluster]
    if groups.isna().any():
        raise ValueError(f"Cluster column {cluster!r} has missing values in rows the "
                         f"model uses.")
    return model.fit(cov_type="cluster", cov_kwds={"groups": groups})


def adjust_pvalues(pvalues, method: str = "holm") -> np.ndarray:
    """Multiple-comparison correction. method: 'holm' or 'fdr_bh'. Raises on a
    missing p-value, which would otherwise count in the family size."""
    pvalues = _no_nan(np.asarray(pvalues, dtype=float), "pvalues")
    return multipletests(pvalues, method=method)[1]


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
