"""The site's map page (ACTION_PLAN "Second goal", Map page; D85, D98): the
seven regions drawn once, coloured by one dataset for one year, with a
selector for the dataset and a slider for the year.

Every value comes from the committed region x year tables, opened through
pin_inputs.load_input; the region outlines come from
data/processed/regions.geojson (Natural Earth admin-1, public domain),
simplified for display. No trend statistic and no test result is drawn
(D85): a colour says how one year compares with the region's own normal.

Written as one HTML fragment (an inline SVG, the values as JSON, a short
script; no map library) that site/map.qmd includes as is. Colours are the
site's CSS variables, so the page follows the light and dark themes; the
styles live with the site theme (src.theme, class rmap).

The ocean under the regions and the tropical Pacific panel (D99) are
drawn from NOAA ERSST v6 by src.ocean. They are a picture only: no test,
no reported number and no forecast reads that data, and the page says so
beside the panels. Each winter's cells go to the page as one character per
cell; the script draws them on a canvas, as bands interpolated between the
cells or as the cells themselves.

  layer_cells(spec, table)  per region and year: (class index, text)
  shapes(regions)           SVG path and label point per region
  sea(fields, frame, ...)   the ocean panels' cells and lookups
  land(world, frame, ...)   land outside the regions, for both pictures
  build()                   the page's whole payload
  fragment(payload)         the HTML

Run:  python -m src.map_page
"""
from __future__ import annotations

import html
import json
import string
from pathlib import Path

import numpy as np
import pandas as pd

from src import geo
from src.config import (ENSO_INDEX, FIRE_FIRST_YEAR, MAP_DISPLAY_CRS, MAP_LAYERS,
                        MAP_MIN_PART_KM2, MAP_NORMAL_YEARS, MAP_SIMPLIFY_KM, MAP_START_LAYER,
                        MAP_WIDTH, MIN_FIRE_HA, NATURAL_EARTH_LAND_RAW, NINO34_BOX, REGIONS,
                        RESULTS, SST_EDGES, SST_LAND_MIN_DEG2, SST_LAND_SIMPLIFY_DEG,
                        SST_LATTICE_PX, SST_LIMIT_C, SST_NORMAL_YEARS, SST_PANELS, SST_STEP_C,
                        SST_TOKENS, SST_TROPICS_WIDTH)

OUT = RESULTS / "figures" / "region_map.html"
ENSO_TABLE = "climate_controls_region_year.csv"
# Wording shown on the page: drafts for the owner (2026-10-12).
REGION_NAMES = {"PNW": "Pacific Northwest", "BC": "British Columbia", "AB": "Alberta",
                "AK": "Alaska", "YT": "Yukon", "NorCal": "Northern California",
                "SoCal": "Southern California"}
N0, N1 = MAP_NORMAL_YEARS
LAYER_TEXT = {
    "fire": ("Burned area", "Hectares burned in the fire season by fires of "
             f"{MIN_FIRE_HA} ha or more, against the region's typical season.",
             ("under a tenth of typical", "a tenth to half", "half to twice typical",
              "2 to 10 times", "over 10 times typical")),
    "rain": ("Winter rain", f"October to March precipitation, as a share of the region's "
             f"{N0}-{N1} average.",
             ("under 60% of average", "60 to 85%", "85 to 115%", "115 to 140%",
              "over 140% of average")),
    "snow": ("Snowpack", f"Snow on the ground on 1 April, as a share of the region's "
             f"{N0}-{N1} average (ERA5-Land).",
             ("under 50% of average", "50 to 80%", "80 to 120%", "120 to 150%",
              "over 150% of average")),
    "temp": ("Summer temperature", f"June to August mean temperature against the region's "
             f"{N0}-{N1} average.",
             ("more than 1 °C cooler", "0.3 to 1 °C cooler", "within 0.3 °C",
              "0.3 to 1 °C warmer", "more than 1 °C warmer")),
}
# One character per ocean cell: the value floored to SST_STEP_C and clipped
# to SST_LIMIT_C either side of zero; the last character marks land or ice.
SST_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
SST_HALF = round(SST_LIMIT_C / SST_STEP_C)
S0, S1 = SST_NORMAL_YEARS
SEA_TEXT = {
    "legend": ("over 1 °C cooler", "0.4 to 1 °C cooler", "within 0.4 °C", "0.4 to 1 °C warmer",
               "over 1 °C warmer"),
    "what": f"Sea-surface temperature, December to February, against the {S0}-{S1} winter "
            "average, with the mean of the whole tropics removed. The same colours are used "
            "for the ocean on the map above. They are a separate scale from the regions' "
            "colours: purple to amber is sea temperature only.",
    "smooth": "Bands are drawn between the 2° cells the temperature was reconstructed on, so "
              "their edges look finer than the data is.",
    "cells": "Each square is one 2° cell, about 200 km across, the grid the temperature was "
             "reconstructed on. This is the closer reading of the numbers: one value per "
             "square, nothing drawn between them.",
    "caution": "The sea-surface temperature (NOAA ERSST v6) was added for these pictures. No "
               "test, no reported number and no forecast on this site reads it. The tests "
               "found no reliable link from El Niño itself to burned area, so a warm ocean "
               "here does not forecast a fire season.",
}


