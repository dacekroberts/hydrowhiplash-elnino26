"""Tests for src/winter_figures.py on synthetic ERA5-Land data (no data files)."""
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely.geometry import box

from src import winter_figures as wf

YEARS = range(1995, 2001)   # winters 1996-2000 complete; 1998 is on the map


@pytest.fixture
def inputs():
    time = pd.date_range("1995-01-01", "2000-12-01", freq="MS")
    lat, lon = np.arange(33.05, 47, 0.5), np.arange(-121.95, -115, 0.5)
    rng = np.random.default_rng(0)
    tp = xr.DataArray(rng.uniform(10, 100, (len(time), len(lat), len(lon))).astype("float32"),
                      coords={"valid_time": time, "latitude": lat, "longitude": lon},
                      dims=("valid_time", "latitude", "longitude"))
    datasets = {"main": xr.Dataset({"tp": tp})}
    regions = gpd.GeoDataFrame({"region": ["PNW", "SoCal"], "role": ["primary", "contrast"]},
                               geometry=[box(-121, 44, -119, 46), box(-118, 33.5, -116, 35)],
                               crs="EPSG:4326")

    def classify(enso):
        years = list(range(1996, 2001))
        phase = ["el_nino" if v >= 0.5 else "la_nina" if v <= -0.5 else "neutral" for v in enso]
        return pd.DataFrame({"year": years, "winter": [f"{y - 1}-{y}" for y in years],
                             "enso_djf": enso, "phase": phase,
                             "strong": [v >= 1.5 for v in enso]})

    oni = classify([0.1, -0.7, 2.2, -1.4, -1.7])
    by_index = {"ONI": oni, "RONI": classify([0.6, -0.4, 2.4, -1.5, -1.9])}
    return regions, datasets, oni, by_index


def test_writes_the_three_phase1_figures(inputs, tmp_path, monkeypatch):
    regions, datasets, oni, by_index = inputs
    calls = {}

    def fake_map(pcts, regions, region_pct, title, out, **kw):
        # The map needs cartopy's Natural Earth layers (a download); check its inputs.
        calls.update(pcts=pcts, region_pct=region_pct, title=title)
        out.write_bytes(b"png")
        return out

    monkeypatch.setattr(wf.figures, "percent_of_normal_map", fake_map)
    monkeypatch.setattr(wf, "ENSO_INDEX", "ONI")
    paths = wf.make_figures(regions, datasets, oni, by_index, out_dir=tmp_path)

    assert [p.name for p in paths] == ["djf_precip_series_oni.png", wf.MAP_FILE,
                                       "djf_precip_series_oni_vs_roni.png"]
    assert all(p.stat().st_size > 0 for p in paths)
    assert calls["title"] == "Winter 1997-98 (Dec-Feb) precipitation, % of the 1950-2026 mean"
    assert list(calls["region_pct"].index) == ["PNW", "SoCal"]


def test_map_inputs_are_percent_of_the_all_winter_mean(inputs):
    regions, datasets, oni, _ = inputs
    table, _ = wf.era5.build_winter_precip_table(regions, oni, datasets)
    pcts, region_pct = wf.map_inputs(table, datasets, winter=1998)
    djf = wf.era5.winter_total(datasets["main"]["tp"])
    expected = djf.sel(year=1998) / djf.mean("year") * 100
    xr.testing.assert_allclose(pcts[0], expected)
    pnw = table[table["region"] == "PNW"].set_index("year")["precip_djf_mm"]
    assert region_pct["PNW"] == pytest.approx(pnw.loc[1998] / pnw.mean() * 100)


def test_comparison_keeps_every_winter_per_index(inputs):
    regions, datasets, oni, by_index = inputs
    table, _ = wf.era5.build_winter_precip_table(regions, oni, datasets)
    tables = wf.series_by_index(table, by_index)
    assert list(tables) == ["ONI", "RONI"]
    for name, t in tables.items():
        assert len(t) == len(table)                    # every winter, every phase
        assert (t.groupby("year")["phase"].first()
                == by_index[name].set_index("year")["phase"]).all()
