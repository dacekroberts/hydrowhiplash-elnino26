"""Parks Canada gap: the fire table with NBAC's national-park area added (D69).

CNFDB holds no Parks Canada polygon for 2016-2021, and the provinces do not
map fires inside the national parks, so the seasons in PARKS_GAP_SEASONS
(AB 2016-2019) are short of their park fires. NBAC splits its fire events at
national park boundaries (ADMIN_NAME NBAC_PARK_ADMIN), so it measures the
missing park area directly. This module builds FIRE_REGION_TABLE_PARKS: the
main fire table with that area added for the flagged seasons, for a reported
sensitivity run (exploratory, not registered; owner 2026-10-08).

NBAC park area is built the way the main table is: NBAC parts dissolved by
GID (year and NFIREID), prescribed parts dropped, the whole fire's area from
src.geo.area_ha floored at MIN_FIRE_HA, the park parts clipped to the
region, then unioned per season. NBAC has no ignition date (AG_SDATE agency
start, HS_SDATE first hotspot), so a fire counts for its YEAR; the run
prints how many park parts carry a known start month outside the region's
FIRE_SEASON_MONTHS.

Measured 2026-10-08 (session 7 scratch): summed over AB 1984-2017, NBAC park
area and CNFDB Parks Canada area agree within 1% (1,250,741 vs 1,259,913
ha); single seasons differ more: within 5% in 5 of the 14 AB seasons where
both are above 0 (2011 65,235 vs 66,172 ha; 2015 334,954 vs 332,647 ha),
within 15% in 7, up to about 2x (2007 164,360 vs 85,810 ha; 2023 676,985
vs 886,790 ha). So one season's added area is an estimate with that spread.
Non-Parks Canada CNFDB polygons (whole fire at the floor) overlapping the
added NBAC park pieces: AB 2016 181 ha (of 6,855), 2017 1 ha, 2018 and
2019 0 ha, so the sum double counts at most 0.04% of a season.

Run:  python -m src.parks_gap   (after python -m src.fire)

The committed copy holds values derived from CNFDB and NBAC (Open
Government Licence - Canada); they stay under those terms (LICENSE-CONTENT,
DATA_SOURCES.md notices 10 and 11).
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from src.config import (CRS_EQUAL_AREA, FIRE_REGION_TABLE, FIRE_REGION_TABLE_PARKS,
                        FIRE_SEASON_MONTHS, MIN_FIRE_HA, NBAC_FILES, NBAC_PARK_ADMIN, NBAC_RAW,
                        NBAC_RELEASE, PARKS_GAP_SEASONS, RESULTS)
from src.geo import area_ha
from src.regions import load_regions

COMMITTED = RESULTS / "tables" / FIRE_REGION_TABLE_PARKS.name
NBAC_SHP = ("/vsizip/" + (NBAC_RAW / NBAC_FILES[0]).as_posix()
            + f"/NBAC_merged_1972_to_2025_{NBAC_RELEASE}.shp")
NBAC_COLUMNS = ["YEAR", "GID", "ADMIN_NAME", "ADMIN_DIV", "PRESCRIBED", "AG_SDATE", "HS_SDATE"]


def read_nbac_year(year: int, path: str = NBAC_SHP) -> gpd.GeoDataFrame:
    """One NBAC year in CRS_EQUAL_AREA, prescribed parts dropped, geometry
    repaired, with each part's area and its whole fire's area (GID)."""
    nb = pyogrio.read_dataframe(path, where=f"YEAR = {year}", columns=NBAC_COLUMNS,
                                force_2d=True)
    nb = nb[nb["PRESCRIBED"].isna()].to_crs(CRS_EQUAL_AREA)
    nb = nb.set_geometry(nb.geometry.make_valid())
    return whole_fire_area(nb)


def whole_fire_area(parts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """part_ha from src.geo.area_ha and fire_ha, the sum over the parts that
    share a GID (NBAC splits a fire at provincial and park boundaries)."""
    parts = parts.assign(part_ha=area_ha(parts))
    return parts.assign(fire_ha=parts.groupby("GID")["part_ha"].transform("sum"))


def park_pieces(parts: gpd.GeoDataFrame, region: gpd.GeoDataFrame,
                floor: float = MIN_FIRE_HA) -> gpd.GeoDataFrame:
    """Park parts (ADMIN_NAME NBAC_PARK_ADMIN) of fires whose whole area
    reaches the floor, clipped to the region."""
    parks = parts[(parts["ADMIN_NAME"] == NBAC_PARK_ADMIN) & (parts["fire_ha"] >= floor)]
    if parks.empty:
        return parks.assign(region=pd.Series(dtype=str))
    return gpd.overlay(parks, region[["region", "geometry"]], how="intersection",
                       keep_geom_type=True)


def union_ha(pieces: gpd.GeoDataFrame) -> float:
    if pieces.empty:
        return 0.0
    return float(area_ha(gpd.GeoDataFrame(geometry=[pieces.geometry.union_all()],
                                          crs=pieces.crs)).iloc[0])


def start_month_outside(pieces: gpd.GeoDataFrame, months: tuple[int, int]) -> int:
    """Park parts whose known start month (AG_SDATE, else HS_SDATE) lies
    outside the season window (a window without wrap, as AB's)."""
    start = pd.to_datetime(pieces["AG_SDATE"]).fillna(pd.to_datetime(pieces["HS_SDATE"]))
    m = start.dt.month
    return int((m.notna() & ~m.between(*months)).sum())


def park_area(seasons: dict[str, tuple[int, int]] = PARKS_GAP_SEASONS) -> pd.DataFrame:
    """NBAC park area (ha), park fires and parts dated outside the window,
    per flagged region and season."""
    regions = load_regions().to_crs(CRS_EQUAL_AREA)
    rows = []
    for region, (first, last) in seasons.items():
        shape = regions[regions["region"] == region]
        for year in range(first, last + 1):
            pieces = park_pieces(read_nbac_year(year), shape)
            rows.append({"region": region, "year": year, "nbac_park_ha": union_ha(pieces),
                         "n_nbac_park": int(pieces["GID"].nunique()) if len(pieces) else 0,
                         "n_dated_outside": start_month_outside(pieces, FIRE_SEASON_MONTHS[region])
                         if len(pieces) else 0})
    return pd.DataFrame(rows)


def with_park_area(table: pd.DataFrame, parks: pd.DataFrame) -> pd.DataFrame:
    """The main table with nbac_park_ha added to burn_ha for the flagged
    seasons (0 elsewhere), log_burn recomputed and zero_fire updated."""
    out = table.merge(parks[["region", "year", "nbac_park_ha", "n_nbac_park"]],
                      on=["region", "year"], how="left", validate="one_to_one")
    out[["nbac_park_ha", "n_nbac_park"]] = out[["nbac_park_ha", "n_nbac_park"]].fillna(0)
    out["n_nbac_park"] = out["n_nbac_park"].astype(int)
    out["burn_ha"] = out["burn_ha"] + out["nbac_park_ha"]
    out["log_burn"] = np.log1p(out["burn_ha"])
    out["zero_fire"] = out["zero_fire"] & (out["nbac_park_ha"] == 0)
    return out


def main() -> None:
    parks = park_area()
    table = pd.read_csv(FIRE_REGION_TABLE)
    out = with_park_area(table, parks)
    for path in (FIRE_REGION_TABLE_PARKS, COMMITTED):
        path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(out)} rows")
    # fire columns only (no ENSO column printed; D62 firm line)
    report = parks.merge(table[["region", "year", "burn_ha"]], on=["region", "year"])
    report["missing_share"] = report["nbac_park_ha"] / (report["burn_ha"] + report["nbac_park_ha"])
    report["log_burn_change"] = (np.log1p(report["burn_ha"] + report["nbac_park_ha"])
                                 - np.log1p(report["burn_ha"]))
    print(report.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