def _signed(x: float, digits: int = 1) -> str:
    return f"{'−' if x < 0 else '+'}{abs(x):.{digits}f}"


def layer_cells(key: str, table: pd.DataFrame) -> dict[str, dict[int, tuple[int, str]]]:
    """{region: {year: (class index 0-4, text)}} for one layer. A year with
    no value has no entry (drawn as "no data")."""
    _, column, measure, edges, _, detail = MAP_LAYERS[key]
    cells: dict[str, dict[int, tuple[int, str]]] = {}
    for region, g in table.groupby("region"):
        g = g.sort_values("year")
        normal = g[g["year"].between(N0, N1)]
        if measure == "ratio":
            # the typical season of the history chart: back-transformed mean
            # log burned area over seasons with a counted fire
            burned = g[~g["zero_fire"].astype(bool)]
            base = float(np.expm1(burned["log_burn"].mean()))
            score = g[column] / base
        elif measure == "pct":
            score = 100 * g[column] / float(normal[column].mean())
        elif measure == "diff":
            score = g[column] - float(normal[column].mean())
        else:  # "as_is": the table already holds the percent of normal
            score = g[column]
        out = {}
        for year, value, raw in zip(g["year"], score, g[detail]):
            if pd.isna(value) or pd.isna(raw):
                continue
            klass = int(np.searchsorted(edges, value, side="right"))
            if measure == "ratio":
                text = (f"no fire of {MIN_FIRE_HA} ha or more" if raw == 0 else
                        f"{raw:,.0f} ha · {value:.2g} times a typical season")
            elif measure == "diff":
                text = f"{raw:.1f} °C · {_signed(value)} °C against average"
            else:
                text = f"{raw:,.0f} mm · {value:.0f}% of average"
            out[int(year)] = (klass, text)
        cells[region] = out
    return cells


def shapes(regions) -> dict:
    """The region outlines as SVG paths in a MAP_WIDTH-wide box: projected
    to MAP_DISPLAY_CRS, parts under MAP_MIN_PART_KM2 dropped, outlines
    simplified to MAP_SIMPLIFY_KM. For display only; nothing is measured
    from these shapes."""
    parts = regions[["region", "geometry"]].explode(index_parts=False).reset_index(drop=True)
    parts = parts[geo.area_ha(parts) / 100 >= MAP_MIN_PART_KM2]
    flat = parts.to_crs(MAP_DISPLAY_CRS)
    flat["geometry"] = flat.geometry.simplify(MAP_SIMPLIFY_KM * 1000, preserve_topology=True)
    x0, y0, x1, y1 = flat.total_bounds
    pad = 0.02 * (x1 - x0)
    scale = MAP_WIDTH / (x1 - x0 + 2 * pad)
    height = (y1 - y0 + 2 * pad) * scale

    def point(x, y):
        return f"{(x - x0 + pad) * scale:.1f} {(y1 - y + pad) * scale:.1f}"

    def ring(coords):
        return "M" + "L".join(point(x, y) for x, y in list(coords)[:-1]) + "Z"

    out = {}
    for region in REGIONS:
        polygons = list(flat.loc[flat["region"] == region, "geometry"])
        path = "".join(ring(p.exterior.coords) + "".join(ring(i.coords) for i in p.interiors)
                       for p in polygons)
        largest = max(polygons, key=lambda p: p.area).representative_point()
        out[region] = {"d": path, "label": point(largest.x, largest.y)}
    # frame: what turns a map unit back into projected metres (for the ocean)
    return {"width": MAP_WIDTH, "height": round(height, 1), "regions": out,
            "frame": (x0 - pad, y1 + pad, scale)}


