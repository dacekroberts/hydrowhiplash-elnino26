"""Seasonal-outlook prediction model, version 1c (D83; spec section 9).

Exploratory, and agreed after version 1b's results and all of run1 were
seen. Reported apart from the registered tests; the registered 2027
forecast stays the H3a model.

Two variants on version 1b's model (src/prediction_1b.py), fixed in config
before either is run:
- last_burn: spring_inputs plus the region's burned area of the season
  before (burn_lag1);
- ceiling: 1b's hindsight plus summer SPEI-3 and summer soil moisture. It
  cannot forecast. It measures how much of the trend-only error the
  summer's seasonal means account for.

variants.csv repeats version 1b's rows above the two new ones.

Usage:
    python -m src.prediction_1c
"""
import pandas as pd

from src import prediction, prediction_1b, run_guard
from src.config import (FORWARD_MIN_TRAIN_YEARS, PRED_1B_RUN, PRED_1C_RUN, PRED_1C_VARIANTS,
                        PRED_GROUPS, RESULTS)
from src.pin_inputs import load_input
from src.run_hypotheses import INPUTS

OUTCOME = prediction.OUTCOME
SUMMER = {"spei": ("spei3_jja",), "snow": ("soil_moisture",)}


def add_last_burn(frame: pd.DataFrame, min_train: int = FORWARD_MIN_TRAIN_YEARS) -> pd.DataFrame:
    """Add `burn_lag1`, the region's outcome of the season before.

    A region's first season has no earlier one in the table: it takes the
    mean of the region's `burn_lag1` over its next `min_train - 1` seasons,
    which are training data at every step of the expanding forecast.
    Raises unless every region's years are consecutive."""
    out = frame.sort_values(["region", "year"]).reset_index(drop=True)
    by_region = out.groupby("region", sort=False)
    if (by_region["year"].diff().dropna() != 1).any():
        raise ValueError("A region's seasons are not consecutive years.")
    out["burn_lag1"] = by_region[OUTCOME].shift(1)
    early = by_region.cumcount() < min_train
    fill = out[early].groupby("region")["burn_lag1"].mean()
    first = out["burn_lag1"].isna()
    out.loc[first, "burn_lag1"] = out.loc[first, "region"].map(fill)
    return out


def frame_1c(fire: pd.DataFrame, controls: pd.DataFrame, swe: pd.DataFrame,
             spei: pd.DataFrame, snow: pd.DataFrame,
             min_train: int = FORWARD_MIN_TRAIN_YEARS) -> pd.DataFrame:
    """prediction_1b.frame_1b plus summer SPEI-3, summer soil moisture and
    last season's burned area. Raises on a missing value."""
    out = prediction_1b.frame_1b(fire, controls, swe, spei, snow)
    for table, cols in ((spei, SUMMER["spei"]), (snow, SUMMER["snow"])):
        out = out.merge(table[["region", "year", *cols]], on=["region", "year"], how="left",
                        validate="one_to_one")
    if out.isna().any().any():
        raise ValueError(f"Missing values in {out.columns[out.isna().any()].tolist()}.")
    return add_last_burn(out, min_train)


def main() -> None:
    names = [INPUTS[k] for k in prediction.TABLES] + [prediction_1b.SNOW_TABLE]
    frame = frame_1c(*(load_input(name) for name in names))
    skills = {}
    for variant, (predictors, by_region, scaled) in PRED_1C_VARIANTS.items():
        raw, coefs = prediction_1b.expanding_forecast(frame, predictors, by_region, scaled)
        pred = prediction_1b.add_intervals(raw)
        skills[variant] = prediction_1b.skill_table(pred)
        for name, table in zip(prediction.OUTPUTS, (pred, skills[variant].copy(), coefs)):
            table.insert(0, "variant", variant)
            run_guard.write_result(table, f"{variant}/{name}", PRED_1C_RUN, inputs=names)
        print(f"{variant}: done", flush=True)
    earlier = f"{PRED_1B_RUN}/variants.csv"
    summary = pd.concat([pd.read_csv(RESULTS / "tables" / earlier),
                         prediction_1b.variants_table(skills, PRED_GROUPS)], ignore_index=True)
    run_guard.write_result(summary, "variants.csv", PRED_1C_RUN, inputs=[*names, earlier])
    print(summary[["variant", "scope", "n", "skill", "skill_low", "skill_high", "skill_scaled",
                   "skill_scaled_low", "skill_scaled_high", "coverage", "bss_trend",
                   "bss_trend_low", "bss_trend_high"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
