"""The hypothesis runner (Phase 4): every registered test of ANALYSIS_PLAN.md
and the runs reported beside them, in one pass (owner, 2026-10-12;
DECISIONS.md 2026-10-12 "First hypothesis runs planned"; D73, D75, D82).

main() calls run_guard.preflight first, opens tables only through
pin_inputs.load_input (the raw ONI and RONI files through
pin_inputs.enso_raw_path), computes every table before writing any, and
writes only through run_guard.write_result. Nothing computed is printed:
the run reports file names and row counts.

Tables written to results/tables/<run>/:
  registered_tests.csv  the 52 registered tests in plan order (H1, H2, H3a,
            H3b, H4, H5, H6, C1, C2), Holm and BH within each family of
            CORRECTION_FAMILIES, the size label and the plain OLS check
  reported_beside.csv   uncorrected, `run_kind` naming each: oni_robustness,
            frozen_rules, parks_nbac, zero_fire, station_z, strong_only,
            strong_flip, h4_secondary, h6_combined, block_bootstrap, h3_gap,
            lag1_autocorrelation
  validation.csv        leave-one-year-out and expanding-window checks of
            the H3a and single-predictor H6 models, and the trend-only model

Columns run effect size, CI, percent change, then p-values (ANALYSIS_PLAN
"Reporting rules"). The 2027 forecast intervals are not made here: the DJF
2027 RONI value does not exist yet.

Run:  python -m src.run_hypotheses --run run1
"""
from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from src import pin_inputs, run_guard, stats
from src.config import (ALPHA, CLIMATE_FIRST_YEAR, COMPOUNDING_REGIONS, CORRECTION_FAMILIES,
                        ENSO_INDEX, ENSO_ROBUSTNESS_INDEX, FIRE_FIRST_YEAR,
                        FIRE_LAST_YEAR_BY_REGION, H1_VALUE, H4_NORTH, H4_REFERENCE, H4_REGIONS,
                        N_BOOTSTRAP, N_PERMUTATIONS, PARKS_GAP_SEASONS, POOLED_LAST_YEAR,
                        PREDICTION_ALPHA, RESULTS, SWE_CHECK_COLUMN, SWE_TEST_COLUMN,
                        TEST_DIRECTIONS, ZERO_YEAR_PCT_LIMIT)
from src.download_oni import classify_winters, parse

INPUTS = {"fire": "fire_region_year.csv", "frozen": "fire_region_year_frozen_rules.csv",
          "parks": "fire_region_year_parks_nbac.csv",
          "controls": "climate_controls_region_year.csv",
          "swe": "station_swe_region_year.csv", "spei": "whiplash_swe_region_year.csv"}
OUTPUTS = ("registered_tests.csv", "reported_beside.csv", "validation.csv")

INTERACTION = "enso_djf:year_c"
H3A_FORMULA = "log_burn ~ enso_djf + year"
H5_FORMULA = "log_burn ~ precip_anom_lag0 + precip_anom_lag1 + year"
# test -> (formula, tested coefficient); ANALYSIS_PLAN "Headline methods",
# "Supporting methods" and "Secondary tests: compounding"
REGRESSIONS = {
    "H3a": (H3A_FORMULA, "enso_djf"),
    "H3b": ("log_burn ~ enso_djf + temp_jja + year", "enso_djf"),
    "H5_lag0": (H5_FORMULA, "precip_anom_lag0"),
    "H5_lag1": (H5_FORMULA, "precip_anom_lag1"),
    "H6_swe": ("log_burn ~ swe_z + year", "swe_z"),
    "H6_spei": ("log_burn ~ spei3_djf + year", "spei3_djf"),
    "C1": (f"swe_z ~ enso_djf + year_c + {INTERACTION}", INTERACTION),
    "C2": (f"log_burn ~ enso_djf + year_c + {INTERACTION}", INTERACTION),
}
H6_COMBINED = "log_burn ~ swe_z + spei3_djf + year"
TREND_ONLY = "log_burn ~ year"
PLAN_ORDER = ("H1", "H2", "H3a", "H3b", "H4", "H5_lag0", "H5_lag1", "H6_swe", "H6_spei",
              "C1", "C2")
