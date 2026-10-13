"""Burned area of each region and season, split by fire start month at three
issue dates (the sibling prediction project's request of 2026-10-13; D?a).

One row per region, season and issue date: the 291 region-seasons of the
pinned results/tables/fire_region_year.csv times AFTER_DATE_ISSUE_MONTHS.
Every fire rule is src.fire's own (type filter, cutover, whole-fire floor of
MIN_FIRE_HA, clip, season windows, union per source and sources summed,
area through src.geo.area_ha); only the grouping by start month is new.

  after_ha    union area of the season's counted pieces whose fire started
              in the issue month or later (per source, sources summed). In
              a window that wraps the year (NorCal, SoCal), the months of
              the next year (January Y+1) are after every issue date.
  before_ha   the same for pieces whose fire started before the issue month
  undated_ha  the same for pieces without a start month (CNFDB, D59)
  n_after, n_before, n_undated   pieces in each group
  burn_ha     the season's whole area by the main table's rule

It is the area of fires that started after the date, not the area that
burned after it: no source carries growth by day. The three unions can
overlap one another, so their sum can exceed burn_ha.

Held-back seasons (2026 and later everywhere, 2025 in BC, AB and YT) are
dropped by tested_pieces() before anything is summed, and nothing is printed
but the checks, the row count, the path and the checksum.

fire_events.csv holds no geometry, so the pieces are rebuilt from the pinned
fire downloads. `--data-root` names the checkout whose data/ holds them (a
worktree has none); the downloads are read only and checked against
INPUT_PINS_TABLE first. The table is written once, with its provenance
record, by run_guard.write_result.

Run:  python -m src.fire_after_date [--data-root <checkout>]

The table holds values derived from MTBS (public domain), WFIGS (NIFC; its
disclaimer applies) and CNFDB (Open Government Licence - Canada); they stay
under those terms (LICENSE-CONTENT, DATA_SOURCES.md notices 8-10).
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src import fire, pin_inputs, regions as regions_mod, run_guard
from src.config import (AFTER_DATE_ISSUE_MONTHS, AFTER_DATE_RUN, AFTER_DATE_TABLE, CNFDB_RAW,
                        CRS_EQUAL_AREA, FIRE_FIRST_YEAR, FIRE_LAST_YEAR_BY_REGION,
                        FIRE_REGION_TABLE, FIRE_SEASON_MONTHS, INPUT_PINS_TABLE, MTBS_RAW, REGIONS,
                        RESULTS, ROOT)

GROUPS = ("after", "before", "undated")
COLUMNS = ["region", "year", "issue_date", "after_ha", "before_ha", "undated_ha",
           "n_after", "n_before", "n_undated", "burn_ha"]
TOLERANCE_HA = 1e-6
# pinned downloads the pieces are rebuilt from, and the region polygons
MTBS_ZIP = MTBS_RAW / "mtbs_perimeter_data.zip"
CNFDB_ZIP = CNFDB_RAW / "NFDB_poly.zip"
PINNED_DOWNLOADS = (MTBS_ZIP, fire.WFIGS_FILE, CNFDB_ZIP)


def tested_pieces(pieces: pd.DataFrame,
                  last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> pd.DataFrame:
    """Pieces in a season window from FIRE_FIRST_YEAR to their region's last
    test year: every held-back region-season is dropped here."""
    last = pieces["region"].map(last_year)
    keep = pieces["season"].notna() & (pieces["season"] >= FIRE_FIRST_YEAR) & (pieces["season"] <= last)
    return pieces[keep.fillna(False).astype(bool)]


def start_group(pieces: pd.DataFrame, issue_month: int) -> pd.Series:
    """ "after", "before" or "undated" for each piece at an issue date on
    the first of `issue_month`. After: start month at or past the issue
    month, or, in a window that wraps the year, a month of the next year
    (at or below the window's last month). Undated pieces carry a
    placeholder ignition date (src.fire.cnfdb_dates), so the flag is read
    first."""
    month = pieces["ignition"].dt.month
    first = pieces["region"].map({r: m[0] for r, m in FIRE_SEASON_MONTHS.items()})
    last = pieces["region"].map({r: m[1] for r, m in FIRE_SEASON_MONTHS.items()})
    after = (month >= issue_month) | ((first > last) & (month <= last))
    group = np.where(pieces["undated"].astype(bool), "undated", np.where(after, "after", "before"))
    return pd.Series(group, index=pieces.index)


def season_union(pieces: gpd.GeoDataFrame) -> pd.Series:
    """Union area per (region, season): src.fire.union_areas per source,
    sources summed. Empty for no pieces."""
    if len(pieces) == 0:
        return pd.Series(dtype=float)
    return fire.union_areas(pieces).groupby(["region", "season"])["union_ha"].sum()


def split_table(pieces: gpd.GeoDataFrame,
                issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> pd.DataFrame:
    """The table from clipped fire-region pieces (src.fire.clip_to_regions
    output with geometry). Every region and season to its last test year
    has a row per issue date; a group without pieces has area 0."""
    pieces = tested_pieces(pieces, last_year)
    whole = season_union(pieces)
    rows = []
    for label, issue_month in issue_months.items():
        group = start_group(pieces, issue_month)
        area = {name: season_union(pieces[group == name]) for name in GROUPS}
        count = {name: pieces[group == name].groupby(["region", "season"]).size()
                 for name in GROUPS}
        for region in REGIONS:
            for year in range(FIRE_FIRST_YEAR, last_year[region] + 1):
                key = (region, year)
                rows.append({"region": region, "year": year, "issue_date": label,
                             **{f"{name}_ha": float(area[name].get(key, 0.0)) for name in GROUPS},
                             **{f"n_{name}": int(count[name].get(key, 0)) for name in GROUPS},
                             "burn_ha": float(whole.get(key, 0.0))})
    table = pd.DataFrame(rows)[COLUMNS]
    order = {r: i for i, r in enumerate(REGIONS)}
    return (table.assign(_r=table["region"].map(order), _d=table["issue_date"].map(issue_months))
            .sort_values(["_r", "year", "_d"]).drop(columns=["_r", "_d"]).reset_index(drop=True))


def check_table(table: pd.DataFrame, pinned: pd.DataFrame,
                issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> dict[str, list[str]]:
    """The five checks of the request; for each, the rows that fail, named
    by region, year, issue date and column only (no split value is put in
    a message, since the sibling sets its rules before it sees the table)."""
    def where(mask) -> list[str]:
        return [f"{r} {y} at {d}" for r, y, d in
                table.loc[mask, ["region", "year", "issue_date"]].itertuples(index=False)]

    main = pinned.set_index(["region", "year"])
    keys = pd.MultiIndex.from_frame(table[["region", "year"]])
    known = keys.isin(main.index)
    ref = main.reindex(keys)
    out = {}
    out["1 burn_ha equals the pinned table"] = where(
        ~known | ~((table["burn_ha"] - ref["burn_ha"].to_numpy()).abs() <= TOLERANCE_HA))
    n = table[["n_after", "n_before", "n_undated"]].sum(axis=1)
    out["2 piece counts equal n_fires and n_undated"] = where(
        ~known | (n.to_numpy() != ref["n_fires"].to_numpy())
        | (table["n_undated"].to_numpy() != ref["n_undated"].to_numpy()))
    parts = table[["after_ha", "before_ha", "undated_ha"]].sum(axis=1)
    out["3 the three areas sum to at least burn_ha"] = where(
        ~(parts >= table["burn_ha"] - TOLERANCE_HA))
    opens = {label: [r for r, m in FIRE_SEASON_MONTHS.items() if m[0] == month]
             for label, month in issue_months.items()}
    at_open = pd.Series([r in opens[d] for r, d in zip(table["region"], table["issue_date"])],
                        index=table.index)
    out["4 before_ha is 0 where the window opens in the issue month"] = where(
        at_open & ((table["before_ha"] != 0) | (table["n_before"] != 0)))
    held = (table["year"] > table["region"].map(last_year)) | (table["year"] < FIRE_FIRST_YEAR)
    problems = where(held | table.duplicated(["region", "year", "issue_date"])
                     | ~table["issue_date"].isin(list(issue_months)))
    expected = len(issue_months) * sum(last_year[r] - FIRE_FIRST_YEAR + 1 for r in REGIONS)
    if len(table) != expected or len(pinned) * len(issue_months) != expected:
        problems.append(f"{len(table)} rows, expected {expected}")
    out["5 no held-back region-season; one row per region, season and issue date"] = problems
    return out


def reroot(path: Path, data_root: Path) -> Path:
    """`path` (under ROOT) as the same relative path under another checkout."""
    return Path(data_root) / Path(path).relative_to(ROOT)


def verify_downloads(data_root: Path, pins: Path = INPUT_PINS_TABLE) -> list[str]:
    """Check the three fire downloads under `data_root` against the pins
    table; returns their relative paths. Raises on any difference."""
    table = pd.read_csv(pins).set_index("path")
    names = []
    for path in PINNED_DOWNLOADS:
        rel = Path(path).relative_to(ROOT).as_posix()
        if pin_inputs.sha256(reroot(path, data_root)) != table.at[rel, "sha256"]:
            raise pin_inputs.PinnedInputError(f"{rel} under {data_root} differs from its pin.")
        names.append(rel)
    return names


def build_pieces(data_root: Path = ROOT) -> gpd.GeoDataFrame:
    """Steps 1 to 6 of src.fire.main on the downloads under `data_root`,
    with the held-back seasons dropped. Nothing is printed or written."""
    polygons = gpd.read_file(reroot(regions_mod.OUT, data_root))
    polygons = polygons.set_index("region").loc[list(REGIONS)].reset_index()
    prep = fire.Prepare()
    mtbs = "/vsizip/" + reroot(MTBS_ZIP, data_root).as_posix() + "/mtbs_perims_DD.shp"
    fires = [prep(fire.read_mtbs(mtbs)),
             fire.read_wfigs(reroot(fire.WFIGS_FILE, data_root), prepare=prep),
             prep(fire.read_cnfdb(reroot(CNFDB_RAW, data_root)))]
    floored = gpd.GeoDataFrame(pd.concat(fires, ignore_index=True), geometry="geometry",
                               crs=CRS_EQUAL_AREA)
    pieces = fire.clip_to_regions(fire.splice_us(floored), polygons)
    return tested_pieces(pieces)


def main(data_root: Path = ROOT) -> None:
    """Build, check, and write the table once with its provenance record.
    Any failed check stops the run before a file is written."""
    target = RESULTS / "tables" / AFTER_DATE_RUN / AFTER_DATE_TABLE
    if target.exists():
        raise FileExistsError(f"{target} exists; it is written once (run_guard.write_result).")
    inputs = verify_downloads(data_root)
    regions_file = reroot(regions_mod.OUT, data_root)
    inputs.append(f"{regions_mod.OUT.relative_to(ROOT).as_posix()} "
                  f"sha256 {pin_inputs.sha256(regions_file)}")
    pinned = pin_inputs.load_input(FIRE_REGION_TABLE.name)
    inputs.append(f"results/tables/{FIRE_REGION_TABLE.name}")
    table = split_table(build_pieces(data_root))
    checks = check_table(table, pinned)
    for name, problems in checks.items():
        print(f"check {name}: {'pass' if not problems else 'FAIL'}")
        for line in problems[:20]:
            print(f"    {line}")
    if any(checks.values()):
        raise SystemExit("checks failed; no table written")
    path = run_guard.write_result(table, AFTER_DATE_TABLE, AFTER_DATE_RUN, inputs=inputs)
    print(f"wrote {path}: {len(table)} rows, sha256 {pin_inputs.sha256(path)}")


if __name__ == "__main__":
    import sys

    _args = sys.argv[1:]
    main(Path(_args[_args.index("--data-root") + 1]) if "--data-root" in _args else ROOT)
