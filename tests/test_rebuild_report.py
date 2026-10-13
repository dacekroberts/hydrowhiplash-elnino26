"""The pin report after a --rebuild write.

The eight modules that guard a pinned output but never printed the report now
print src.pin_inputs's report once per run, covering the pinned files that run
could have replaced (src/fire.py's pattern; D62). A run that could not have
replaced a pinned file, a stamped rebuild or download or a skipped download,
prints nothing. Throwaway pins tables and made-up files only: no network, no
file outside tmp_path.
"""
import io
import json
import zipfile

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from src import (download_cnfdb, download_mtbs, download_nbac, download_oni,
                 download_wfigs, era5, later, phase2, pin_inputs, regions,
                 snow_soil, stations)

DIFFERS = "pinned inputs now differing from input_pins.csv:"
SAME = "rebuilt files are byte-identical to their pins; no re-pin needed"


# ---------------------------------------------------------------- helpers

def report_count(out: str) -> int:
    """The reports in the captured output; a run prints exactly one."""
    return out.count(DIFFERS) + out.count(SAME)


def relative(root, path) -> str:
    return path.relative_to(root).as_posix()


def pin_tree(tmp_path, monkeypatch, fixed=(), folders=()):
    """A throwaway pins table over tmp_path (the idea of the tree fixture in
    tests/test_run_guard.py, copied, not imported)."""
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(pin_inputs, "FIXED", list(fixed))
    monkeypatch.setattr(pin_inputs, "FOLDERS", list(folders))
    table = tmp_path / "input_pins.csv"
    monkeypatch.setattr(pin_inputs, "INPUT_PINS_TABLE", table)
    # differences() took the pins table as a default argument when it was
    # defined, and report_rebuild() passes none, so move that default with it
    monkeypatch.setattr(pin_inputs.differences, "__defaults__", (table, None))
    pin_inputs.pin(table)
    return table


def later_tree(monkeypatch, tmp_path, processed):
    """src.later's paths under tmp_path, so a stamped run writes nothing
    outside it and its close() finds no pinned table to compare."""
    monkeypatch.setattr(later, "DATA_RAW", tmp_path / "raw")
    monkeypatch.setattr(later, "DATA_PROCESSED", processed)
    monkeypatch.setattr(later, "LATER_RAW", tmp_path / "raw" / "later")
    monkeypatch.setattr(later, "TRACKER_TABLES", tmp_path / "tracker")
    monkeypatch.setattr(later, "RESULTS", tmp_path / "no-pinned-results")
    monkeypatch.setattr(pin_inputs, "head_commit", lambda: "abc1234")


class _Bodies:
    """Stand-in for src.download_nrcs_snow.download: write the body recorded
    for the target's name, so no request leaves the machine."""

    def __init__(self, bodies):
        self.bodies = bodies

    def __call__(self, session, url, target, params=None, headers=None, check=None):
        target.write_bytes(self.bodies[target.name])


def _headers(session, url) -> dict:
    return {"Last-Modified": "Mon, 01 Jan 2026 00:00:00 GMT", "ETag": '"1"',
            "Content-Length": "3"}


class _Response:
    """The piece of a requests.Response the index downloader reads."""

    def __init__(self, text):
        self.text = text
        self.content = text.encode()

    def raise_for_status(self):
        return None


