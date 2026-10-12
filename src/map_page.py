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

  layer_cells(spec, table)  per region and year: (class index, text)
  shapes(regions)           SVG path and label point per region
  build()                   the page's whole payload
  fragment(payload)         the HTML

Run:  python -m src.map_page
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src import geo
from src.config import (ENSO_INDEX, FIRE_FIRST_YEAR, MAP_DISPLAY_CRS, MAP_LAYERS,
                        MAP_MIN_PART_KM2, MAP_NORMAL_YEARS, MAP_SIMPLIFY_KM, MAP_START_LAYER,
                        MAP_WIDTH, MIN_FIRE_HA, REGIONS, RESULTS)

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
    return {"width": MAP_WIDTH, "height": round(height, 1), "regions": out}


def winters(table: pd.DataFrame) -> dict[int, tuple[str, str, bool, float]]:
    """{year: (winter label, phase, strong, DJF index)} from any one region."""
    g = table[table["region"] == next(iter(REGIONS))].dropna(subset=["enso_djf"])
    return {int(y): (f"{int(y) - 1}-{int(y) % 100:02d}", ph, bool(s), round(float(e), 2))
            for y, ph, s, e in zip(g["year"], g["phase"], g["strong"], g["enso_djf"])}


def build(tables: dict[str, pd.DataFrame], regions) -> dict:
    """The page's payload. `tables` maps each table name in MAP_LAYERS (and
    ENSO_TABLE) to its frame."""
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
    return {"index": ENSO_INDEX, "layers": layers, "names": REGION_NAMES,
            "years": {str(y): list(v) for y, v in sorted(years.items())},
            "start": {"layer": MAP_START_LAYER, "year": max(with_fire) if with_fire
                      else max(years)},
            "fire_first_year": FIRE_FIRST_YEAR, "shapes": shapes(regions)}


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
  function draw() {
    var L = D.layers[layer], w = D.years[year];
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
  var marks = q(".rmap-marks");
  nino.forEach(function (y) {
    var m = document.createElement("i");
    m.style.left = (100 * (y - lo) / (hi - lo)) + "%";
    if (D.years[y][2]) m.className = "strong";
    m.title = y + ": " + words(D.years[y]);
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
<div class="rmap-year">
<div class="rmap-step">
<button type="button" data-nino="-1" aria-label="Previous El Niño winter">◂ El Niño</button>
<button type="button" data-step="-1" aria-label="Previous year">‹</button>
<output class="rmap-y" aria-live="polite"></output>
<button type="button" data-step="1" aria-label="Next year">›</button>
<button type="button" data-nino="1" aria-label="Next El Niño winter">El Niño ▸</button>
</div>
<div class="rmap-slide"><input type="range" step="1" aria-label="Year"><div class="rmap-marks" aria-hidden="true"></div></div>
<p class="rmap-when"><span class="rmap-chip"></span><span class="rmap-winter"></span></p>
</div>
<div class="rmap-body">
<svg viewBox="0 0 {shape["width"]} {shape["height"]}" role="group" aria-label="Map of the seven regions">{paths}{labels}</svg>
<div class="rmap-side">
<p class="rmap-title"></p>
<p class="rmap-what"></p>
<ul class="rmap-legend"></ul>
<table class="rmap-table" data-quarto-disable-processing="true"><tbody>{rows}</tbody></table>
</div>
</div>
<script>{SCRIPT}</script>
</div>
"""


def write(payload: dict, out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(fragment(payload).encode("utf-8"))  # LF on every platform
    return out


def main() -> None:
    from src import pin_inputs
    from src.regions import load_regions

    names = {spec[0] for spec in MAP_LAYERS.values()} | {ENSO_TABLE}
    tables = {name: pin_inputs.load_input(name) for name in names}
    out = write(build(tables, load_regions()))
    print(f"wrote {out}: {out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
