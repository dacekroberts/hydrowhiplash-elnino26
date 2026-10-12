"""Interior Alaska check (descriptive; owner, 2026-10-11; climate only).

Does Alaska's climate signal change when the region is cut to the Interior,
where most of its fire burns? The plan keeps Alaska as one region (frozen;
DECISIONS 2026-10-05 "Alaska stays one region") and states the limitation
that its climate means include wet coasts. This measures that limitation:
the climate controls (temp_jja, temp_mam, precip_djf_mm, precip_octmar_mm;
src.climate_vars.climate_regional) for whole AK and for the Interior (NOAA
NCEI climate divisions AK_INTERIOR_DIVISIONS, clipped to the AK polygon),
their correlation, and the El Nino minus other-winters difference of each
in SD units of its own series. No fire table is read; no registered test
reads the output.

Run from the repo root:  python scripts/interior_alaska_check.py
Writes data/processed/interior_alaska_check.csv (not committed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.climate_vars import climate_regional  # noqa: E402
from src.config import (AK_DIVISIONS_FILES, AK_DIVISIONS_RAW, AK_INTERIOR_DIVISIONS,  # noqa: E402
                        CRS_EQUAL_AREA, DATA_PROCESSED)
from src.era5 import assign_domains, join_enso, open_domains, region_masks  # noqa: E402
from src.geo import area_ha  # noqa: E402
from src.regions import load_regions  # noqa: E402

OUT = DATA_PROCESSED / "interior_alaska_check.csv"
VARIABLES = ["temp_jja", "temp_mam", "precip_djf_mm", "precip_octmar_mm"]
INTERIOR = "AK_interior"


def interior_polygon(alaska: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """The Interior divisions, dissolved and clipped to the AK study polygon,
    in the regions' CRS, as a one-row frame with region = INTERIOR."""
    div = gpd.read_file(AK_DIVISIONS_RAW / AK_DIVISIONS_FILES[0])
    div = div[div["FEATURE"].astype(int).isin(AK_INTERIOR_DIVISIONS)]
    if len(div) != len(AK_INTERIOR_DIVISIONS):
        raise ValueError(f"Expected divisions {AK_INTERIOR_DIVISIONS}, found {sorted(div['FEATURE'])}.")
    print("Interior divisions:", ", ".join(sorted(div["Name"])))
    geom = div.to_crs(alaska.crs).geometry.union_all().intersection(alaska.geometry.iloc[0])
    return gpd.GeoDataFrame({"region": [INTERIOR]}, geometry=[geom], crs=alaska.crs)


def main() -> None:
    regions = load_regions()
    alaska = regions[regions["region"] == "AK"].reset_index(drop=True)
    interior = interior_polygon(alaska)
    share = (area_ha(interior.to_crs(CRS_EQUAL_AREA)).iloc[0]
             / area_ha(alaska.to_crs(CRS_EQUAL_AREA)).iloc[0])
    print(f"Interior share of the AK polygon's area: {share:.1%}")
    domain = assign_domains(alaska)["AK"]
    ds = open_domains([domain])[domain]
    parts = []
    for frame in (alaska, interior):  # one mask each: the two polygons overlap
        masks = region_masks(frame, ds)
        print(f"{frame['region'].iloc[0]}: {int(masks.sum())} cells")
        parts.append(climate_regional(ds, masks).compute().to_dataframe().reset_index())
    table = pd.concat(parts)
    table["year"] = table["year"].astype(int)
    table = join_enso(table, pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False, lineterminator="\n")
    print(f"wrote {OUT}: {len(table)} rows, years {table['year'].min()}-{table['year'].max()}")

    wide = table.pivot(index="year", columns="region", values=VARIABLES)
    phase = table.drop_duplicates("year").set_index("year")
    nino, strong = phase["phase"] == "el_nino", phase["strong"].astype(bool)
    rows = []
    for v in VARIABLES:
        pair = wide[v].dropna()
        row = {"variable": v, "n_years": len(pair), "r": pair["AK"].corr(pair[INTERIOR]),
               "mean_AK": pair["AK"].mean(), "mean_interior": pair[INTERIOR].mean()}
        for name in ("AK", INTERIOR):
            z = (pair[name] - pair[name].mean()) / pair[name].std(ddof=1)
            tag = "AK" if name == "AK" else "interior"
            row[f"nino_minus_rest_sd_{tag}"] = z[nino.reindex(z.index)].mean() - z[~nino.reindex(z.index)].mean()
            row[f"strong_minus_rest_sd_{tag}"] = (z[strong.reindex(z.index)].mean()
                                                 - z[~strong.reindex(z.index)].mean())
        rows.append(row)
    print(f"El Nino winters {int(nino.sum())}, strong {int(strong.sum())}, of {len(phase)}")
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
