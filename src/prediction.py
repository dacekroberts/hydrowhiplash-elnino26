"""Seasonal-outlook prediction model, version 1 (D83).

Exploratory: planned after every run1 result was seen, uncorrected and
reported apart from the registered tests; it replaces none of them, and the
registered 2027 forecast stays the H3a model. The scope and every setting
are in docs/prediction_model_spec.md, agreed before any fit.

One pooled linear model across the regions. Each region keeps its own level
and its own year trend, unshrunk; the climate predictors share one
coefficient each across regions and are shrunk (ridge). With a very large
penalty the model is the trend-only baseline exactly, so skill against that
baseline measures what the predictors add and nothing else.

Reads only committed tables in results/tables/ (through
pin_inputs.load_input) and writes to results/tables/<PRED_RUN>/<label>/
through run_guard.write_result, which never overwrites.

Usage:
    python -m src.prediction
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from src import run_guard
from src.config import (FORWARD_MIN_TRAIN_YEARS, N_BOOTSTRAP, PRED_GROUPS,
                        PRED_HINDSIGHT_PREDICTORS, PRED_NO_SNOW_REGIONS, PRED_PREDICTORS,
                        PRED_RIDGE_GRID, PRED_RUN, PRED_SKILL_CI, PRED_TOP_SHARE,
                        PRED_YES_PROBABILITY, PREDICTION_ALPHA, RANDOM_SEED)
from src.pin_inputs import load_input
from src.run_hypotheses import INPUTS, fire_frame

OUTCOME = "log_burn"
TABLES = ("fire", "controls", "swe", "spei")
OUTPUTS = ("predictions.csv", "skill.csv", "coefficients.csv")
# the trend is fitted on year - YEAR_ORIGIN (conditioning only; no effect on a fit)
YEAR_ORIGIN = 2000
INTERVAL_STATS = ("skill", "bss_base", "bss_trend")


# --- frame --------------------------------------------------------------------

def prediction_frame(fire: pd.DataFrame, controls: pd.DataFrame, swe: pd.DataFrame,
                     spei: pd.DataFrame, predictors=PRED_HINDSIGHT_PREDICTORS,
                     no_snow=PRED_NO_SNOW_REGIONS) -> pd.DataFrame:
    """One row per region and fire season with the outcome and `predictors`.

    As run_hypotheses.fire_frame plus precip_octmar_mm. `swe_z` is set to 0
    in the `no_snow` regions (owner, 2026-10-12: "no information", so the
    region stays in the pool); raises if such a region holds a value, or if
    anything else is missing."""
    out = fire_frame(fire, controls, swe, spei).merge(
        controls[["region", "year", "precip_octmar_mm"]], on=["region", "year"], how="left",
        validate="one_to_one")
    blank = out["region"].isin(no_snow)
    if out.loc[blank, "swe_z"].notna().any():
        raise ValueError(f"swe_z holds values in a no-snow region {no_snow}; re-read "
                         "PRED_NO_SNOW_REGIONS.")
    out.loc[blank, "swe_z"] = 0.0
    cols = ["region", "year", OUTCOME, "zero_fire", *predictors]
    if out[cols].isna().any().any():
        missing = out[cols].columns[out[cols].isna().any()].tolist()
        raise ValueError(f"Missing values in {missing}.")
    return out[cols].sort_values(["region", "year"]).reset_index(drop=True)


# --- model --------------------------------------------------------------------

def _trend_design(years) -> np.ndarray:
    t = np.asarray(years, dtype=float) - YEAR_ORIGIN
    return np.column_stack([np.ones_like(t), t])


def _prepare(train: pd.DataFrame, predictors) -> dict:
    """Per region: standardise the predictors on the training seasons, then
    take the region's own level and year trend out of the outcome and out of
    each predictor (plain OLS). Ridge on what is left equals the full model
    with the level and trend terms unpenalised."""
    regions, xs, ys, start = {}, [], [], 0
    for region, g in train.groupby("region", sort=True):
        x = g[list(predictors)].to_numpy(dtype=float)
        mean, sd = x.mean(axis=0), x.std(axis=0, ddof=1)
        sd = np.where(sd > 0, sd, 1.0)  # a constant column (swe_z = 0) stays 0
        z = _trend_design(g["year"])
        if len(g) <= z.shape[1]:
            raise ValueError(f"{region}: {len(g)} training seasons cannot carry a trend.")
        both = np.column_stack([g[OUTCOME].to_numpy(dtype=float), (x - mean) / sd])
        coef, *_ = np.linalg.lstsq(z, both, rcond=None)
        resid = both - z @ coef
        # rows: the region's row range in the stacked arrays
        regions[region] = {"mean": mean, "sd": sd, "trend_y": coef[:, 0],
                           "trend_x": coef[:, 1:], "n": len(g),
                           "rows": slice(start, start + len(g))}
        start += len(g)
        xs.append(resid[:, 1:])
        ys.append(resid[:, 0])
    return {"predictors": tuple(predictors), "regions": regions,
            "x": np.vstack(xs), "y": np.concatenate(ys)}


def _solve(prep: dict, penalty: float) -> dict:
    """Ridge coefficients for one penalty, and each region's residual spread.

    The penalty is per training row: minimise mean squared error +
    penalty * sum(beta^2). `penalty=np.inf` is the trend-only baseline
    (every coefficient 0). The spread is the region's training residual
    standard deviation with the two trend terms taken off the degrees of
    freedom; the shared coefficients are not counted."""
    x, y = prep["x"], prep["y"]
    p = x.shape[1]
    if np.isinf(penalty):
        beta = np.zeros(p)
    else:
        beta = np.linalg.solve(x.T @ x + penalty * len(y) * np.eye(p), x.T @ y)
    resid = y - x @ beta
    spread = {r: float(np.sqrt(np.sum(resid[info["rows"]] ** 2) / (info["n"] - 2)))
              for r, info in prep["regions"].items()}
    return {"predictors": prep["predictors"], "regions": prep["regions"], "beta": beta,
            "penalty": penalty, "spread": spread}


def fit_pooled_ridge(train: pd.DataFrame, predictors=PRED_PREDICTORS,
                     penalty: float = 1.0) -> dict:
    """Fit the pooled model on `train` (columns region, year, log_burn and
    `predictors`) at one penalty. See `_prepare` and `_solve`."""
    return _solve(_prepare(train, predictors), penalty)


def _parts(fitted: dict, new: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Per row of `new`: the region's trend value for the outcome, and the
    standardised predictors with the region's trend taken out. The
    prediction is the first plus the second times the coefficients."""
    base, rest = np.empty(len(new)), np.empty((len(new), len(fitted["predictors"])))
    x = new[list(fitted["predictors"])].to_numpy(dtype=float)
    z = _trend_design(new["year"])
    for region in pd.unique(new["region"]):
        rows = (new["region"] == region).to_numpy()
        info = fitted["regions"][region]
        base[rows] = z[rows] @ info["trend_y"]
        rest[rows] = (x[rows] - info["mean"]) / info["sd"] - z[rows] @ info["trend_x"]
    return base, rest


