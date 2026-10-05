"""Tests for src/describe.py on a table with known group means."""
import pandas as pd
import pytest

from src.describe import phase_summary


def test_phase_summary_known_differences():
    table = pd.DataFrame({
        "region": ["A"] * 6,
        "year": range(1951, 1957),
        "precip": [50.0, 70.0, 100.0, 100.0, 140.0, 140.0],
        "phase": ["el_nino", "el_nino", "neutral", "neutral", "la_nina", "la_nina"],
        "strong": [True, False, False, False, False, False],
    })
    s = phase_summary(table, "precip").iloc[0]
    assert (s["n_el_nino"], s["n_strong"], s["n_neutral"]) == (2, 1, 2)
    assert s["mean_all"] == pytest.approx(100)
    assert s["nino_minus_neutral"] == pytest.approx(-40)
    assert s["nino_minus_neutral_pct"] == pytest.approx(-40)
    assert s["strong_minus_all_pct"] == pytest.approx(-50)
    assert s["nino_minus_neutral_sd"] == pytest.approx(-40 / table["precip"].std())
    assert s["nino_share_below_median"] == 1.0
