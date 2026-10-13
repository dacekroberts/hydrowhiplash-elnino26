"""Tests for src/fire_after_date.py on synthetic fires: the start-month
groups (wrapped windows, undated pieces), held-back seasons dropped and
refused, the scoring-day path (made-up pieces only, never a real held-back
season), the split table's unions, and each of the request's five checks."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from src import fire, fire_after_date as fad
from src.config import AFTER_DATE_ISSUE_MONTHS, CRS_EQUAL_AREA, FIRE_FIRST_YEAR, REGIONS

KM = 1_000
SIDE = (1_000 * 10_000) ** 0.5  # side of a 1,000 ha square, m
LAST = {r: 2025 if r in ("PNW", "AK", "NorCal", "SoCal") else 2024 for r in REGIONS}


@pytest.fixture
def regions():
    # PNW west of x=0, NorCal east, BC to the north (as in tests/test_fire.py).
    return gpd.GeoDataFrame(
        {"region": ["PNW", "NorCal", "BC"]},
        geometry=[box(-100 * KM, 0, 0, 100 * KM), box(0, 0, 100 * KM, 100 * KM),
                  box(-100 * KM, 100 * KM, 100 * KM, 200 * KM)],
        crs=CRS_EQUAL_AREA)


def square(x0, y0, shift=0.0):
    return box(x0 + shift, y0, x0 + shift + SIDE, y0 + SIDE)


def pieces_for(rows, regions):
    df = pd.DataFrame(rows)
    df["ignition"] = pd.to_datetime(df["ignition"])
    for col, default in (("month_known", True), ("date_known", True), ("name", "x"),
                         ("fire_type", "WF")):
        if col not in df:
            df[col] = default
    fires = gpd.GeoDataFrame(df, geometry="geometry", crs=CRS_EQUAL_AREA)
    return fire.clip_to_regions(fire.whole_fire_floor(fires), regions)


def bc_rows():
    # BC 2020: May and July fires overlapping by half, an August fire apart,
    # and an undated fire lying on the August one.
    at = (-50 * KM, 150 * KM)
    return [
        {"source": "CNFDB", "fire_id": "may", "ignition": "2020-05-10", "cnfdb_year": 2020,
         "geometry": square(*at)},
        {"source": "CNFDB", "fire_id": "jul", "ignition": "2020-07-10", "cnfdb_year": 2020,
         "geometry": square(*at, shift=SIDE / 2)},
        {"source": "CNFDB", "fire_id": "aug", "ignition": "2020-08-10", "cnfdb_year": 2020,
         "geometry": square(20 * KM, 150 * KM)},
        {"source": "CNFDB", "fire_id": "none", "ignition": "2020-07-15", "cnfdb_year": 2020,
         "month_known": False, "date_known": False, "geometry": square(20 * KM, 150 * KM)},
    ]


def test_start_group_plain_wrapped_and_undated():
    pieces = pd.DataFrame({
        "region": ["BC", "BC", "BC", "NorCal", "NorCal", "NorCal", "BC"],
        "ignition": pd.to_datetime(["2020-05-31", "2020-07-01", "2020-08-20", "2020-06-15",
                                    "2021-01-05", "2020-12-01", "2020-07-15"]),
        "undated": [False] * 6 + [True]})
    assert list(fad.start_group(pieces, 7)) == ["before", "after", "after", "before",
                                                "after", "after", "undated"]
    # a January fire of a wrapped window is after every issue date
    assert all(fad.start_group(pieces, m)[4] == "after" for m in AFTER_DATE_ISSUE_MONTHS.values())
    assert list(fad.start_group(pieces, 6))[:4] == ["before", "after", "after", "after"]


def test_select_pieces_drop_held_back_and_out_of_window():
    pieces = pd.DataFrame({
        "region": ["PNW", "PNW", "BC", "BC", "NorCal", "PNW"],
        "season": pd.array([2025, 2026, 2024, 2025, FIRE_FIRST_YEAR - 1, pd.NA], dtype="Int64")})
    kept = fad.select_pieces(pieces, fad.development_seasons(LAST))
    assert list(zip(kept["region"], kept["season"])) == [("PNW", 2025), ("BC", 2024)]
    assert len(fad.development_seasons(LAST)) == 291


def test_guard_seasons_refuses_held_back_unless_named():
    dev = [("PNW", 2025), ("BC", 2024)]
    assert fad.guard_seasons(dev, last_year=LAST) == dev
    for asked in ([("PNW", 2026)], [("BC", 2025)], dev + [("YT", 2025)]):
        with pytest.raises(fad.HeldBackSeasonError):
            fad.guard_seasons(asked, last_year=LAST)
    # named but not asked for, or a different season named
    with pytest.raises(fad.HeldBackSeasonError):
        fad.guard_seasons(dev, [("PNW", 2026)], last_year=LAST)
    with pytest.raises(fad.HeldBackSeasonError):
        fad.guard_seasons([("PNW", 2026)], [("PNW", 2027)], last_year=LAST)
    assert fad.guard_seasons([("BC", 2025)], [("BC", 2025)], last_year=LAST) == [("BC", 2025)]
    with pytest.raises(ValueError):
        fad.guard_seasons([("PNW", FIRE_FIRST_YEAR - 1)], last_year=LAST)
    with pytest.raises(ValueError):
        fad.guard_seasons(dev + dev, last_year=LAST)


def scoring_rows():
    # Made-up fires only: a season past PNW's last test year, and one inside it.
    return [
        {"source": "WFIGS", "fire_id": "jun", "ignition": "2026-06-20",
         "geometry": square(-50 * KM, 20 * KM)},
        {"source": "WFIGS", "fire_id": "aug", "ignition": "2026-08-03",
         "geometry": square(-50 * KM, 20 * KM, shift=SIDE / 2)},
        {"source": "WFIGS", "fire_id": "dev", "ignition": "2025-07-01",
         "geometry": square(-80 * KM, 60 * KM)},
    ]


def test_scoring_day_path_on_made_up_pieces(regions):
    pieces = pieces_for(scoring_rows(), regions)
    scored = [("PNW", 2026)]
    with pytest.raises(fad.HeldBackSeasonError):  # refused by default
        fad.split_table(pieces, scored, last_year=LAST)
    table = fad.split_table(pieces, scored, last_year=LAST, scoring_day_seasons=scored)
    assert list(zip(table["region"], table["year"])) == [("PNW", 2026)] * 3
    t = table.set_index("issue_date")
    assert t.loc["1 August", ["after_ha", "before_ha", "burn_ha"]].tolist() == pytest.approx(
        [1_000, 1_000, 1_500])
    assert t.loc["1 June", "before_ha"] == 0
    # the same function gives the same rows when the season is an ordinary one
    later = {**LAST, "PNW": 2026}
    whole = fad.split_table(pieces, last_year=later)
    same = whole[(whole["region"] == "PNW") & (whole["year"] == 2026)].reset_index(drop=True)
    pd.testing.assert_frame_equal(same, table)
    # checked against that day's outcome table
    kept = fad.select_pieces(pieces, scored)
    outcome = fire.region_year_table(kept, later, areas=fire.union_areas(kept))
    assert not any(fad.check_table(table, outcome, scored, last_year=LAST).values())
    extra = fad.check_table(whole, outcome, scored, last_year=later)
    assert extra["5 only the region-seasons asked for; one row per region, season and issue date"]


def test_default_build_never_holds_a_held_back_row(regions):
    table = fad.split_table(pieces_for(scoring_rows(), regions), last_year=LAST)
    assert not fad.held_back(zip(table["region"], table["year"]), LAST)
    assert table.loc[table["region"] == "PNW", "year"].max() == 2025


def test_split_table_unions_each_group(regions):
    table = fad.split_table(pieces_for(bc_rows(), regions), last_year=LAST)
    assert list(table.columns) == fad.COLUMNS
    assert len(table) == 3 * sum(LAST[r] - FIRE_FIRST_YEAR + 1 for r in REGIONS)
    t = table.set_index(["region", "year", "issue_date"])
    june, july, august = (t.loc[("BC", 2020, d)] for d in ("1 June", "1 July", "1 August"))
    # whole season: May and July overlap by half (1,500 ha) plus August (1,000 ha)
    assert june["burn_ha"] == pytest.approx(2_500)
    assert (june["after_ha"], june["before_ha"]) == pytest.approx((2_000, 1_000))
    assert (july["after_ha"], july["before_ha"]) == pytest.approx((2_000, 1_000))
    assert (august["after_ha"], august["before_ha"]) == pytest.approx((1_000, 1_500))
    assert (august["n_after"], august["n_before"], august["n_undated"]) == (1, 2, 1)
    # the undated piece lies on the August fire: the groups overlap, so the
    # three areas sum to more than the whole
    assert august["undated_ha"] == pytest.approx(1_000)
    assert june["after_ha"] + june["before_ha"] + june["undated_ha"] > june["burn_ha"]
    assert t.loc[("BC", 2019, "1 July"), ["after_ha", "burn_ha", "n_after"]].sum() == 0


def test_split_table_wrapped_window_and_held_back(regions):
    at = (20 * KM, 20 * KM)
    rows = [
        {"source": "WFIGS", "fire_id": "jun", "ignition": "2024-06-20", "geometry": square(*at)},
        {"source": "WFIGS", "fire_id": "jan", "ignition": "2025-01-08",
         "geometry": square(60 * KM, 20 * KM)},
        {"source": "WFIGS", "fire_id": "held", "ignition": "2026-07-01", "geometry": square(*at)},
        {"source": "WFIGS", "fire_id": "pnw", "ignition": "2025-06-02",
         "geometry": square(-50 * KM, 20 * KM)},
    ]
    table = fad.split_table(pieces_for(rows, regions), last_year=LAST)
    assert table["year"].max() == 2025
    t = table.set_index(["region", "year", "issue_date"])
    assert t.loc[("NorCal", 2024, "1 August"), "after_ha"] == pytest.approx(1_000)  # January
    assert t.loc[("NorCal", 2024, "1 August"), "before_ha"] == pytest.approx(1_000)
    assert t.loc[("NorCal", 2024, "1 June"), "before_ha"] == 0
    assert t.loc[("PNW", 2025, "1 June"), ["before_ha", "n_before"]].sum() == 0


def checked(regions):
    pieces = pieces_for(bc_rows(), regions)
    kept = fad.select_pieces(pieces, fad.development_seasons(LAST))
    pinned = fire.region_year_table(kept, LAST, areas=fire.union_areas(kept))
    return fad.split_table(pieces, last_year=LAST), pinned


def failing(table, pinned):
    return [name[0] for name, rows in fad.check_table(table, pinned, last_year=LAST).items()
            if rows]


def test_check_table_passes_a_built_table(regions):
    assert failing(*checked(regions)) == []


def test_check_table_names_each_failure_without_values(regions):
    table, pinned = checked(regions)
    row = table.index[(table["region"] == "BC") & (table["year"] == 2020)
                      & (table["issue_date"] == "1 July")][0]

    bad = table.copy()
    bad.loc[row, "burn_ha"] += 1e-3
    assert failing(bad, pinned) == ["1"]
    bad = table.copy()
    bad.loc[row, "n_after"] += 1
    assert failing(bad, pinned) == ["2"]
    bad = table.copy()
    bad.loc[row, ["n_undated", "n_before"]] += [1, -1]  # total kept, undated wrong
    assert failing(bad, pinned) == ["2"]
    bad = table.copy()
    bad.loc[row, "after_ha"] = 123.456
    result = fad.check_table(bad, pinned, last_year=LAST)
    assert failing(bad, pinned) == ["3"]
    assert [rows for rows in result.values() if rows] == [["BC 2020 at 1 July"]]
    bad = table.copy()
    pnw = bad.index[(bad["region"] == "PNW") & (bad["issue_date"] == "1 June")][0]
    bad.loc[pnw, "before_ha"] = 5.0
    assert "4" in failing(bad, pinned)
    held = table.iloc[[row]].assign(year=2025)  # BC 2025 is held back
    assert "5" in failing(pd.concat([table, held], ignore_index=True), pinned)
    assert "5" in failing(table.drop(index=row), pinned)


def test_verify_downloads_and_reroot(tmp_path):
    pins = pd.DataFrame({"path": [], "sha256": []})
    rows = []
    for path in fad.PINNED_DOWNLOADS:
        target = fad.reroot(path, tmp_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.name.encode())
        rows.append({"path": target.relative_to(tmp_path).as_posix(),
                     "sha256": fad.pin_inputs.sha256(target)})
    pins = pd.DataFrame(rows)
    pins.to_csv(tmp_path / "pins.csv", index=False)
    assert fad.verify_downloads(tmp_path, tmp_path / "pins.csv") == list(pins["path"])
    fad.reroot(fad.MTBS_ZIP, tmp_path).write_bytes(b"changed")
    with pytest.raises(fad.pin_inputs.PinnedInputError):
        fad.verify_downloads(tmp_path, tmp_path / "pins.csv")