# every burned-area test (zero-fire, frozen-rules and Parks Canada runs)
BURN_TESTS = ("H2", "H3a", "H3b", "H4", "H5_lag0", "H5_lag1", "H6_swe", "H6_spei", "C2")
# registered tests that use the ENSO index (ONI robustness runs; D52)
ONI_FIRE_TESTS = ("H2", "H3a", "H3b", "H4", "C2")
CLIMATE_TESTS = ("H1", "C1")
H4_REGION_LABEL = f"{'/'.join(H4_NORTH)} minus {H4_REFERENCE}"

COLUMNS = ["run_kind", "enso_index", "fire_table", "family", "test", "region", "term",
           "outcome", "method", "alternative", "years", "n", "n_group", "n_zero",
           "estimate", "ci_low", "ci_high", "ci_method", "pct_change", "pct_low", "pct_high",
           "se", "statistic", "df", "p", "p_holm", "p_bh", "significant",
           "size", "size_shape", "plain_ols_p", "plain_ols_size", "note"]
VALIDATION_COLUMNS = ["model", "formula", "region", "method", "years", "n", "interval",
                      "coverage", "rmse", "mae", "rmse_trend", "mae_trend", "skill"]


# --- frames -------------------------------------------------------------------

def fire_frame(fire: pd.DataFrame, controls: pd.DataFrame, swe: pd.DataFrame,
               spei: pd.DataFrame) -> pd.DataFrame:
    """One row per region and fire season (FIRE_FIRST_YEAR to the region's
    FIRE_LAST_YEAR_BY_REGION) with the outcome and every predictor the
    burned-area tests read. `swe_z` is SWE_TEST_COLUMN, `swe_station_z` the
    station check."""
    out = fire[["region", "year", "log_burn", "zero_fire", "enso_djf", "phase"]].copy()
    out = out[(out["year"] >= FIRE_FIRST_YEAR)
              & (out["year"] <= out["region"].map(FIRE_LAST_YEAR_BY_REGION))]
    for table, cols in ((controls, ["temp_jja", "precip_anom_lag0", "precip_anom_lag1"]),
                        (swe, [SWE_TEST_COLUMN, SWE_CHECK_COLUMN]), (spei, ["spei3_djf"])):
        out = out.merge(table[["region", "year", *cols]], on=["region", "year"], how="left",
                        validate="one_to_one")
    out = out.rename(columns={SWE_TEST_COLUMN: "swe_z", SWE_CHECK_COLUMN: "swe_station_z"})
    return out.sort_values(["region", "year"]).reset_index(drop=True)


def climate_frame(controls: pd.DataFrame, swe: pd.DataFrame) -> pd.DataFrame:
    """One row per region and winter from CLIMATE_FIRST_YEAR + 1 (H1, C1)."""
    out = controls[["region", "year", H1_VALUE, "enso_djf", "phase"]].merge(
        swe[["region", "year", SWE_TEST_COLUMN, SWE_CHECK_COLUMN]], on=["region", "year"],
        how="left", validate="one_to_one")
    out = out[out["year"] >= CLIMATE_FIRST_YEAR + 1]
    out = out.rename(columns={SWE_TEST_COLUMN: "swe_z", SWE_CHECK_COLUMN: "swe_station_z"})
    return out.sort_values(["region", "year"]).reset_index(drop=True)


def with_index(frame: pd.DataFrame, winters: pd.DataFrame) -> pd.DataFrame:
    """`frame` with enso_djf and phase taken from `winters` (one row per
    year, as download_oni.classify_winters) instead of its own."""
    out = frame.drop(columns=["enso_djf", "phase"]).merge(
        winters[["year", "enso_djf", "phase"]], on="year", how="left", validate="many_to_one")
    if out["enso_djf"].isna().any():
        missing = sorted(out.loc[out["enso_djf"].isna(), "year"].unique())
        raise ValueError(f"No index value for year(s) {missing}.")
    return out.sort_values(["region", "year"]).reset_index(drop=True)


def check_index(frame: pd.DataFrame, winters: pd.DataFrame) -> None:
    """Raise unless the frame's enso_djf equals `winters` year by year: the
    committed tables must hold the pinned raw file's values."""
    merged = frame.merge(winters[["year", "enso_djf"]], on="year", how="left",
                         suffixes=("", "_raw"), validate="many_to_one")
    if not np.allclose(merged["enso_djf"], merged["enso_djf_raw"], rtol=0, atol=1e-9):
        raise ValueError("enso_djf in the input tables differs from the pinned raw index file.")


