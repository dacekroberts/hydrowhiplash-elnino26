"""The map page (D85, D98) and the interactive winter chart: made-up tables
and square regions, no data/ and no network."""
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from src import interactive, map_page, theme
from src.config import (MAP_LAYERS, MAP_NORMAL_YEARS, NINO34_BOX, REGIONS, SST_EDGES, SST_PANELS,
                        SST_STEP_C)

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
    assert "cdn.plot.ly" not in text and "<script src=" not in text   # the page loads the library


def test_plotly_library_is_written_for_the_site_to_serve(tmp_path):
    out = interactive.write_plotly_lib(tmp_path / "libs" / "plotly.min.js")
    head = out.read_bytes()[:400].decode("utf-8")
    assert "plotly.js" in head and "MIT" in head and out.stat().st_size > 1_000_000


def sea_fields():
    import xarray as xr

    lat, lon = np.arange(-88.0, 89.0, 2.0), np.arange(0.0, 360.0, 2.0)
    data = np.zeros((2, lat.size, lon.size))
    (b0, b1), (c0, c1) = NINO34_BOX
    box = ((lat[:, None] >= b0) & (lat[:, None] <= b1) & (lon[None, :] >= c0) & (lon[None, :] <= c1))
    data[1][box] = 1.7
    data[:, lat > 60, :] = np.nan                              # stands in for land and ice
    field = xr.DataArray(data, coords={"year": [1997, 1998], "lat": lat, "lon": lon},
                         dims=("year", "lat", "lon"))
    return xr.Dataset({"relative": field})


def test_encode_keeps_every_cell_in_its_class():
    step = round(1 / SST_STEP_C)
    assert all(abs(e * step - round(e * step)) < 1e-9 for e in SST_EDGES)  # edges on the step
    values = np.array([-5.0, -1.0, -0.41, -0.4, 0.39, 0.4, 0.999, 1.0, 9.0, np.nan])
    text = map_page.encode(values)
    assert text[-1] == map_page.SST_ALPHABET[-1] and len(text) == values.size
    tenths = [map_page.SST_ALPHABET.index(c) - map_page.SST_HALF for c in text[:-1]]
    edges = [round(e * step) for e in SST_EDGES]
    assert ([int(np.searchsorted(edges, t, side="right")) for t in tenths]
            == [int(np.searchsorted(SST_EDGES, v, side="right")) for v in values[:-1]])


def test_ocean_panels_carry_cells_a_lookup_and_the_caution(regions):
    payload = map_page.build(tables(), regions, sea_fields())
    sea = payload["sea"]
    assert "frame" not in payload["shapes"]
    for key in ("coast", "tropics"):
        grid = sea[key]
        (la0, la1), (lo0, lo1) = SST_PANELS[key]
        assert (grid["lat0"], grid["lon0"], grid["cell"]) == (la0, lo0, 2.0)
        assert all(len(row) == grid["nlat"] * grid["nlon"] for row in grid["years"].values())
        lattice = grid["lattice"]
        assert len(lattice["fi"]) == len(lattice["fj"]) == lattice["nx"] * lattice["ny"]
        assert (lattice["nx"] - 1) * lattice["stepx"] >= grid["canvas"][0]
    # the made-up regions sit at 40-44N, so every lookup point lies near those latitudes
    row = (np.array(sea["coast"]["lattice"]["fi"]) * 2 + sea["coast"]["lat0"])
    assert 36 < row.min() and row.max() < 48
    zero = map_page.SST_ALPHABET[map_page.SST_HALF]
    tropics = sea["tropics"]
    assert set(tropics["years"]["1997"]) == {zero} and len(set(tropics["years"]["1998"])) == 2
    assert map_page.SST_ALPHABET[-1] in sea["coast"]["years"]["1998"]      # the cells north of 60
    assert sea["nino34"] == {"1997": 0.0, "1998": 1.7}
    left, top, wide, tall = tropics["box"]
    assert 0 < left < left + wide < 100 and 0 < top < top + tall < 100
    page = map_page.fragment(payload)
    assert page.count("<canvas") == 2 and 'name="rmap-sea"' in page
    assert page.count('class="rmap-sea-mini"') == 1 and page.count('class="rmap-ramp"') == 1
    assert 'value="cells"' in page and "No test, no reported number and no forecast" in page
    plain = map_page.fragment(map_page.build(tables(), regions))
    assert "<canvas" not in plain and 'class="rmap-ocean"' not in plain and '"sea":null' in plain


