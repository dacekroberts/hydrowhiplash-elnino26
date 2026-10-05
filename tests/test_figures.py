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