def _region(frame: pd.DataFrame, region: str) -> pd.DataFrame:
    return frame[frame["region"] == region].sort_values("year").reset_index(drop=True)


def _years(g: pd.DataFrame) -> str:
    return f"{int(g['year'].min())}-{int(g['year'].max())}"


# --- one test, one row --------------------------------------------------------

def _percent(row: dict, g: pd.DataFrame) -> dict:
    """Percent-change columns for an estimate on log_burn, left empty where
    zero-fire seasons exceed ZERO_YEAR_PCT_LIMIT of the rows (ANALYSIS_PLAN
    "Zero-fire years")."""
    if g["zero_fire"].astype(bool).mean() <= ZERO_YEAR_PCT_LIMIT:
        row.update(pct_change=float(stats.percent_change(row["estimate"])),
                   pct_low=float(stats.percent_change(row["ci_low"])),
                   pct_high=float(stats.percent_change(row["ci_high"])))
    return row


def _t_fields(res: dict) -> dict:
    return {"estimate": res["estimate"], "ci_low": res["ci_low"], "ci_high": res["ci_high"],
            "ci_method": "t, 95%", "se": res["se"], "statistic": res["t"], "df": res["df"],
            "p": res["p"], "alternative": res["alternative"]}


def diff_row(g: pd.DataFrame, value: str, in_group, alternative: str,
             n_perm: int, n_boot: int) -> dict:
    """Difference in means of the detrended `value`, group minus rest:
    permutation p and percentile bootstrap CI (H1, H2, strong-only)."""
    in_group = np.asarray(in_group, dtype=bool)
    if in_group.sum() < 2 or (~in_group).sum() < 2:
        raise ValueError(f"{g['region'].iloc[0]}: a group of {int(in_group.sum())} against "
                         f"{int((~in_group).sum())} years cannot be compared.")
    detr = stats.detrend(g, value).to_numpy()
    perm = stats.permutation_test(detr, in_group, n_perm=n_perm, alternative=alternative)
    ci = stats.bootstrap_ci_diff(detr, in_group, n_boot=n_boot)
    return {"term": "group minus rest", "outcome": f"{value}, detrended",
            "method": "permutation test", "alternative": alternative, "years": _years(g),
            "n": len(g), "n_group": perm["n_group"], "estimate": perm["diff"],
            "ci_low": ci["ci_low"], "ci_high": ci["ci_high"],
            "ci_method": "percentile bootstrap, 95%", "p": perm["p"],
            "note": f"{ci['n_distinct_group']} distinct resamples of the group"}


def coef_row(test: str, region: str, g: pd.DataFrame, zero: bool = False) -> dict:
    """One per-region regression test: Newey-West estimate, CI and p in the
    registered direction, its size label, and the plain OLS p where that
    check is reported. `zero` adds the zero-fire indicators."""
    formula, term = REGRESSIONS[test]
    alternative = TEST_DIRECTIONS[test][region]
    if "year_c" in formula:
        g = g.assign(year_c=stats.center_year(g))
    data = g
    if zero:
        formula, data = stats.with_zero_indicators(formula, g)
    row = _t_fields(stats.coef_test(stats.fit_ols_hac(formula, data), term, alternative))
    outcome = formula.split("~")[0].strip()
    row.update(term=term, outcome=outcome, method="Newey-West", years=_years(g), n=len(g))
    if outcome == "log_burn":
        row["n_zero"] = int(g["zero_fire"].sum())
        _percent(row, g)
    shape = run_guard.size_shape(test, region)
    row.update(size=run_guard.size_label(shape)["size"], size_shape=shape)
    plain = run_guard.plain_ols_shape(test, region)
    if plain is not None:
        check = stats.coef_test(stats.fit_ols_plain(formula, data), term, alternative)
        row.update(plain_ols_p=check["p"], plain_ols_size=run_guard.size_label(plain)["size"])
    return row


def h4_panel(frame: pd.DataFrame) -> pd.DataFrame:
    """H4's balanced panel: H4_REGIONS, seasons to POOLED_LAST_YEAR (D57)."""
    panel = frame[frame["region"].isin(H4_REGIONS) & (frame["year"] <= POOLED_LAST_YEAR)]
    return panel.sort_values(["region", "year"]).reset_index(drop=True)