def test_land_backdrop_is_cut_to_each_picture(regions):
    # land over the east end of the made-up regions, land far outside both pictures, land in the tropics
    world = gpd.GeoDataFrame(geometry=[box(-118, 38, -100, 46), box(0, 40, 10, 50),
                                       box(-80, -10, -70, 10)], crs="EPSG:4326")
    payload = map_page.build(tables(), regions, sea_fields(), world)
    backdrop = payload["land"]
    assert backdrop["coast"].count("M") == 1 and backdrop["tropics"].count("M") == 1
    width, height = payload["shapes"]["width"], payload["shapes"]["height"]
    xs = [float(pair.split()[0]) for pair in backdrop["coast"][1:-1].split("L")]
    assert min(xs) > width / 2 and max(xs) <= width + 0.1     # the east side, inside the frame
    tw, th = payload["sea"]["tropics"]["canvas"]
    pts = [tuple(map(float, pair.split())) for pair in backdrop["tropics"][1:-1].split("L")]
    assert all(0 <= x <= tw and 0 <= y <= th for x, y in pts)
    assert min(x for x, _ in pts) > 0.9 * tw                  # 80W-70W, the strip's east end
    page = map_page.fragment(payload)
    assert page.count('<path class="land"') == 2 and '"land":true' in page
    assert '<path class="land"' not in map_page.fragment(map_page.build(tables(), regions))


def test_chart_fragment_carries_the_dark_colours_for_every_token_it_uses(tmp_path):
    from src import figures

    swaps = interactive.theme_swaps()
    light, dark = theme.colours("light"), theme.colours("dark")
    assert swaps["dark"][light["surface"].lower()] == dark["surface"]
    assert swaps["dark"][light["water"].lower()] == dark["water"]
    assert len(swaps["dark"]) == len(figures.COLOUR_TOKENS) + len(figures.FAMILY_TOKENS)
    out = interactive.winter_rain_html(tables()["climate_controls_region_year.csv"], tmp_path)
    text = out.read_text("utf-8")
    assert text.count('id="winter-rain-history-figure"') == 1 and "Plotly.react" in text
    figure = text.split('id="winter-rain-history-figure">')[1].split("</script>")[0]
    assert "<" not in figure and light["surface"] in figure and dark["surface"] not in figure


def test_chart_fragment_keeps_a_tapped_bar_in_a_readout(tmp_path):
    out = interactive.winter_rain_html(tables()["climate_controls_region_year.csv"], tmp_path)
    text = out.read_text("utf-8")
    assert text.startswith('<div class="chart-box">') and text.rstrip().endswith("</div>")
    assert text.count('id="winter-rain-history-readout"') == 1
    assert interactive.READOUT_HINT in text and 'el.on("plotly_click", pick)' in text
    figure = json.loads(text.split('id="winter-rain-history-figure">')[1].split("</script>")[0])
    bars = [t for t in figure["data"] if t["type"] == "bar" and t.get("hovertext")]
    assert len(bars) == len(REGIONS)
    for bar in bars:
        assert "<" not in bar["name"] and bar["name"].split(" ")[0] in REGIONS
        assert bar["unselected"]["marker"]["opacity"] == interactive.UNPICKED_OPACITY
        assert bar["selected"]["marker"]["opacity"] == 1


def test_map_fragment_links_regions_the_key_and_a_readout(regions):
    page = map_page.fragment(map_page.build(tables(), regions))
    assert page.count('class="rmap-readout"') == 1 and map_page.READOUT_HINT in page
    assert page.index('class="rmap-map"') < page.index('class="rmap-readout"') \
        < page.index('class="rmap-side"')
    for piece in ("function mark()", "function watch(el, what)", "li.dataset.klass = at",
                  '"path[data-region], tr[data-region]"'):
        assert piece in map_page.SCRIPT, piece
    assert "function link(" not in map_page.SCRIPT
