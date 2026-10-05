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
    monkeypatch.setattr(download_era5, "OUT", tmp_path)
    monkeypatch.setattr(download_era5.cdsapi, "Client", lambda: client, raising=False)
    if stops:
        with pytest.raises(SystemExit):
            download_era5.main()
        assert client.calls == 1  # no further years requested
    else:
        download_era5.main()  # other errors skip the year and carry on
        assert client.calls > 1
