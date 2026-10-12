"""The map page (D85, D98) and the interactive winter chart: made-up tables
and square regions, no data/ and no network."""
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from src import interactive, map_page, theme
from src.config import MAP_LAYERS, MAP_NORMAL_YEARS, REGIONS

YEARS = range(1984, 2026)


def enso(year):
    djf = 2.0 if year == 1998 else 0.8 if year % 7 == 0 else -0.2
    return {"enso_djf": djf, "phase": "el_nino" if djf >= 0.5 else "neutral",
            "strong": djf >= 1.5, "winter": f"{year - 1}-{year % 100:02d}"}


def tables():
    fire, clim, snow = [], [], []
    for i, region in enumerate(REGIONS):
        for year in YEARS:
            ha = 0.0 if (region, year) == ("SoCal", 2014) else 1000.0 * (i + 1)
            if (region, year) == ("PNW", 1998):
                ha = 50_000.0
            if not (region in ("BC", "AB", "YT") and year == 2025):
                fire.append({"region": region, "year": year, "burn_ha": ha,
                             "log_burn": np.log1p(ha), "zero_fire": ha == 0, **enso(year)})
            clim.append({"region": region, "year": year,
                         "precip_octmar_mm": 200.0 if year == 1998 else 100.0,
                         "precip_djf_mm": 150.0 if year == 1998 else 50.0,
                         "temp_jja": 15.0 + (2.0 if year == 1998 else 0.0), **enso(year)})
            snow.append({"region": region, "year": year,
                         "era5_swe_pct": np.nan if region == "SoCal" else 100.0,
                         "era5_swe_apr1_mm": 0.1 if region == "SoCal" else 120.0, **enso(year)})
    return {"fire_region_year.csv": pd.DataFrame(fire),
            "climate_controls_region_year.csv": pd.DataFrame(clim),
            "station_swe_region_year.csv": pd.DataFrame(snow)}


@pytest.fixture
def regions():
    squares = [box(-150 + 5 * i, 40, -146 + 5 * i, 44) for i in range(len(REGIONS))]
    return gpd.GeoDataFrame({"region": list(REGIONS)}, geometry=squares, crs="EPSG:4326")


def test_layer_cells_class_a_year_against_the_regions_own_normal():
    t = tables()
    fire = map_page.layer_cells("fire", t["fire_region_year.csv"])
    assert fire["PNW"][1998][0] == 4 and "50,000 ha" in fire["PNW"][1998][1]
    assert fire["PNW"][2000][0] == 2                      # near a typical season
    assert fire["SoCal"][2014] == (0, "no fire of 405 ha or more")
    assert 2025 not in fire["BC"] and 2025 in fire["PNW"]  # the Canadian record stops a year early
    rain = map_page.layer_cells("rain", t["climate_controls_region_year.csv"])
    n0, n1 = MAP_NORMAL_YEARS
    normal = (200.0 + 100.0 * (n1 - n0)) / (n1 - n0 + 1)
    assert rain["AK"][1998] == (4, f"200 mm · {100 * 200 / normal:.0f}% of average")
    assert rain["AK"][2001][0] == 2
    temp = map_page.layer_cells("temp", t["climate_controls_region_year.csv"])
    assert temp["YT"][1998][0] == 4 and temp["YT"][1998][1].startswith("17.0 °C · +1.9")
    snow = map_page.layer_cells("snow", t["station_swe_region_year.csv"])
    assert snow["SoCal"] == {} and snow["BC"][1990] == (2, "120 mm · 100% of average")


def test_a_value_on_an_edge_goes_to_the_class_above():
    edges = MAP_LAYERS["rain"][3]
    assert int(np.searchsorted(edges, edges[0], side="right")) == 1


def test_every_layer_names_five_colours_the_theme_defines():
    for key, (_, _, measure, edges, tokens, _) in MAP_LAYERS.items():
        assert len(edges) == 4 and list(edges) == sorted(edges), key
        assert len(tokens) == 5 and measure in ("ratio", "pct", "diff", "as_is"), key
        assert len(map_page.LAYER_TEXT[key][2]) == 5, key
        for token in tokens:
            for name in theme.themes():
                assert theme.colour(token, name).startswith("#"), (key, token, name)


def test_fragment_draws_seven_regions_and_carries_every_value(regions):
    payload = map_page.build(tables(), regions)
    page = map_page.fragment(payload)
    assert page.count("<path data-region=") == len(REGIONS)
    assert page.count('name="rmap-layer"') == len(MAP_LAYERS)
    assert page.count("<tr data-region=") == len(REGIONS)
    assert 'class="rmap-key"' in page and "La Niña" in page  # the strip under the slider has its key
    data = json.loads(page.split('<script type="application/json">')[1].split("</script>")[0]
                      .replace("<\\/", "</"))
    assert set(data["layers"]) == set(MAP_LAYERS) and set(data["names"]) == set(REGIONS)
    assert data["start"] == {"layer": "fire", "year": 1998}   # the last strong winter with fire
    assert data["years"]["1998"] == ["1997-98", "el_nino", True, 2.0]
    assert data["layers"]["fire"]["cells"]["PNW"]["1998"][0] == 4
    assert "#" not in "".join(t for layer in data["layers"].values() for t, _ in layer["legend"])
    for shape in data["shapes"]["regions"].values():
        assert shape["d"].startswith("M") and shape["d"].endswith("Z")


def test_winter_rain_html_labels_every_panel(tmp_path):
    table = tables()["climate_controls_region_year.csv"]
    out = interactive.winter_rain_html(table, tmp_path)
    text = out.read_text("utf-8")
    assert text.count('id="winter-rain-history"') == 1
    assert "vs average winter" in text and "January year" in text
    # Plotly writes non-ASCII letters as escapes, so the legend is matched on its ASCII part
    assert "winter (shaded year)" in text and "(darker tick)" in text
    assert text.count('"showticklabels":true') >= len(REGIONS)
