"""Size of the gate's tests on synthetic null data (no fire data).

The share of synthetic datasets with no true effect in which each test gives
p < 0.05: a test with the right size rejects about 5% of them. Covers the H4
contrast and joint F test (Driscoll-Kraay, df = years - 1, and
year-clustered) on a 5-region, 41-year panel, and the per-region Newey-West
coefficient test (H3a shape, 42 years), with errors independent across
years (rho 0) and AR(1) with rho 0.3. Settings from src/config.py.

Run from the repo root:  python scripts/stats_size_check.py [reps]
Measured 2026-10-08 (1,000 reps each; Monte Carlo SE about 0.007): see
docs/methods_register.md "Statistics", row "Test size (simulated)".
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import stats  # noqa: E402
from src.config import H4_REGIONS, RANDOM_SEED  # noqa: E402

YEARS = np.arange(1984, 2025)


def ar1(rng, n, rho):
    e = rng.normal(0, 1, n)
    out = np.empty(n)
    out[0] = e[0] / np.sqrt(1 - rho ** 2)
    for i in range(1, n):
        out[i] = rho * out[i - 1] + e[i]
    return out * np.sqrt(1 - rho ** 2)


def null_panel(rng, rho):
    enso = rng.normal(0, 1, len(YEARS))
    return pd.concat([pd.DataFrame({"region": r, "year": YEARS, "enso_djf": enso,
                                    "log_burn": 10 + i + 0.5 * ar1(rng, len(YEARS), rho)})
                      for i, r in enumerate(H4_REGIONS)], ignore_index=True)


def null_series(rng, rho, n=42):
    years = np.arange(1984, 1984 + n)
    return pd.DataFrame({"year": years, "enso_djf": rng.normal(0, 1, n),
                         "log_burn": 10 + 0.5 * ar1(rng, n, rho)})


def main(reps: int = 1000) -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []
    for rho in (0.0, 0.3):
        hits = dict.fromkeys(["DK contrast", "DK joint F", "clustered contrast",
                              "clustered joint F", "HAC two-sided", "HAC one-sided"], 0)
        for _ in range(reps):
            df = null_panel(rng, rho)
            for tag, fit in (("DK", stats.fit_driscoll_kraay(stats.H4_FORMULA, df)),
                             ("clustered", stats.fit_pooled(stats.H4_FORMULA, df))):
                out = stats.h4_test(fit)
                hits[f"{tag} contrast"] += out["contrast"]["p"] < 0.05
                hits[f"{tag} joint F"] += out["joint"]["p"] < 0.05
            fit = stats.fit_ols_hac("log_burn ~ enso_djf + year", null_series(rng, rho))
            hits["HAC two-sided"] += stats.coef_test(fit, "enso_djf")["p"] < 0.05
            hits["HAC one-sided"] += stats.coef_test(fit, "enso_djf", "greater")["p"] < 0.05
        rows += [{"rho": rho, "test": k, "rejection_rate": v / reps} for k, v in hits.items()]
    table = pd.DataFrame(rows).pivot(index="test", columns="rho", values="rejection_rate")
    print(f"share of {reps} null datasets with p < 0.05 (nominal 0.05; "
          f"Monte Carlo SE {np.sqrt(0.05 * 0.95 / reps):.3f})")
    print(table.round(3).to_string())


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