def _zip_bytes(name: str, body: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(name, body)
    return buffer.getvalue()


def _geojson() -> bytes:
    feature = {"type": "Feature", "properties": {"a": 1},
               "geometry": {"type": "Point", "coordinates": [0.0, 0.0]}}
    return json.dumps({"type": "FeatureCollection", "features": [feature]}).encode()


# ---------------------------------------------------------------- phase2

def test_phase2_reports_the_committed_table_once(tmp_path, monkeypatch, capsys):
    committed = tmp_path / "results" / "tables" / "whiplash_swe_region_year.csv"
    committed.parent.mkdir(parents=True)
    committed.write_bytes(b"region,year\nPNW,2024\n")   # yesterday's rebuild
    table = pin_tree(tmp_path, monkeypatch, fixed=[committed])
    monkeypatch.setattr(phase2, "OUT", tmp_path / "processed" / "whiplash_swe_region_year.csv")
    monkeypatch.setattr(phase2, "COMMITTED", committed)
    data = pd.DataFrame({"region": ["PNW"], "year": [2025]})

    phase2.write_tables(data, rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1
    assert f"changed: {relative(tmp_path, committed)}" in out

    pin_inputs.pin(table)                       # the rebuilt bytes, re-pinned
    phase2.write_tables(data, rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1 and SAME in out

    with pytest.raises(pin_inputs.PinnedInputError, match="whiplash"):
        phase2.write_tables(data)               # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0

    later_tree(monkeypatch, tmp_path, tmp_path / "processed")
    phase2.write_tables(data, rebuild=True, ctx=later.paths("2026-11-08"))
    assert report_count(capsys.readouterr().out) == 0   # a stamped write is not pinned


# ---------------------------------------------------------------- snow_soil

def grid() -> xr.Dataset:
    """A 12-month ERA5-Land stand-in holding the variables main indexes."""
    months = pd.date_range("2000-01-01", periods=12, freq="MS")
    return xr.Dataset({name: (era5.TIME, np.zeros(12))
                       for name in ("sf", "tp", "swvl1", "swvl2")},
                      coords={era5.TIME: months})


def _fake_snow_soil_inputs(monkeypatch):
    """The region, ERA5 grids and computed columns snow_soil.main needs (the
    grid work is not under test)."""
    coords = {"region": ["PNW"], "year": [2000]}
    monkeypatch.setattr(regions, "load_regions", lambda: pd.DataFrame({"region": ["PNW"]}))
    monkeypatch.setattr(era5, "assign_domains", lambda regs: pd.Series({"PNW": "main"}))
    monkeypatch.setattr(era5, "open_domains",
                        lambda names, ctx=None: {name: grid() for name in names})
    monkeypatch.setattr(era5, "open_era5", lambda directory, paths=None: grid())
    monkeypatch.setattr(era5, "region_masks", lambda regs, ds: xr.DataArray(
        [True], dims=["region"], coords={"region": ["PNW"]}))
    monkeypatch.setattr(snow_soil, "snowfall_fraction", lambda sf, tp, masks, months=None:
                        xr.Dataset({"snowfall_frac": (("region", "year"), [[0.5]]),
                                    "sf_season_mm": (("region", "year"), [[50.0]]),
                                    "tp_season_mm": (("region", "year"), [[100.0]])},
                                   coords=coords))
    monkeypatch.setattr(snow_soil, "soil_moisture",
                        lambda ds, masks, months=None, weights=None: xr.DataArray(
                            [[0.2]], dims=["region", "year"], coords=coords))
    monkeypatch.setattr(snow_soil, "snow_soil_table",
                        lambda regional, winters: pd.DataFrame({
                            "region": ["PNW"], "year": [2000], "snowfall_frac": [0.5],
                            "soil_moisture": [0.2]}))


def test_snow_soil_reports_the_committed_table_once(tmp_path, monkeypatch, capsys):
    committed = tmp_path / "results" / "tables" / "snow_soil_region_year.csv"
    committed.parent.mkdir(parents=True)
    committed.write_bytes(b"region,year\nPNW,2000\n")
    table = pin_tree(tmp_path, monkeypatch, fixed=[committed])
    processed = tmp_path / "processed"
    processed.mkdir()
    monkeypatch.setattr(snow_soil, "COMMITTED", committed)
    monkeypatch.setattr(snow_soil, "SNOW_SOIL_TABLE", processed / "snow_soil_region_year.csv")
    pd.DataFrame({"year": [2000], "winter": ["1999-2000"], "enso_index": "RONI",
                  "enso_djf": 0.0, "phase": "neutral", "strong": False}).to_csv(
        processed / "el_nino_winters.csv", index=False)
    later_tree(monkeypatch, tmp_path, processed)
    _fake_snow_soil_inputs(monkeypatch)

    snow_soil.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1
    assert f"changed: {relative(tmp_path, committed)}" in out

    pin_inputs.pin(table)
    snow_soil.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1 and SAME in out

    with pytest.raises(pin_inputs.PinnedInputError, match="snow_soil"):
        snow_soil.main()                        # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0

    snow_soil.main(stamp="2026-11-08")
    assert report_count(capsys.readouterr().out) == 0   # a stamped rebuild writes no pinned file


# ---------------------------------------------------------------- stations

def _fake_stations(monkeypatch, tmp_path, committed):
    """stations.main's paths and inputs under tmp_path (the cleaning rules
    are not under test)."""
    processed = tmp_path / "processed"
    processed.mkdir(exist_ok=True)
    monkeypatch.setattr(stations, "COMMITTED_INDEX", committed)
    monkeypatch.setattr(stations, "STATION_TABLE", processed / "station_swe_apr1.csv")
    monkeypatch.setattr(stations, "STATION_INDEX_TABLE",
                        processed / "station_swe_region_year.csv")
    era5_csv = processed / "swe_april1_region_year.csv"
    pd.DataFrame({"region": "PNW", "year": [1991, 1992, 1993], "winter": "1990-1991",
                  "swe_apr1_mm": [100.0, 200.0, 300.0], "enso_index": "RONI",
                  "enso_djf": 0.0, "phase": "neutral", "strong": False}).to_csv(
        era5_csv, index=False)
    monkeypatch.setattr(stations, "ERA5_SWE", era5_csv)
    built = pd.DataFrame({"region": "PNW", "year": [1991, 1992, 1993], "station_id": "s1",
                          "source": "nrcs", "network": "SNOTEL", "method": "pillow",
                          "swe_apr1_mm": [100.0, 200.0, 300.0]})
    monkeypatch.setattr(stations, "build", lambda: (built, {}))


def test_stations_reports_the_committed_index_once(tmp_path, monkeypatch, capsys):
    committed = tmp_path / "results" / "tables" / "station_swe_region_year.csv"
    committed.parent.mkdir(parents=True)
    committed.write_bytes(b"region,year\nPNW,1995\n")
    table = pin_tree(tmp_path, monkeypatch, fixed=[committed])
    _fake_stations(monkeypatch, tmp_path, committed)

    stations.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1
    assert f"changed: {relative(tmp_path, committed)}" in out

    pin_inputs.pin(table)
    stations.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1 and SAME in out

    with pytest.raises(pin_inputs.PinnedInputError, match="station_swe_region_year"):
        stations.main()                         # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0

    # the written table is not a pinned input: nothing could have been replaced
    monkeypatch.setattr(stations, "COMMITTED_INDEX",
                        tmp_path / "results" / "tables" / "other.csv")
    stations.main(rebuild=True)
    assert report_count(capsys.readouterr().out) == 0


# ---------------------------------------------------------------- download_oni

def test_download_oni_reports_the_pinned_index_files_once(tmp_path, monkeypatch, capsys):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    raw.mkdir()
    processed.mkdir()
    index_path = raw / "roni.ascii.txt"
    index_csv = processed / "enso_index.csv"
    winters_csv = processed / "el_nino_winters.csv"
    for path in (index_path, index_csv, winters_csv):
        path.write_bytes(b"old\n")
    table = pin_tree(tmp_path, monkeypatch, fixed=[index_path, index_csv, winters_csv])
    monkeypatch.setattr(download_oni, "DATA_RAW", raw)
    monkeypatch.setattr(download_oni, "DATA_PROCESSED", processed)
    text = "SEAS YR TOTAL ANOM\nDJF 1995 -0.9 -0.9\nDJF 1998 2.4 2.4\n"
    monkeypatch.setattr(download_oni.requests, "get",
                        lambda url, timeout: _Response(text))

    download_oni.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1
    assert f"changed: {relative(tmp_path, index_path)}" in out

    pin_inputs.pin(table)
    download_oni.main(rebuild=True)
    out = capsys.readouterr().out
    assert report_count(out) == 1 and SAME in out

    with pytest.raises(pin_inputs.PinnedInputError, match="roni.ascii.txt"):
        download_oni.main()                     # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0


def test_download_oni_stamped_retrieval_prints_no_report(tmp_path, monkeypatch, capsys):
    processed = tmp_path / "processed"
    processed.mkdir()
    later_tree(monkeypatch, tmp_path, processed)
    monkeypatch.setattr(download_oni, "DATA_RAW", tmp_path / "raw")
    monkeypatch.setattr(download_oni, "DATA_PROCESSED", processed)
    monkeypatch.setattr(download_oni.requests, "get",
                        lambda url, timeout: _Response("SEAS YR TOTAL ANOM\nDJF 1995 -0.9 -0.9\n"))

    download_oni.download_stamped("2027-03-02")   # its own folder, never a pinned path

    assert report_count(capsys.readouterr().out) == 0
    assert (later.LATER_RAW / "2027-03-02" / "enso" / later.RECORD_NAME).exists()


# ---------------------------------------------------------------- cnfdb, nbac

@pytest.mark.parametrize("module, files", [
    (download_cnfdb, download_cnfdb.CNFDB_FILES),
    (download_nbac, download_nbac.NBAC_FILES)])
def test_download_sources_report_the_pinned_folder_once(module, files, tmp_path,
                                                        monkeypatch, capsys):
    out = tmp_path / "download"
    out.mkdir()
    bodies = {"listing.html": b"new listing"}
    bodies.update({name: ("new " + name).encode() for name in files})
    for name in bodies:
        (out / name).write_bytes(b"old")
    table = pin_tree(tmp_path, monkeypatch, folders=[out])
    monkeypatch.setattr(module, "OUT", out)
    monkeypatch.setattr(module, "download", _Bodies(bodies))
    monkeypatch.setattr(module, "server_headers", _headers)
    monkeypatch.setattr(module, "now_utc", lambda: "2026-10-13T00:00:00+00:00")
    monkeypatch.setattr(module.requests, "Session", lambda: object())

    module.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1
    assert f"changed: {relative(tmp_path, out / files[0])}" in out_text

    pin_inputs.pin(table)                       # the retrieval as it now stands
    module.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1 and SAME in out_text

    with pytest.raises(pin_inputs.PinnedInputError, match=files[0]):
        module.main([])                         # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0

    later_tree(monkeypatch, tmp_path, tmp_path / "processed")
    module.main(["--rebuild", "--stamp", "2027-01-04"])  # a stamped download is not pinned
    assert report_count(capsys.readouterr().out) == 0


# ---------------------------------------------------------------- mtbs

def test_download_mtbs_reports_the_pinned_folder_once(tmp_path, monkeypatch, capsys):
    out = tmp_path / "mtbs"
    out.mkdir()
    target = out / "mtbs_perimeter_data.zip"
    target.write_bytes(b"old release")
    archive = _zip_bytes("release.txt", b"release notes")
    table = pin_tree(tmp_path, monkeypatch, folders=[out])
    monkeypatch.setattr(download_mtbs, "OUT", out)
    monkeypatch.setattr(download_mtbs, "download", _Bodies({target.name: archive}))
    monkeypatch.setattr(download_mtbs, "server_headers",
                        lambda session, url: {"Last-Modified": "Mon, 01 Jan 2026 00:00:00 GMT",
                                              "ETag": '"1"', "Content-Length": str(len(archive))})
    monkeypatch.setattr(download_mtbs, "now_utc", lambda: "2026-10-13T00:00:00+00:00")
    monkeypatch.setattr(download_mtbs.requests, "Session", lambda: object())

    download_mtbs.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1
    assert f"changed: {relative(tmp_path, target)}" in out_text

    pin_inputs.pin(table)
    download_mtbs.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1 and SAME in out_text

    download_mtbs.main(["--rebuild"])           # the zip is present: nothing is written
    assert report_count(capsys.readouterr().out) == 0

    with pytest.raises(pin_inputs.PinnedInputError, match=target.name):
        download_mtbs.main([])                  # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0


# ---------------------------------------------------------------- wfigs

class _Session:
    """The one direct call the snapshot downloader makes on the session."""

    def get(self, *args, **kwargs):
        return None


def test_download_wfigs_reports_the_pinned_folder_once(tmp_path, monkeypatch, capsys):
    out = tmp_path / "wfigs"
    out.mkdir()
    target = out / "wfigs_perimeters.geojson"
    target.write_bytes(b"{}")
    table = pin_tree(tmp_path, monkeypatch, folders=[out])
    monkeypatch.setattr(download_wfigs, "OUT", out)
    monkeypatch.setattr(download_wfigs, "download",
                        _Bodies({target.name: _geojson(), "item.json": b"{}",
                                 "layer.json": b"{}"}))
    monkeypatch.setattr(download_wfigs, "request_export", lambda session: {
        "status": "Completed", "resultUrl": "https://example.test/export.geojson",
        "recordCount": 1})
    monkeypatch.setattr(download_wfigs, "now_utc", lambda: "2026-10-13T00:00:00+00:00")
    monkeypatch.setattr(download_wfigs.requests, "Session", _Session)

    download_wfigs.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1
    assert f"changed: {relative(tmp_path, target)}" in out_text

    pin_inputs.pin(table)
    download_wfigs.main(["--rebuild", "--refresh"])
    out_text = capsys.readouterr().out
    assert report_count(out_text) == 1 and SAME in out_text

    download_wfigs.main(["--rebuild"])          # the snapshot is present: nothing is written
    assert report_count(capsys.readouterr().out) == 0

    with pytest.raises(pin_inputs.PinnedInputError, match=target.name):
        download_wfigs.main([])                 # no --rebuild: refused before any write
    assert report_count(capsys.readouterr().out) == 0
