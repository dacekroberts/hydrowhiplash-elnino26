"""Offline tests for the station snowpack downloads (NRCS, BC, Yukon, CanSWE)."""
import hashlib
import json
from datetime import date

import pytest
import requests

from src import download_bc_snow, download_canswe, download_nrcs_snow, download_yukon_snow


class _Response:
    def __init__(self, status=200, body=b"", fail_midway=False):
        self.status_code, self.body, self.fail_midway = status, body, fail_midway

    def iter_content(self, chunk_size=1):
        yield self.body[: len(self.body) // 2]
        if self.fail_midway:
            raise requests.exceptions.ChunkedEncodingError("connection dropped")
        yield self.body[len(self.body) // 2:]

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class _Session:
    """Records every GET; answers with responder(url, params) or a fixed response."""

    def __init__(self, responder):
        self.responder, self.calls = responder, []

    def get(self, url, params=None, headers=None, timeout=None, stream=False):
        self.calls.append({"url": url, "params": params or {}, "headers": headers or {}})
        return self.responder(url, params or {})


def _nrcs_responder(n_sntl=85, n_snow=3):
    stations = ([{"stationTriplet": f"{i}:WA:SNTL", "networkCode": "SNTL"} for i in range(n_sntl)]
                + [{"stationTriplet": f"S{i}:WA:SNOW", "networkCode": "SNOW"}
                   for i in range(n_snow)])

    def respond(url, params):
        if url.endswith("stations"):
            return _Response(body=json.dumps(stations).encode())
        return _Response(body=b"[]")
    return respond


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(download_nrcs_snow.time, "sleep", lambda s: None)


def _use(monkeypatch, module, tmp_path, session):
    monkeypatch.setattr(module, "OUT", tmp_path)
    monkeypatch.setattr(module.requests, "Session", lambda: session)


# NRCS

def test_stations_request_keeps_discontinued_sites():
    p = download_nrcs_snow.stations_params("WA")
    assert p["activeOnly"] == "false"
    assert p["returnStationElements"] == "true"
    assert p["stationTriplets"] == "*:WA:SNTL,*:WA:SNOW"
    assert p["elements"] == "WTEQ"


@pytest.mark.parametrize("network, duration", [("SNTL", "MONTHLY"), ("SNOW", "SEMIMONTHLY")])
def test_data_request_duration_per_network(network, duration):
    p = download_nrcs_snow.data_params(["1:WA:" + network], network, date(2026, 10, 5))
    assert p["duration"] == duration and p["periodRef"] == "START"
    assert p["returnFlags"] == "true" and p["returnSuspectData"] == "true"
    assert p["beginDate"] == "1950-01-01" and p["endDate"] == "2026-10-05"


def test_nrcs_batches_and_files(monkeypatch, tmp_path, no_sleep):
    session = _Session(_nrcs_responder())
    _use(monkeypatch, download_nrcs_snow, tmp_path, session)
    download_nrcs_snow.main(["WA"])
    data_calls = [c for c in session.calls if c["url"].endswith("data")]
    sizes = [len(c["params"]["stationTriplets"].split(",")) for c in data_calls]
    assert sizes == [40, 40, 5, 3]  # SNTL in batches of 40, then SNOW
    assert [c["params"]["duration"] for c in data_calls] == ["MONTHLY"] * 3 + ["SEMIMONTHLY"]
    assert (tmp_path / "data_WA_SNTL_003.json").exists()
    assert (tmp_path / "data_WA_SNOW_001.json").exists()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert len(manifest["files"]) == 4 and len(manifest["files"][2]["triplets"]) == 5
    assert not list(tmp_path.glob("*.tmp"))


def test_nrcs_skips_existing_unless_refresh(monkeypatch, tmp_path, no_sleep):
    session = _Session(_nrcs_responder(n_sntl=2, n_snow=0))
    _use(monkeypatch, download_nrcs_snow, tmp_path, session)
    download_nrcs_snow.main(["WA"])
    assert len(session.calls) == 2  # metadata plus one batch
    download_nrcs_snow.main(["WA"])
    assert len(session.calls) == 2  # nothing requested again
    download_nrcs_snow.main(["WA", "--refresh"])
    assert len(session.calls) == 4


def test_partial_download_leaves_no_file(monkeypatch, tmp_path, no_sleep):
    session = _Session(lambda url, params: _Response(body=b"[1, 2, 3]", fail_midway=True))
    target = tmp_path / "x.json"
    with pytest.raises(requests.exceptions.ChunkedEncodingError):
        download_nrcs_snow.download(session, "https://example.test", target)
    assert not target.exists() and not list(tmp_path.iterdir())
    assert len(session.calls) == download_nrcs_snow.HTTP_RETRIES + 1


def test_error_page_is_not_saved(monkeypatch, tmp_path):
    session = _Session(lambda url, params: _Response(body=b"<html>busy</html>"))
    target = tmp_path / "x.json"
    with pytest.raises(json.JSONDecodeError):
        download_nrcs_snow.download(session, "https://example.test", target,
                                    check=download_nrcs_snow.check_json_list)
    assert not list(tmp_path.iterdir())


def test_server_error_is_retried(monkeypatch, tmp_path, no_sleep):
    answers = iter([_Response(status=503), _Response(body=b"[]")])
    session = _Session(lambda url, params: next(answers))
    download_nrcs_snow.download(session, "https://example.test", tmp_path / "x.json")
    assert len(session.calls) == 2 and (tmp_path / "x.json").read_bytes() == b"[]"


def test_nrcs_client_error_stops(monkeypatch, tmp_path, no_sleep):
    session = _Session(lambda url, params: _Response(status=400))
    _use(monkeypatch, download_nrcs_snow, tmp_path, session)
    with pytest.raises(SystemExit):
        download_nrcs_snow.main()
    assert len(session.calls) == 1  # no retry, no further states


# BC and Yukon

BC_CSV = (b"Snow Course Name, Number, Elev. metres, Date of Survey, Snow Depth cm, "
          b"Water Equiv. mm,  Survey Code, Snow Line Elev. m, Density %, Survey Period\r\n"
          b"HANSARD,1A06A,608,2026/02/27,42,130,,,31,01-Mar\r\n")
YUKON_CSV = (b'"# Description: test"\n""\n'
             b"location_code,location_name,parameter,units,sample_date,target_date,"
             b"year,month,result,flag\n08AA-SC01,Canyon Lake,snow water equivalent,mm,"
             b"1975-03-21,1975-04-01,1975,4,124,Actual\n")


@pytest.mark.parametrize("module, body", [(download_bc_snow, BC_CSV),
                                          (download_yukon_snow, YUKON_CSV)])
def test_csv_sources_saved_as_published_and_skipped(monkeypatch, tmp_path, module, body):
    session = _Session(lambda url, params: _Response(body=body))
    _use(monkeypatch, module, tmp_path, session)
    module.main()
    files = sorted(p.name for p in tmp_path.iterdir())
    assert len(files) == 2 and all((tmp_path / f).read_bytes() == body for f in files)
    module.main()
    assert len(session.calls) == 2  # skipped on the second run
    module.main(["--refresh"])
    assert len(session.calls) == 4


def test_yukon_asks_for_csv(monkeypatch, tmp_path):
    session = _Session(lambda url, params: _Response(body=YUKON_CSV))
    _use(monkeypatch, download_yukon_snow, tmp_path, session)
    download_yukon_snow.main()
    assert all(c["headers"].get("Accept") == "text/csv" for c in session.calls)


@pytest.mark.parametrize("module", [download_bc_snow, download_yukon_snow])
def test_csv_sources_reject_json_answer(monkeypatch, tmp_path, no_sleep, module):
    session = _Session(lambda url, params: _Response(body=b'{"error": "x"}'))
    _use(monkeypatch, module, tmp_path, session)
    with pytest.raises(ValueError):
        module.main()
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("module", [download_bc_snow, download_yukon_snow])
def test_csv_sources_client_error_stops(monkeypatch, tmp_path, module):
    session = _Session(lambda url, params: _Response(status=403))
    _use(monkeypatch, module, tmp_path, session)
    with pytest.raises(SystemExit):
        module.main()
    assert len(session.calls) == 1


# CanSWE

NC_BODY = b"fake netcdf bytes"
PDF_BODY = b"fake pdf bytes"


def _record(nc_md5=None):
    def entry(key, body, md5=None):
        return {"key": key, "size": len(body),
                "checksum": "md5:" + (md5 or hashlib.md5(body).hexdigest()),
                "links": {"self": f"https://zenodo.test/files/{key}/content"}}
    return {"files": [entry("CanSWE-CanEEN_1928-2025_v8.zip", b"zip"),
                      entry("LisezMoi_CanSWE_v8.pdf", b"fr"),
                      entry("ReadMe_CanSWE_v8.pdf", PDF_BODY),
                      entry("CanSWE-CanEEN_1928-2025_v8.nc", NC_BODY, nc_md5)]}


def _canswe_responder(record):
    bodies = {"CanSWE-CanEEN_1928-2025_v8.nc": NC_BODY, "ReadMe_CanSWE_v8.pdf": PDF_BODY}

    def respond(url, params):
        if "/files/" not in url:
            return _Response(body=json.dumps(record).encode())
        return _Response(body=bodies[url.split("/files/")[1].split("/")[0]])
    return respond


def test_canswe_selection_excludes_zip():
    picked = download_canswe.select_files(_record())
    assert [p["key"] for p in picked] == ["CanSWE-CanEEN_1928-2025_v8.nc", "ReadMe_CanSWE_v8.pdf"]
    assert picked[0]["url"].endswith("CanSWE-CanEEN_1928-2025_v8.nc/content")


def test_canswe_downloads_then_skips_when_md5_matches(monkeypatch, tmp_path):
    session = _Session(_canswe_responder(_record()))
    _use(monkeypatch, download_canswe, tmp_path, session)
    download_canswe.main()
    assert (tmp_path / "CanSWE-CanEEN_1928-2025_v8.nc").read_bytes() == NC_BODY
    assert (tmp_path / "ReadMe_CanSWE_v8.pdf").read_bytes() == PDF_BODY
    assert not (tmp_path / "CanSWE-CanEEN_1928-2025_v8.zip").exists()
    assert len(session.calls) == 3
    download_canswe.main()
    assert len(session.calls) == 4  # only the record is fetched again


def test_canswe_md5_mismatch_leaves_no_file(monkeypatch, tmp_path):
    session = _Session(_canswe_responder(_record(nc_md5="0" * 32)))
    _use(monkeypatch, download_canswe, tmp_path, session)
    with pytest.raises(ValueError, match="md5 mismatch"):
        download_canswe.main()
    assert not (tmp_path / "CanSWE-CanEEN_1928-2025_v8.nc").exists()
    assert not list(tmp_path.glob("*.tmp"))
