"""Tests for src/pin_inputs.py (trap 7: pin the inputs before the tests)."""
import hashlib

import pytest

from src import pin_inputs


@pytest.fixture
def tree(tmp_path, monkeypatch):
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "a.csv").write_bytes(b"x,y\n1,2\n")
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "z.zip").write_bytes(b"zip")
    fixed = tmp_path / "roni.txt"
    fixed.write_bytes(b"DJF 1.5\n")
    pins = tables / "input_pins.csv"
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(pin_inputs, "FIXED", [fixed, tables / "a.csv"])
    monkeypatch.setattr(pin_inputs, "FOLDERS", [raw])
    monkeypatch.setattr(pin_inputs, "INPUT_PINS_TABLE", pins)
    return tmp_path, pins


def test_pin_records_sha256_and_skips_its_own_table(tree):
    root, pins = tree
    table = pin_inputs.pin(pins)
    assert set(table["path"]) == {"roni.txt", "tables/a.csv", "raw/z.zip"}
    row = table.set_index("path").loc["roni.txt"]
    assert row["sha256"] == hashlib.sha256(b"DJF 1.5\n").hexdigest()
    pin_inputs.verify(pins)  # unchanged inputs pass


def test_verify_reports_changed_missing_and_new_files(tree):
    root, pins = tree
    pin_inputs.pin(pins)
    (root / "roni.txt").write_bytes(b"DJF 1.6\n")  # a revised index value
    (root / "raw" / "y.zip").write_bytes(b"new\n")  # a stray download
    (root / "tables" / "a.csv").unlink()
    with pytest.raises(ValueError) as err:
        pin_inputs.verify(pins)
    msg = str(err.value)
    assert "changed: roni.txt" in msg
    assert "not pinned: raw/y.zip" in msg
    assert "missing: tables/a.csv" in msg


def test_results_written_beside_the_input_tables_are_not_refused(tree):
    # Round 3 M1: a hypothesis run writes its own table to results/tables/;
    # the input tables are pinned by name, so verify still passes.
    root, pins = tree
    pin_inputs.pin(pins)
    (root / "tables" / "h3a_results.csv").write_bytes(b"term,p\nenso_djf,0.2\n")
    pin_inputs.verify(pins)


def test_assert_pinned_accepts_inputs_and_refuses_the_rest(tree):
    # Round 4 L6: the loaders' check that every table they open is pinned
    root, pins = tree
    assert pin_inputs.assert_pinned(root / "tables" / "a.csv") == (root / "tables" / "a.csv").resolve()
    assert pin_inputs.assert_pinned(root / "raw" / "z.zip")
    (root / "tables" / "new_input.csv").write_bytes(b"x\n")
    with pytest.raises(ValueError, match="Not a pinned input"):
        pin_inputs.assert_pinned(root / "tables" / "new_input.csv")


def test_real_pin_list_names_inputs_only():
    from src.config import PINNED_RESULT_TABLES, TEST_SIZE_TABLE
    assert TEST_SIZE_TABLE.name not in PINNED_RESULT_TABLES
    assert "input_pins.csv" not in PINNED_RESULT_TABLES
    assert len(PINNED_RESULT_TABLES) == len(set(PINNED_RESULT_TABLES)) == 7
