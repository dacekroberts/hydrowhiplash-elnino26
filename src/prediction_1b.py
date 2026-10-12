"""Seasonal-outlook prediction model, version 1b (D83; spec section 8).

Exploratory, and every choice here was made after version 1's results and
all of run1 were seen. Reported apart from the registered tests; the
registered 2027 forecast stays the H3a model.

Five changes to version 1 (src/prediction.py), agreed by the owner on
2026-10-12:
1. each region has its own coefficient per predictor, shrunk toward a
   shared one (two penalties; "no regional departures" is version 1);
2. each region's errors are divided by its own training spread around its
   trend when the penalties are chosen, and in a second skill figure;
3. more spring inputs (PRED_1B_VARIANTS);
4. the yes or no bar is a distance above the region's trend;
5. intervals use the region's own earlier unseen-year errors.

The variants are fixed in config before any is run, and all are written,
with version 1's runs scored the same way beside them (variants.csv).

Usage:
    python -m src.prediction_1b
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from src import prediction, run_guard
from src.config import (FORWARD_MIN_TRAIN_YEARS, N_BOOTSTRAP, PRED_1B_GRID,
                        PRED_1B_MIN_PAST_ERRORS, PRED_1B_RUN, PRED_1B_VARIANTS, PRED_GROUPS,
                        PRED_RUN, PRED_TOP_SHARE, PREDICTION_ALPHA, RANDOM_SEED, RESULTS)
from src.pin_inputs import load_input
from src.run_hypotheses import INPUTS

OUTCOME = prediction.OUTCOME
SNOW_TABLE = "snow_soil_region_year.csv"
EXTRA = {"controls": ("precip_anom_lag1", "temp_mam"), "snow": ("snowfall_frac",)}
V1_RUNS = {"v1": "forecast", "v1_hindsight": "hindsight"}  # variants.csv label -> v1 folder


# --- frame --------------------------------------------------------------------

def frame_1b(fire: pd.DataFrame, controls: pd.DataFrame, swe: pd.DataFrame,
             spei: pd.DataFrame, snow: pd.DataFrame) -> pd.DataFrame:
    """prediction.prediction_frame plus last winter's precipitation anomaly,
    March to May temperature and the snowfall share. Raises on a missing
    value."""
    out = prediction.prediction_frame(fire, controls, swe, spei)
    for table, cols in ((controls, EXTRA["controls"]), (snow, EXTRA["snow"])):
        out = out.merge(table[["region", "year", *cols]], on=["region", "year"], how="left",
                        validate="one_to_one")
    if out.isna().any().any():
        raise ValueError(f"Missing values in {out.columns[out.isna().any()].tolist()}.")
    return out


# --- model --------------------------------------------------------------------

def _prepare(train: pd.DataFrame, predictors, scaled: bool) -> dict:
    """prediction._prepare, plus per region: `spread`, the standard
    deviation of the outcome around the region's trend (the trend-only
    model's training spread); `scale`, that spread when `scaled` and 1
    otherwise, by which the detrended outcome is divided before the fit;
    and the detrended outcome itself (`above_trend`, log points)."""
    prep = prediction._prepare(train, predictors)
    p = len(predictors)
    y = prep["y"].copy()
    blocks = np.zeros((len(y), p * len(prep["regions"])))
    for k, info in enumerate(prep["regions"].values()):
        rows = info["rows"]
        info["above_trend"] = prep["y"][rows].copy()
        info["spread"] = float(np.sqrt(np.sum(prep["y"][rows] ** 2) / (info["n"] - 2)))
        info["scale"] = info["spread"] if scaled else 1.0
        info["block"] = slice(p * (k + 1), p * (k + 2))
        y[rows] /= info["scale"]
        blocks[rows, p * k:p * (k + 1)] = prep["x"][rows]
    design = np.hstack([prep["x"], blocks])  # shared columns, then one block per region
    prep.update(y=y, design=design, gram=design.T @ design, moment=design.T @ y)
    return prep


def _solve(prep: dict, shared: float, regional: float) -> dict:
    """Coefficients per region for one pair of penalties (per training row,
    as in version 1): `shared` on the coefficients every region has in
    common, `regional` on each region's departure from them.
    `regional=np.inf` allows no departures (version 1's model);
    `shared=np.inf` as well gives the trend-only baseline. Returns
    {region: coefficients}, in units of the region's scale."""
    p, n = len(prep["predictors"]), len(prep["y"])
    theta = np.zeros(prep["design"].shape[1])
    if not np.isinf(shared):
        size = p if np.isinf(regional) else len(theta)
        penalty = np.full(size, n * shared)
        penalty[p:] = n * regional if size > p else 0
        theta[:size] = np.linalg.solve(prep["gram"][:size, :size] + np.diag(penalty),
                                       prep["moment"][:size])
    return {region: theta[:p] + theta[info["block"]] for region, info in prep["regions"].items()}


def _predict(prep: dict, betas: dict, new: pd.DataFrame) -> np.ndarray:
    base, rest = prediction._parts(prep, new)
    per_row = np.array([betas[r] * prep["regions"][r]["scale"] for r in new["region"]])
    return base + np.einsum("ij,ij->i", rest, per_row)


def penalty_pairs(grid=PRED_1B_GRID, by_region: bool = True) -> list[tuple[float, float]]:
    """(shared, regional) pairs tried, smallest first. The regional penalty
    may also be infinite (no departures); without `by_region` it always is."""
    regional = [*grid, np.inf] if by_region else [np.inf]
    return [(float(s), float(r)) for s in grid for r in regional]


def choose_penalties(train: pd.DataFrame, predictors, by_region: bool, scaled: bool,
                     grid=PRED_1B_GRID) -> tuple[float, float]:
    """The penalty pair with the lowest leave-one-year-out error inside
    `train` (as prediction.choose_penalty). With `scaled`, each error is
    divided by its region's scale first, so no region decides the penalties
    by the size of its swings. A tie goes to the later, heavier pair."""
    pairs = penalty_pairs(grid, by_region)
    sse = np.zeros(len(pairs))
    for year in np.sort(train["year"].unique()):
        held = train[train["year"] == year]
        prep = _prepare(train[train["year"] != year], predictors, scaled)
        actual = held[OUTCOME].to_numpy(dtype=float)
        scale = held["region"].map(lambda r: prep["regions"][r]["scale"]).to_numpy()
        for k, (shared, regional) in enumerate(pairs):
            error = (actual - _predict(prep, _solve(prep, shared, regional), held)) / scale
            sse[k] += np.sum(error ** 2)
    return pairs[len(pairs) - 1 - int(np.argmin(sse[::-1]))]


# --- scoring on unseen seasons --------------------------------------------------

def expanding_forecast(df: pd.DataFrame, predictors, by_region: bool, scaled: bool,
                       grid=PRED_1B_GRID, min_train: int = FORWARD_MIN_TRAIN_YEARS,
                       top_share: float = PRED_TOP_SHARE,
                       ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Predict every season from seasons before it only (as
    prediction.expanding_forecast), with the version 1b model.

    Returns (predictions, coefficients). Predictions hold, per region and
    year: the prediction and the trend-only prediction; `scale`, the
    region's training spread around its trend (the divisor of the scaled
    skill, whether or not the fit was scaled); `train_spread`, the model's
    training residual spread in log points; and `cut_above_trend`, the
    (1 - top_share) quantile of the training seasons' distances above the
    trend. Intervals and the yes or no columns are added by
    `add_intervals`. Coefficients are one row per year, region and
    predictor, in log points per standard deviation of the predictor."""
    rows, coefs = [], []
    for year in np.sort(df["year"].unique()):
        train = df[df["year"] < year]
        counts = train.groupby("region").size()
        ready = counts.index[counts >= min_train]
        new = df[(df["year"] == year) & df["region"].isin(ready)]
        if new.empty:
            continue
        train = train[train["region"].isin(ready)]
        shared, regional = choose_penalties(train, predictors, by_region, scaled, grid)
        prep = _prepare(train, predictors, scaled)
        betas = _solve(prep, shared, regional)
        nothing = _solve(prep, np.inf, np.inf)
        info = prep["regions"]
        spread = {}
        for region, i in info.items():
            fitted = prep["x"][i["rows"]] @ betas[region] * i["scale"]
            spread[region] = float(np.sqrt(np.sum((i["above_trend"] - fitted) ** 2)
                                           / (i["n"] - 2)))
            for name, value in zip(predictors, betas[region] * i["scale"]):
                coefs.append({"year": int(year), "region": region, "predictor": name,
                              "coefficient": value, "penalty_shared": shared,
                              "penalty_region": regional})
        region = new["region"]
        rows.append(pd.DataFrame({
            "region": region.to_numpy(), "year": int(year),
            "n_train": region.map(counts).to_numpy(),
            "penalty_shared": shared, "penalty_region": regional,
            "actual": new[OUTCOME].to_numpy(dtype=float),
            "predicted": _predict(prep, betas, new),
            "predicted_trend": _predict(prep, nothing, new),
            "scale": region.map(lambda r: info[r]["spread"]).to_numpy(),
            "train_spread": region.map(spread).to_numpy(),
            "cut_above_trend": region.map(
                lambda r: np.quantile(info[r]["above_trend"], 1 - top_share)).to_numpy()}))
    return pd.concat(rows, ignore_index=True), pd.DataFrame(coefs)


def add_intervals(pred: pd.DataFrame, min_past: int = PRED_1B_MIN_PAST_ERRORS,
                  alpha: float = PREDICTION_ALPHA) -> pd.DataFrame:
    """Intervals and the yes or no outcome, from earlier seasons only.

    The spread behind a region's interval for year Y is the root mean
    square of that region's own unseen-year errors before Y, once
    `min_past` of them exist; before that, the training spread
    (`train_spread`; `scale` for the trend-only model). `spread_from` says
    which. "Yes" is an actual value more than `cut_above_trend` above the
    trend-only prediction; its probability is read off the prediction and
    the same spread."""
    z = norm.ppf(1 - alpha / 2)
    out = pred.sort_values(["region", "year"]).reset_index(drop=True)
    for suffix, fallback in (("", "train_spread"), ("_trend", "scale")):
        squared = (out["actual"] - out["predicted" + suffix]) ** 2
        earlier = squared.groupby(out["region"])
        count = earlier.cumcount()
        past = np.sqrt((earlier.cumsum() - squared) / count.where(count > 0))
        use_past = count >= min_past
        spread = past.where(use_past, out[fallback])
        if not suffix:
            out["spread_from"] = np.where(use_past, "past errors", "training")
        out["spread" + suffix] = spread
        out["pi_low" + suffix] = out["predicted" + suffix] - z * spread
        out["pi_high" + suffix] = out["predicted" + suffix] + z * spread
        out["covered" + suffix] = ((out["pi_low" + suffix] <= out["actual"])
                                   & (out["actual"] <= out["pi_high" + suffix]))
        bar = out["predicted_trend"] + out["cut_above_trend"]
        out["p_yes" + suffix] = norm.sf((bar - out["predicted" + suffix]) / spread)
    out["actual_yes"] = out["actual"] > out["predicted_trend"] + out["cut_above_trend"]
    return out.sort_values(["year", "region"]).reset_index(drop=True)


def _scaled(pred: pd.DataFrame) -> pd.DataFrame:
    out = pred.copy()
    for col in ("actual", "predicted", "predicted_trend"):
        out[col] = out[col] / out["scale"]
    return out


def skill_table(pred: pd.DataFrame, groups=PRED_GROUPS, n_boot: int = N_BOOTSTRAP,
                seed: int = RANDOM_SEED) -> pd.DataFrame:
    """prediction.skill_table plus `skill_scaled` and its interval: the same
    skill with every error divided by its region's `scale` first, so each
    region counts about equally in a pooled figure. Within one region the
    two differ only through the scale changing from year to year."""
    table = prediction.skill_table(pred, groups, n_boot, seed)
    scaled = prediction.skill_table(_scaled(pred), groups, n_boot, seed).set_index("scope")
    for col in ("skill", "skill_low", "skill_high"):
        table[col.replace("skill", "skill_scaled")] = table["scope"].map(scaled[col]).to_numpy()
    return table


def rescore_v1(v1: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """Version 1's predictions with version 1b's intervals and yes or no bar,
    so its row in variants.csv is on the same terms. `scale` and
    `cut_above_trend` come from `reference` (any 1b variant: they depend on
    the trend-only fit alone); `train_spread` is recovered from version 1's
    own interval."""
    keys = ["region", "year"]
    out = v1[[*keys, "n_train", "actual", "predicted", "predicted_trend"]].merge(
        reference[[*keys, "scale", "cut_above_trend", "predicted_trend"]], on=keys,
        validate="one_to_one", suffixes=("", "_1b"))
    if len(out) != len(v1) or not np.allclose(out["predicted_trend"], out["predicted_trend_1b"]):
        raise ValueError("Version 1 and version 1b disagree on the trend-only prediction.")
    half = norm.ppf(1 - PREDICTION_ALPHA / 2)
    width = v1.set_index(keys)["pi_high"] - v1.set_index(keys)["predicted"]
    out["train_spread"] = (width / half).reindex(pd.MultiIndex.from_frame(out[keys])).to_numpy()
    return add_intervals(out.drop(columns="predicted_trend_1b"))


def variants_table(skills: dict[str, pd.DataFrame], groups=PRED_GROUPS) -> pd.DataFrame:
    """Every variant's rows for the groups in `groups`, in the order run."""
    rows = [table[table["scope"].isin(groups)].assign(variant=name)
            for name, table in skills.items()]
    out = pd.concat(rows, ignore_index=True)
    return out[["variant", *[c for c in out.columns if c != "variant"]]]


def main() -> None:
    names = [INPUTS[k] for k in prediction.TABLES] + [SNOW_TABLE]
    frame = frame_1b(*(load_input(name) for name in names))
    skills, reference = {}, None
    for variant, (predictors, by_region, scaled) in PRED_1B_VARIANTS.items():
        raw, coefs = expanding_forecast(frame, predictors, by_region, scaled)
        pred = add_intervals(raw)
        reference = pred if reference is None else reference
        skills[variant] = skill_table(pred)
        for name, table in zip(prediction.OUTPUTS, (pred, skills[variant].copy(), coefs)):
            table.insert(0, "variant", variant)
            run_guard.write_result(table, f"{variant}/{name}", PRED_1B_RUN, inputs=names)
        print(f"{variant}: done", flush=True)
    v1 = {}
    for label, folder in V1_RUNS.items():
        v1[label] = skill_table(rescore_v1(
            pd.read_csv(RESULTS / "tables" / PRED_RUN / folder / "predictions.csv"), reference))
    summary = variants_table({**v1, **skills})
    run_guard.write_result(summary, "variants.csv", PRED_1B_RUN,
                           inputs=[*names, *(f"{PRED_RUN}/{f}/predictions.csv"
                                             for f in V1_RUNS.values())])
    print(summary[["variant", "scope", "n", "skill", "skill_low", "skill_high", "skill_scaled",
                   "skill_scaled_low", "skill_scaled_high", "coverage", "bss_trend",
                   "bss_trend_low", "bss_trend_high"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
