"""Stamped paths for later downloads and rebuilds (D73): no network, no data/."""
import json
import sys
import types
from datetime import date

import pandas as pd
import pytest

sys.modules.setdefault("cdsapi", types.SimpleNamespace(Client=object))  # not needed offline

from src import (download_bc_snow, download_era5, download_era5_april1,  # noqa: E402
                 download_oni, later, pin_inputs)


@pytest.fixture
def tree(monkeypatch, tmp_path):
    """A later tree and a data/raw stand-in under tmp_path."""
    raw = tmp_path / "raw"
    monkeypatch.setattr(later, "LATER_RAW", raw / "later")
    monkeypatch.setattr(later, "DATA_RAW", raw)
    monkeypatch.setattr(later, "TRACKER_TABLES", tmp_path / "tracker")
    return raw


def test_take_stamp_forms():
    args = ["north", "--stamp", "2026-11-07", "--refresh"]
    assert later.take_stamp(args) == "2026-11-07" and args == ["north", "--refresh"]
    args = ["--stamp", "north"]  # a bare flag followed by a domain name
    assert later.take_stamp(args, today=date(2026, 11, 8)) == "2026-11-08" and args == ["north"]
    args = ["north"]
    assert later.take_stamp(args) is None and args == ["north"]
    with pytest.raises(SystemExit):
        later.take_stamp(["--stamp", "2026-13-01"])


def test_mirror_keeps_the_source_folder(tree):
    assert later.mirror(tree / "fire" / "cnfdb", "2027-01-04") == \
        tree / "later" / "2027-01-04" / "fire" / "cnfdb"
    assert later.mirror(tree.parent / "elsewhere", "2027-01-04").name == "elsewhere"
    assert later.tables_dir("2026-11-07") == tree.parent / "tracker" / "2026-11-07"


def test_record_closes_a_folder(tree):
    out = later.open_folder(tree / "enso", "2027-03-02")
    with pytest.raises(later.StampedFolderError):  # nothing downloaded
        later.record(out, "2027-03-02", "url")
    (out / "roni.ascii.txt").write_bytes(b"DJF 2027 1.9\n")
    (out / "half.tmp").write_bytes(b"x")
    with pytest.raises(later.StampedFolderError):  # unfinished file
        later.record(out, "2027-03-02", "url")
    (out / "half.tmp").unlink()
    content = json.loads(later.record(out, "2027-03-02", "url").read_text("utf-8"))
    assert content["stamp"] == "2027-03-02"
    assert content["files"]["roni.ascii.txt"] == {
        "bytes": 13, "sha256": pin_inputs.sha256(out / "roni.ascii.txt")}
    with pytest.raises(later.StampedFolderError):  # closed: never rewritten
        later.open_folder(tree / "enso", "2027-03-02")
    later.open_folder(tree / "enso", "2027-04-04")  # another stamp is a new record


def test_open_folder_refuses_a_pinned_folder(tree, monkeypatch):
    pinned = tree / "later" / "2027-01-04" / "fire" / "cnfdb" / "NFDB_poly.zip"
    monkeypatch.setattr(pin_inputs, "pinned_files", lambda: [pinned])
    with pytest.raises(later.StampedFolderError):
        later.open_folder(tree / "fire" / "cnfdb", "2027-01-04")


def test_index_download_leaves_the_pinned_files_alone(tree, monkeypatch):
    monkeypatch.setattr(download_oni, "DATA_RAW", tree)
    tree.mkdir(parents=True)
    pinned = tree / "roni.ascii.txt"
    pinned.write_bytes(b"pinned")
    monkeypatch.setattr(download_oni.requests, "get", lambda url, timeout: types.SimpleNamespace(
        content=b"SEAS YR TOTAL ANOM\nDJF 2027 28.9 1.9\n", raise_for_status=lambda: None))
    out = download_oni.download_stamped("2027-03-02")
    assert out == tree / "later" / "2027-03-02" / "enso"
    assert sorted(p.name for p in out.iterdir()) == ["oni.ascii.txt", later.RECORD_NAME,
                                                     "roni.ascii.txt"]
    assert pinned.read_bytes() == b"pinned"
    assert download_oni.parse(out / "roni.ascii.txt")["anom"].iloc[-1] == 1.9