def encode(values: np.ndarray) -> str:
    """One character per cell, row by row from the southernmost latitude."""
    assert 2 * SST_HALF + 1 < len(SST_ALPHABET)
    k = np.floor(np.round(values / SST_STEP_C, 6))  # the rounding only removes float noise
    k = np.clip(k, -SST_HALF, SST_HALF) + SST_HALF
    return "".join(SST_ALPHABET[-1] if np.isnan(v) else SST_ALPHABET[int(v)] for v in k.ravel())


def sea_grid(field, key: str) -> dict:
    """The cells of one panel (SST_PANELS[key]) for every winter."""
    (la0, la1), (lo0, lo1) = SST_PANELS[key]
    part = field.sel(lat=slice(la0, la1), lon=slice(lo0, lo1)).transpose("year", "lat", "lon")
    lat, lon = part["lat"].values, part["lon"].values
    return {"lat0": float(lat[0]), "lon0": float(lon[0]), "cell": float(lat[1] - lat[0]),
            "nlat": int(lat.size), "nlon": int(lon.size),
            "years": {str(int(y)): encode(part.sel(year=y).values) for y in part["year"].values}}


def sea(fields, frame: tuple[float, float, float], width: int, height: float) -> dict:
    """The ocean panels' payload from src.ocean.winter_anomalies' `relative`
    field. Each panel carries its cells and a lookup from canvas pixel to
    fractional cell position (`fi` north, `fj` east), given on a coarse
    lattice the script interpolates: for the coast panel the lattice is the
    inverse of the map's projection, for the tropical panel it is the four
    corners of a plain latitude-longitude picture."""
    from pyproj import Transformer

    from src import ocean

    field = fields["relative"]
    coast, tropics = sea_grid(field, "coast"), sea_grid(field, "tropics")
    left, top, scale = frame
    h = int(round(height))
    xs = np.arange(0, width + SST_LATTICE_PX, SST_LATTICE_PX)
    ys = np.arange(0, h + SST_LATTICE_PX, SST_LATTICE_PX)
    px, py = np.meshgrid(xs, ys)
    lon, lat = Transformer.from_crs(MAP_DISPLAY_CRS, "EPSG:4326", always_xy=True).transform(
        left + px / scale, top - py / scale)
    coast["canvas"] = [width, h]
    coast["lattice"] = {
        "nx": int(xs.size), "ny": int(ys.size), "stepx": SST_LATTICE_PX, "stepy": SST_LATTICE_PX,
        "fi": np.round((lat - coast["lat0"]) / coast["cell"], 2).ravel().tolist(),
        "fj": np.round((lon % 360 - coast["lon0"]) / coast["cell"], 2).ravel().tolist()}
    # the tropical panel: half a cell beyond the outer cell centres on every side
    cell = tropics["cell"]
    per_cell = SST_TROPICS_WIDTH / tropics["nlon"]
    th = int(round(per_cell * tropics["nlat"]))
    tropics["canvas"] = [SST_TROPICS_WIDTH, th]
    top_fi, right_fj = tropics["nlat"] - 0.5, tropics["nlon"] - 0.5
    tropics["lattice"] = {"nx": 2, "ny": 2, "stepx": SST_TROPICS_WIDTH, "stepy": th,
                          "fi": [top_fi, top_fi, -0.5, -0.5], "fj": [-0.5, right_fj, -0.5, right_fj]}
    (b0, b1), (c0, c1) = NINO34_BOX
    west, south = tropics["lon0"] - cell / 2, tropics["lat0"] - cell / 2
    span_x, span_y = cell * tropics["nlon"], cell * tropics["nlat"]
    tropics["box"] = [round(100 * v, 2) for v in (
        (c0 - west) / span_x, 1 - (b1 - south) / span_y, (c1 - c0) / span_x, (b1 - b0) / span_y)]
    step = round(1 / SST_STEP_C)
    return {"alphabet": SST_ALPHABET, "half": SST_HALF, "step": step,
            "edges": [round(e * step) for e in SST_EDGES],
            "legend": [[t, c] for t, c in zip(SST_TOKENS, SEA_TEXT["legend"])],
            "text": {k: SEA_TEXT[k] for k in ("smooth", "cells")},
            "nino34": {str(int(y)): round(float(v), 2) for y, v in ocean.nino34(field).items()},
            "coast": coast, "tropics": tropics}