def predict(model: dict, new: pd.DataFrame) -> np.ndarray:
    """Predicted log_burn for each row of `new`, in its row order."""
    base, rest = _parts(model, new)
    return base + rest @ model["beta"]


def choose_penalty(train: pd.DataFrame, predictors=PRED_PREDICTORS,
                   grid=PRED_RIDGE_GRID) -> tuple[float, np.ndarray]:
    """The penalty in `grid` with the lowest leave-one-year-out error inside
    `train`: each training year is left out in turn (every region's row for
    that year together), the model is fitted on the rest and predicts it.
    Returns the penalty and the mean squared error per grid value. A tie
    goes to the larger penalty. Squared errors are pooled as they are, so
    regions with wide swings weigh most (a stated limit)."""
    grid = np.asarray(grid, dtype=float)
    sse = np.zeros(len(grid))
    for year in np.sort(train["year"].unique()):
        held = train[train["year"] == year]
        prep = _prepare(train[train["year"] != year], predictors)
        # every penalty at once, from one eigendecomposition of x'x
        values, vectors = np.linalg.eigh(prep["x"].T @ prep["x"])
        betas = vectors @ ((vectors.T @ prep["x"].T @ prep["y"])[:, None]
                           / (values[:, None] + grid * len(prep["y"])))
        base, rest = _parts(prep, held)
        error = held[OUTCOME].to_numpy(dtype=float)[:, None] - (base[:, None] + rest @ betas)
        sse += np.sum(error ** 2, axis=0)
    best = len(grid) - 1 - int(np.argmin(sse[::-1]))
    return float(grid[best]), sse / len(train)


# --- scoring on unseen seasons --------------------------------------------------

