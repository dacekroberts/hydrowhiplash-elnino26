"""The measured numbers the methods page quotes, as one committed table.

site/methods.qmd reads only results/. Eight of its numbers were typed from
DECISIONS.md and the methods register; this script recomputes each from the
table or measurement file behind it and writes
results/tables/methods_numbers.csv, one row per number:

  measure   what is measured (see MEASURES below)
  group     the region, year or variable the value belongs to; "all" if none
  value     the number
  unit      ha, percent, ratio, correlation, count
  n         how many items the value rests on (fires, years, winters, pairs)
  basis     the file it was computed from

No polygon is read here: the inputs are tables. Four of them are
measurement outputs in data/processed/ that are not committed
(nbac_coverage_fires.csv, parks_gap_measure.csv, interior_alaska_check.csv,
mtbs_wfigs_pairs.csv), so the script runs only in the main checkout, after
the scripts that write them.

Run from the repo root:  python scripts/methods_numbers.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402

TABLES = config.RESULTS / "tables"
OUT = TABLES / "methods_numbers.csv"
COLUMNS = ["measure", "group", "value", "unit", "n", "basis"]
CANADA = ("BC", "AB", "YT")
MEASURES = {
    "overlap_double_counted": "area that summing overlapping perimeters would count twice "
                              "(double_ha), over every region-season of the fire table",
    "enso_class_differs": "winters whose class (El Nino, neutral or La Nina, or strong or not) "
                          "differs between the two indices",
    "enso_phase_differs": "winters whose phase alone differs between the two indices",
    "enso_index_correlation": "correlation of the two indices' DJF values",
    "nbac_missing_share": "uncovered NBAC area of fires missing from CNFDB, on provincial and "
                          "territorial land, as a share of NBAC area on that land",
    "cnfdb_park_area": "CNFDB Parks Canada burned area counted in the season, three regions summed",
    "defence_land_share": "NBAC burned area on defence land as a share of the region's counted "
                          "burned area",
    "defence_land_area": "NBAC burned area on defence land",
    "station_correlation_z": "correlation of the ERA5-Land and station 1 April snowpack series, "
                             "standardised",
    "station_correlation_pct": "the same correlation on percent of the 1991-2020 normal",
    "interior_alaska_correlation": "correlation of Interior Alaska with the statewide series",
    "wfigs_over_mtbs_median": "median WFIGS area over MTBS area on one-to-one fire pairs",
    "wfigs_over_mtbs_total": "total WFIGS area over total MTBS area on the same pairs",
}


def row(measure, group, value, unit, n, basis) -> dict:
    assert measure in MEASURES, measure
    return {"measure": measure, "group": str(group), "value": value, "unit": unit,
            "n": int(n), "basis": basis}


def overlap_rows(fire: pd.DataFrame) -> list[dict]:
    basis = "results/tables/fire_region_year.csv"
    rows = [row("overlap_double_counted", "all", fire["double_ha"].sum(), "ha", len(fire), basis)]
    for source, group in fire[fire["double_ha"] > 0].groupby("source"):
        rows.append(row("overlap_double_counted", source, group["double_ha"].sum(), "ha",
                        len(group), basis))
    return rows


def enso_rows(main: pd.DataFrame, check: pd.DataFrame) -> list[dict]:
    """`main` and `check`: classified winters under the two indices."""
    both = main.set_index("year").join(check.set_index("year"), lsuffix="_a", rsuffix="_b",
                                       how="inner")
    phase = both["phase_a"] != both["phase_b"]
    strong = both["strong_a"] != both["strong_b"]
    basis = "pinned RONI and ONI files (data/raw), classified by src.download_oni"
    return [
        row("enso_class_differs", "all", int((phase | strong).sum()), "count", len(both), basis),
        row("enso_phase_differs", "all", int(phase.sum()), "count", len(both), basis),
        row("enso_index_correlation", "all", both["enso_djf_a"].corr(both["enso_djf_b"]),
            "correlation", len(both), basis),
    ]


def nbac_rows(fires: pd.DataFrame, share: float = config.NBAC_MISSING_SHARE) -> list[dict]:
    """`fires`: nbac_coverage_fires.csv (one row per NBAC fire, region and
    land label). A fire is missing where more than `share` of its area in
    the region is uncovered, all labels together, as
    scripts/nbac_coverage.classify does; the share reported is on the land
    that is neither national park nor defence land."""
    per = fires.groupby(["region", "year", "GID"])[["nbac_ha", "uncovered_ha"]].sum()
    missing = (per["uncovered_ha"] / per["nbac_ha"] > share).rename("missing")
    fires = fires.join(missing, on=["region", "year", "GID"])
    land = fires[~fires["ADMIN_NAME"].isin([config.NBAC_PARK_ADMIN, config.NBAC_DND_ADMIN])]
    rows = []
    for region in CANADA:
        sub = land[land["region"] == region]
        gone = sub[sub["missing"]]
        rows.append(row("nbac_missing_share", region,
                        100 * gone["uncovered_ha"].sum() / sub["nbac_ha"].sum(), "percent",
                        gone["GID"].nunique(), "data/processed/nbac_coverage_fires.csv"))
    return rows


def parks_rows(measure: pd.DataFrame, first: int = 2010) -> list[dict]:
    basis = "data/processed/parks_gap_measure.csv"
    by_year = measure[measure["year"] >= first].groupby("year")["cnfdb_pc_ha"].sum()
    rows = [row("cnfdb_park_area", year, value, "ha", measure["region"].nunique(), basis)
            for year, value in by_year.items()]
    for region, group in measure[measure["year"] <= config.CNFDB_LAST_YEAR].groupby("region"):
        seasons = int((group["nbac_dnd_ha"] > 0).sum())
        rows.append(row("defence_land_area", region, group["nbac_dnd_ha"].sum(), "ha", seasons,
                        basis))
        rows.append(row("defence_land_share", region,
                        100 * group["nbac_dnd_ha"].sum() / group["burn_ha"].sum(), "percent",
                        seasons, basis))
    return rows


def station_rows(table: pd.DataFrame) -> list[dict]:
    basis = "results/tables/station_swe_region_year.csv"
    rows = []
    for measure, a, b in (("station_correlation_z", "era5_swe_z", "station_swe_z"),
                          ("station_correlation_pct", "era5_swe_pct", "station_swe_pct")):
        for region, group in table.dropna(subset=[a, b]).groupby("region", sort=False):
            rows.append(row(measure, region, group[a].corr(group[b]), "correlation", len(group),
                            basis))
    return rows


def interior_rows(check: pd.DataFrame, whole: str = "AK", part: str = "AK_interior") -> list[dict]:
    wide = check.pivot(index="year", columns="region")
    rows = []
    for variable in ("temp_jja", "temp_mam", "precip_djf_mm", "precip_octmar_mm"):
        pair = wide[variable][[whole, part]].dropna()
        rows.append(row("interior_alaska_correlation", variable, pair[whole].corr(pair[part]),
                        "correlation", len(pair), "data/processed/interior_alaska_check.csv"))
    return rows


def pair_rows(pairs: pd.DataFrame) -> list[dict]:
    basis = "data/processed/mtbs_wfigs_pairs.csv (scripts/source_pairs.py)"
    rows = []
    for year, group in pairs.groupby("year"):
        rows.append(row("wfigs_over_mtbs_median", int(year), group["ratio"].median(), "ratio",
                        len(group), basis))
        rows.append(row("wfigs_over_mtbs_total", int(year),
                        group["wfigs_ha"].sum() / group["mtbs_ha"].sum(), "ratio", len(group),
                        basis))
    return rows


def build() -> pd.DataFrame:
    from src import download_oni, pin_inputs

    processed = config.DATA_PROCESSED
    winters = {index: download_oni.classify_winters(
        download_oni.parse(pin_inputs.enso_raw_path(index)), index)
        for index in (config.ENSO_INDEX, config.ENSO_ROBUSTNESS_INDEX)}
    last = pd.read_csv(processed / "el_nino_winters.csv")["year"].max()
    winters = {k: v[v["year"] <= last] for k, v in winters.items()}
    rows = (overlap_rows(pd.read_csv(TABLES / "fire_region_year.csv"))
            + enso_rows(winters[config.ENSO_INDEX], winters[config.ENSO_ROBUSTNESS_INDEX])
            + nbac_rows(pd.read_csv(processed / "nbac_coverage_fires.csv"))
            + parks_rows(pd.read_csv(processed / "parks_gap_measure.csv"))
            + station_rows(pd.read_csv(TABLES / "station_swe_region_year.csv"))
            + interior_rows(pd.read_csv(processed / "interior_alaska_check.csv"))
            + pair_rows(pd.read_csv(processed / "mtbs_wfigs_pairs.csv")))
    table = pd.DataFrame(rows, columns=COLUMNS)
    table["value"] = table["value"].astype(float).round(4)
    return table


def main() -> None:
    table = build()
    OUT.write_bytes(table.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    print(f"wrote {OUT}: {len(table)} rows")
    print(table.drop(columns="basis").to_string(index=False))


if __name__ == "__main__":
    main()
