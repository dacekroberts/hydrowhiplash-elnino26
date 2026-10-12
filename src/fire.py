"""Fire perimeters to the region x season burned-area table (Phase 3).

Steps, in order (rules in ANALYSIS_PLAN.md "Fire record rules", values in
src/config.py, measured counts in docs/methods_register.md "Fire"):
  1. Read MTBS, WFIGS and CNFDB as published (src.download_mtbs,
     src.download_wfigs, src.download_cnfdb), one row per fire with source,
     fire_id, name, fire_type, ignition date and geometry.
  2. Keep wildfires: MTBS_KEEP_TYPES, WFIGS_KEEP_TYPES, CNFDB without the
     prescribed-burn cause or flag. Every drop is counted.
  3. Splice the US record: MTBS for fires ignited before MTBS_WFIGS_CUTOVER,
     WFIGS from it.
  4. Measure each whole fire with src.geo.area_ha (CRS_EQUAL_AREA) and keep
     fires of at least MIN_FIRE_HA, before any clipping.
  5. Clip each kept fire to the regions of its own country (FIRE_COUNTRY);
     each region gets its clipped hectares.
  6. Assign each fire-region piece to that region's fire season by ignition
     date (FIRE_SEASON_MONTHS; California's January fires belong to the
     season before). CNFDB fires with a year but no month count for season
     YEAR, flagged (D59).
  7. Sum per region and season, 1984 to each region's last test year
     (FIRE_LAST_YEAR_BY_REGION), zero-fire seasons kept, and join the ENSO
     phase of the winter before.

Writes FIRE_EVENTS_TABLE (one row per fire-region piece, no geometry),
FIRE_REGION_TABLE and its committed copy in results/tables/, and prints the
source-agreement check (D60, re-run on 2023 by D61).

Run:  python -m src.fire

The committed copy holds values derived from MTBS (public domain), WFIGS
(NIFC; its disclaimer applies) and CNFDB (Open Government Licence - Canada);
they stay under those terms (LICENSE-CONTENT, DATA_SOURCES.md notices 8-10).
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from src import pin_inputs
from src.config import (CNFDB_MERGE_KM, CNFDB_PRESCRIBED_CAUSE, CNFDB_RAW, CRS_EQUAL_AREA, DATA_PROCESSED,
                        FIRE_COUNTRY, FIRE_EVENTS_TABLE, FIRE_FIRST_YEAR,
                        FIRE_LAST_YEAR_BY_REGION, FIRE_READ_BBOX, FIRE_REGION_TABLE,
                        FIRE_REGION_TABLE_FROZEN,
                        FIRE_SEASON_MONTHS, MIN_FIRE_HA, MTBS_KEEP_TYPES, MTBS_RAW, PARKS_GAP_SEASONS,
                        MTBS_UNKNOWN_TYPE, MTBS_WFIGS_CUTOVER, REGIONS, RESULTS,
                        SOURCE_AGREEMENT_MAX_LOG_DIFF, SOURCE_CHECK_YEAR, WFIGS_DEFAULT_TZ,
                        WFIGS_KEEP_TYPES, WFIGS_RAW, WFIGS_STATE_TZ)
from src.era5 import join_enso
from src.geo import area_ha
from src.regions import load_regions

MTBS_SHP = "/vsizip/" + (MTBS_RAW / "mtbs_perimeter_data.zip").as_posix() + "/mtbs_perims_DD.shp"
WFIGS_FILE = WFIGS_RAW / "wfigs_perimeters.geojson"
CNFDB_SHPS = ["NFDB_poly_1972to2020_20250630.shp", "NFDB_poly_2021to2024_20250630.shp"]
COMMITTED = RESULTS / "tables" / FIRE_REGION_TABLE.name
COMMITTED_FROZEN = RESULTS / "tables" / FIRE_REGION_TABLE_FROZEN.name
WINTERS = DATA_PROCESSED / "el_nino_winters.csv"
COLUMNS = ["source", "fire_id", "name", "fire_type", "ignition", "month_known",
           "date_known", "geometry"]


# 1. Read ------------------------------------------------------------------

def read_mtbs(path: str = MTBS_SHP) -> gpd.GeoDataFrame:
    """MTBS burned-area boundaries; ignition date from ig_date."""
    raw = pyogrio.read_dataframe(path, bbox=FIRE_READ_BBOX, force_2d=True)
    out = gpd.GeoDataFrame({
        "source": "MTBS", "fire_id": raw["event_id"], "name": raw["incid_name"],
        "fire_type": raw["incid_type"], "ignition": pd.to_datetime(raw["ig_date"]),
        "month_known": True, "date_known": True}, geometry=raw.geometry, crs=raw.crs)
    return out[COLUMNS]


def local_dates(utc: pd.Series, state: pd.Series) -> pd.Series:
    """UTC discovery times to the calendar date in the origin state's zone."""
    out = pd.Series(pd.NaT, index=utc.index, dtype="datetime64[ns]")
    zones = state.map(WFIGS_STATE_TZ).fillna(WFIGS_DEFAULT_TZ)
    for zone in zones.unique():
        sel = zones == zone
        out[sel] = utc[sel].dt.tz_convert(zone).dt.tz_localize(None).dt.normalize()
    return out


