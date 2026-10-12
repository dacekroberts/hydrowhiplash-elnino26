"""Phase 2 region x year table: whiplash, April 1 SWE and the ENSO phase.

Joins the outputs of `python -m src.whiplash` and `python -m src.snow`
(both in data/processed/), keeping every winter whatever its phase. Year Y is
winter (Y-1)-Y: DJF SPEI and April 1 SWE of that winter, JJA SPEI and the
fire season of year Y.

Run:  python -m src.phase2   (writes data/processed/whiplash_swe_region_year.csv
                               and the committed copy in results/tables/)

The committed copy holds values derived from ERA5-Land (CC-BY 4.0) and the
ENSO index (public domain); they stay under those terms (LICENSE-CONTENT,
DATA_SOURCES.md).
"""
from __future__ import annotations

import pandas as pd

from src.config import DATA_PROCESSED, REGIONS, RESULTS

WHIPLASH = DATA_PROCESSED / "whiplash_region_year.csv"
SWE = DATA_PROCESSED / "swe_april1_region_year.csv"
OUT = DATA_PROCESSED / "whiplash_swe_region_year.csv"
COMMITTED = RESULTS / "tables" / OUT.name
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


def write_tables(table: pd.DataFrame, rebuild: bool = False, ctx=None) -> None:
    """Write the table to data/processed/ and its committed copy to
    results/tables/. The committed copy is a pinned input: refused without
    `rebuild`, whoever calls (a notebook cell included; cold check
    2026-10-11 M1)."""
    from src import later, pin_inputs

    ctx = ctx or later.paths(None)
    if not ctx.stamp:  # a stamped rebuild writes beside the pinned copy (D88)
        pin_inputs.guard_write([COMMITTED], rebuild)
    for path in (ctx.processed(OUT), ctx.table(COMMITTED)):
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(table)} rows, {table['region'].nunique()} regions, "
              f"years {table['year'].min()}-{table['year'].max()}")


def main(rebuild: bool = False, stamp: str | None = None) -> None:
    from src import later, pin_inputs

    ctx = later.paths(stamp)
    # refused before any read, as in the other builders; write_tables guards
    # again for callers that skip main
    if not stamp:
        pin_inputs.guard_write([COMMITTED], rebuild)
    write_tables(build_table(pd.read_csv(ctx.processed(WHIPLASH)),
                             pd.read_csv(ctx.processed(SWE))), rebuild, ctx)
    ctx.close("phase2")


if __name__ == "__main__":
    import sys

    from src import later as _later

    _argv = sys.argv[1:]
    _stamp = _later.take_stamp(_argv)
    main(rebuild="--rebuild" in _argv, stamp=_stamp)
