"""Parks Canada gap: the fire table with NBAC's national-park area added (D69).

CNFDB holds no Parks Canada polygon at or above 405 ha in BC, AB or YT for
2016-2021 (none at all for 2018-2020; Nahanni, NWT, only in 2016-2017; 2021
small fires only; D71), and the provinces do not map fires inside the
national parks, so the seasons in PARKS_GAP_SEASONS
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

Measured 2026-10-08 (`--measure`, unions per season as burn_ha): NBAC park
area in AB 1984-2017 is 1.3% above CNFDB's Parks Canada area (1,250,741 vs
1,234,910 ha); in the 25 seasons where both are above 0, single seasons
agree within 5% in 6 and within 15% in 11, the ratio running 0.45 (1985)
to 2.08 (2008). NBAC runs below CNFDB in most large seasons (2003 0.68,
2004 0.74, 2012 0.84), consistent with NBAC removing unburned islands and
water, so the added area is more likely low than high (round 4 F3).
Non-Parks Canada CNFDB polygons (whole fire at the floor) overlapping the
added NBAC park pieces: AB 2016 181 ha (of 6,855), 2017 1 ha, 2018 and
2019 0 ha, so the sum double counts at most 0.04% of a season.

Run:  python -m src.parks_gap             (after python -m src.fire)
      python -m src.parks_gap --measure   the register's figures (MEASURE_TABLE in
                                          data/processed/, about 20 minutes)

The committed copy holds values derived from CNFDB and NBAC (Open
Government Licence - Canada); they stay under those terms (LICENSE-CONTENT,
DATA_SOURCES.md notices 10 and 11).
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from src.config import (CNFDB_LAST_YEAR, CRS_EQUAL_AREA, DATA_PROCESSED, FIRE_FIRST_YEAR,
                        FIRE_REGION_TABLE, FIRE_REGION_TABLE_PARKS, FIRE_SEASON_MONTHS,
                        MIN_FIRE_HA, NBAC_DND_ADMIN, NBAC_FILES, NBAC_PARK_ADMIN, NBAC_RAW,
                        NBAC_RELEASE, PARKS_GAP_SEASONS, RESULTS)
from src.geo import area_ha
from src.regions import load_regions

COMMITTED = RESULTS / "tables" / FIRE_REGION_TABLE_PARKS.name
NBAC_SHP = ("/vsizip/" + (NBAC_RAW / NBAC_FILES[0]).as_posix()
            + f"/NBAC_merged_1972_to_2025_{NBAC_RELEASE}.shp")
NBAC_COLUMNS = ["YEAR", "GID", "ADMIN_NAME", "ADMIN_DIV", "PRESCRIBED", "AG_SDATE", "HS_SDATE"]
MEASURE_TABLE = DATA_PROCESSED / "parks_gap_measure.csv"
CANADA = ("BC", "AB", "YT")


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
                floor: float = MIN_FIRE_HA, admin: str = NBAC_PARK_ADMIN) -> gpd.GeoDataFrame:
    """Parts labelled `admin` (national parks by default; NBAC_DND_ADMIN for
    defence lands) of fires whose whole area reaches the floor, clipped to
    the region."""
    parks = parts[(parts["ADMIN_NAME"] == admin) & (parts["fire_ha"] >= floor)]
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


# Measurement behind the register's "Parks Canada gap" and "Defence lands"
# rows (audit 2026-10-08 round 4 L1, L2, M2, F3, process) -------------------

def per_season_union(pieces: gpd.GeoDataFrame, keys: list[str]) -> pd.Series:
    """Union area (ha) per group of `keys`; empty input gives an empty Series."""
    if pieces.empty:
        return pd.Series(dtype=float)
    return pieces.groupby(keys).apply(union_ha)


def nbac_admin_area(years: range, regions: gpd.GeoDataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """NBAC park and defence-land area per region and season (union of the
    clipped parts of fires at the floor), and park area per park
    (ADMIN_DIV), for every year in `years`."""
    rows, by_park = [], []
    for year in years:
        parts = read_nbac_year(year)
        for admin, col in ((NBAC_PARK_ADMIN, "nbac_park_ha"), (NBAC_DND_ADMIN, "nbac_dnd_ha")):
            pieces = park_pieces(parts, regions, admin=admin)
            for region, ha in per_season_union(pieces, ["region"]).items():
                rows.append({"region": region, "year": year, col: ha})
            if admin == NBAC_PARK_ADMIN:
                for (region, park), ha in per_season_union(pieces, ["region", "ADMIN_DIV"]).items():
                    by_park.append({"region": region, "year": year, "park": park, "ha": ha})
    out = (pd.DataFrame(rows).groupby(["region", "year"]).sum(min_count=1).reset_index()
           if rows else pd.DataFrame(columns=["region", "year"]))
    return out, pd.DataFrame(by_park)


def cnfdb_pc_area(regions: gpd.GeoDataFrame) -> pd.DataFrame:
    """CNFDB Parks Canada area per region and season by the main build's own
    rules (read_cnfdb with the 1 km dissolve, wildfires, whole-fire floor,
    clip, season window), as a union per season like burn_ha."""
    from src.fire import clip_to_regions, keep_wildfires, read_cnfdb, whole_fire_floor

    fires, _ = keep_wildfires(read_cnfdb())
    fires = whole_fire_floor(fires)
    pieces = clip_to_regions(fires[fires["fire_id"].str.startswith("PC:")], regions)
    pieces = pieces[pieces["season"].notna()]
    area = per_season_union(pieces, ["region", "season"])
    return pd.DataFrame([{"region": r, "year": int(y), "cnfdb_pc_ha": ha}
                         for (r, y), ha in area.items()])


def measure() -> pd.DataFrame:
    """Write MEASURE_TABLE (region, year, nbac_park_ha, cnfdb_pc_ha,
    nbac_dnd_ha, burn_ha; BC, AB, YT, 1984 to CNFDB_LAST_YEAR) and print the
    figures the register quotes. Fire columns only; no ENSO column is read."""
    regions = load_regions()
    regions = regions[regions["region"].isin(CANADA)].to_crs(CRS_EQUAL_AREA)
    years = range(FIRE_FIRST_YEAR, CNFDB_LAST_YEAR + 1)
    nbac, by_park = nbac_admin_area(years, regions)
    grid = pd.MultiIndex.from_product([CANADA, years], names=["region", "year"]).to_frame(index=False)
    table = pd.read_csv(FIRE_REGION_TABLE, usecols=["region", "year", "burn_ha"])
    m = (grid.merge(nbac, how="left").merge(cnfdb_pc_area(regions), how="left")
         .merge(table, how="left"))
    for col in ("nbac_park_ha", "nbac_dnd_ha", "cnfdb_pc_ha"):
        m[col] = m[col].fillna(0.0)
    MEASURE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    m.round(1).to_csv(MEASURE_TABLE, index=False, lineterminator="\n")
    print(f"wrote {MEASURE_TABLE}: {len(m)} rows")
    print_measure(m, by_park)
    return m


def print_measure(m: pd.DataFrame, by_park: pd.DataFrame) -> None:
    """The register's figures from the measure table (unions per season)."""
    def span(a, b):
        return m["year"].between(a, b)

    print("\nParks Canada share of counted area (CNFDB PC union / burn_ha):")
    for a, b in ((1984, 2017), (2010, 2017), (2021, 2024)):
        g = m[span(a, b)].groupby("region")[["cnfdb_pc_ha", "burn_ha"]].sum()
        print(f"  {a}-{b}: " + ", ".join(f"{r} {g.at[r, 'cnfdb_pc_ha'] / g.at[r, 'burn_ha']:.2%}"
                                          for r in CANADA))
    ab = m[(m["region"] == "AB") & span(1984, 2017)]
    both = ab[(ab["nbac_park_ha"] > 0) & (ab["cnfdb_pc_ha"] > 0)].copy()
    both["ratio"] = both["nbac_park_ha"] / both["cnfdb_pc_ha"]
    print(f"\nAB 1984-2017, NBAC park vs CNFDB PC, both unions: {ab['nbac_park_ha'].sum():,.0f} vs "
          f"{ab['cnfdb_pc_ha'].sum():,.0f} ha (ratio {ab['nbac_park_ha'].sum() / ab['cnfdb_pc_ha'].sum():.3f}); "
          f"both above 0 in {len(both)} seasons, within 5% in {(abs(both['ratio'] - 1) <= 0.05).sum()}, "
          f"within 15% in {(abs(both['ratio'] - 1) <= 0.15).sum()}; ratio "
          f"{both['ratio'].min():.2f} ({both.loc[both['ratio'].idxmin(), 'year']}) to "
          f"{both['ratio'].max():.2f} ({both.loc[both['ratio'].idxmax(), 'year']})")
    big = both[both["cnfdb_pc_ha"] >= 50_000].sort_values("year")
    print("  seasons with CNFDB PC >= 50,000 ha (ratio): "
          + ", ".join(f"{y} {r:.2f}" for y, r in zip(big["year"], big["ratio"])))
    print("\nGap seasons 2016-2021, NBAC park area (share of the season added, log_burn change):")
    gap = m[span(2016, 2021) & (m["nbac_park_ha"] > 0)]
    for _, r in gap.iterrows():
        print(f"  {r['region']} {r['year']}: {r['nbac_park_ha']:,.0f} ha "
              f"({r['nbac_park_ha'] / (r['burn_ha'] + r['nbac_park_ha']):.1%}, "
              f"{np.log1p(r['burn_ha'] + r['nbac_park_ha']) - np.log1p(r['burn_ha']):+.3f}); "
              f"CNFDB PC {r['cnfdb_pc_ha']:,.0f} ha")
    dnd = m[m["nbac_dnd_ha"] > 0]
    print(f"\nDefence lands: {dnd.groupby('region')['nbac_dnd_ha'].sum().round(0).to_dict()} ha in "
          f"{dnd.groupby('region').size().to_dict()} seasons; AB share of counted area "
          f"{dnd.loc[dnd['region'] == 'AB', 'nbac_dnd_ha'].sum() / m.loc[m['region'] == 'AB', 'burn_ha'].sum():.2%}")
    d = dnd[dnd["region"] == "AB"].assign(
        added=lambda x: x["nbac_dnd_ha"] / (x["burn_ha"] + x["nbac_dnd_ha"]),
        log_change=lambda x: np.log1p(x["burn_ha"] + x["nbac_dnd_ha"]) - np.log1p(x["burn_ha"]))
    print(d.sort_values("added", ascending=False)[["year", "nbac_dnd_ha", "burn_ha", "added", "log_change"]]
          .round(3).to_string(index=False))
    if len(by_park):
        parks = by_park.groupby("park")["ha"].sum().sort_values(ascending=False)
        print(f"\nNBAC park area by park, summed over per-season unions, 1984-{CNFDB_LAST_YEAR}: "
              f"total {parks.sum():,.0f} ha; " + ", ".join(f"{k} {v:,.0f}" for k, v in parks.head(6).items())
              + f"; WB share {parks.get('WB', 0) / parks.sum():.1%}")


def main() -> None:
    import sys

    if "--measure" in sys.argv[1:]:
        measure()
        return
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