def read_wfigs(path: Path = WFIGS_FILE, first_year: int = SOURCE_CHECK_YEAR,
               prepare=None, chunk: int = 1_000) -> gpd.GeoDataFrame:
    """WFIGS incident perimeters discovered from `first_year` (UTC year),
    the only ones used (the D60 check year and every year after the
    cutover); ignition date = local discovery date.

    The file holds 73.5 M vertices with Z: attributes are read first and
    geometry only for the selected rows, in 2D, `chunk` rows at a time;
    `prepare` (e.g. the type filter and floor) runs on each chunk before
    the next is read, so only its survivors stay in memory.
    """
    cols = ["poly_IncidentName", "attr_UniqueFireIdentifier", "attr_IncidentTypeCategory",
            "attr_FireDiscoveryDateTime", "attr_POOState"]
    attrs = pyogrio.read_dataframe(path, columns=cols, read_geometry=False, fid_as_index=True)
    utc_all = pd.to_datetime(attrs["attr_FireDiscoveryDateTime"], utc=True,
                             format="%a, %d %b %Y %H:%M:%S GMT")
    fids = attrs.index[utc_all.dt.year >= first_year].to_numpy()
    parts = []
    for start in range(0, len(fids), chunk):
        part = pyogrio.read_dataframe(path, columns=cols, fids=fids[start:start + chunk],
                                      force_2d=True)
        part = part.cx[FIRE_READ_BBOX[0]:FIRE_READ_BBOX[2], FIRE_READ_BBOX[1]:FIRE_READ_BBOX[3]]
        part = wfigs_frame(part)
        parts.append(prepare(part) if prepare else part)
    return pd.concat(parts, ignore_index=True)


