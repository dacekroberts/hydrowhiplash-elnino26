"""MTBS against WFIGS on the fires both hold, for the methods page.

The US fire record is MTBS through 2023 and WFIGS from 2024
(MTBS_WFIGS_CUTOVER). This measures how the two products compare on the
same fires: for each calendar year in SOURCE_PAIR_YEARS, every WFIGS
wildfire of at least MIN_FIRE_HA (whole fire) that touches a US study
region is matched to the MTBS wildfires of at least MIN_FIRE_HA ignited in
the same calendar year whose outlines overlap it. A pair is one-to-one when
the WFIGS fire overlaps exactly one MTBS fire and that MTBS fire overlaps
no other WFIGS fire; only those pairs are compared, so a complex mapped as
one outline in one product and several in the other is left out. The ratio
is the WFIGS whole-fire area over the MTBS whole-fire area, both measured in
the equal-area CRS (src.geo.area_ha).

Descriptive; no ENSO column is read and no test uses it. Reads the pinned
MTBS and WFIGS files (fire polygons): ask the owner before running.

Run from the repo root:  python scripts/source_pairs.py
Writes data/processed/mtbs_wfigs_pairs.csv (one row per one-to-one pair,
not committed) and prints the yearly summary; scripts/methods_numbers.py
puts the summary into results/tables/methods_numbers.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import (CRS_EQUAL_AREA, DATA_PROCESSED, FIRE_COUNTRY,  # noqa: E402
                        SOURCE_PAIR_YEARS)

OUT = DATA_PROCESSED / "mtbs_wfigs_pairs.csv"
M2_PER_HA = 10_000


def one_to_one_pairs(wfigs: gpd.GeoDataFrame, mtbs: gpd.GeoDataFrame) -> pd.DataFrame:
    """One row per one-to-one pair among fires of one year. Both frames are
    in the equal-area CRS and carry `fire_id`, `name` and `fire_ha`. Two
    outlines overlap when their intersection has area; touching edges do
    not count."""
    cols = ["wfigs_id", "wfigs_name", "wfigs_ha", "mtbs_id", "mtbs_name", "mtbs_ha",
            "overlap_ha", "ratio"]
    if wfigs.empty or mtbs.empty:
        return pd.DataFrame(columns=cols)
    w = wfigs.reset_index(drop=True)
    m = mtbs.reset_index(drop=True)
    hits = gpd.sjoin(w[["geometry"]], m[["geometry"]], predicate="intersects")
    hits = hits.rename(columns={"index_right": "m"}).rename_axis("w").reset_index()
    overlap = w.geometry.iloc[hits["w"]].reset_index(drop=True).intersection(
        m.geometry.iloc[hits["m"]].reset_index(drop=True))
    hits["overlap_ha"] = overlap.area.to_numpy() / M2_PER_HA
    hits = hits[hits["overlap_ha"] > 0]
    single = (hits.groupby("w")["m"].transform("size") == 1) & \
             (hits.groupby("m")["w"].transform("size") == 1)
    hits = hits[single]
    out = pd.DataFrame({
        "wfigs_id": w["fire_id"].iloc[hits["w"]].to_numpy(),
        "wfigs_name": w["name"].iloc[hits["w"]].to_numpy(),
        "wfigs_ha": w["fire_ha"].iloc[hits["w"]].to_numpy(),
        "mtbs_id": m["fire_id"].iloc[hits["m"]].to_numpy(),
        "mtbs_name": m["name"].iloc[hits["m"]].to_numpy(),
        "mtbs_ha": m["fire_ha"].iloc[hits["m"]].to_numpy(),
        "overlap_ha": hits["overlap_ha"].to_numpy(),
    })
    out["ratio"] = out["wfigs_ha"] / out["mtbs_ha"]
    return out[cols]


def summarise(pairs: pd.DataFrame) -> pd.DataFrame:
    """Per year: pairs, median ratio, and total WFIGS area over total MTBS."""
    rows = []
    for year, group in pairs.groupby("year"):
        rows.append({"year": int(year), "pairs": len(group),
                     "median_ratio": group["ratio"].median(),
                     "total_ratio": group["wfigs_ha"].sum() / group["mtbs_ha"].sum()})
    return pd.DataFrame(rows, columns=["year", "pairs", "median_ratio", "total_ratio"])


def main() -> None:
    from src import pin_inputs
    from src.fire import Prepare, read_mtbs, read_wfigs
    from src.regions import load_regions

    pin_inputs.guard_write([OUT])  # not a pinned path; stops a mistaken target
    first, last = SOURCE_PAIR_YEARS
    regions = load_regions()
    us = regions[regions["region"].map(FIRE_COUNTRY) == "US"].to_crs(CRS_EQUAL_AREA)
    study = us.geometry.union_all()
    prep = Prepare()
    mtbs = prep(read_mtbs())
    wfigs = read_wfigs(first_year=first, prepare=prep)
    wfigs = wfigs[wfigs.geometry.intersects(study)]
    parts = []
    for year in range(first, last + 1):
        w = wfigs[wfigs["ignition"].dt.year == year]
        m = mtbs[mtbs["ignition"].dt.year == year]
        pairs = one_to_one_pairs(w, m)
        pairs.insert(0, "year", year)
        parts.append(pairs)
        print(f"{year}: {len(w)} WFIGS fires in the US regions, {len(m)} MTBS fires in the "
              f"read box, {len(pairs)} one-to-one pairs", flush=True)
    table = pd.concat(parts, ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.round(4).to_csv(OUT, index=False, lineterminator="\n")
    print(f"wrote {OUT}: {len(table)} pairs")
    print(summarise(table).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