def h4_rows(panel: pd.DataFrame, formula: str = stats.H4_FORMULA, zero: bool = False,
            secondary: bool = False) -> list[dict]:
    """The H4 contrast with Driscoll-Kraay errors (the registered test when
    `formula` is H4_FORMULA). `secondary` adds its joint F test and the
    year-clustered contrast and joint F. Size labels are those measured for
    H4_FORMULA and are left empty for another formula."""
    labelled = formula == stats.H4_FORMULA
    base = {"region": H4_REGION_LABEL, "outcome": "log_burn", "years": _years(panel),
            "n": len(panel), "n_zero": int(panel["zero_fire"].sum())}
    data = panel
    if zero:
        formula, data = stats.with_zero_indicators(formula, panel)
    fits = [("Driscoll-Kraay", "", stats.fit_driscoll_kraay(formula, data))]
    if secondary:
        fits.append(("year-clustered", "_clustered", stats.fit_pooled(formula, data)))
    rows = []
    for method, suffix, fit in fits:
        res = stats.h4_test(fit)
        kinds = [("contrast", _percent({**_t_fields(res["contrast"]),
                                        "term": "mean north slope minus SoCal slope"}, panel))]
        if secondary:
            joint = res["joint"]
            kinds.append(("joint_f", {"term": "all four interactions", "statistic": joint["F"],
                                      "df": joint["df_den"], "p": joint["p"], "alternative": "F",
                                      "note": f"F({joint['df_num']}, {joint['df_den']:g})"}))
        for kind, fields in kinds:
            row = {**base, **fields, "method": method}
            if labelled:
                shape = run_guard.size_shape("H4", kind + suffix)
                row.update(size=run_guard.size_label(shape)["size"], size_shape=shape)
            rows.append(row)
    return rows


# --- groups of tests ----------------------------------------------------------

def _regions(test: str, only=None) -> list[str]:
    return [r for r, alt in TEST_DIRECTIONS[test].items()
            if alt is not None and (only is None or r in only)]


def fire_rows(frame: pd.DataFrame, tests=BURN_TESTS, regions=None, zero: bool = False,
              n_perm: int = N_PERMUTATIONS, n_boot: int = N_BOOTSTRAP) -> list[dict]:
    """Burned-area tests on one fire frame. `regions` limits the per-region
    tests (H4 is kept when any of them is in its panel); `zero` is the
    zero-fire sensitivity run, made only where a zero-fire season exists
    (H2 drops those seasons and detrends without them, regressions and H4
    add indicators)."""
    rows = []
    for test in tests:
        if test == "H4":
            panel = h4_panel(frame)
            in_panel = regions is None or set(regions) & set(H4_REGIONS)
            if in_panel and (not zero or panel["zero_fire"].any()):
                rows += [{"test": "H4", **row} for row in h4_rows(panel, zero=zero)]
            continue
        for region in _regions(test, regions):
            g = _region(frame, region)
            if zero and not g["zero_fire"].any():
                continue
            if test == "H2":
                kept = g[~g["zero_fire"].astype(bool)].reset_index(drop=True) if zero else g
                row = diff_row(kept, "log_burn", kept["phase"] == "el_nino",
                               TEST_DIRECTIONS[test][region], n_perm, n_boot)
                row["n_zero"] = int(g["zero_fire"].sum())
            else:
                row = coef_row(test, region, g, zero=zero)
            rows.append({"test": test, "region": region, **row})
    return rows


def climate_rows(frame: pd.DataFrame, tests=CLIMATE_TESTS, n_perm: int = N_PERMUTATIONS,
                 n_boot: int = N_BOOTSTRAP) -> list[dict]:
    """H1 (DJF precipitation, El Nino winters against the rest) and C1
    (snowpack x centred year) on the climate frame."""
    rows = []
    for test in tests:
        for region in _regions(test):
            g = _region(frame, region)
            if test == "H1":
                row = diff_row(g, H1_VALUE, g["phase"] == "el_nino",
                               TEST_DIRECTIONS[test][region], n_perm, n_boot)
            else:
                row = coef_row(test, region, g)
            rows.append({"test": test, "region": region, **row})
    return rows


def station_rows(fire: pd.DataFrame, climate: pd.DataFrame) -> list[dict]:
    """H6 SWE and C1 repeated on the station index z, over each region's
    station record (ANALYSIS_PLAN "HAC series"); regions without one are
    left out."""
    rows = []
    for test, frame in (("H6_swe", fire), ("C1", climate)):
        for region in _regions(test):
            g = _region(frame, region)
            g = g[g["swe_station_z"].notna()].assign(swe_z=lambda d: d["swe_station_z"])
            if len(g):
                rows.append({"test": test, "region": region,
                             **coef_row(test, region, g.reset_index(drop=True)),
                             "note": "station index z in place of the ERA5-Land z"})
    return rows


