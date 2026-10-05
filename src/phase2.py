"""Phase 2 region x year table: whiplash, April 1 SWE and the ENSO phase.

Joins the outputs of `python -m src.whiplash` and `python -m src.snow`
(both in data/processed/), keeping every winter whatever its phase. Year Y is
winter (Y-1)-Y: DJF SPEI and April 1 SWE of that winter, JJA SPEI and the
fire season of year Y.

Run:  python -m src.phase2   (writes data/processed/whiplash_swe_region_year.csv)
"""
from __future__ import annotations

import pandas as pd

from src.config import DATA_PROCESSED, REGIONS

WHIPLASH = DATA_PROCESSED / "whiplash_region_year.csv"
SWE = DATA_PROCESSED / "swe_april1_region_year.csv"
OUT = DATA_PROCESSED / "whiplash_swe_region_year.csv"
ENSO_COLS = ["winter", "enso_index", "enso_djf", "phase", "strong"]


def build_table(whiplash: pd.DataFrame, swe: pd.DataFrame) -> pd.DataFrame:
    """Outer join on region and year; the ENSO columns must agree."""
    table = whiplash.merge(swe, on=["region", "year"], how="outer",
                           suffixes=("", "_swe"), validate="one_to_one")
    for col in ENSO_COLS:
        other = table.pop(f"{col}_swe")
        both = table[col].notna() & other.notna()
        if (table.loc[both, col] != other[both]).any():
            raise ValueError(f"ENSO column {col} differs between the whiplash and SWE tables.")
        table[col] = table[col].fillna(other)
    table["region"] = pd.Categorical(table["region"], categories=list(REGIONS), ordered=True)
    table = table.sort_values(["region", "year"]).reset_index(drop=True)
    table["region"] = table["region"].astype(str)
    lead = ["region", "year", "winter", "whiplash", "spei3_djf", "spei3_jja", "swe_apr1_mm"]
    return table[lead + [c for c in table.columns if c not in lead]]


def main() -> None:
    table = build_table(pd.read_csv(WHIPLASH), pd.read_csv(SWE))
    table.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(table)} rows, {table['region'].nunique()} regions, "
          f"years {table['year'].min()}-{table['year'].max()}")


if __name__ == "__main__":
    main()
