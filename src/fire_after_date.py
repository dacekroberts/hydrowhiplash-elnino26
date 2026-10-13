"""Burned area of each region and season, split by fire start month at three
issue dates (the sibling prediction project's request of 2026-10-13; D103).

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
refused by default: split_table() builds only the region-seasons it is given,
drops every other piece before anything is summed (select_pieces), and
raises HeldBackSeasonError for a season after its region's last test year.
Nothing is printed but the checks, the row count, the path and the checksum.

Scoring-day path (the sibling's request, "The scoring-day path"; fixed
2026-10-13, run later). The split of a held-back season is built by the same
split_table(), unchanged: the scored region-seasons are passed as `seasons`
and named again in `scoring_day_seasons`, an argument not used before that
season's scoring day. The pieces come from that day's fire rebuild (the one
that makes the outcome numbers), check_table() runs against the outcome
table, and the rows are written beside the outcome numbers and handed over in
the same approved read. That path is tested on made-up pieces only
(tests/test_fire_after_date.py). The commit frozen for scoring is in
DECISIONS.md 2026-10-13; a later change to this module is a logged decision,
told to the sibling before the next scoring day.

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


class HeldBackSeasonError(RuntimeError):
    """A held-back region-season was asked for without being named in
    `scoring_day_seasons`, or named there without being asked for."""


def development_seasons(last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> list[tuple[str, int]]:
    """Every (region, season) from FIRE_FIRST_YEAR to the region's last test
    year, in REGIONS order: the seasons of the pinned fire table."""
    return [(region, year) for region in REGIONS
            for year in range(FIRE_FIRST_YEAR, last_year[region] + 1)]


def held_back(seasons, last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> list[tuple[str, int]]:
    """The (region, season) pairs after their region's last test year."""
    return [(r, int(y)) for r, y in seasons if int(y) > last_year[r]]


