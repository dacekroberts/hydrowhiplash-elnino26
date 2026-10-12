"""Smoke tests for src/figures.py helpers added after Phase 1."""
import pandas as pd

from src import figures


def test_winter_series_columns_writes_png(tmp_path):
    years = list(range(2000, 2006))
    table = pd.DataFrame({"region": "R", "year": years,
                          "phase": ["el_nino", "neutral"] * 3, "strong": [True] + [False] * 5,
                          "a": [90.0, 100, 110, None, 95, 105], "b": [80.0, 100, 120, 90, 95, 105]})
    out = figures.winter_series_columns(table, {"Stations": "a", "Grid": "b"}, "% of normal",
                                        "ONI", tmp_path / "x.png")
    assert out.exists() and out.stat().st_size > 0


def _fire_table():
    years = list(range(2000, 2006))
    return pd.DataFrame({"region": "R", "year": years,
                         "phase": ["el_nino", "neutral"] * 3, "strong": [True] + [False] * 5,
                         "log_burn": [10.0, 12.0, 0.0, 11.0, 9.0, 13.0],
                         "zero_fire": [False, False, True, False, False, False]})


def test_season_anomaly_is_centred_on_seasons_with_fire():
    out = figures.season_anomaly(_fire_table())
    assert pd.isna(out.loc[2, "anomaly"])  # the zero-fire season is a marker, not a bar
    assert abs(out["anomaly"].sum()) < 1e-9  # mean of the 5 seasons with fire is 11
    assert out.loc[0, "anomaly"] == -1.0 and out.loc[5, "anomaly"] == 2.0


def test_fire_season_series_writes_png(tmp_path):
    out = figures.fire_season_series(pd.concat([_fire_table(), _fire_table().assign(region="S")]),
                                     "RONI", tmp_path / "f.png")
    assert out.exists() and out.stat().st_size > 0
