"""Burned area of each unit and season, and its start-month split, for the
sibling prediction project's stage 6 (its request of 2026-11-06,
docs/sibling_request_units.md; route R1; D113).

The units are the sibling's 129 ecoregion units (units_c.gpkg, ESRI:102008),
read only from the path given and refused unless the file's sha256 is
UNITS_LAYER_SHA256. Every fire rule is src.fire's own: the type filter, the
MTBS/WFIGS cutover, the whole-fire floor of MIN_FIRE_HA before any clip,
CNFDB parts within CNFDB_MERGE_KM merged, each region's season window, area
through src.geo.area_ha. The one change: each kept fire is clipped to the
units of its region's country instead of to the regions (clip_to_units), and
each source's pieces are unioned within a unit, the sources summed. A unit's
season window is its region's. A fire that crosses a unit border is a piece
in each unit it reaches, so n_fires does not sum to the region's.

  fire_unit_year.csv                    unit, region, year, burn_ha,
                                        n_fires, n_undated
  fire_after_issue_date_unit_year.csv   unit, region, year, issue_date,
                                        after_ha, before_ha, undated_ha,
                                        n_after, n_before, n_undated, burn_ha
                                        (groups as src.fire_after_date)

Every unit appears in every season of its region, zero seasons kept.
Held-back seasons (2026 and later everywhere, 2025 in BC, AB and YT) are
never built: the seasons are src.fire_after_date.development_seasons(),
guarded by its guard_seasons(), and every other piece is dropped before
anything is summed (select_pieces). This module has no scoring-day path.

check_tables() runs the request's checks: the unit and season set is exactly
the layer's units times their region's seasons; no held-back or later row;
units summed to each region equal the pinned fire_region_year.csv burn_ha,
and each split area column summed equals the pinned split table, to
TOLERANCE_HA. A failed check stops the run before a file is written; the
largest gap per column is printed (development seasons only).

Run:  python -m src.fire_units --units <path to units_c.gpkg>

The tables hold values derived from MTBS (public domain), WFIGS (NIFC; its
disclaimer applies) and CNFDB (Open Government Licence - Canada), and unit
boundaries from EPA Level III ecoregions and the Ecological Framework of
Canada (Open Government Licence - Canada); they stay under those terms
(LICENSE-CONTENT, DATA_SOURCES.md).
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely

from src import fire, fire_after_date as fad, pin_inputs, run_guard
from src.geo import area_ha
from src.config import (AFTER_DATE_ISSUE_MONTHS, AFTER_DATE_RUN, AFTER_DATE_TABLE, CNFDB_RAW,
                        CRS_EQUAL_AREA, FIRE_COUNTRY, FIRE_LAST_YEAR_BY_REGION,
                        FIRE_REGION_TABLE, FIRE_SEASON_MONTHS, REGIONS, RESULTS, ROOT,
                        UNITS_AFTER_DATE_TABLE, UNITS_FIRE_RUN, UNITS_FIRE_TABLE,
                        UNITS_LAYER_SHA256)

TOLERANCE_HA = fad.TOLERANCE_HA
UNIT_COLUMNS = ["unit", "region", "year", "burn_ha", "n_fires", "n_undated"]
SPLIT_COLUMNS = ["unit", "region", "year", "issue_date", "after_ha", "before_ha", "undated_ha",
                 "n_after", "n_before", "n_undated", "burn_ha"]
SPLIT_AREAS = ["after_ha", "before_ha", "undated_ha", "burn_ha"]
PINNED_SPLIT = RESULTS / "tables" / AFTER_DATE_RUN / AFTER_DATE_TABLE


class UnitsLayerError(RuntimeError):
    """The unit layer differs from its pin or does not fit the regions."""


def polygonal(geom):
    """The polygon parts of a repaired geometry (make_valid can return a
    collection holding lines or points along a self-touching ring)."""
    if geom is None or geom.is_empty:
        return geom
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    parts = [g for g in shapely.get_parts(geom) if g.geom_type in ("Polygon", "MultiPolygon")]
    return shapely.union_all(parts) if parts else shapely.Polygon()


def prepare_units(units: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """unit, region and geometry in CRS_EQUAL_AREA, each geometry repaired
    after projection (the superseded units_b held 23 invalid polygons in
    EPSG:4326 and 21 once projected; overlay refuses invalid input). A layer
    already in ESRI:102008 and valid passes through unchanged (measured
    2026-11-06 on a GeoPackage: coordinates bit-identical). Raises for a duplicate
    unit or a region outside REGIONS."""
    units = units[["unit", "region", "geometry"]].to_crs(CRS_EQUAL_AREA)
    if units["unit"].duplicated().any():
        raise UnitsLayerError("a unit id is listed twice")
    unknown = sorted(set(units["region"]) - set(REGIONS))
    if unknown:
        raise UnitsLayerError(f"units under regions not in the study: {unknown}")
    geoms = units.geometry.make_valid().map(polygonal)
    return units.set_geometry(gpd.GeoSeries(geoms, index=units.index, crs=CRS_EQUAL_AREA))


def load_units(path: Path, expected_sha256: str = UNITS_LAYER_SHA256) -> gpd.GeoDataFrame:
    """The unit layer at `path`, refused unless its sha256 is the pinned one."""
    digest = pin_inputs.sha256(Path(path))
    if digest != expected_sha256:
        raise UnitsLayerError(f"{path} has sha256 {digest}, expected {expected_sha256}.")
    return prepare_units(gpd.read_file(path))


def clip_to_units(fires: gpd.GeoDataFrame, units: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """src.fire.clip_to_regions with units in place of regions: one row per
    fire-unit piece of its own country (the unit's region's FIRE_COUNTRY),
    with unit, region, clipped_ha (src.geo.area_ha) and the region's season
    of the fire. Season and undated rules are clip_to_regions' own."""
    units = units[["unit", "region", "geometry"]].to_crs(CRS_EQUAL_AREA)
    country = fires["source"].map({"MTBS": "US", "WFIGS": "US", "CNFDB": "CA"})
    pieces = []
    for code in ("US", "CA"):
        own = units[units["region"].map(FIRE_COUNTRY) == code]
        pieces.append(gpd.overlay(fires[country == code], own, how="intersection",
                                  keep_geom_type=True))
    cut = gpd.GeoDataFrame(pd.concat(pieces, ignore_index=True), geometry="geometry",
                           crs=CRS_EQUAL_AREA)
    cut["clipped_ha"] = area_ha(cut)
    cut["season"] = pd.Series(pd.NA, index=cut.index, dtype="Int64")
    for region, months in FIRE_SEASON_MONTHS.items():
        sel = cut["region"] == region
        cut.loc[sel, "season"] = fire.season_year(cut.loc[sel, "ignition"], months)
    undated = ~cut["month_known"].astype(bool)
    if "cnfdb_year" in cut:
        cut.loc[undated, "season"] = cut.loc[undated, "cnfdb_year"].astype("Int64")
    cut["undated"] = undated
    return cut


