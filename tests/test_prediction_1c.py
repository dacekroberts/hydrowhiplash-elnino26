"""Tests for src/prediction_1c.py on synthetic region x year tables: no
committed table and no data/ is read."""
import numpy as np
import pandas as pd
import pytest

from src import prediction_1c
from src.config import PRED_1B_VARIANTS, PRED_1C_VARIANTS, REGIONS
from tests.test_prediction import _tables


def _frame(years=range(1984, 1990)) -> pd.DataFrame:
    rows = [{"region": r, "year": y, "log_burn": 10.0 * k + (y - 1984)}
            for k, r in enumerate(("N", "S")) for y in years]
    return pd.DataFrame(rows)


def test_last_burn_is_the_season_before_within_the_region():
    out = prediction_1c.add_last_burn(_frame().sample(frac=1, random_state=0), min_train=4)
    later = out[out["year"] > 1984]
    assert np.allclose(later["burn_lag1"], later["log_burn"] - 1)
    assert len(out) == 12 and not out["burn_lag1"].isna().any()


def test_first_season_takes_the_mean_of_early_training_seasons_only():
    frame = _frame()
    out = prediction_1c.add_last_burn(frame, min_train=4).set_index(["region", "year"])
    # lags of 1985 to 1987 are the outcomes of 1984 to 1986
    assert out.loc[("N", 1984), "burn_lag1"] == pytest.approx(1.0)
    assert out.loc[("S", 1984), "burn_lag1"] == pytest.approx(11.0)
    changed = frame.copy()
    changed.loc[changed["year"] >= 1987, "log_burn"] += 100.0
    again = prediction_1c.add_last_burn(changed, min_train=4).set_index(["region", "year"])
    assert again.loc[("N", 1984), "burn_lag1"] == pytest.approx(1.0)


def test_last_burn_refuses_a_missing_year():
    with pytest.raises(ValueError, match="consecutive"):
        prediction_1c.add_last_burn(_frame().query("year != 1986"))


def test_frame_1c_adds_the_columns_and_refuses_gaps():
    fire, controls, swe, spei = _tables()
    controls = controls.assign(temp_mam=5.0)
    spei = spei.assign(spei3_jja=0.4)
    snow = controls[["region", "year"]].assign(snowfall_frac=0.4, soil_moisture=0.25)
    frame = prediction_1c.frame_1c(fire, controls, swe, spei, snow, min_train=2)
    assert {"spei3_jja", "soil_moisture", "burn_lag1", "snowfall_frac"} <= set(frame.columns)
    assert len(frame) == 2 * len(REGIONS)
    assert np.allclose(frame["burn_lag1"], 10.0)
    gap = snow.assign(soil_moisture=[np.nan] + [0.25] * (len(snow) - 1))
    with pytest.raises(ValueError, match="soil_moisture"):
        prediction_1c.frame_1c(fire, controls, swe, spei, gap, min_train=2)


def test_variants_are_fixed_and_only_the_ceiling_reads_summer():
    assert list(PRED_1C_VARIANTS) == ["last_burn", "ceiling"]
    summer = {"temp_jja", "spei3_jja", "soil_moisture"}
    assert not summer & set(PRED_1C_VARIANTS["last_burn"][0])
    assert summer <= set(PRED_1C_VARIANTS["ceiling"][0])
    assert set(PRED_1C_VARIANTS["last_burn"][0]) == {*PRED_1B_VARIANTS["spring_inputs"][0],
                                                     "burn_lag1"}
    assert set(PRED_1C_VARIANTS["ceiling"][0]) == {*PRED_1B_VARIANTS["hindsight"][0],
                                                   "spei3_jja", "soil_moisture"}
    for _, by_region, scaled in PRED_1C_VARIANTS.values():
        assert by_region and scaled
