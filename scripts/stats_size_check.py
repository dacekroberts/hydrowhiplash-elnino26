"""Size of the gate's tests on synthetic null data (no fire data).

The share of synthetic datasets with no true effect in which each test gives
p < 0.05: a test with the right size rejects about 5% of them. One row per
test shape, with the registered tests whose p it labels (D66; audit
2026-10-08 round 2 L1): the H4 contrast and joint F (Driscoll-Kraay, df =
years - 1, and year-clustered) on a 5-region, 41-year panel; the
per-region Newey-West ENSO coefficient (H3a), the same with a persistent
control (H3b), a persistent predictor (H5, H6, predictor AR(1) 0.27, the
largest real lag-1 autocorrelation) and the enso x year_c interaction over
42 fire seasons (C2) and 76 winters (C1); plus the plain OLS check beside
each (D66; for the H4 contrast measured, not reported, round 2 M1).
Scenarios: errors independent; AR(1) rho 0.3 over years; AR(1) 0.3 with
the regions' errors correlated 0.5 within a year (the realistic case). The
printed labels use that scenario for the H4 panel shapes; a single region's
series has no region correlation, so for the per-region shapes the two
AR(1) 0.3 scenarios are the same model and are pooled into one
"AR(1) 0.3, pooled" row of 2 x reps datasets, which the labels use (audit
2026-10-08 round 3 L4: one 1,000-dataset draw carries about +/- 0.014).
`mc_se` is each row's own Monte Carlo SE at 5%; print it beside the label.
`--bootstrap` adds the year-block bootstrap p (dropped by D66; slow).

Run from the repo root:  python scripts/stats_size_check.py [reps] [--bootstrap]
Writes results/tables/test_size.csv (TEST_SIZE_TABLE); measured values in
docs/methods_register.md "Statistics", row "Test size (simulated)".
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import stats  # noqa: E402
from src.config import H4_NORTH, H4_REGIONS, RANDOM_SEED, TEST_SIZE_TABLE  # noqa: E402

YEARS = np.arange(1984, 2025)
BOOT = 499
LABEL_SCENARIO = "AR(1) 0.3, regions r 0.5"
POOLED_SCENARIO = "AR(1) 0.3, pooled"
SCENARIOS = {"independent": (0.0, 0.0), "AR(1) 0.3": (0.3, 0.0), LABEL_SCENARIO: (0.3, 0.5)}
PANEL_SHAPES = ("H4 ", )  # shapes whose name starts so are fitted on the region panel
PREDICTOR_AR = 0.27
# shape: (registered tests it labels, method, sidedness)
SHAPES = {
    "H4 contrast, DK": ("H4 contrast", "Driscoll-Kraay", "two-sided"),
    "H4 joint F, DK": ("H4 joint F", "Driscoll-Kraay", "F"),
    "H4 contrast, clustered": ("H4 contrast, year-clustered model", "year-clustered", "two-sided"),
    "H4 joint F, clustered": ("H4 joint F, year-clustered model", "year-clustered", "F"),
    "H4 contrast, plain OLS": ("not reported (round 2 M1)", "plain OLS", "two-sided"),
    "H3a, NW one-sided": ("H3a PNW/BC/AB", "Newey-West", "one-sided"),
    "H3a, NW two-sided": ("H3a NorCal, SoCal, AK, YT", "Newey-West", "two-sided"),
    "H3a, plain OLS two-sided": ("H3a check", "plain OLS", "two-sided"),
    "H3a, plain OLS one-sided": ("H3a check, PNW/BC/AB", "plain OLS", "one-sided"),
    "H3b, NW one-sided": ("H3b PNW/BC/AB", "Newey-West", "one-sided"),
    "H3b, NW two-sided": ("H3b NorCal, SoCal, AK, YT", "Newey-West", "two-sided"),
    "H3b, plain OLS two-sided": ("H3b check", "plain OLS", "two-sided"),
    "H3b, plain OLS one-sided": ("H3b check, PNW/BC/AB", "plain OLS", "one-sided"),
    "persistent predictor, NW one-sided": ("H5, H6 one-sided", "Newey-West", "one-sided"),
    "persistent predictor, NW two-sided": ("H5, H6 two-sided", "Newey-West", "two-sided"),
    "C2 interaction, NW two-sided": ("C2", "Newey-West", "two-sided"),
    "C2 interaction, plain OLS two-sided": ("C2 check", "plain OLS", "two-sided"),
    "C1 interaction, NW one-sided": ("C1", "Newey-West", "one-sided"),
    "C1 interaction, plain OLS one-sided": ("C1 check", "plain OLS", "one-sided"),
    "H4 contrast, block bootstrap": ("dropped (D66)", "year-block bootstrap", "two-sided"),
    "H3a, block bootstrap two-sided": ("dropped (D66)", "year-block bootstrap", "two-sided"),
}


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
    """One region's null series: white ENSO, a control persistent at AR 0.5
    and correlated 0.4 with ENSO (temp_jja, H3b), a predictor at
    PREDICTOR_AR (H5, H6), centred year; errors AR(1) rho."""
    years = np.arange(1984, 1984 + n)
    enso = rng.normal(0, 1, n)
    return pd.DataFrame({"year": years, "year_c": years - years.mean(), "enso_djf": enso,
                         "temp_jja": 0.4 * enso + np.sqrt(1 - 0.16) * ar1(rng, (n,), 0.5),
                         "x": ar1(rng, (n,), PREDICTOR_AR),
                         "log_burn": 10 + 0.5 * ar1(rng, (n,), rho)})


def main(reps: int = 1000, bootstrap: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    contrast = {stats.h4_interaction_name(r): 1 / len(H4_NORTH) for r in H4_NORTH}
    h3a = "log_burn ~ enso_djf + year"
    h3b = "log_burn ~ enso_djf + temp_jja + year"
    pers = "log_burn ~ x + year"
    inter = "log_burn ~ enso_djf + year_c + enso_djf:year_c"
    rows = []
    for label, (rho, r_regions) in SCENARIOS.items():
        hits: dict[str, int] = {}

        def hit(name, p):
            hits[name] = hits.get(name, 0) + (p < 0.05)

        def coef(name, formula, data, term, alternative="two-sided", plain=False):
            fit = (stats.fit_ols_plain(formula, data) if plain
                   else stats.fit_ols_hac(formula, data))
            hit(name, stats.coef_test(fit, term, alternative)["p"])

        for _ in range(reps):
            df = null_panel(rng, rho, r_regions)
            for tag, fit in (("DK", stats.fit_driscoll_kraay(stats.H4_FORMULA, df)),
                             ("clustered", stats.fit_pooled(stats.H4_FORMULA, df))):
                out = stats.h4_test(fit)
                hit(f"H4 contrast, {tag}", out["contrast"]["p"])
                hit(f"H4 joint F, {tag}", out["joint"]["p"])
            hit("H4 contrast, plain OLS",
                stats.contrast_test(stats.fit_ols_plain(stats.H4_FORMULA, df), contrast)["p"])
            s = null_series(rng, rho)
            coef("H3a, NW one-sided", h3a, s, "enso_djf", "greater")
            coef("H3a, NW two-sided", h3a, s, "enso_djf")
            coef("H3a, plain OLS two-sided", h3a, s, "enso_djf", plain=True)
            # one-sided check beside the one-sided registered test (owner,
            # 2026-10-11, D80); draws nothing from rng, so every other row
            # reproduces the 2026-10-08 values
            coef("H3a, plain OLS one-sided", h3a, s, "enso_djf", "greater", plain=True)
            coef("H3b, NW one-sided", h3b, s, "enso_djf", "greater")
            coef("H3b, NW two-sided", h3b, s, "enso_djf")
            coef("H3b, plain OLS two-sided", h3b, s, "enso_djf", plain=True)
            coef("H3b, plain OLS one-sided", h3b, s, "enso_djf", "greater", plain=True)
            coef("persistent predictor, NW one-sided", pers, s, "x", "greater")
            coef("persistent predictor, NW two-sided", pers, s, "x")
            coef("C2 interaction, NW two-sided", inter, s, "enso_djf:year_c")
            coef("C2 interaction, plain OLS two-sided", inter, s, "enso_djf:year_c", plain=True)
            w = null_series(rng, rho, n=76)
            coef("C1 interaction, NW one-sided", inter, w, "enso_djf:year_c", "less")
            coef("C1 interaction, plain OLS one-sided", inter, w, "enso_djf:year_c", "less",
                 plain=True)
            if bootstrap:
                hit("H4 contrast, block bootstrap",
                    stats.block_bootstrap_p(stats.H4_FORMULA, df, contrast, n_boot=BOOT,
                                            seed=int(rng.integers(1 << 31)))["p"])
                hit("H3a, block bootstrap two-sided",
                    stats.block_bootstrap_p(h3a, s, {"enso_djf": 1.0}, n_boot=BOOT,
                                            seed=int(rng.integers(1 << 31)))["p"])
        rows += [{"shape": k, "labels": SHAPES[k][0], "method": SHAPES[k][1],
                  "sidedness": SHAPES[k][2], "scenario": label,
                  "label_scenario": label == LABEL_SCENARIO and k.startswith(PANEL_SHAPES),
                  "reps": reps, "rejection_rate": v / reps} for k, v in hits.items()]
    table = pd.DataFrame(rows)
    ar = table[table["scenario"].isin(["AR(1) 0.3", LABEL_SCENARIO])
               & ~table["shape"].str.startswith(PANEL_SHAPES)]
    pooled = (ar.groupby(["shape", "labels", "method", "sidedness"], sort=False)
              .agg(rejection_rate=("rejection_rate", "mean"), reps=("reps", "sum")).reset_index()
              .assign(scenario=POOLED_SCENARIO, label_scenario=True))
    table = pd.concat([table, pooled[table.columns]], ignore_index=True)
    table["mc_se"] = np.sqrt(0.05 * 0.95 / table["reps"])
    table["measured"] = datetime.date.today().isoformat()
    TEST_SIZE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    table.round(4).to_csv(TEST_SIZE_TABLE, index=False, lineterminator="\n")
    wide = table.pivot(index="shape", columns="scenario", values="rejection_rate")
    print(f"share of {reps} null datasets with p < 0.05 (nominal 0.05; "
          f"Monte Carlo SE {np.sqrt(0.05 * 0.95 / reps):.3f}, pooled "
          f"{np.sqrt(0.05 * 0.95 / (2 * reps)):.3f})"
          + (f"; bootstrap {BOOT} draws" if bootstrap else ""))
    print(wide[list(SCENARIOS) + [POOLED_SCENARIO]].reindex([k for k in SHAPES if k in wide.index])
          .round(3).to_string())
    labels = table[table["label_scenario"]]
    print("labels:")
    print(labels[["shape", "scenario", "rejection_rate", "mc_se"]].round(3).to_string(index=False))
    print(f"wrote {TEST_SIZE_TABLE}")
    return table


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(int(args[0]) if args else 1000, bootstrap="--bootstrap" in sys.argv)