def strong_rows(fire: pd.DataFrame, climate: pd.DataFrame, flip: bool, n_perm: int,
                n_boot: int) -> list[dict]:
    """Strong El Nino winters against all other years for H1 and H2
    (exploratory, two-sided, uncorrected; D53); `flip` flips the flag of
    every winter in the near-threshold band together (D52)."""
    rows = []
    for test, frame, value in (("H1", climate, H1_VALUE), ("H2", fire, "log_burn")):
        for region in _regions(test):
            g = _region(frame, region)
            strong = stats.strong_flags(g["enso_djf"], flip_band=flip)
            rows.append({"test": test, "region": region,
                         **diff_row(g, value, strong, "two-sided", n_perm, n_boot)})
    return rows


def h6_combined_rows(fire: pd.DataFrame) -> list[dict]:
    """Both H6 predictors together (reported, not tested), two-sided, where
    both are tested alone."""
    rows = []
    for region in [r for r in _regions("H6_swe") if r in _regions("H6_spei")]:
        g = _region(fire, region)
        fit = stats.fit_ols_hac(H6_COMBINED, g)
        for term in ("swe_z", "spei3_djf"):
            row = _percent(_t_fields(stats.coef_test(fit, term)), g)
            rows.append({"test": "H6_combined", "region": region, "term": term,
                         "outcome": "log_burn", "method": "Newey-West", "years": _years(g),
                         "n": len(g), "n_zero": int(g["zero_fire"].sum()), **row})
    return rows


def _beta(d: pd.DataFrame, cols: list[str]) -> np.ndarray:
    """OLS coefficients of log_burn on an intercept and `cols` (year
    centred, which leaves the other slopes unchanged)."""
    x = [d[c].to_numpy(dtype=float) - (d[c].mean() if c == "year" else 0.0) for c in cols]
    design = np.column_stack([np.ones(len(d)), *x])
    return np.linalg.lstsq(design, d["log_burn"].to_numpy(dtype=float), rcond=None)[0]


def _enso_h3a(d: pd.DataFrame) -> float:
    return float(_beta(d, ["enso_djf", "year"])[1])


def _enso_h3b(d: pd.DataFrame) -> float:
    return float(_beta(d, ["enso_djf", "temp_jja", "year"])[1])


def block_rows(fire: pd.DataFrame, n_boot: int = N_BOOTSTRAP) -> list[dict]:
    """Moving-block bootstrap CIs of the enso_djf coefficients of H3a and
    H3b (the check on the HAC results), and of their gap, H3a minus H3b
    (reported with a CI, not tested)."""
    rows = []
    for region in _regions("H3a"):
        g = _region(fire, region)
        for kind, test, stat in (("block_bootstrap", "H3a", _enso_h3a),
                                 ("block_bootstrap", "H3b", _enso_h3b),
                                 ("h3_gap", "H3a minus H3b",
                                  lambda d: _enso_h3a(d) - _enso_h3b(d))):
            ci = stats.block_bootstrap_ci(g, stat, n_boot=n_boot)
            row = {"estimate": ci["estimate"], "ci_low": ci["ci_low"], "ci_high": ci["ci_high"]}
            rows.append({"run_kind": kind, "test": test, "region": region, "term": "enso_djf",
                         "outcome": "log_burn", "method": "OLS", "years": _years(g),
                         "n": len(g), "n_zero": int(g["zero_fire"].sum()),
                         "ci_method": f"moving-block bootstrap, blocks of {ci['block_len']}, 95%",
                         **_percent(row, g)})
    return rows


