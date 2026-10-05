"""Tests for src/phase2.py."""
import pandas as pd
import pytest

from src import phase2


def tables():
    enso = {"winter": ["1950-1951", "1951-1952"], "enso_index": "ONI",
            "enso_djf": [-0.8, 0.5], "phase": ["la_nina", "el_nino"], "strong": [False, False]}
    w = pd.DataFrame({"region": ["BC", "BC"], "year": [1951, 1952], "whiplash": [1.0, -2.0],
                      "spei3_djf": [0.5, 1.0], "spei3_jja": [1.5, -1.0], **enso})
    s = pd.DataFrame({"region": ["BC", "BC"], "year": [1951, 1952],
                      "swe_apr1_mm": [400.0, 350.0], **enso})
    return w, s


def test_build_table_joins_and_keeps_every_winter():
    w, s = tables()
    t = phase2.build_table(w, s)
    assert list(t.columns[:7]) == ["region", "year", "winter", "whiplash", "spei3_djf",
                                   "spei3_jja", "swe_apr1_mm"]
    assert t["phase"].tolist() == ["la_nina", "el_nino"] and len(t) == 2


def test_build_table_rejects_disagreeing_enso_columns():
    w, s = tables()
    s.loc[1, "phase"] = "neutral"
    with pytest.raises(ValueError):
        phase2.build_table(w, s)


def test_write_tables_writes_both_copies(tmp_path, monkeypatch):
    monkeypatch.setattr(phase2, "OUT", tmp_path / "processed" / "t.csv")
    monkeypatch.setattr(phase2, "COMMITTED", tmp_path / "results" / "tables" / "t.csv")
    w, s = tables()
    phase2.write_tables(phase2.build_table(w, s))
    a = (tmp_path / "processed" / "t.csv").read_bytes()
    assert a == (tmp_path / "results" / "tables" / "t.csv").read_bytes()
    assert b"\r\n" not in a  # LF, matching .gitattributes