class _Client:
    def __init__(self):
        self.years = []

    def retrieve(self, dataset, request, target):
        self.years.append(request["year"])
        with open(target, "wb") as fh:
            fh.write(b"nc")


def test_era5_stamped_run_requests_only_unfinished_years(tree, monkeypatch):
    monkeypatch.setattr(download_era5, "RAW", tree)
    monkeypatch.setattr(download_era5, "CLIMATE_FIRST_YEAR", 2025)
    base = tree / "era5_land"
    base.mkdir(parents=True)
    (base / "era5_land_2025.nc").write_bytes(b"full")
    (base / "era5_land_2026_partial.nc").write_bytes(b"to july")
    client = _Client()
    download_era5.download_domain(client, "main", date(2026, 11, 8), stamp="2026-11-08")
    assert len(client.years) == 1 and "2026" in str(client.years[0])
    out = tree / "later" / "2026-11-08" / "era5_land"
    assert (out / "era5_land_2026_partial.nc").read_bytes() == b"nc"
    assert (out / later.RECORD_NAME).exists()
    assert (base / "era5_land_2026_partial.nc").read_bytes() == b"to july"  # untouched
    assert sorted(p.name for p in base.iterdir()) == ["era5_land_2025.nc",
                                                      "era5_land_2026_partial.nc"]


def test_april1_stamped_run_writes_beside(tree, monkeypatch):
    monkeypatch.setattr(download_era5_april1, "RAW", tree)
    base = tree / "era5_land_april1"
    base.mkdir(parents=True)
    (base / download_era5_april1.FILENAME).write_bytes(b"to 2026")
    download_era5_april1.download_domain(_Client(), "main", date(2027, 4, 8), "2027-04-08")
    out = tree / "later" / "2027-04-08" / "era5_land_april1"
    assert (out / download_era5_april1.FILENAME).read_bytes() == b"nc"
    assert (base / download_era5_april1.FILENAME).read_bytes() == b"to 2026"


def test_station_download_takes_the_flag(tree, monkeypatch):
    class Session:
        def get(self, url, params=None, headers=None, timeout=None, stream=False):
            body = (download_bc_snow.HEADER_START + ",x\n").encode()
            return types.SimpleNamespace(
                status_code=200, headers={}, raise_for_status=lambda: None,
                iter_content=lambda chunk_size=None: iter([body]), content=body, text=body.decode())

    base = tree / "bc_snow"
    monkeypatch.setattr(download_bc_snow, "OUT", base)
    monkeypatch.setattr(download_bc_snow.requests, "Session", Session)
    download_bc_snow.main(["--stamp", "2027-04-04"])
    out = tree / "later" / "2027-04-04" / "bc_snow"
    assert (out / later.RECORD_NAME).exists() and not base.exists()


def test_compare_tables_reports_changed_and_added_cells():
    old = pd.DataFrame({"region": ["PNW", "PNW"], "year": [2025, 2026],
                        "precip": [100.0, 80.0], "temp_jja": [17.5, float("nan")]})
    new = pd.DataFrame({"region": ["PNW", "PNW", "PNW"], "year": [2025, 2026, 2027],
                        "precip": [100.0, 80.0, 60.0],
                        "temp_jja": [17.5, 18.25, float("nan")]})
    diff = later.compare_tables(old, new, ["region", "year"])
    assert diff.drop(columns="old").to_dict("records") == [
        {"region": "PNW", "year": 2026, "column": "temp_jja", "new": 18.25, "change": "changed"},
        {"region": "PNW", "year": 2027, "column": "precip", "new": 60.0, "change": "added"}]
    assert diff["old"].isna().all()
    assert later.compare_tables(old, old.copy(), ["region", "year"]).empty
    with pytest.raises(ValueError):
        later.compare_tables(old, new.drop(columns="precip"), ["region", "year"])