def lag1_rows(fire: pd.DataFrame, climate: pd.DataFrame) -> list[dict]:
    """Lag-1 autocorrelation of each outcome series: log_burn and its
    detrended residuals (every region), detrended H1 precipitation and the
    C1 snowpack z (their tested regions)."""
    series = []
    for region in FIRE_LAST_YEAR_BY_REGION:
        g = _region(fire, region)
        series += [(region, "log_burn", g),
                   (region, "log_burn, detrended", g.assign(v=stats.detrend(g, "log_burn")))]
    for region in _regions("H1"):
        g = _region(climate, region)
        series.append((region, f"{H1_VALUE}, detrended", g.assign(v=stats.detrend(g, H1_VALUE))))
    for region in _regions("C1"):
        series.append((region, "swe_z", _region(climate, region)))
    return [{"run_kind": "lag1_autocorrelation", "region": region, "outcome": outcome,
             "method": "lag-1 autocorrelation", "years": _years(g), "n": len(g),
             "estimate": stats.lag1_autocorrelation(g, "v" if "v" in g else outcome)}
            for region, outcome, g in series]


def validation_rows(fire: pd.DataFrame) -> list[dict]:
    """Leave-one-year-out and expanding-window checks of the H3a and the two
    single-predictor H6 models, with the trend-only model's expanding-window
    error and each model's skill against it (D50, D53)."""
    interval = f"{100 * (1 - PREDICTION_ALPHA):g}%"
    rows = []
    for model in ("H3a", "H6_swe", "H6_spei"):
        formula = REGRESSIONS[model][0]
        for region in (FIRE_LAST_YEAR_BY_REGION if model == "H3a" else _regions(model)):
            g = _region(fire, region)
            base = {"region": region, "years": _years(g), "interval": interval}
            loyo = stats.loyo_prediction(formula, g)
            err = (loyo["actual"] - loyo["predicted"]).to_numpy(dtype=float)
            rows.append({**base, "model": model, "formula": formula,
                         "method": "leave-one-year-out", "n": len(loyo),
                         "coverage": float(loyo["covered"].mean()),
                         "rmse": float(np.sqrt(np.mean(err ** 2))),
                         "mae": float(np.mean(np.abs(err)))})
            forward = stats.expanding_window(formula, g)
            trend = stats.expanding_window(TREND_ONLY, g)
            skill = stats.forecast_skill(forward, trend)
            summary = stats.validation_summary(forward)
            held = f"{int(forward['year'].min())}-{int(forward['year'].max())}"
            rows.append({**base, "model": model, "formula": formula, "years": held,
                         "method": "expanding window", "n": summary["n"],
                         "coverage": summary["coverage"], "rmse": summary["rmse"],
                         "mae": summary["mae"], "rmse_trend": skill["rmse_trend"],
                         "mae_trend": skill["mae_trend"], "skill": skill["skill"]})
            if model == "H3a":
                summary = stats.validation_summary(trend)
                rows.append({**base, "model": "trend only", "formula": TREND_ONLY,
                             "years": held, "method": "expanding window", "n": summary["n"],
                             "coverage": summary["coverage"], "rmse": summary["rmse"],
                             "mae": summary["mae"]})
    return rows


# --- the registered set and its corrections ------------------------------------

def add_corrections(rows: list[dict]) -> list[dict]:
    """Holm and BH within each family of CORRECTION_FAMILIES, significance
    by Holm at ALPHA (D50); H4 is a family of one. Raises unless the rows
    are exactly the registered tests."""
    by_key = {(row["test"], row["region"]): row for row in rows}
    if len(by_key) != len(rows):
        raise ValueError("A registered test appears twice.")
    done = 0
    for family in CORRECTION_FAMILIES:
        tests = stats.family_tests(family)
        adjusted = stats.run_family(family, {key: by_key[key]["p"] for key in tests if key in by_key})
        for _, adj in adjusted.iterrows():
            by_key[(adj["test"], adj["region"])].update(
                family=family, p_holm=adj["p_holm"], p_bh=adj["p_bh"],
                significant=bool(adj["significant"]))
        done += len(tests)
    h4 = by_key[("H4", H4_REGION_LABEL)]
    h4.update(family="H4", p_holm=h4["p"], p_bh=h4["p"], significant=bool(h4["p"] < ALPHA))
    if done + 1 != len(rows):
        raise ValueError(f"{len(rows)} rows for {done + 1} registered tests.")
    return rows


def _tag(rows: list[dict], **fields) -> list[dict]:
    return [{**fields, **row} for row in rows]