def winters(table: pd.DataFrame) -> dict[int, tuple[str, str, bool, float]]:
    """{year: (winter label, phase, strong, DJF index)} from any one region."""
    g = table[table["region"] == next(iter(REGIONS))].dropna(subset=["enso_djf"])
    return {int(y): (f"{int(y) - 1}-{int(y) % 100:02d}", ph, bool(s), round(float(e), 2))
            for y, ph, s, e in zip(g["year"], g["phase"], g["strong"], g["enso_djf"])}


def _rings(shape, point) -> str:
    """An SVG path of a polygon or multipolygon, `point` turning (x, y) into text."""
    def ring(coords):
        return "M" + "L".join(point(x, y) for x, y in list(coords)[:-1]) + "Z"

    polygons = [] if shape.is_empty else getattr(shape, "geoms", [shape])
    return "".join(ring(p.exterior.coords) + "".join(ring(i.coords) for i in p.interiors)
                   for p in polygons if p.geom_type == "Polygon")


def land(world, frame: tuple[float, float, float], width: int, height: float,
         tropics: dict | None = None) -> dict:
    """Land for the page's two pictures from Natural Earth's land polygons
    (`world`, EPSG:4326, split at the 180th meridian): a backdrop, so that
    the ocean stops at a coast and not at the edge of a 2 degree cell. Display
    only. `coast`: a path in the map's own units, cut to its frame. `tropics`:
    a path in the tropical panel's canvas units, when that panel is given."""
    import geopandas as gpd
    from shapely.affinity import translate
    from shapely.geometry import box
    from shapely.ops import unary_union

    whole = unary_union(list(world.geometry))
    left, top, scale = frame
    view = box(left, top - height / scale, left + width / scale, top)
    # the two sides of the 180th meridian that the map's frame can reach
    sides = gpd.GeoSeries([whole.intersection(box(-180, 5, -80, 89)),
                           whole.intersection(box(120, 5, 180, 89))], crs="EPSG:4326")
    flat = unary_union(list(sides.to_crs(MAP_DISPLAY_CRS))).intersection(view)
    flat = flat.simplify(MAP_SIMPLIFY_KM * 1000, preserve_topology=True)
    parts = [p for p in getattr(flat, "geoms", [flat])
             if p.geom_type == "Polygon" and p.area / 1e6 >= MAP_MIN_PART_KM2]
    out = {"coast": _rings(unary_union(parts), lambda x, y: (
        f"{(x - left) * scale:.1f} {(top - y) * scale:.1f}"))}
    if tropics:
        cell = tropics["cell"]
        west, south = tropics["lon0"] - cell / 2, tropics["lat0"] - cell / 2
        east, north = west + cell * tropics["nlon"], south + cell * tropics["nlat"]
        tw, th = tropics["canvas"]
        strip = unary_union([whole.intersection(box(west, south, 180, north)),
                             translate(whole.intersection(box(-180, south, east - 360, north)),
                                       xoff=360)])
        strip = strip.simplify(SST_LAND_SIMPLIFY_DEG, preserve_topology=True)
        parts = [p for p in getattr(strip, "geoms", [strip])
                 if p.geom_type == "Polygon" and p.area >= SST_LAND_MIN_DEG2]
        out["tropics"] = _rings(unary_union(parts), lambda x, y: (
            f"{(x - west) / (east - west) * tw:.1f} {(north - y) / (north - south) * th:.1f}"))
    return out


def build(tables: dict[str, pd.DataFrame], regions, fields=None, world=None) -> dict:
    """The page's payload. `tables` maps each table name in MAP_LAYERS (and
    ENSO_TABLE) to its frame; `fields` is src.ocean.winter_anomalies' result,
    or None for a page without the ocean panels; `world` is Natural Earth's
    land, or None for a page without land outside the regions."""
    layers = {}
    for key, (name, _, _, _, tokens, _) in MAP_LAYERS.items():
        label, what, classes = LAYER_TEXT[key]
        cells = layer_cells(key, tables[name])
        layers[key] = {"label": label, "what": what,
                       "legend": [[t, c] for t, c in zip(tokens, classes)],
                       "cells": {r: {str(y): list(v) for y, v in cells.get(r, {}).items()}
                                 for r in REGIONS}}
    years = winters(tables[ENSO_TABLE])
    with_fire = [y for y, (_, ph, strong, _) in years.items()
                 if strong and ph == "el_nino"
                 and all(str(y) in layers["fire"]["cells"][r] for r in REGIONS)]
    shape = shapes(regions)
    frame = shape.pop("frame")
    ocean = None if fields is None else sea(fields, frame, shape["width"], shape["height"])
    backdrop = None if world is None else land(world, frame, shape["width"], shape["height"],
                                               ocean and ocean["tropics"])
    return {"index": ENSO_INDEX, "layers": layers, "names": REGION_NAMES,
            "years": {str(y): list(v) for y, v in sorted(years.items())},
            "start": {"layer": MAP_START_LAYER, "year": max(with_fire) if with_fire
                      else max(years)},
            "fire_first_year": FIRE_FIRST_YEAR, "shapes": shape, "sea": ocean,
            "land": backdrop}