def expanding_forecast(df: pd.DataFrame, predictors=PRED_PREDICTORS, grid=PRED_RIDGE_GRID,
                       min_train: int = FORWARD_MIN_TRAIN_YEARS,
                       alpha: float = PREDICTION_ALPHA, top_share: float = PRED_TOP_SHARE,
                       ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Predict every season from seasons before it only.

    For each year Y: train on every region-season before Y, choose the
    penalty inside those seasons (`choose_penalty`), and predict year Y for
    every region with at least `min_train` training seasons, all at once.
    The trend-only baseline is the same fit with the predictors switched
    off. Intervals are prediction +- z * the region's training residual
    spread. The yes or no outcome is whether log_burn is above the
    (1 - top_share) quantile of the region's training seasons; its
    probability is read off the same prediction and spread.

    Only the fit is forward-looking: swe_z and spei3_djf are built on fixed
    reference periods that contain later years (trap 8, as in
    stats.expanding_window).

    Returns (predictions, coefficients): one row per region and predicted
    year, and one row per predicted year with the penalty and the
    coefficients per standard deviation of each predictor."""
    z = norm.ppf(1 - alpha / 2)
    rows, coefs = [], []
    for year in np.sort(df["year"].unique()):
        train = df[df["year"] < year]
        counts = train.groupby("region").size()
        ready = counts.index[counts >= min_train]
        new = df[(df["year"] == year) & df["region"].isin(ready)]
        if new.empty:
            continue
        train = train[train["region"].isin(ready)]
        penalty, _ = choose_penalty(train, predictors, grid)
        prep = _prepare(train, predictors)
        fits = {"": _solve(prep, penalty), "_trend": _solve(prep, np.inf)}
        cuts = train.groupby("region")[OUTCOME].quantile(1 - top_share)
        block = pd.DataFrame({"region": new["region"].to_numpy(), "year": int(year),
                              "n_train": new["region"].map(counts).to_numpy(),
                              "penalty": penalty,
                              "actual": new[OUTCOME].to_numpy(dtype=float),
                              "cut": new["region"].map(cuts).to_numpy()})
        block["actual_yes"] = block["actual"] > block["cut"]
        for suffix, fit in fits.items():
            spread = block["region"].map(fit["spread"]).to_numpy()
            pred = predict(fit, new)
            block["predicted" + suffix] = pred
            block["pi_low" + suffix] = pred - z * spread
            block["pi_high" + suffix] = pred + z * spread
            block["covered" + suffix] = ((block["pi_low" + suffix] <= block["actual"])
                                         & (block["actual"] <= block["pi_high" + suffix]))
            block["p_yes" + suffix] = norm.sf((block["cut"].to_numpy() - pred) / spread)
        rows.append(block)
        coefs.append({"year": int(year), "n_train_rows": len(train), "penalty": penalty,
                      **dict(zip(predictors, fits[""]["beta"]))})
    return pd.concat(rows, ignore_index=True), pd.DataFrame(coefs)


def _brier_terms(pred: pd.DataFrame, top_share: float) -> dict[str, np.ndarray]:
    yes = pred["actual_yes"].to_numpy(dtype=float)
    return {"model": (pred["p_yes"].to_numpy() - yes) ** 2,
            "trend": (pred["p_yes_trend"].to_numpy() - yes) ** 2,
            "base": (top_share - yes) ** 2}


def skill_scores(pred: pd.DataFrame, top_share: float = PRED_TOP_SHARE,
                 yes_probability: float = PRED_YES_PROBABILITY) -> dict:
    """Scores over the rows of `pred` (as expanding_forecast).

    skill = 1 - RMSE(model) / RMSE(trend only); above 0 the predictors beat
    the trend. Brier score = mean (probability - outcome)^2 for the yes or
    no outcome; bss_base and bss_trend = 1 - Brier(model) / Brier(reference)
    against a constant `top_share` and against the trend-only probability.
    A "yes" call is a probability of `yes_probability` or more."""
    err = (pred["actual"] - pred["predicted"]).to_numpy()
    err_t = (pred["actual"] - pred["predicted_trend"]).to_numpy()
    rmse, rmse_t = float(np.sqrt(np.mean(err ** 2))), float(np.sqrt(np.mean(err_t ** 2)))
    brier = {k: float(v.mean()) for k, v in _brier_terms(pred, top_share).items()}
    yes = pred["actual_yes"].to_numpy(dtype=bool)
    called = pred["p_yes"].to_numpy() >= yes_probability
    return {"n": len(pred), "rmse": rmse, "rmse_trend": rmse_t, "skill": 1 - rmse / rmse_t,
            "mae": float(np.mean(np.abs(err))), "mae_trend": float(np.mean(np.abs(err_t))),
            "coverage": float(pred["covered"].mean()),
            "coverage_trend": float(pred["covered_trend"].mean()),
            "brier": brier["model"], "brier_trend": brier["trend"], "brier_base": brier["base"],
            "bss_base": 1 - brier["model"] / brier["base"],
            "bss_trend": 1 - brier["model"] / brier["trend"],
            "n_yes": int(yes.sum()), "n_called": int(called.sum()),
            "hits": int((yes & called).sum()), "false_alarms": int((~yes & called).sum())}


def bootstrap_skill(pred: pd.DataFrame, n_boot: int = N_BOOTSTRAP, seed: int = RANDOM_SEED,
                    level: float = PRED_SKILL_CI, top_share: float = PRED_TOP_SHARE) -> dict:
    """Percentile intervals on skill, bss_base and bss_trend from resampling
    the unseen years with replacement. Whole years are drawn, so every
    region's row for a year stays together (regions share a year's weather).
    Returns {stat_low, stat_high}; descriptive, not a test."""
    terms = _brier_terms(pred, top_share)
    terms["err"] = (pred["actual"] - pred["predicted"]).to_numpy() ** 2
    terms["err_trend"] = (pred["actual"] - pred["predicted_trend"]).to_numpy() ** 2
    sums = pd.DataFrame(terms).groupby(pred["year"].to_numpy()).sum()
    draws = np.random.default_rng(seed).integers(0, len(sums), size=(n_boot, len(sums)))
    total = {k: sums[k].to_numpy()[draws].sum(axis=1) for k in sums}
    with np.errstate(divide="ignore", invalid="ignore"):
        stats = {"skill": 1 - np.sqrt(total["err"] / total["err_trend"]),
                 "bss_base": 1 - total["model"] / total["base"],
                 "bss_trend": 1 - total["model"] / total["trend"]}
    tail = (1 - level) / 2
    out = {}
    for name in INTERVAL_STATS:
        low, high = np.nanquantile(stats[name], [tail, 1 - tail])
        out[name + "_low"], out[name + "_high"] = float(low), float(high)
    return out


def skill_table(pred: pd.DataFrame, groups=PRED_GROUPS, n_boot: int = N_BOOTSTRAP,
                seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Scores and intervals for each group in `groups`, then each region."""
    scopes = {**{name: list(members) for name, members in groups.items()},
              **{region: [region] for region in pred["region"].unique()}}
    rows = []
    for scope, members in scopes.items():
        part = pred[pred["region"].isin(members)]
        if part.empty:
            continue
        rows.append({"scope": scope, "years": f"{part['year'].min()}-{part['year'].max()}",
                     **skill_scores(part), **bootstrap_skill(part, n_boot, seed)})
    return pd.DataFrame(rows)


