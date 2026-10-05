"""Descriptive comparisons of ENSO phases over the full record (no tests).

Inferential statistics live in src/stats.py and follow ANALYSIS_PLAN.md; the
functions here only summarise, for sanity checks and exploration.
"""
from __future__ import annotations

import pandas as pd


def phase_summary(table: pd.DataFrame, value: str) -> pd.DataFrame:
    """Per region: group means and El Nino differences for `value`.

    `table` is a tidy region x year table with `phase` and `strong` columns,
    every winter included. Differences are reported three ways: in the value's
    units, as % of the all-winter mean, and in standard deviations of all
    winters (a standardised effect size).
    """
    rows = []
    for region, g in table.groupby("region", sort=False):
        v = g[value]
        nino = g["phase"] == "el_nino"
        strong = nino & g["strong"]
        neutral = g["phase"] == "neutral"
        mean_all, sd_all = v.mean(), v.std(ddof=1)
        diff_neutral = v[nino].mean() - v[neutral].mean()
        diff_all = v[nino].mean() - mean_all
        diff_strong = v[strong].mean() - mean_all
        rows.append({
            "region": region,
            "n_all": len(v), "n_el_nino": int(nino.sum()), "n_strong": int(strong.sum()),
            "n_neutral": int(neutral.sum()),
            "mean_all": mean_all, "mean_el_nino": v[nino].mean(),
            "mean_strong": v[strong].mean(), "mean_neutral": v[neutral].mean(),
            "mean_la_nina": v[g["phase"] == "la_nina"].mean(),
            "nino_minus_neutral": diff_neutral,
            "nino_minus_neutral_pct": 100 * diff_neutral / mean_all,
            "nino_minus_neutral_sd": diff_neutral / sd_all,
            "nino_minus_all_pct": 100 * diff_all / mean_all,
            "strong_minus_all_pct": 100 * diff_strong / mean_all,
            "strong_minus_all_sd": diff_strong / sd_all,
            "nino_share_below_median": (v[nino] < v.median()).mean(),
        })
    return pd.DataFrame(rows)
