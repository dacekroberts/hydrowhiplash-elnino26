"""NBAC fire area with no CNFDB polygon under it, BC, AB and YT (fire only).

For the deferred NBAC re-run decision (audit 2026-10-08 round 4 F1; to be
decided before the first hypothesis test): for each NBAC fire at or above
MIN_FIRE_HA (parts dissolved by GID, prescribed parts dropped), its parts
clipped to the regions, the area not covered by any CNFDB polygon of the
same YEAR (any agency, any size, prescribed included), summed per region,
year, ADMIN_NAME and ADMIN_DIV. Shows whether anything beyond the national
parks (D69) and defence lands (round 4 M2) is missing from CNFDB. NBAC has
no ignition date, so a fire counts for its YEAR. No ENSO column is read.

Run from the repo root:  python scripts/nbac_coverage.py   (about 20 minutes)
Writes data/processed/nbac_coverage.csv (not committed) and prints totals.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import (CNFDB_LAST_YEAR, CNFDB_RAW, CRS_EQUAL_AREA, DATA_PROCESSED,  # noqa: E402
                        FIRE_FIRST_YEAR, MIN_FIRE_HA)
from src.fire import CNFDB_SHPS  # noqa: E402
from src.geo import area_ha  # noqa: E402
from src.parks_gap import CANADA, read_nbac_year  # noqa: E402
from src.regions import load_regions  # noqa: E402

OUT = DATA_PROCESSED / "nbac_coverage.csv"
CNFDB_ZIP = "/vsizip/" + (CNFDB_RAW / "NFDB_poly.zip").as_posix() + "/"


def cnfdb_year(year: int) -> gpd.GeoDataFrame:
    """Every CNFDB polygon of one YEAR, in CRS_EQUAL_AREA, geometry repaired.
    The filtered field must be among `columns`: pyogrio returns no rows,
    silently, when it is not (found 2026-10-08; every year here has rows)."""
    raw = pd.concat([pyogrio.read_dataframe(CNFDB_ZIP + shp, columns=["SRC_AGENCY", "YEAR"],
                                            where=f"YEAR = {year}", force_2d=True)
                     for shp in CNFDB_SHPS], ignore_index=True)
    if raw.empty:
        raise ValueError(f"No CNFDB polygon read for {year}: check the where filter.")
    raw = gpd.GeoDataFrame(raw, geometry="geometry").to_crs(CRS_EQUAL_AREA)
    return raw.set_geometry(raw.geometry.make_valid())


def coverage_year(year: int, regions: gpd.GeoDataFrame) -> pd.DataFrame:
    """Per region and NBAC admin label: NBAC area and the part of it no
    CNFDB polygon of the same year covers (ha)."""
    parts = read_nbac_year(year)
    parts = parts[parts["fire_ha"] >= MIN_FIRE_HA]
    pieces = gpd.overlay(parts, regions[["region", "geometry"]], how="intersection",
                         keep_geom_type=True)
    if pieces.empty:
        return pd.DataFrame()
    pieces["admin_div"] = pieces["ADMIN_DIV"].fillna("")
    cn = cnfdb_year(year)
    cover = cn.geometry.union_all() if len(cn) else None
    pieces["nbac_ha"] = area_ha(pieces)
    left = pieces.geometry if cover is None else pieces.geometry.difference(cover)
    pieces["uncovered_ha"] = area_ha(gpd.GeoDataFrame(geometry=left, crs=CRS_EQUAL_AREA))
    out = (pieces.groupby(["region", "ADMIN_NAME", "admin_div"])[["nbac_ha", "uncovered_ha"]]
           .sum().reset_index())
    return out.assign(year=year)


def main() -> None:
    regions = load_regions()
    regions = regions[regions["region"].isin(CANADA)].to_crs(CRS_EQUAL_AREA)
    table = pd.concat([coverage_year(y, regions)
                       for y in range(FIRE_FIRST_YEAR, CNFDB_LAST_YEAR + 1)], ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.round(1).to_csv(OUT, index=False, lineterminator="\n")
    print(f"wrote {OUT}: {len(table)} rows")
    by = table.groupby(["region", "ADMIN_NAME", "admin_div"])[["nbac_ha", "uncovered_ha"]].sum()
    by["uncovered_share"] = by["uncovered_ha"] / by["nbac_ha"]
    print("\nby region and NBAC admin label, 1984-2024 (ha):")
    print(by[by["nbac_ha"] > 0].round(3).to_string())
    reg = table.groupby("region")[["nbac_ha", "uncovered_ha"]].sum()
    print("\nby region:", (reg["uncovered_ha"] / reg["nbac_ha"]).round(3).to_dict())
    season = table.groupby(["region", "year"])[["nbac_ha", "uncovered_ha"]].sum()
    season["share"] = season["uncovered_ha"] / season["nbac_ha"]
    print("\nseasons where more than 20% of NBAC area has no CNFDB polygon under it:")
    print(season[season["share"] > 0.2].round(3).to_string())


if __name__ == "__main__":
    main()
