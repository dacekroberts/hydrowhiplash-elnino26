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