def guard_seasons(seasons, scoring_day_seasons=(),
                  last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> list[tuple[str, int]]:
    """Return `seasons` as a list, or raise. A season before FIRE_FIRST_YEAR
    or listed twice is refused. A held-back season is refused unless
    `scoring_day_seasons` names it, and `scoring_day_seasons` must name
    exactly the held-back seasons asked for, so a scoring-day build cannot
    take in a season beyond the ones being scored."""
    seasons = [(r, int(y)) for r, y in seasons]
    if len(set(seasons)) != len(seasons):
        raise ValueError("a region-season is listed twice")
    early = [s for s in seasons if s[1] < FIRE_FIRST_YEAR]
    if early:
        raise ValueError(f"before the fire record starts ({FIRE_FIRST_YEAR}): {early}")
    asked = set(held_back(seasons, last_year))
    named = {(r, int(y)) for r, y in scoring_day_seasons}
    if asked != named:
        raise HeldBackSeasonError(
            f"held-back region-seasons asked for: {sorted(asked)}; named in "
            f"scoring_day_seasons: {sorted(named)}. A held-back season is built only on its "
            "scoring day, named in both (DECISIONS.md 2026-10-13).")
    return seasons


def select_pieces(pieces: pd.DataFrame, seasons) -> pd.DataFrame:
    """The pieces of the given (region, season) pairs; every other piece,
    so every season not asked for, is dropped here."""
    wanted = pd.MultiIndex.from_tuples(list(seasons))
    in_season = pieces["season"].notna().to_numpy()
    keys = pd.MultiIndex.from_arrays([pieces["region"].to_numpy(),
                                      pieces["season"].fillna(-1).astype(int).to_numpy()])
    return pieces[in_season & keys.isin(wanted)]


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


def split_table(pieces: gpd.GeoDataFrame, seasons=None,
                issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION, *,
                scoring_day_seasons=()) -> pd.DataFrame:
    """The table from clipped fire-region pieces (src.fire.clip_to_regions
    output with geometry), for the (region, season) pairs in `seasons`
    (default development_seasons), in that order. Each has a row per issue
    date; a group without pieces has area 0. A held-back season raises
    unless it is also named in `scoring_day_seasons` (guard_seasons); that
    argument is not used before the season's scoring day."""
    seasons = guard_seasons(development_seasons(last_year) if seasons is None else seasons,
                            scoring_day_seasons, last_year)
    pieces = select_pieces(pieces, seasons)
    whole = season_union(pieces)
    by_date = {}
    for label, issue_month in issue_months.items():
        group = start_group(pieces, issue_month)
        area = {name: season_union(pieces[group == name]) for name in GROUPS}
        count = {name: pieces[group == name].groupby(["region", "season"]).size()
                 for name in GROUPS}
        by_date[label] = (area, count)
    rows = []
    for key in seasons:
        for label, (area, count) in by_date.items():
            rows.append({"region": key[0], "year": key[1], "issue_date": label,
                         **{f"{name}_ha": float(area[name].get(key, 0.0)) for name in GROUPS},
                         **{f"n_{name}": int(count[name].get(key, 0)) for name in GROUPS},
                         "burn_ha": float(whole.get(key, 0.0))})
    return pd.DataFrame(rows)[COLUMNS]


def check_table(table: pd.DataFrame, pinned: pd.DataFrame, seasons=None,
                issue_months: dict[str, int] = AFTER_DATE_ISSUE_MONTHS,
                last_year: dict[str, int] = FIRE_LAST_YEAR_BY_REGION) -> dict[str, list[str]]:
    """The five checks of the request; for each, the rows that fail, named
    by region, year and issue date only (no split value is put in a
    message, since the sibling sets its rules before it sees the table).
    `pinned` is the season table the rows must agree with (region, year,
    burn_ha, n_fires, n_undated): the pinned fire table, or on a scoring
    day that day's outcome table. `seasons` are the (region, season) pairs
    the table was built for (default development_seasons); check 5 fails
    for any other row, so for a held-back row in the development table."""
    seasons = (development_seasons(last_year) if seasons is None
               else [(r, int(y)) for r, y in seasons])

    def where(mask) -> list[str]:
        return [f"{r} {y} at {d}" for r, y, d in
                table.loc[np.asarray(mask, dtype=bool),
                          ["region", "year", "issue_date"]].itertuples(index=False)]

    main = pinned.set_index(["region", "year"])
    keys = pd.MultiIndex.from_arrays([table["region"].to_numpy(), table["year"].to_numpy()])
    known = keys.isin(main.index)
    ref = main.reindex(keys)
    out = {}
    out["1 burn_ha equals the season table"] = where(
        ~known | ~(np.abs(table["burn_ha"].to_numpy() - ref["burn_ha"].to_numpy()) <= TOLERANCE_HA))
    n = table[["n_after", "n_before", "n_undated"]].sum(axis=1).to_numpy()
    out["2 piece counts equal n_fires and n_undated"] = where(
        ~known | (n != ref["n_fires"].to_numpy())
        | (table["n_undated"].to_numpy() != ref["n_undated"].to_numpy()))
    parts = table[["after_ha", "before_ha", "undated_ha"]].sum(axis=1)
    out["3 the three areas sum to at least burn_ha"] = where(
        ~(parts >= table["burn_ha"] - TOLERANCE_HA))
    opens = {label: [r for r, m in FIRE_SEASON_MONTHS.items() if m[0] == month]
             for label, month in issue_months.items()}
    at_open = np.array([r in opens.get(d, ()) for r, d in zip(table["region"], table["issue_date"])],
                       dtype=bool)
    out["4 before_ha is 0 where the window opens in the issue month"] = where(
        at_open & ((table["before_ha"] != 0) | (table["n_before"] != 0)).to_numpy())
    unasked = ~keys.isin(pd.MultiIndex.from_tuples(seasons))
    problems = where(unasked | table.duplicated(["region", "year", "issue_date"]).to_numpy()
                     | ~table["issue_date"].isin(list(issue_months)).to_numpy())
    expected = len(issue_months) * len(seasons)
    if len(table) != expected:
        problems.append(f"{len(table)} rows, expected {expected}")
    out["5 only the region-seasons asked for; one row per region, season and issue date"] = problems
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
    """Steps 1 to 6 of src.fire.main on the pinned downloads under
    `data_root`, cut to development_seasons, so no piece of a held-back
    season is returned. Nothing is printed or written."""
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
    return select_pieces(pieces, development_seasons())


def main(data_root: Path = ROOT) -> None:
    """Build the development table (development_seasons, no held-back
    season), check it, and write it once with its provenance record. Any
    failed check stops the run before a file is written."""
    target = RESULTS / "tables" / AFTER_DATE_RUN / AFTER_DATE_TABLE
    if target.exists():
        raise FileExistsError(f"{target} exists; it is written once (run_guard.write_result).")
    inputs = verify_downloads(data_root)
    regions_file = reroot(regions_mod.OUT, data_root)
    inputs.append(f"{regions_mod.OUT.relative_to(ROOT).as_posix()} "
                  f"sha256 {pin_inputs.sha256(regions_file)}")
    pinned = pin_inputs.load_input(FIRE_REGION_TABLE.name)
    inputs.append(f"results/tables/{FIRE_REGION_TABLE.name}")
    seasons = development_seasons()
    if held_back(seasons) or len(seasons) != len(pinned):
        raise HeldBackSeasonError("the development table is the pinned table's seasons only")
    table = split_table(build_pieces(data_root), seasons)
    checks = check_table(table, pinned, seasons)
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
