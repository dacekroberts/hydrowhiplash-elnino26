"""Stamped rebuilds (D88): builders read a later retrieval over the files on
disk and write beside the pinned tables. Made-up files only."""
import json

import pandas as pd
import pytest

from src import later, phase2, pin_inputs


@pytest.fixture
def tree(monkeypatch, tmp_path):
    raw = tmp_path / "raw"
    monkeypatch.setattr(later, "LATER_RAW", raw / "later")
    monkeypatch.setattr(later, "DATA_RAW", raw)
    monkeypatch.setattr(later, "DATA_PROCESSED", tmp_path / "processed")
    monkeypatch.setattr(later, "TRACKER_TABLES", tmp_path / "results" / "tables" / "tracker")
    monkeypatch.setattr(later, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(pin_inputs, "pinned_files", lambda: [])
    monkeypatch.setattr(pin_inputs, "head_commit", lambda: "abc1234")
    return raw


def _retrieval(folder, stamp, files):
    out = later.open_folder(folder, stamp)
    for name, body in files.items():
        (out / name).write_bytes(body)
    later.record(out, stamp, "test")
    return out


def test_base_paths_are_the_usual_ones(tree):
    ctx = later.paths(None)
    assert ctx.stamp is None and ctx.era5_paths(tree / "era5_land") is None
    assert ctx.processed(tree / "x.csv") == tree / "x.csv"
    assert ctx.table(tree / "t.csv") == tree / "t.csv"
    assert ctx.raw_file(tree / "a", "f.nc") == tree / "a" / "f.nc"
    assert ctx.close("anything") is None


def test_latest_reads_only_closed_retrievals_up_to_the_stamp(tree):
    folder = tree / "era5_land"
    assert later.latest(folder, "2027-01-01") is None
    first = _retrieval(folder, "2026-11-08", {"era5_land_2026_partial.nc": b"oct"})
    second = _retrieval(folder, "2026-12-08", {"era5_land_2026_partial.nc": b"nov"})
    later.open_folder(folder, "2026-12-20")  # open, never recorded
    assert later.latest(folder, "2026-11-07") is None
    assert later.latest(folder, "2026-11-30") == first
    assert later.latest(folder, "2027-01-01") == second


def test_era5_paths_lay_the_retrieval_over_the_files_on_disk(tree):
    base = tree / "era5_land"
    base.mkdir(parents=True)
    for name in ("era5_land_2024.nc", "era5_land_2025.nc", "era5_land_2026_partial.nc"):
        (base / name).write_bytes(b"base")
    ctx = later.paths("2027-02-08")
    assert ctx.era5_paths(base) is None  # nothing retrieved yet
    stamped = _retrieval(base, "2027-02-08", {"era5_land_2026.nc": b"full",
                                             "era5_land_2027_partial.nc": b"jan"})
    assert ctx.era5_paths(base) == [base / "era5_land_2024.nc", base / "era5_land_2025.nc",
                                    stamped / "era5_land_2026.nc",
                                    stamped / "era5_land_2027_partial.nc"]
    assert list(ctx.read) == ["2027-02-08/era5_land"]
    assert (base / "era5_land_2026_partial.nc").read_bytes() == b"base"


def test_raw_file_and_output_paths(tree):
    base = tree / "era5_land_april1"
    ctx = later.paths("2027-04-08")
    assert ctx.raw_file(base, "era5_land_april1.nc") == base / "era5_land_april1.nc"
    stamped = _retrieval(base, "2027-04-08", {"era5_land_april1.nc": b"x"})
    assert ctx.raw_file(base, "era5_land_april1.nc") == stamped / "era5_land_april1.nc"
    assert ctx.processed(tree / "swe.csv") == later.DATA_PROCESSED / "later" / "2027-04-08" / "swe.csv"
    assert ctx.table(tree / "t.csv") == later.TRACKER_TABLES / "2027-04-08" / "t.csv"


def test_table_refuses_a_pinned_path(tree, monkeypatch):
    ctx = later.paths("2027-04-08")
    target = later.TRACKER_TABLES / "2027-04-08" / "t.csv"
    monkeypatch.setattr(pin_inputs, "pinned_files", lambda: [target])
    with pytest.raises(later.StampedFolderError):
        ctx.table(tree / "t.csv")


def test_winters_come_from_a_stamped_index_when_there_is_one(tree):
    later.DATA_PROCESSED.mkdir(parents=True)
    pd.DataFrame({"year": [2026], "enso_djf": [-0.4]}).to_csv(
        later.DATA_PROCESSED / "el_nino_winters.csv", index=False)
    ctx = later.paths("2027-03-05")
    assert list(ctx.winters()["year"]) == [2026]  # pinned table: no retrieval
    _retrieval(tree / "enso", "2027-03-02", {
        "roni.ascii.txt": b"SEAS YR TOTAL ANOM\nDJF 2026 26.0 -0.4\nDJF 2027 28.9 1.9\n"})
    winters = ctx.winters().set_index("year")
    assert winters.loc[2027, "enso_djf"] == 1.9 and bool(winters.loc[2027, "strong"])
    assert winters.loc[2027, "winter"] == "2026-2027"


def test_a_named_index_retrieval_wins_over_a_later_one(tree):
    first = b"SEAS YR TOTAL ANOM\nDJF 2027 28.9 1.9\n"
    revised = b"SEAS YR TOTAL ANOM\nDJF 2027 28.8 1.7\n"
    _retrieval(tree / "enso", "2027-03-02", {"roni.ascii.txt": first})
    _retrieval(tree / "enso", "2027-05-14", {"roni.ascii.txt": revised})
    latest = later.paths("2027-05-20").winters().set_index("year")
    assert latest.loc[2027, "enso_djf"] == 1.7
    ctx = later.paths("2027-05-20", "2027-03-02")
    assert ctx.winters().set_index("year").loc[2027, "enso_djf"] == 1.9
    assert list(ctx.read) == ["2027-03-02/enso"]
    with pytest.raises(later.StampedFolderError):
        later.paths("2027-05-20", "2027-04-01").winters()  # no such retrieval
    with pytest.raises(later.StampedFolderError):
        later.paths("2027-03-01", "2027-03-02")  # named retrieval after the stamp
    with pytest.raises(SystemExit):
        later.paths(None, "2027-03-02")
    args = ["--rebuild", "--index-stamp", "2027-03-02", "--stamp"]
    assert later.take_index_stamp(args) == "2027-03-02" and args == ["--rebuild", "--stamp"]


def test_stamped_phase2_writes_beside_and_reports_changed_cells(tree, monkeypatch):
    processed, results = later.DATA_PROCESSED, later.RESULTS / "tables"
    monkeypatch.setattr(phase2, "REGIONS", ["PNW"])
    name = phase2.COMMITTED.name
    pinned = results / name
    monkeypatch.setattr(phase2, "COMMITTED", pinned)
    enso = {"winter": "w", "enso_index": "RONI", "enso_djf": 0.1, "phase": "neutral",
            "strong": False}

    def tables(years, spei):
        whip = pd.DataFrame([{"region": "PNW", "year": y, **enso, "whiplash": 0.0,
                              "spei3_djf": s, "spei3_jja": 0.0}
                             for y, s in zip(years, spei)])
        swe = pd.DataFrame([{"region": "PNW", "year": y, **enso, "swe_apr1_mm": 100.0}
                            for y in years])
        return whip, swe

    results.mkdir(parents=True)
    phase2.build_table(*tables([2025, 2026], [0.5, 0.7])).to_csv(pinned, index=False)
    before = pinned.read_bytes()
    stamped = processed / "later" / "2026-11-08"
    stamped.mkdir(parents=True)
    whip, swe = tables([2025, 2026, 2027], [0.5, 0.9, 1.1])
    whip.to_csv(stamped / phase2.WHIPLASH.name, index=False)
    swe.to_csv(stamped / phase2.SWE.name, index=False)

    phase2.main(stamp="2026-11-08")

    folder = later.TRACKER_TABLES / "2026-11-08"
    assert pinned.read_bytes() == before
    assert len(pd.read_csv(folder / name)) == 3
    record = json.loads((folder / later.REBUILD_RECORD).read_text("utf-8"))
    assert record["builders"]["phase2"]["tables"] == [name]
    changes = pd.read_csv(folder / later.CHANGES_NAME)
    changed = changes[changes["change"] == "changed"]
    assert changed[["year", "column", "old", "new"]].astype(str).values.tolist() == [
        ["2026", "spei3_djf", "0.7", "0.9"]]
    assert set(changes.loc[changes["change"] == "added", "year"]) == {2027}
