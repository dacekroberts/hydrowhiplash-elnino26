"""Tests for src/phase2_figures.py on small synthetic tables (no data files)."""
import numpy as np
import pandas as pd

from src import phase2_figures as pf

YEARS = list(range(1985, 2026))


def enso(years):
    v = np.resize([0.1, 1.8, -0.9, 0.7], len(years))
    return pd.DataFrame({"year": years, "winter": [f"{y - 1}-{y}" for y in years],
                         "enso_index": "RONI", "enso_djf": v,
                         "phase": np.where(v >= 0.5, "el_nino", np.where(v <= -0.5, "la_nina",
                                                                         "neutral")),
                         "strong": v >= 1.5})


def tables():
    rng = np.random.default_rng(0)
    e = enso(YEARS)
    parts, index, soil = [], [], []
    for region, swe in (("PNW", 300.0), ("BC", 450.0), ("SoCal", 0.06)):
        n = len(YEARS)
        parts.append(e.assign(region=region, whiplash=rng.normal(size=n),
                              swe_apr1_mm=swe * (1 + 0.1 * rng.normal(size=n))))
        index.append(e.assign(region=region,
                              station_swe_pct=rng.uniform(50, 150, n) if region != "SoCal" else np.nan,
                              era5_swe_pct=rng.uniform(50, 150, n)))
        soil.append(e.assign(region=region, snowfall_frac=rng.uniform(0, 1, n),
                             soil_moisture=rng.uniform(0.1, 0.4, n)))
    return pd.concat(parts), pd.concat(index), pd.concat(soil)


def test_region_rules_replace_name_literals():
    phase2, index, _ = tables()
    assert pf.swe_regions(phase2) == ["PNW", "BC"]      # SoCal's normal is under 10 mm
    assert pf.station_regions(index) == ["PNW", "BC"]   # no station index for SoCal


def test_writes_the_five_phase2_figures(tmp_path):
    paths = pf.make_figures(*tables(), out_dir=tmp_path, enso_index="RONI")
    assert [p.name for p in paths] == [
        "whiplash_series_roni.png", "swe_april1_series_roni.png",
        "swe_april1_stations_vs_era5_roni.png", "snowfall_fraction_series_roni.png",
        "soil_moisture_jja_series_roni.png"]
    assert all(p.stat().st_size > 0 for p in paths)