def wfigs_frame(raw: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """WFIGS rows in the common columns."""
    utc = pd.to_datetime(raw["attr_FireDiscoveryDateTime"], utc=True,
                         format="%a, %d %b %Y %H:%M:%S GMT")
    out = gpd.GeoDataFrame({
        "source": "WFIGS", "fire_id": raw["attr_UniqueFireIdentifier"],
        "name": raw["poly_IncidentName"], "fire_type": raw["attr_IncidentTypeCategory"],
        "ignition": local_dates(utc, raw["attr_POOState"]),
        "month_known": True, "date_known": True}, geometry=raw.geometry, crs=raw.crs)
    return out[COLUMNS]


def cnfdb_dates(year: pd.Series, month: pd.Series, day: pd.Series) -> pd.DataFrame:
    """Ignition date from the agency YEAR, MONTH, DAY; missing parts are 0 or null.

    month_known: the season window can be checked. date_known: the day is
    known too (season length). A fire with a month but no day gets the 15th
    for the window only.
    """
    month = month.fillna(0).astype(int)
    day = day.fillna(0).astype(int)
    month_known = month.between(1, 12)
    date_known = month_known & day.between(1, 31)
    parts = pd.DataFrame({"year": year.astype(int), "month": month.where(month_known, 7),
                          "day": day.where(date_known, 15)})
    ignition = pd.to_datetime(parts, errors="coerce")
    return pd.DataFrame({"ignition": ignition, "month_known": month_known,
                         "date_known": date_known & ignition.notna()})


def read_cnfdb(folder: Path = CNFDB_RAW) -> gpd.GeoDataFrame:
    """CNFDB agency polygons from FIRE_FIRST_YEAR; fire_type is "prescribed"
    for the prescribed-burn cause or flag, else the CAUSE code."""
    zip_path = "/vsizip/" + (folder / "NFDB_poly.zip").as_posix() + "/"
    raw = pd.concat([pyogrio.read_dataframe(zip_path + shp, where=f"YEAR >= {FIRE_FIRST_YEAR}",
                                            force_2d=True)
                     for shp in CNFDB_SHPS], ignore_index=True)
    raw = gpd.GeoDataFrame(raw, geometry="geometry")
    prescribed = (raw["CAUSE"] == CNFDB_PRESCRIBED_CAUSE) | (raw["PRESCRIBED"].str.lower() == "yes")
    dates = cnfdb_dates(raw["YEAR"], raw["MONTH"], raw["DAY"])
    out = gpd.GeoDataFrame({
        "source": "CNFDB", "fire_id": raw["SRC_AGENCY"] + ":" + raw["FIRE_ID"].fillna("").astype(str),
        "name": raw["FIRENAME"], "fire_type": raw["CAUSE"].where(~prescribed, "prescribed"),
        **{k: dates[k] for k in dates}}, geometry=raw.geometry, crs=raw.crs)
    out["cnfdb_year"] = raw["YEAR"].astype(int)
    out["fire_key"] = raw["FIRE_ID"].fillna("").astype(str).str.strip() != ""
    return dissolve_cnfdb(out[COLUMNS + ["cnfdb_year", "fire_key"]])


def merge_components(geoms: gpd.GeoSeries, max_km: float = CNFDB_MERGE_KM) -> np.ndarray:
    """Component label for each geometry: parts that touch or lie within
    max_km of another part (in CRS_EQUAL_AREA) share a label, chained."""
    g = geoms.make_valid().to_crs(CRS_EQUAL_AREA).to_numpy()
    label = np.arange(len(g))

    def root(i):
        while label[i] != i:
            i = label[i]
        return i

    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            if g[i].distance(g[j]) <= max_km * 1000:
                label[root(j)] = root(i)
    return np.array([root(i) for i in range(len(g))])


def dissolve_cnfdb(fires: gpd.GeoDataFrame, max_km: float = CNFDB_MERGE_KM) -> gpd.GeoDataFrame:
    """One row per CNFDB fire: polygons sharing agency, YEAR and FIRE_ID
    (fire_id and cnfdb_year) are merged before the whole-fire floor, so the
    floor sees each fire's whole area (ANALYSIS_PLAN "Fire record rules";
    audit 2026-10-08 M3: 136 such groups since 1984, e.g. BC 2003-N40570).
    Within a group only parts that touch or lie within max_km of another
    part merge (D67; audit round 2 H1): agencies reuse FIRE_ID within a
    year, so BC 1998-N40187 (349 + 207 ha, 25 km apart) is two fires.
    Further parts stay separate fires under the same fire_id. Polygons
    with a blank FIRE_ID (`fire_key` False; MB 625, SK 45, Parks Canada 9)
    are never merged.

    A merged fire takes the ignition date, date flag and fire_type of its
    earliest part with a known month; it is undated only if no part has a
    month. `n_parts` counts the polygons."""
    fires = fires.assign(n_parts=1)
    keyed = fires[fires["fire_key"]]
    dup = keyed.duplicated(["fire_id", "cnfdb_year"], keep=False)
    single = [fires[~fires["fire_key"]], keyed[~dup]]
    merged = []
    for _, g in keyed[dup].groupby(["fire_id", "cnfdb_year"], sort=False):
        for _, part in g.groupby(merge_components(g.geometry, max_km), sort=False):
            if len(part) == 1:
                single.append(part)
                continue
            dated = part[part["month_known"]]
            first = (dated if len(dated) else part).sort_values("ignition").iloc[0].copy()
            first["n_parts"] = len(part)
            first["geometry"] = part.geometry.make_valid().union_all()
            merged.append(first)
    single = pd.concat(single)
    if merged:
        single = pd.concat([single, gpd.GeoDataFrame(merged, geometry="geometry", crs=fires.crs)])
    return gpd.GeoDataFrame(single.drop(columns="fire_key"), geometry="geometry",
                            crs=fires.crs).reset_index(drop=True)


# 2-4. Filter, splice, whole-fire floor ------------------------------------

def keep_wildfires(fires: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """Drop prescribed and other non-wildfire types; return kept fires and
    the count of every (source, fire_type) with its fate."""
    keep = pd.Series(False, index=fires.index)
    keep |= (fires["source"] == "MTBS") & fires["fire_type"].isin(MTBS_KEEP_TYPES)
    keep |= (fires["source"] == "WFIGS") & fires["fire_type"].isin(WFIGS_KEEP_TYPES)
    keep |= (fires["source"] == "CNFDB") & (fires["fire_type"] != "prescribed")
    counts = (fires.assign(kept=keep).groupby(["source", "fire_type", "kept"], dropna=False)
              .size().rename("n").reset_index())
    return fires[keep], counts


def splice_us(fires: gpd.GeoDataFrame, cutover: str = MTBS_WFIGS_CUTOVER) -> gpd.GeoDataFrame:
    """MTBS fires ignited before the cutover, WFIGS fires from it; CNFDB unchanged."""
    cut = pd.Timestamp(cutover)
    keep = ((fires["source"] == "CNFDB")
            | ((fires["source"] == "MTBS") & (fires["ignition"] < cut))
            | ((fires["source"] == "WFIGS") & (fires["ignition"] >= cut)))
    return fires[keep]


def whole_fire_floor(fires: gpd.GeoDataFrame, floor: float = MIN_FIRE_HA) -> gpd.GeoDataFrame:
    """Repair geometry, measure each whole fire in the equal-area CRS
    (src.geo.area_ha), keep fires of at least `floor` hectares."""
    fires = fires.to_crs(CRS_EQUAL_AREA)
    fires = fires.set_geometry(fires.geometry.make_valid())
    fires = fires.assign(fire_ha=area_ha(fires))
    return fires[fires["fire_ha"] >= floor]


# 5-6. Clip and assign seasons ---------------------------------------------

def season_year(ignition: pd.Series, months: tuple[int, int]) -> pd.Series:
    """Fire season of each ignition date under (first, last) months, or NA
    outside the window. A last month below the first wraps into the next
    year, and those months belong to the season before: (6, 1) puts
    January Y+1 in season Y."""
    first, last = months
    month, year = ignition.dt.month, ignition.dt.year
    if first <= last:
        inside, season = month.between(first, last), year
    else:
        inside = (month >= first) | (month <= last)
        season = year.where(month >= first, year - 1)
    return season.where(inside).astype("Int64")


def clip_to_regions(fires: gpd.GeoDataFrame, regions: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """One row per fire-region piece of its own country, with clipped_ha
    (src.geo.area_ha) and the region's season of the fire."""
    regions = regions[["region", "geometry"]].to_crs(CRS_EQUAL_AREA)
    country = fires["source"].map({"MTBS": "US", "WFIGS": "US", "CNFDB": "CA"})
    pieces = []
    for code in ("US", "CA"):
        own = regions[regions["region"].map(FIRE_COUNTRY) == code]
        cut = gpd.overlay(fires[country == code], own, how="intersection", keep_geom_type=True)
        pieces.append(cut)
    cut = pd.concat(pieces, ignore_index=True)
    cut = gpd.GeoDataFrame(cut, geometry="geometry", crs=CRS_EQUAL_AREA)
    cut["clipped_ha"] = area_ha(cut)
    cut["season"] = pd.Series(pd.NA, index=cut.index, dtype="Int64")
    for region, months in FIRE_SEASON_MONTHS.items():
        sel = cut["region"] == region
        cut.loc[sel, "season"] = season_year(cut.loc[sel, "ignition"], months)
    undated = ~cut["month_known"].astype(bool)
    if "cnfdb_year" in cut:
        cut.loc[undated, "season"] = cut.loc[undated, "cnfdb_year"].astype("Int64")
    cut["undated"] = undated
    return cut


# 7. Table ------------------------------------------------------------------

def season_days(group: pd.DataFrame) -> float:
    """Days from the first to the last counted fire with a full date; NaN
    with fewer than 2 such fires (descriptive only)."""
    dated = group.loc[group["date_known"].astype(bool), "ignition"]
    if len(dated) < 2:
        return np.nan
    return float((dated.max() - dated.min()).days)


def parks_gap(region: pd.Series, year: pd.Series,
              seasons: dict[str, tuple[int, int]] = PARKS_GAP_SEASONS) -> pd.Series:
    """True for the seasons where CNFDB holds no Parks Canada polygon and
    NBAC shows park area missing (PARKS_GAP_SEASONS; D69)."""
    return pd.Series([r in seasons and seasons[r][0] <= y <= seasons[r][1]
                      for r, y in zip(region, year)], index=region.index)


def region_year_table(pieces: pd.DataFrame,
                      last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION,
                      areas: pd.DataFrame | None = None) -> pd.DataFrame:
    """Every region and season from FIRE_FIRST_YEAR to the region's last
    test year, zero-fire seasons kept (burn_ha 0, log_burn 0). `parks_gap`
    flags the seasons short of Parks Canada fires (D69).

    burn_ha is the union area of the season's counted pieces, per source,
    summed over sources (`areas`, from union_areas; D61), so overlapping
    polygons count once; double_ha is the overlap left out. Without
    `areas` the clipped areas are summed.
    """
    if areas is not None:
        per_season = areas.groupby(["region", "season"])[["union_ha", "double_ha"]].sum()
    rows = []
    for region in REGIONS:
        own = pieces[(pieces["region"] == region) & pieces["season"].notna()]
        for year in range(FIRE_FIRST_YEAR, last_year[region] + 1):
            g = own[own["season"] == year]
            rows.append({
                "region": region, "year": year, "n_fires": len(g),
                "burn_ha": (float(per_season["union_ha"].get((region, year), 0.0))
                            if areas is not None else float(g["clipped_ha"].sum())),
                "double_ha": (float(per_season["double_ha"].get((region, year), 0.0))
                              if areas is not None else 0.0),
                "n_undated": int(g["undated"].sum()),
                "n_unknown_type": int((g["fire_type"] == MTBS_UNKNOWN_TYPE).sum()),
                "first_fire": g.loc[g["date_known"].astype(bool), "ignition"].min(),
                "last_fire": g.loc[g["date_known"].astype(bool), "ignition"].max(),
                "season_days": season_days(g),
                "source": "+".join(sorted(g["source"].unique())) or "none",
            })
    table = pd.DataFrame(rows)
    table["log_burn"] = np.log1p(table["burn_ha"])
    table["zero_fire"] = table["n_fires"] == 0
    table["parks_gap"] = parks_gap(table["region"], table["year"])
    for col in ("first_fire", "last_fire"):
        table[col] = pd.to_datetime(table[col]).dt.strftime("%Y-%m-%d")
    return table


def source_agreement(fires_us: gpd.GeoDataFrame, regions: gpd.GeoDataFrame,
                     year: int = SOURCE_CHECK_YEAR) -> pd.DataFrame:
    """D60, re-run on 2023 (D61): union burned area of fires ignited in
    calendar `year`, in each US region's `year` window, from MTBS only and
    from WFIGS only under identical rules, and
    d = log(1 + ha_WFIGS) - log(1 + ha_MTBS)."""
    in_year = fires_us["ignition"].dt.year == year
    out = []
    for source in ("MTBS", "WFIGS"):
        sub = whole_fire_floor(fires_us[in_year & (fires_us["source"] == source)])
        pieces = clip_to_regions(sub, regions)
        pieces = pieces[pieces["season"] == year]  # each region's window, as in the table
        areas = union_areas(pieces) if len(pieces) else pd.DataFrame(columns=["region", "union_ha"])
        out.append(areas.groupby("region")["union_ha"].sum().rename(f"ha_{source.lower()}"))
    table = pd.concat(out, axis=1).reindex([r for r in REGIONS if FIRE_COUNTRY[r] == "US"]).fillna(0)
    table["d"] = np.log1p(table["ha_wfigs"]) - np.log1p(table["ha_mtbs"])
    table["exceeds"] = table["d"].abs() >= SOURCE_AGREEMENT_MAX_LOG_DIFF
    return table.reset_index(names="region")


def union_areas(pieces: gpd.GeoDataFrame) -> pd.DataFrame:
    """Per region, season and source: the summed clipped_ha, the area of
    the pieces' union (src.geo.area_ha) and double_ha, the difference
    (area that summing would count twice; 0 if no counted fires overlap)."""
    rows = []
    for (region, season, source), g in pieces.groupby(["region", "season", "source"]):
        union = g.geometry.union_all()
        union_ha = area_ha(gpd.GeoDataFrame(geometry=[union], crs=pieces.crs)).iloc[0]
        rows.append({"region": region, "season": int(season), "source": source,
                     "sum_ha": g["clipped_ha"].sum(), "union_ha": union_ha})
    out = pd.DataFrame(rows)
    # floating-point sum minus union leaves noise of -4e-9 to 4e-10 ha where no
    # pieces overlap (86 region-seasons negative; audit 2026-10-08 round 4
    # L8), so double_ha is rounded to a microhectare and clipped at 0
    out["double_ha"] = (out["sum_ha"] - out["union_ha"]).round(6).clip(lower=0.0)
    return out


def read_events(path: Path = FIRE_EVENTS_TABLE) -> pd.DataFrame:
    """FIRE_EVENTS_TABLE (one row per counted fire-region piece in a season
    window, written by main) with its dates and flags typed."""
    events = pd.read_csv(path, parse_dates=["ignition"], dtype={"fire_id": str})
    for col in ("month_known", "date_known", "undated"):
        events[col] = events[col].astype(bool)
    events["season"] = events["season"].astype("Int64")
    return events


def frozen_rules_pieces(pieces: pd.DataFrame) -> pd.DataFrame:
    """The pieces the rules as frozen would count (D62): MTBS "Other" fires
    dropped (the frozen list names Wildfire, Wildland Fire Use and Unknown;
    D58) and CNFDB fires without a month dropped (the frozen text assigns
    by ignition date; D59). The cutover and the floor are the same in both."""
    other = (pieces["source"] == "MTBS") & (pieces["fire_type"] == MTBS_UNKNOWN_TYPE)
    return pieces[~other & ~pieces["undated"].astype(bool)]


def frozen_rules_table(pieces: pd.DataFrame,
                       last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> pd.DataFrame:
    """Region x season table under the rules as frozen (D62): summed
    clipped area instead of the union (D61), frozen_rules_pieces, and the
    frozen years (US 1984-2025, Canada 1984-2024; FIRE_LAST_YEAR_BY_REGION,
    set before any fire data, D57, and kept by the D61 re-run)."""
    return region_year_table(frozen_rules_pieces(pieces), last_year=last_year)


def main_frozen(rebuild: bool = False) -> None:
    """Build FIRE_REGION_TABLE_FROZEN and its committed copy from
    FIRE_EVENTS_TABLE; prints burned-area totals of both tables by region
    over all seasons (no ENSO column printed; D62 firm line). The committed
    copy is a pinned input: refused without `rebuild` (--rebuild)."""
    pin_inputs.guard_write([COMMITTED_FROZEN], rebuild)
    events = read_events()
    table = join_enso(frozen_rules_table(events), pd.read_csv(WINTERS))
    for path in (FIRE_REGION_TABLE_FROZEN, COMMITTED_FROZEN):
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(table)} rows")
    pin_inputs.report_rebuild([COMMITTED_FROZEN])
    main_table = pd.read_csv(FIRE_REGION_TABLE)
    dropped = events.drop(frozen_rules_pieces(events).index)
    totals = pd.DataFrame({
        "main_ha": main_table.groupby("region")["burn_ha"].sum(),
        "frozen_ha": table.groupby("region")["burn_ha"].sum(),
        "main_fires": main_table.groupby("region")["n_fires"].sum(),
        "frozen_fires": table.groupby("region")["n_fires"].sum(),
        "dropped_other": dropped[dropped["fire_type"] == MTBS_UNKNOWN_TYPE].groupby("region").size(),
        "dropped_undated": dropped[dropped["undated"]].groupby("region").size(),
        "zero_seasons_main": main_table.groupby("region")["zero_fire"].sum(),
        "zero_seasons_frozen": table.groupby("region")["zero_fire"].sum(),
    }).reindex(list(REGIONS)).fillna(0)
    totals["ratio"] = totals["frozen_ha"] / totals["main_ha"]
    print(totals.round(3).to_string())


def write_tables(table: pd.DataFrame, rebuild: bool = False) -> None:
    """Write the table and its committed copy, a pinned input: refused
    without `rebuild`, whoever calls (cold check 2026-10-11 M1)."""
    pin_inputs.guard_write([COMMITTED], rebuild)
    for path in (FIRE_REGION_TABLE, COMMITTED):
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(table)} rows")


class Prepare:
    """Type filter, then the whole-fire floor, on one batch of fires;
    collects the per-type counts and the floor's survivors per source."""

    def __init__(self):
        self.types, self.floor = [], []

    def __call__(self, fires: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        kept, counts = keep_wildfires(fires)
        self.types.append(counts)
        floored = whole_fire_floor(kept)
        self.floor.append(kept.groupby("source").size().rename("wildfires").to_frame()
                          .join(floored.groupby("source").size().rename("at_floor")))
        return floored

    def summary(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        types = (pd.concat(self.types).groupby(["source", "fire_type", "kept"], dropna=False)["n"]
                 .sum().reset_index())
        return types, pd.concat(self.floor).groupby(level=0).sum()


def main(rebuild: bool = False) -> None:
    """Build FIRE_EVENTS_TABLE and the region x season table. Both are
    pinned inputs: refused without `rebuild` (--rebuild)."""
    pin_inputs.guard_write([FIRE_EVENTS_TABLE, COMMITTED], rebuild)
    regions = load_regions()
    prep = Prepare()
    fires = [prep(read_mtbs()), read_wfigs(prepare=prep), prep(read_cnfdb())]
    floored = gpd.GeoDataFrame(pd.concat(fires, ignore_index=True), geometry="geometry",
                               crs=CRS_EQUAL_AREA)
    types, floor = prep.summary()
    print(types.to_string(index=False))
    print(f"wildfires and fires of at least {MIN_FIRE_HA} ha (whole fire):")
    print(floor.to_string())
    print("source agreement (D60):")
    print(source_agreement(floored[floored["source"] != "CNFDB"], regions).to_string(index=False))
    spliced = splice_us(floored)
    print(f"after the cutover: {spliced.groupby('source').size().to_dict()}")
    pieces = clip_to_regions(spliced, regions)
    out_of_season = pieces["season"].isna()
    print(f"fire-region pieces {len(pieces):,}; outside the season window {out_of_season.sum():,} "
          f"({pieces.loc[out_of_season, 'clipped_ha'].sum():,.0f} ha)")
    pieces = pieces[~out_of_season]
    areas = union_areas(pieces)
    print("overlap left out by source (ha):",
          areas.groupby("source")["double_ha"].sum().round(0).to_dict())
    print(areas.sort_values("double_ha", ascending=False).head(10).to_string(index=False))
    FIRE_EVENTS_TABLE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(pieces.drop(columns="geometry")).to_csv(FIRE_EVENTS_TABLE, index=False,
                                                         lineterminator="\n")
    table = region_year_table(pieces, areas=areas)
    table = join_enso(table, pd.read_csv(WINTERS))
    write_tables(table, rebuild)
    pin_inputs.report_rebuild([FIRE_EVENTS_TABLE, COMMITTED])


if __name__ == "__main__":
    import sys

    _rebuild = "--rebuild" in sys.argv[1:]
    main_frozen(_rebuild) if "--frozen-rules" in sys.argv[1:] else main(_rebuild)
