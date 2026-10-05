"""Tests for download helpers that run without network access."""
import io
import sys
import types
from datetime import date

import pytest

sys.modules.setdefault("cdsapi", types.SimpleNamespace(Client=object))  # not needed offline

from src import download_era5, download_oni  # noqa: E402


def test_classify_winters_columns_and_start():
    raw = io.StringIO("SEAS YR TOTAL ANOM\nDJF 1950 24.7 -1.5\nDJF 1951 25.0 -0.8\n"
                      "DJF 1998 29.0 2.4\nDJF 2017 26.3 -0.3\n")
    out = download_oni.classify_winters(download_oni.parse(raw))
    assert list(out.columns) == ["year", "winter", "enso_djf", "phase", "strong"]
    assert out["year"].min() == 1951  # winter 1949-50 dropped: no ERA5-Land
    row = out.set_index("year").loc[1998]
    assert row["phase"] == "el_nino" and bool(row["strong"])


@pytest.mark.parametrize("today, year, expected", [
    (date(2026, 10, 4), 2025, list(range(1, 13))),
    (date(2026, 10, 4), 2026, list(range(1, 8))),   # 3-month lag: through July
    (date(2027, 2, 10), 2026, list(range(1, 12))),  # through November
    (date(2027, 2, 10), 2027, []),
    (date(2027, 4, 1), 2027, [1]),
])
def test_months_available_respects_lag(today, year, expected):
    assert download_era5.months_available(year, today) == expected


class _HTTPError(Exception):
    def __init__(self, status):
        super().__init__(f"{status} Client Error")
        self.response = types.SimpleNamespace(status_code=status)


class _FakeClient:
    def __init__(self, status):
        self.status, self.calls = status, 0

    def retrieve(self, *args):
        self.calls += 1
        raise _HTTPError(self.status)


@pytest.mark.parametrize("status, stops", [(403, True), (401, True), (500, False)])
def test_access_errors_stop_the_run(monkeypatch, tmp_path, status, stops):
    client = _FakeClient(status)
    monkeypatch.setattr(download_era5, "RAW", tmp_path)
    monkeypatch.setattr(download_era5.cdsapi, "Client", lambda: client, raising=False)
    if stops:
        with pytest.raises(SystemExit):
            download_era5.main()
        assert client.calls == 1  # no further years requested
    else:
        download_era5.main()  # other errors skip the year and carry on
        assert client.calls > 1


class _RecordingClient:
    def __init__(self):
        self.requests = []

    def retrieve(self, dataset, req, target):
        self.requests.append((req, target))
        raise _HTTPError(500)  # nothing written; every year is attempted


def test_variable_set_goes_to_its_own_folder(monkeypatch, tmp_path):
    client = _RecordingClient()
    monkeypatch.setattr(download_era5, "RAW", tmp_path)
    monkeypatch.setattr(download_era5.cdsapi, "Client", lambda: client, raising=False)
    download_era5.main(["--set", "snow_soil", "north"])
    req, target = client.requests[0]
    assert req["variable"] == ["snowfall", "volumetric_soil_water_layer_1",
                               "volumetric_soil_water_layer_2"]
    assert req["area"] == [71.5, -169, 51, -123.5]
    assert (tmp_path / "era5_land_north_snow_soil").is_dir()
    assert not (tmp_path / "era5_land_north").exists()  # core folder untouched


def test_default_set_is_core(monkeypatch, tmp_path):
    client = _RecordingClient()
    monkeypatch.setattr(download_era5, "RAW", tmp_path)
    monkeypatch.setattr(download_era5.cdsapi, "Client", lambda: client, raising=False)
    download_era5.main(["main"])
    req, _ = client.requests[0]
    assert req["variable"] == ["total_precipitation", "2m_temperature",
                               "snow_depth_water_equivalent"]
    assert (tmp_path / "era5_land").is_dir()


@pytest.mark.parametrize("args", [["--set"], ["--set", "nope"]])
def test_bad_variable_set_stops(args):
    with pytest.raises(SystemExit):
        download_era5.main(args)


from src import download_era5_april1  # noqa: E402


@pytest.mark.parametrize("today, last", [
    (date(2026, 10, 4), 2026),
    (date(2027, 4, 3), 2026),   # inside the hourly lag
    (date(2027, 4, 8), 2027),
])
def test_april1_years_respect_hourly_lag(today, last):
    years = download_era5_april1.april1_years(today)
    assert years[0] == 1950 and years[-1] == last


def test_april1_request_is_one_snapshot_per_year():
    req = download_era5_april1.request([1950, 1951], [71.5, -169, 51, -123.5])
    assert req["month"] == ["04"] and req["day"] == ["01"] and req["time"] == ["00:00"]
    assert req["variable"] == ["snow_depth_water_equivalent"]
    assert req["year"] == ["1950", "1951"]


def test_april1_access_error_stops(monkeypatch, tmp_path):
    monkeypatch.setattr(download_era5_april1, "RAW", tmp_path)
    monkeypatch.setattr(download_era5_april1.cdsapi, "Client", lambda: _FakeClient(403),
                        raising=False)
    with pytest.raises(SystemExit):
        download_era5_april1.main(["main"])
