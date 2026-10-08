"""Tests for the fire download scripts: zip, size and feature-count checks
and the WFIGS Hub export polling, without network access."""
import json
import zipfile

import pytest

from src import download_cnfdb, download_mtbs, download_wfigs


def test_check_zip_accepts_good_and_rejects_truncated(tmp_path):
    good = tmp_path / "a.zip"
    with zipfile.ZipFile(good, "w") as zf:
        zf.writestr("x.txt", "hello" * 1000)
    download_mtbs.check_zip(good)
    bad = tmp_path / "b.zip"
    bad.write_bytes(good.read_bytes()[:-40])
    with pytest.raises(Exception):
        download_mtbs.check_zip(bad)


def test_size_check_matches_server_length(tmp_path):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"x" * 10)
    download_cnfdb.size_check(10, is_zip=False)(f)
    with pytest.raises(ValueError):
        download_cnfdb.size_check(11, is_zip=False)(f)


def test_count_check_compares_feature_count(tmp_path):
    f = tmp_path / "p.geojson"
    feature = {"type": "Feature", "properties": {"a": 1},
               "geometry": {"type": "Point", "coordinates": [0, 0]}}
    f.write_text(json.dumps({"type": "FeatureCollection", "features": [feature, feature]}))
    download_wfigs.count_check(2)(f)
    with pytest.raises(ValueError):
        download_wfigs.count_check(3)(f)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def get(self, *args, **kwargs):
        return FakeResponse(self.payloads.pop(0))


def test_request_export_polls_until_completed(monkeypatch):
    monkeypatch.setattr(download_wfigs, "POLL_S", 0)
    session = FakeSession([{"status": "ExportingData", "progressInPercent": 50},
                           {"status": "Completed", "resultUrl": "u", "recordCount": 2}])
    assert download_wfigs.request_export(session)["resultUrl"] == "u"


def test_request_export_gives_up(monkeypatch):
    monkeypatch.setattr(download_wfigs, "POLL_S", 0)
    monkeypatch.setattr(download_wfigs, "WFIGS_EXPORT_WAIT_S", -1)
    with pytest.raises(SystemExit):
        download_wfigs.request_export(FakeSession([{"status": "Pending"}]))