SCRIPT = """
(function () {
  var root = document.getElementById("region-map");
  var D = JSON.parse(root.querySelector("script[type='application/json']").textContent);
  var years = Object.keys(D.years).map(Number), lo = years[0], hi = years[years.length - 1];
  var nino = years.filter(function (y) { return D.years[y][1] === "el_nino"; });
  var layer = D.start.layer, year = D.start.year;
  var slider = root.querySelector("input[type=range]");
  var q = function (s) { return root.querySelector(s); };
  function words(w) {
    if (w[1] === "el_nino") return w[2] ? "Strong El Niño winter" : "El Niño winter";
    return w[1] === "la_nina" ? "La Niña winter" : "Neutral winter";
  }
  // The ocean panels (D99), a picture only. Each panel: a canvas, the
  // winter's cells as one character each, and a lookup from pixel to cell.
  var S = D.sea, seaOn = !!S, seaSmooth = true, MISSING = -999, panels = [];
  var reach = D.land ? 0.02 : 0.5;
  function panel(canvas, G) {
    var W = canvas.width, H = canvas.height, T = G.lattice, n = W * H;
    var FI = new Float32Array(n), FJ = new Float32Array(n);
    for (var y = 0; y < H; y++) {
      var v = (y + 0.5) / T.stepy, b = Math.min(T.ny - 2, Math.floor(v)), t = v - b;
      for (var x = 0; x < W; x++) {
        var u = (x + 0.5) / T.stepx, a = Math.min(T.nx - 2, Math.floor(u)), s = u - a;
        var k = b * T.nx + a, k2 = k + T.nx;
        FI[y * W + x] = (T.fi[k] * (1 - s) + T.fi[k + 1] * s) * (1 - t) +
          (T.fi[k2] * (1 - s) + T.fi[k2 + 1] * s) * t;
        FJ[y * W + x] = (T.fj[k] * (1 - s) + T.fj[k + 1] * s) * (1 - t) +
          (T.fj[k2] * (1 - s) + T.fj[k2 + 1] * s) * t;
      }
    }
    var ctx = canvas.getContext("2d"), img = ctx.createImageData(W, H), px = img.data;
    var vals = new Int16Array(G.nlat * G.nlon), last = S.alphabet.length - 1;
    function klass(v) {
      var c = 0;
      while (c < S.edges.length && v >= S.edges[c]) c++;
      return c;
    }
    return function (rgb) {
      var str = G.years[year];
      if (!str) { ctx.clearRect(0, 0, W, H); return; }
      for (var i = 0; i < vals.length; i++) {
        var code = S.alphabet.indexOf(str.charAt(i));
        vals[i] = code === last ? MISSING : code - S.half;
      }
      for (var p = 0; p < n; p++) {
        var fi = FI[p], fj = FJ[p], c = -1, ii, jj, val;
        if (seaSmooth) {
          // a pixel between cells: the mean of the up to four around it, by
          // distance; drawn where at least half that weight is ocean, or, when
          // land is drawn over the picture, wherever any of it is
          var i0 = Math.floor(fi), j0 = Math.floor(fj), di = fi - i0, dj = fj - j0;
          var sum = 0, wsum = 0;
          for (var q4 = 0; q4 < 4; q4++) {
            ii = i0 + (q4 >> 1); jj = j0 + (q4 & 1);
            if (ii < 0 || jj < 0 || ii >= G.nlat || jj >= G.nlon) continue;
            val = vals[ii * G.nlon + jj];
            if (val === MISSING) continue;
            var wt = ((q4 >> 1) ? di : 1 - di) * ((q4 & 1) ? dj : 1 - dj);
            sum += wt * (val + 0.5); wsum += wt;   // + 0.5: the middle of the floored step
          }
          if (wsum >= reach) c = klass(sum / wsum);
        } else {
          // the cell the pixel lies in, with a thin gap at each cell's edge
          ii = Math.round(fi); jj = Math.round(fj);
          if (ii >= 0 && jj >= 0 && ii < G.nlat && jj < G.nlon &&
              Math.abs(fi - ii) < 0.47 && Math.abs(fj - jj) < 0.47) {
            val = vals[ii * G.nlon + jj];
            if (val !== MISSING) c = klass(val);
          }
        }
        var o = 4 * p;
        if (c < 0) { px[o + 3] = 0; continue; }
        px[o] = rgb[c][0]; px[o + 1] = rgb[c][1]; px[o + 2] = rgb[c][2]; px[o + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
    };
  }
  function palette() {  // the theme's colours, as the canvas needs numbers
    var probe = document.createElement("canvas").getContext("2d"), style = getComputedStyle(root);
    return S.legend.map(function (item) {
      probe.fillStyle = style.getPropertyValue("--" + item[0]).trim();
      var hex = probe.fillStyle;
      return [1, 3, 5].map(function (at) { return parseInt(hex.substr(at, 2), 16); });
    });
  }
  function signed(x, digits) { return (x < 0 ? "−" : "+") + Math.abs(x).toFixed(digits); }
  function drawSea() {
    if (!S) return;
    root.querySelectorAll(".rmap-sea, .rmap-ocean").forEach(function (el) { el.hidden = !seaOn; });
    root.querySelectorAll("input[name=rmap-sea-style]").forEach(function (el) { el.disabled = !seaOn; });
    if (!seaOn) return;
    var w = D.years[year], box = S.nino34[year], rgb = palette();
    panels.forEach(function (paint) { paint(rgb); });
    q(".rmap-sea-title").textContent = "Tropical Pacific, winter " + w[0];
    q(".rmap-sea-note").textContent = S.text[seaSmooth ? "smooth" : "cells"] +
      (box === undefined ? "" : " Mean of the outlined Niño 3.4 box on this picture: " +
        signed(box, 1) + " °C. NOAA's " + D.index + " for the winter is " + signed(w[3], 2) +
        "; it is rescaled after the same subtraction, so the two differ a little.");
    q(".rmap-tropics canvas").setAttribute("aria-label", "Sea-surface temperature of the " +
      "tropical Pacific, winter " + w[0] + (box === undefined ? "" : ": Niño 3.4 box mean " +
        signed(box, 1) + " °C against average"));
  }
  if (S) {
    panels.push(panel(q("canvas.rmap-sea"), S.coast), panel(q(".rmap-tropics canvas"), S.tropics));
    q("input[name=rmap-sea]").addEventListener("change", function (e) {
      seaOn = e.target.checked; drawSea();
    });
    root.querySelectorAll("input[name=rmap-sea-style]").forEach(function (input) {
      input.addEventListener("change", function () { seaSmooth = input.value === "smooth"; drawSea(); });
    });
    // a change of theme changes the colours a canvas was painted with
    new MutationObserver(function () { setTimeout(drawSea, 60); })
      .observe(document.body, {attributes: true, attributeFilter: ["class"]});
  }
  function draw() {
    var L = D.layers[layer], w = D.years[year];
    drawSea();
    q(".rmap-y").textContent = year;
    slider.value = year;
    slider.setAttribute("aria-valuetext", year + ", " + words(w));
    var chip = q(".rmap-chip");
    chip.textContent = words(w);
    chip.className = "rmap-chip" + (w[1] === "el_nino" ? (w[2] ? " strong" : " nino") : "");
    q(".rmap-winter").textContent = "Winter " + w[0] + " · December to February " + D.index +
      " " + (w[3] < 0 ? "−" : "+") + Math.abs(w[3]).toFixed(2);
    q(".rmap-what").textContent = L.what;
    q(".rmap-title").textContent = L.label + ", " + year;
    var legend = q(".rmap-legend");
    legend.innerHTML = "";
    L.legend.concat([["", "no data"]]).forEach(function (item) {
      var li = document.createElement("li"), sw = document.createElement("i");
      if (item[0]) sw.style.background = "var(--" + item[0] + ")"; else sw.className = "none";
      li.appendChild(sw);
      li.appendChild(document.createTextNode(item[1]));
      legend.appendChild(li);
    });
    Object.keys(D.names).forEach(function (r) {
      var cell = L.cells[r][year], path = q("path[data-region='" + r + "']");
      var row = q("tr[data-region='" + r + "']");
      var text = cell ? cell[1] : (layer === "fire" && year < D.fire_first_year ?
        "the fire record starts in " + D.fire_first_year : "no data for this year");
      path.style.fill = cell ? "var(--" + L.legend[cell[0]][0] + ")" : "";
      path.classList.toggle("none", !cell);
      path.querySelector("title").textContent = D.names[r] + ", " + year + ": " + text;
      var sw = row.querySelector(".sw");
      if (!sw) {  // made here: a page builder may drop an empty element from a table
        sw = document.createElement("span");
        row.querySelector("th").insertBefore(sw, row.querySelector("th").firstChild);
      }
      sw.style.background = cell ? "var(--" + L.legend[cell[0]][0] + ")" : "";
      sw.className = cell ? "sw" : "sw none";
      row.querySelector("td").textContent = text;
    });
  }
  function go(y) { year = Math.min(hi, Math.max(lo, y)); draw(); }
  slider.min = lo; slider.max = hi;
  slider.addEventListener("input", function () { go(Number(slider.value)); });
  root.querySelectorAll("input[name=rmap-layer]").forEach(function (input) {
    input.checked = input.value === layer;
    input.addEventListener("change", function () { layer = input.value; draw(); });
  });
  q("[data-step='-1']").addEventListener("click", function () { go(year - 1); });
  q("[data-step='1']").addEventListener("click", function () { go(year + 1); });
  q("[data-nino='-1']").addEventListener("click", function () {
    var before = nino.filter(function (y) { return y < year; });
    if (before.length) go(before[before.length - 1]);
  });
  q("[data-nino='1']").addEventListener("click", function () {
    var after = nino.filter(function (y) { return y > year; });
    if (after.length) go(after[0]);
  });
  // The strip under the slider: one cell per winter, coloured by its class
  // (owner, 2026-10-12). A click on a cell goes to that year.
  var marks = q(".rmap-marks");
  years.forEach(function (y) {
    var w = D.years[y], m = document.createElement("i");
    m.style.left = (100 * (y - lo) / (hi - lo)) + "%";
    m.style.width = (100 / (hi - lo)) + "%";
    m.className = w[1] === "el_nino" ? (w[2] ? "strong" : "nino") :
      (w[1] === "la_nina" ? "nina" : "neutral");
    m.title = y + ": " + words(w);
    m.addEventListener("click", function () { go(y); });
    marks.appendChild(m);
  });
  function link(a, b) {
    root.querySelectorAll(a).forEach(function (el) {
      var other = function () { return q(b + "[data-region='" + el.dataset.region + "']"); };
      ["mouseenter", "focus"].forEach(function (e) {
        el.addEventListener(e, function () { other().classList.add("on"); el.classList.add("on"); });
      });
      ["mouseleave", "blur"].forEach(function (e) {
        el.addEventListener(e, function () { other().classList.remove("on"); el.classList.remove("on"); });
      });
    });
  }
  link("path[data-region]", "tr");
  link("tr[data-region]", "path");
  draw();
})();
"""