def beats_trend(skill: pd.DataFrame, scope: str = "all seven") -> bool:
    """The agreed rule for version 2 (owner, 2026-10-12): the forecast run's
    skill on log burned area over all regions has an interval wholly above
    zero. Where it does not, the next step is a conversation with the owner,
    not a second model."""
    return bool(skill.set_index("scope").at[scope, "skill_low"] > 0)


# --- runs ---------------------------------------------------------------------

def runs(frame: pd.DataFrame) -> dict[str, tuple[pd.DataFrame, tuple[str, ...]]]:
    """Label -> (frame, predictors). "forecast" is the forecast run;
    "hindsight" adds June to August temperature and cannot forecast;
    "no_zero_fire" is the forecast run without the zero-fire seasons, in
    training and in scoring (SoCal 2014)."""
    return {"forecast": (frame, PRED_PREDICTORS),
            "hindsight": (frame, PRED_HINDSIGHT_PREDICTORS),
            "no_zero_fire": (frame[~frame["zero_fire"].astype(bool)], PRED_PREDICTORS)}


def main() -> None:
    names = [INPUTS[k] for k in TABLES]
    frame = prediction_frame(*(load_input(name) for name in names))
    # one run folder with a sub-folder per label, so run_guard reads the
    # labels as one run and none marks the next as written from a dirty tree
    for label, (data, predictors) in runs(frame).items():
        pred, coefs = expanding_forecast(data, predictors)
        skill = skill_table(pred)
        for name, table in zip(OUTPUTS, (pred, skill, coefs)):
            table.insert(0, "run", label)
            run_guard.write_result(table, f"{label}/{name}", PRED_RUN, inputs=names)
        print(f"\n{PRED_RUN}/{label}: predictors {', '.join(predictors)}")
        print(skill[["scope", "years", "n", "skill", "skill_low", "skill_high", "coverage",
                     "bss_base", "bss_trend"]].round(3).to_string(index=False))
        if label == "forecast":
            print(f"Version 2 rule (interval on pooled skill above zero): {beats_trend(skill)}")


if __name__ == "__main__":
    main()