def compute_all(tables: dict[str, pd.DataFrame], robustness_winters: pd.DataFrame,
                n_perm: int = N_PERMUTATIONS, n_boot: int = N_BOOTSTRAP) -> dict[str, pd.DataFrame]:
    """Every output table from the input tables (keys of INPUTS) and the
    classified winters of ENSO_ROBUSTNESS_INDEX. Reads no file."""
    draws = {"n_perm": n_perm, "n_boot": n_boot}
    side = (tables["controls"], tables["swe"], tables["spei"])
    fire = fire_frame(tables["fire"], *side)
    climate = climate_frame(tables["controls"], tables["swe"])
    main = {"enso_index": ENSO_INDEX, "fire_table": INPUTS["fire"]}

    registered = fire_rows(fire, **draws) + climate_rows(climate, **draws)
    registered.sort(key=lambda row: PLAN_ORDER.index(row["test"]))  # stable: region order kept
    registered = _tag(add_corrections(registered), run_kind="registered", **main)

    oni = {"enso_index": ENSO_ROBUSTNESS_INDEX, "fire_table": INPUTS["fire"]}
    fire_oni, climate_oni = with_index(fire, robustness_winters), with_index(climate, robustness_winters)
    beside = _tag(fire_rows(fire_oni, ONI_FIRE_TESTS, **draws) + climate_rows(climate_oni, **draws),
                  run_kind="oni_robustness", **oni)
    beside += _tag(fire_rows(fire_frame(tables["frozen"], *side), **draws),
                   run_kind="frozen_rules", enso_index=ENSO_INDEX, fire_table=INPUTS["frozen"])
    beside += _tag(fire_rows(fire_frame(tables["parks"], *side), regions=tuple(PARKS_GAP_SEASONS),
                             **draws),
                   run_kind="parks_nbac", enso_index=ENSO_INDEX, fire_table=INPUTS["parks"])
    beside += _tag(fire_rows(fire, zero=True, **draws), run_kind="zero_fire", **main)
    beside += _tag(station_rows(fire, climate), run_kind="station_z", **main)
    for tags, f, c in ((main, fire, climate), (oni, fire_oni, climate_oni)):
        for flip in (False, True):
            beside += _tag(strong_rows(f, c, flip, **draws),
                           run_kind="strong_flip" if flip else "strong_only", **tags)
    panel = h4_panel(fire)
    secondary = h4_rows(panel, secondary=True)[1:]  # the first row is the registered contrast
    secondary += [{**row, "note": "model with temp_jja"}
                  for row in h4_rows(panel, stats.H4_FORMULA_TEMP, secondary=True)]
    beside += _tag(secondary, run_kind="h4_secondary", test="H4", **main)
    beside += _tag(h6_combined_rows(fire), run_kind="h6_combined", **main)
    beside += _tag(block_rows(fire, n_boot), **main)
    beside += _tag(lag1_rows(fire, climate), **main)

    return {"registered_tests.csv": pd.DataFrame(registered, columns=COLUMNS),
            "reported_beside.csv": pd.DataFrame(beside, columns=COLUMNS),
            "validation.csv": pd.DataFrame(validation_rows(fire), columns=VALIDATION_COLUMNS)}


def main(run: str) -> None:
    if not re.fullmatch(r"run[1-9]\d*", run):
        raise SystemExit(f"--run takes run1, run2, ...; got {run!r}.")
    existing = [name for name in OUTPUTS if (RESULTS / "tables" / run / name).exists()]
    if existing:
        raise SystemExit(f"results/tables/{run}/ already holds {existing}; results are never "
                         "overwritten (docs/post_results_protocol.md).")
    passed = run_guard.preflight(run=run)
    tables = {key: pin_inputs.load_input(name) for key, name in INPUTS.items()}
    raw = {index: pin_inputs.enso_raw_path(index) for index in (ENSO_INDEX, ENSO_ROBUSTNESS_INDEX)}
    winters = {index: classify_winters(parse(path), index) for index, path in raw.items()}
    for key in ("fire", "frozen", "parks", "controls"):
        check_index(tables[key], winters[ENSO_INDEX])
    results = compute_all(tables, winters[ENSO_ROBUSTNESS_INDEX])
    inputs = [f"results/tables/{name}" for name in INPUTS.values()]
    inputs += [path.relative_to(pin_inputs.ROOT.resolve()).as_posix() for path in raw.values()]
    for name, table in results.items():
        path = run_guard.write_result(table, name, run, inputs=inputs, commit=passed["commit"])
        print(f"wrote {path.relative_to(pin_inputs.ROOT)} ({len(table)} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", required=True, help="run folder to write, e.g. run1")
    main(parser.parse_args().run)
