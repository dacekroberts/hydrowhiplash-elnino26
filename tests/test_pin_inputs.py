"""Tests for src/pin_inputs.py (trap 7: pin the inputs before the tests)."""
import hashlib

import pytest

from src import pin_inputs


@pytest.fixture
def tree(tmp_path, monkeypatch):
    folder = tmp_path / "tables"
    folder.mkdir()
    (folder / "a.csv").write_bytes(b"x,y\n1,2\n")
    fixed = tmp_path / "roni.txt"
    fixed.write_bytes(b"DJF 1.5\n")
    pins = folder / "input_pins.csv"
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(pin_inputs, "FIXED", [fixed])
    monkeypatch.setattr(pin_inputs, "FOLDERS", [folder])
    monkeypatch.setattr(pin_inputs, "INPUT_PINS_TABLE", pins)
    return tmp_path, pins


def test_pin_records_sha256_and_skips_its_own_table(tree):
    root, pins = tree
    table = pin_inputs.pin(pins)
    assert set(table["path"]) == {"roni.txt", "tables/a.csv"}
    row = table.set_index("path").loc["roni.txt"]
    assert row["sha256"] == hashlib.sha256(b"DJF 1.5\n").hexdigest()
    pin_inputs.verify(pins)  # unchanged inputs pass


def test_verify_reports_changed_missing_and_new_files(tree):
    root, pins = tree
    pin_inputs.pin(pins)
    (root / "roni.txt").write_bytes(b"DJF 1.6\n")  # a revised index value
    (root / "tables" / "b.csv").write_bytes(b"new\n")
    (root / "tables" / "a.csv").unlink()
    with pytest.raises(ValueError) as err:
        pin_inputs.verify(pins)
    msg = str(err.value)
    assert "changed: roni.txt" in msg
    assert "not pinned: tables/b.csv" in msg
    assert "missing: tables/a.csv" in msg