def unit_union(pieces: gpd.GeoDataFrame) -> pd.Series:
    """Union area per (unit, season): src.fire.union_areas per source with
    the unit as its grouping key, sources summed. Empty for no pieces."""
    if len(pieces) == 0:
        return pd.Series(dtype=float)
    areas = fire.union_areas(pieces.assign(region=pieces["unit"]))
    return areas.groupby(["region", "season"])["union_ha"].sum()


def unit_seasons(units: pd.DataFrame, seasons) -> list[tuple[str, str, int]]:
    """(unit, region, season) for every unit of each region and every season
    of that region in `seasons`: regions in REGIONS order, units by id,
    seasons ascending."""
    by_region = units.groupby("region")["unit"].apply(sorted).to_dict()
    years = {}
    for region, year in seasons:
        years.setdefault(region, []).append(int(year))
    return [(unit, region, year) for region in REGIONS if region in years
            for unit in by_region.get(region, []) for year in sorted(years[region])]


def unit_table(pieces: gpd.GeoDataFrame, units: pd.DataFrame, seasons=None,
               last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> pd.DataFrame:
    """fire_unit_year rows from clip_to_units pieces, for the region-seasons
    in `seasons` (default development_seasons; a held-back one raises)."""
    seasons = fad.guard_seasons(fad.development_seasons(last_year) if seasons is None
                                else seasons, (), last_year)
    pieces = fad.select_pieces(pieces, seasons)
    area = unit_union(pieces)
    count = pieces.groupby(["unit", "season"]).size()
    undated = pieces.groupby(["unit", "season"])["undated"].sum()
    rows = [{"unit": u, "region": r, "year": y, "burn_ha": float(area.get((u, y), 0.0)),
             "n_fires": int(count.get((u, y), 0)), "n_undated": int(undated.get((u, y), 0))}
            for u, r, y in unit_seasons(units, seasons)]
    return pd.DataFrame(rows, columns=UNIT_COLUMNS)


def unit_split_table(pieces: gpd.GeoDataFrame, units: pd.DataFrame, seasons=None,
                     issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                     last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> pd.DataFrame:
    """fire_after_issue_date_unit_year rows: src.fire_after_date.split_table
    per unit (its start_group, unions per unit)."""
    seasons = fad.guard_seasons(fad.development_seasons(last_year) if seasons is None
                                else seasons, (), last_year)
    pieces = fad.select_pieces(pieces, seasons)
    whole = unit_union(pieces)
    by_date = {}
    for label, issue_month in issue_months.items():
        group = fad.start_group(pieces, issue_month)
        area = {name: unit_union(pieces[group == name]) for name in fad.GROUPS}
        count = {name: pieces[group == name].groupby(["unit", "season"]).size()
                 for name in fad.GROUPS}
        by_date[label] = (area, count)
    rows = []
    for u, r, y in unit_seasons(units, seasons):
        for label, (area, count) in by_date.items():
            rows.append({"unit": u, "region": r, "year": y, "issue_date": label,
                         **{f"{n}_ha": float(area[n].get((u, y), 0.0)) for n in fad.GROUPS},
                         **{f"n_{n}": int(count[n].get((u, y), 0)) for n in fad.GROUPS},
                         "burn_ha": float(whole.get((u, y), 0.0))})
    return pd.DataFrame(rows, columns=SPLIT_COLUMNS)


def _gaps(table: pd.DataFrame, pinned: pd.DataFrame, keys: list[str], columns: list[str]) -> dict:
    """Per column: the largest |units summed - pinned| over the pinned keys,
    where it is, and how many keys exceed TOLERANCE_HA. A key with no unit
    row counts its pinned value as the gap."""
    sums = table.groupby(keys, as_index=False)[columns].sum()
    both = pinned[keys + columns].merge(sums, on=keys, how="left", suffixes=("", "_units"))
    out = {}
    for col in columns:
        gap = (both[col] - both[f"{col}_units"].fillna(0.0)).abs()
        i = int(gap.to_numpy().argmax()) if len(gap) else 0
        out[col] = {"max_gap_ha": float(gap.max()) if len(gap) else 0.0,
                    "at": " ".join(str(both.iloc[i][k]) for k in keys) if len(gap) else "",
                    "n_over": int((gap > TOLERANCE_HA).sum())}
    return out


def check_tables(table: pd.DataFrame, split: pd.DataFrame, pinned: pd.DataFrame,
                 pinned_split: pd.DataFrame, units: pd.DataFrame, seasons=None,
                 issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                 last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> dict[str, dict]:
    """The request's checks. Each entry: `ok`, `problems` (lines naming
    units, regions and seasons, never an area) and, for the sum checks,
    `gaps` per column (largest gap in ha, where, how many over tolerance)."""
    seasons = (fad.development_seasons(last_year) if seasons is None
               else [(r, int(y)) for r, y in seasons])
    expected = set(unit_seasons(units, seasons))
    expected_split = {(u, r, y, d) for u, r, y in expected for d in issue_months}
    out = {}
    for name, frame, want, cols in (
            ("unit table", table, expected, ["unit", "region", "year"]),
            ("split table", split, expected_split, ["unit", "region", "year", "issue_date"])):
        have = [tuple(row) for row in frame[cols].itertuples(index=False)]
        problems = []
        if len(set(have)) != len(have):
            problems.append(f"{len(have) - len(set(have))} rows held twice")
        missing, extra = want - set(have), set(have) - want
        if missing or extra:
            problems.append(f"{len(missing)} rows missing, {len(extra)} not expected "
                            f"(e.g. {sorted(missing or extra)[:3]})")
        out[f"1 {name}: the unit and season set is exact"] = {"ok": not problems,
                                                             "problems": problems}
    late = pd.concat([table[["region", "year"]], split[["region", "year"]]])
    late = late[late["year"] > late["region"].map(last_year)]
    out["2 no held-back or later season"] = {
        "ok": late.empty,
        "problems": [f"{len(late)} rows after their region's last test year"] if len(late) else []}
    keyed = ["region", "year"]
    gaps = _gaps(table, pinned, keyed, ["burn_ha"])
    out["3 units sum to the pinned region burn_ha"] = {
        "ok": all(g["n_over"] == 0 for g in gaps.values()), "gaps": gaps,
        "problems": [f"{c}: {g['n_over']} region-seasons over {TOLERANCE_HA} ha"
                     for c, g in gaps.items() if g["n_over"]]}
    gaps = _gaps(split, pinned_split, keyed + ["issue_date"], SPLIT_AREAS)
    out["4 each split column sums to the pinned split table"] = {
        "ok": all(g["n_over"] == 0 for g in gaps.values()), "gaps": gaps,
        "problems": [f"{c}: {g['n_over']} rows over {TOLERANCE_HA} ha"
                     for c, g in gaps.items() if g["n_over"]]}
    both = split.merge(table, on=["unit", "region", "year"], suffixes=("", "_unit"))
    off = int(((both["burn_ha"] - both["burn_ha_unit"]).abs() > TOLERANCE_HA).sum()
              + (both["n_undated"] != both["n_undated_unit"]).sum()
              + (both[["n_after", "n_before", "n_undated"]].sum(axis=1) != both["n_fires"]).sum())
    out["5 the split's burn_ha and counts agree with the unit table"] = {
        "ok": off == 0, "problems": [f"{off} disagreements"] if off else []}
    return out


def build_unit_pieces(units: gpd.GeoDataFrame, data_root: Path = ROOT) -> gpd.GeoDataFrame:
    """src.fire_after_date.build_pieces with clip_to_units in place of
    clip_to_regions, cut to development_seasons, so no piece of a held-back
    season is returned. Nothing is printed or written."""
    prep = fire.Prepare()
    mtbs = "/vsizip/" + fad.reroot(fad.MTBS_ZIP, data_root).as_posix() + "/mtbs_perims_DD.shp"
    fires = [prep(fire.read_mtbs(mtbs)),
             fire.read_wfigs(fad.reroot(fire.WFIGS_FILE, data_root), prepare=prep),
             prep(fire.read_cnfdb(fad.reroot(CNFDB_RAW, data_root)))]
    floored = gpd.GeoDataFrame(pd.concat(fires, ignore_index=True), geometry="geometry",
                               crs=CRS_EQUAL_AREA)
    pieces = clip_to_units(fire.splice_us(floored), units)
    return fad.select_pieces(pieces, fad.development_seasons())


def load_pinned_split(path: Path = PINNED_SPLIT) -> pd.DataFrame:
    """The region split table, refused unless it matches its provenance record."""
    record = pd.read_json(path.with_name(path.name + ".provenance.json"), typ="series")
    if pin_inputs.sha256(path) != record["result_sha256"]:
        raise pin_inputs.PinnedInputError(f"{path} differs from its provenance record.")
    return pd.read_csv(path)


def report(checks: dict[str, dict]) -> None:
    """Print each check, its problems and its largest gaps (no table value)."""
    for name, result in checks.items():
        print(f"check {name}: {'pass' if result['ok'] else 'FAIL'}")
        for line in result["problems"][:20]:
            print(f"    {line}")
        for col, g in result.get("gaps", {}).items():
            print(f"    largest gap {col}: {g['max_gap_ha']:.3e} ha at {g['at']}; "
                  f"{g['n_over']} over tolerance")


def main(units_path: Path, data_root: Path = ROOT) -> None:
    """Build both tables for development_seasons, check them, and write them
    once with their provenance records. Any failed check stops the run
    before a file is written."""
    targets = [RESULTS / "tables" / UNITS_FIRE_RUN / n
               for n in (UNITS_FIRE_TABLE, UNITS_AFTER_DATE_TABLE)]
    if any(t.exists() for t in targets):
        raise FileExistsError("a unit fire table exists; they are written once.")
    inputs = fad.verify_downloads(data_root)
    units = load_units(units_path)
    inputs.append(f"units_c.gpkg (sibling) sha256 {UNITS_LAYER_SHA256}")
    pinned = pin_inputs.load_input(FIRE_REGION_TABLE.name)
    pinned_split = load_pinned_split()
    inputs += [f"results/tables/{FIRE_REGION_TABLE.name}",
               f"results/tables/{AFTER_DATE_RUN}/{AFTER_DATE_TABLE}"]
    seasons = fad.development_seasons()
    if fad.held_back(seasons) or len(seasons) != len(pinned):
        raise fad.HeldBackSeasonError("the unit tables are the pinned table's seasons only")
    pieces = build_unit_pieces(units, data_root)
    print(f"fire-unit pieces in development seasons: {len(pieces):,}")
    table = unit_table(pieces, units, seasons)
    split = unit_split_table(pieces, units, seasons)
    checks = check_tables(table, split, pinned, pinned_split, units, seasons)
    report(checks)
    if not all(c["ok"] for c in checks.values()):
        raise SystemExit("checks failed; no table written")
    for frame, name in ((table, UNITS_FIRE_TABLE), (split, UNITS_AFTER_DATE_TABLE)):
        path = run_guard.write_result(frame, name, UNITS_FIRE_RUN, inputs=inputs)
        print(f"wrote {path}: {len(frame)} rows, sha256 {pin_inputs.sha256(path)}")


if __name__ == "__main__":
    import sys

    _args = sys.argv[1:]
    if "--units" not in _args:
        raise SystemExit("usage: python -m src.fire_units --units <units_c.gpkg>")
    main(Path(_args[_args.index("--units") + 1]),
         Path(_args[_args.index("--data-root") + 1]) if "--data-root" in _args else ROOT)
