"""The methods page's measured numbers: row builders on made-up tables, and
the committed table's shape."""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import methods_numbers  # noqa: E402
import source_pairs  # noqa: E402

from src.config import CRS_EQUAL_AREA  # noqa: E402


def _fires(boxes):
    geoms = [box(*b) for b in boxes]
    frame = gpd.GeoDataFrame({"fire_id": [f"f{i}" for i in range(len(geoms))],
                              "name": [f"n{i}" for i in range(len(geoms))]},
                             geometry=geoms, crs=CRS_EQUAL_AREA)
    return frame.assign(fire_ha=frame.geometry.area / 10_000)


def test_only_one_to_one_pairs_are_compared():
    # WFIGS: A alone over one MTBS fire; B and C both over one MTBS fire;
    # D over two MTBS fires; E touching an MTBS fire along an edge only.
    wfigs = _fires([(0, 0, 3000, 3000), (10000, 0, 12000, 3000), (12000, 0, 14000, 3000),
                    (20000, 0, 26000, 3000), (30000, 0, 33000, 3000)])
    mtbs = _fires([(0, 0, 3000, 2700), (10000, 0, 14000, 3000), (20000, 0, 23000, 3000),
                   (23000, 0, 26000, 3000), (33000, 0, 36000, 3000)])
    pairs = source_pairs.one_to_one_pairs(wfigs, mtbs)
    assert pairs[["wfigs_id", "mtbs_id"]].values.tolist() == [["f0", "f0"]]
    assert pairs["ratio"].iloc[0] == pytest.approx(900 / 810)
    assert pairs["overlap_ha"].iloc[0] == pytest.approx(810)
    assert source_pairs.one_to_one_pairs(wfigs.iloc[:0], mtbs).empty


def test_pair_summary_and_rows():
    pairs = pd.DataFrame({"year": [2021, 2021, 2022], "ratio": [0.9, 1.1, 0.98],
                          "wfigs_ha": [900.0, 1100.0, 980.0], "mtbs_ha": [1000.0, 1000.0, 1000.0]})
    summary = source_pairs.summarise(pairs).set_index("year")
    assert summary.loc[2021, "pairs"] == 2 and summary.loc[2021, "median_ratio"] == 1.0
    rows = pd.DataFrame(methods_numbers.pair_rows(pairs))
    assert rows[rows["measure"] == "wfigs_over_mtbs_total"]["value"].tolist() == [1.0, 0.98]
    assert rows["n"].tolist() == [2, 2, 1, 1]


def test_enso_rows_count_class_changes():
    a = pd.DataFrame({"year": [1, 2, 3, 4], "phase": ["el_nino", "neutral", "el_nino", "la_nina"],
                      "strong": [True, False, False, False], "enso_djf": [1.6, 0.1, 0.7, -0.9]})
    b = a.assign(phase=["el_nino", "el_nino", "el_nino", "la_nina"],
                 strong=[False, False, False, False])
    rows = {r["measure"]: r for r in methods_numbers.enso_rows(a, b)}
    assert rows["enso_class_differs"]["value"] == 2 and rows["enso_class_differs"]["n"] == 4
    assert rows["enso_phase_differs"]["value"] == 1


def test_nbac_share_is_on_provincial_land_and_uses_uncovered_area():
    fires = pd.DataFrame({
        "region": ["AB"] * 4 + ["BC", "YT"], "year": 2000,
        "GID": ["a", "a", "b", "c", "d", "e"],
        "ADMIN_NAME": ["AB", "PC", "AB", "DND", "BC", "YT"],
        "nbac_ha": [600.0, 400.0, 1000.0, 500.0, 100.0, 100.0],
        "uncovered_ha": [500.0, 100.0, 100.0, 500.0, 0.0, 0.0]})
    rows = {r["group"]: r for r in methods_numbers.nbac_rows(fires, share=0.5)}
    # fire a is missing as a whole (600 of 1,000 ha uncovered); its 500 ha on
    # provincial land over the 1,600 ha of NBAC area on provincial land
    assert rows["AB"]["value"] == pytest.approx(100 * 500 / 1600) and rows["AB"]["n"] == 1
    assert rows["BC"]["value"] == 0 and rows["BC"]["n"] == 0


def test_station_and_overlap_rows():
    table = pd.DataFrame({"region": ["PNW"] * 4, "era5_swe_z": [0.0, 1.0, 2.0, 3.0],
                          "station_swe_z": [0.0, 2.0, 4.0, 6.0],
                          "era5_swe_pct": [1.0, 2.0, 3.0, None],
                          "station_swe_pct": [3.0, 2.0, 1.0, 5.0]})
    rows = methods_numbers.station_rows(table)
    assert [(r["measure"], round(r["value"], 6), r["n"]) for r in rows] == [
        ("station_correlation_z", 1.0, 4), ("station_correlation_pct", -1.0, 3)]
    fire = pd.DataFrame({"source": ["MTBS", "MTBS", "WFIGS"], "double_ha": [10.0, 0.0, 5.0]})
    rows = {r["group"]: r["value"] for r in methods_numbers.overlap_rows(fire)}
    assert rows == {"all": 15.0, "MTBS": 10.0, "WFIGS": 5.0}


def test_committed_table_shape():
    if not methods_numbers.OUT.exists():
        pytest.skip("methods_numbers.csv not built yet")
    table = pd.read_csv(methods_numbers.OUT)
    assert list(table.columns) == methods_numbers.COLUMNS
    assert set(table["measure"]) == set(methods_numbers.MEASURES)
    assert not table.duplicated(["measure", "group"]).any()
    assert table["value"].notna().all()
