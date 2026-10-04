"""Build the study-region polygons from Natural Earth boundaries.

Regions (definitions in src/config.py):
  PNW     Washington + Oregon + Idaho
  BC      British Columbia
  AB      Alberta
  NorCal  California north of CA_SPLIT_LAT
  SoCal   California south of CA_SPLIT_LAT

Writes data/processed/regions.geojson in CRS_GEOGRAPHIC, plus each region's
area in hectares, measured in CRS_EQUAL_AREA.

Run:  python -m src.regions
"""
import geopandas as gpd
from shapely.geometry import box

from src.config import (CA_SPLIT_LAT, CRS_GEOGRAPHIC, DATA_PROCESSED,
                        NATURAL_EARTH_ADMIN1_URL, PNW_STATES, REGIONS)
from src.geo import area_ha

OUT = DATA_PROCESSED / "regions.geojson"


def main() -> None:
    admin1 = gpd.read_file(NATURAL_EARTH_ADMIN1_URL)
    # Global admin-1 names repeat across countries; keep US and Canada only so
    # each name is unique and .loc returns one geometry.
    admin1 = admin1[admin1["adm0_a3"].isin(["USA", "CAN"])]
    by_name = admin1.set_index("name")
    if not by_name.index.is_unique:
        raise SystemExit("Duplicate admin-1 names in US/Canada subset; check the Natural Earth file.")

    ca = by_name.loc["California", "geometry"]
    geometry = {
        "PNW": by_name.loc[PNW_STATES].union_all(),
        "BC": by_name.loc["British Columbia", "geometry"],
        "AB": by_name.loc["Alberta", "geometry"],
        "NorCal": ca.intersection(box(-130, CA_SPLIT_LAT, -110, 45)),
        "SoCal": ca.intersection(box(-130, 30, -110, CA_SPLIT_LAT)),
    }

    regions = gpd.GeoDataFrame(
        {"region": list(REGIONS), "role": list(REGIONS.values())},
        geometry=[geometry[name] for name in REGIONS],
        crs=CRS_GEOGRAPHIC,
    )
    regions["area_ha"] = area_ha(regions).round(0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    regions.to_file(OUT, driver="GeoJSON")
    print(f"wrote {OUT}")
    print(regions[["region", "role", "area_ha"]].to_string(index=False))


if __name__ == "__main__":
    main()