def fragment(payload: dict) -> str:
    """The page's HTML: controls, the SVG, a legend and a table of the seven
    values (the same numbers for a reader who cannot use the map)."""
    shape = payload["shapes"]
    esc = html.escape
    ocean = payload.get("sea")
    backdrop = payload.pop("land", None) or {}
    payload["land"] = bool(backdrop)       # the script needs to know only that it is there
    land_path = f'<path class="land" d="{backdrop["coast"]}"/>' if backdrop else ""
    sea_controls = sea_canvas = sea_block = ""
    if ocean:
        cw, ch = ocean["coast"]["canvas"]
        tw, th = ocean["tropics"]["canvas"]
        left, top, wide, tall = ocean["tropics"]["box"]
        swatches = "".join(f'<li><i style="background: var(--{t})"></i>{esc(c)}</li>'
                           for t, c in ocean["legend"])
        sea_controls = (
            '<fieldset class="rmap-layers rmap-sea-opts"><legend>Ocean</legend>'
            '<label><input type="checkbox" name="rmap-sea" checked><span>Show the ocean</span></label>'
            '<label><input type="radio" name="rmap-sea-style" value="smooth" checked>'
            '<span>Smoothed</span></label>'
            '<label><input type="radio" name="rmap-sea-style" value="cells">'
            '<span>2° cells, as measured</span></label></fieldset>')
        sea_canvas = f'<canvas class="rmap-sea" width="{cw}" height="{ch}" aria-hidden="true"></canvas>'
        tropics_land = (f'<svg class="rmap-land" viewBox="0 0 {tw} {th}" preserveAspectRatio="none" '
                        f'aria-hidden="true"><path class="land" d="{backdrop["tropics"]}"/></svg>'
                        if backdrop.get("tropics") else "")
        sea_block = f"""<div class="rmap-ocean">
<p class="rmap-title rmap-sea-title"></p>
<div class="rmap-tropics"><canvas width="{tw}" height="{th}" role="img"></canvas>{tropics_land}<div class="rmap-box" style="left:{left}%;top:{top}%;width:{wide}%;height:{tall}%"><span>Niño 3.4</span></div></div>
<p class="rmap-what">{esc(SEA_TEXT["what"])}</p>
<ul class="rmap-legend rmap-sea-legend">{swatches}<li><i class="land"></i>land or sea ice</li></ul>
<p class="rmap-what rmap-sea-note"></p>
<p class="rmap-caution"><strong>A picture only.</strong> {esc(SEA_TEXT["caution"])}</p>
</div>
"""
    radios = "".join(
        f'<label><input type="radio" name="rmap-layer" value="{key}">'
        f'<span><i style="background: var(--{MAP_LAYERS[key][4][3]})"></i>{esc(layer["label"])}'
        f'</span></label>' for key, layer in payload["layers"].items())
    paths = "".join(
        f'<path data-region="{r}" tabindex="0" d="{s["d"]}"><title></title></path>'
        for r, s in shape["regions"].items())
    labels = "".join(
        f'<text x="{s["label"].split()[0]}" y="{s["label"].split()[1]}">{r}</text>'
        for r, s in shape["regions"].items())
    rows = "".join(
        f'<tr data-region="{r}" tabindex="0"><th scope="row">{esc(name)}</th><td></td></tr>'
        for r, name in payload["names"].items())
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<div class="rmap" id="region-map">
<script type="application/json">{data}</script>
<fieldset class="rmap-layers"><legend>Show</legend>{radios}</fieldset>
{sea_controls}
<div class="rmap-year">
<div class="rmap-step">
<button type="button" data-nino="-1" aria-label="Previous El Niño winter">◂ El Niño</button>
<button type="button" data-step="-1" aria-label="Previous year">‹</button>
<output class="rmap-y" aria-live="polite"></output>
<button type="button" data-step="1" aria-label="Next year">›</button>
<button type="button" data-nino="1" aria-label="Next El Niño winter">El Niño ▸</button>
</div>
<div class="rmap-slide"><input type="range" step="1" aria-label="Year"><div class="rmap-marks" aria-hidden="true"></div></div>
<p class="rmap-key" aria-hidden="true"><i class="strong"></i>strong El Niño<i class="nino"></i>El Niño<i class="neutral"></i>neutral<i class="nina"></i>La Niña<span>each winter, by its December to February index</span></p>
<p class="rmap-when"><span class="rmap-chip"></span><span class="rmap-winter"></span></p>
</div>
<div class="rmap-body">
<div class="rmap-map">{sea_canvas}<svg viewBox="0 0 {shape["width"]} {shape["height"]}" role="group" aria-label="Map of the seven regions">{land_path}{paths}{labels}</svg></div>
<div class="rmap-side">
<p class="rmap-title"></p>
<p class="rmap-what"></p>
<ul class="rmap-legend"></ul>
<table class="rmap-table" data-quarto-disable-processing="true"><tbody>{rows}</tbody></table>
</div>
</div>
{sea_block}<script>{SCRIPT}</script>
</div>
"""


def write(payload: dict, out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(fragment(payload).encode("utf-8"))  # LF on every platform
    return out


def main() -> None:
    import geopandas as gpd

    from src import ocean, pin_inputs
    from src.regions import load_regions

    names = {spec[0] for spec in MAP_LAYERS.values()} | {ENSO_TABLE}
    tables = {name: pin_inputs.load_input(name) for name in names}
    world = gpd.read_file(NATURAL_EARTH_LAND_RAW)
    out = write(build(tables, load_regions(), ocean.winter_anomalies(), world))
    print(f"wrote {out}: {out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
