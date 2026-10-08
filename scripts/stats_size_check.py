"""Size of the gate's tests on synthetic null data (no fire data).

The share of synthetic datasets with no true effect in which each test gives
p < 0.05: a test with the right size rejects about 5% of them. Covers the H4
contrast and joint F test (Driscoll-Kraay, df = years - 1, and
year-clustered) on a 5-region, 41-year panel, and the per-region Newey-West
coefficient test (H3a shape, 42 years), plus the M1(b) size checks beside
them (plain OLS p, year-block bootstrap p; audit 2026-10-08). Scenarios:
errors independent; AR(1) rho 0.3 over years; AR(1) 0.3 with the regions'
errors correlated 0.5 within a year (the audit's realistic case). Settings
from src/config.py; the bootstrap uses BOOT draws per dataset here (the
analysis uses N_BOOTSTRAP).

Run from the repo root:  python scripts/stats_size_check.py [reps]
Measured 2026-10-08: see docs/methods_register.md "Statistics", row "Test
size (simulated)".
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import stats  # noqa: E402
from src.config import H4_NORTH, H4_REGIONS, RANDOM_SEED  # noqa: E402

YEARS = np.arange(1984, 2025)
BOOT = 499
SCENARIOS = {"independent": (0.0, 0.0), "AR(1) 0.3": (0.3, 0.0),
             "AR(1) 0.3, regions r 0.5": (0.3, 0.5)}


def ar1(rng, shape, rho):
    """AR(1) along the first axis, unit variance."""
    e = rng.normal(0, 1, shape)
    out = np.empty(shape)
    out[0] = e[0]
    for i in range(1, shape[0]):
        out[i] = rho * out[i - 1] + np.sqrt(1 - rho ** 2) * e[i]
    return out


def null_panel(rng, rho, r_regions):
    n, k = len(YEARS), len(H4_REGIONS)
    common = ar1(rng, (n, 1), rho)
    own = ar1(rng, (n, k), rho)
    noise = np.sqrt(r_regions) * common + np.sqrt(1 - r_regions) * own
    enso = rng.normal(0, 1, n)
    return pd.concat([pd.DataFrame({"region": r, "year": YEARS, "enso_djf": enso,
                                    "log_burn": 10 + i + 0.5 * noise[:, i]})
                      for i, r in enumerate(H4_REGIONS)], ignore_index=True)


def null_series(rng, rho, n=42):
    years = np.arange(1984, 1984 + n)
    return pd.DataFrame({"year": years, "enso_djf": rng.normal(0, 1, n),
                         "log_burn": 10 + 0.5 * ar1(rng, (n,), rho)})


def main(reps: int = 1000) -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    contrast = {stats.h4_interaction_name(r): 1 / len(H4_NORTH) for r in H4_NORTH}
    h3a = "log_burn ~ enso_djf + year"
    rows = []
    for label, (rho, r_regions) in SCENARIOS.items():
        hits: dict[str, int] = {}

        def hit(name, p):
            hits[name] = hits.get(name, 0) + (p < 0.05)

        for _ in range(reps):
            df = null_panel(rng, rho, r_regions)
            for tag, fit in (("DK", stats.fit_driscoll_kraay(stats.H4_FORMULA, df)),
                             ("clustered", stats.fit_pooled(stats.H4_FORMULA, df))):
                out = stats.h4_test(fit)
                hit(f"H4 contrast, {tag}", out["contrast"]["p"])
                hit(f"H4 joint F, {tag}", out["joint"]["p"])
            hit("H4 contrast, plain OLS",
                stats.contrast_test(stats.fit_ols_plain(stats.H4_FORMULA, df), contrast)["p"])
            hit("H4 contrast, block bootstrap",
                stats.block_bootstrap_p(stats.H4_FORMULA, df, contrast, n_boot=BOOT,
                                        seed=int(rng.integers(1 << 31)))["p"])
            s = null_series(rng, rho)
            fit = stats.fit_ols_hac(h3a, s)
            hit("H3a shape, Newey-West two-sided", stats.coef_test(fit, "enso_djf")["p"])
            hit("H3a shape, Newey-West one-sided",
                stats.coef_test(fit, "enso_djf", "greater")["p"])
            hit("H3a shape, plain OLS two-sided",
                stats.coef_test(stats.fit_ols_plain(h3a, s), "enso_djf")["p"])
            hit("H3a shape, block bootstrap two-sided",
                stats.block_bootstrap_p(h3a, s, {"enso_djf": 1.0}, n_boot=BOOT,
                                        seed=int(rng.integers(1 << 31)))["p"])
        rows += [{"scenario": label, "test": k, "rejection_rate": v / reps}
                 for k, v in hits.items()]
    table = pd.DataFrame(rows).pivot(index="test", columns="scenario", values="rejection_rate")
    print(f"share of {reps} null datasets with p < 0.05 (nominal 0.05; "
          f"Monte Carlo SE {np.sqrt(0.05 * 0.95 / reps):.3f}); bootstrap {BOOT} draws")
    print(table[list(SCENARIOS)].round(3).to_string())


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
