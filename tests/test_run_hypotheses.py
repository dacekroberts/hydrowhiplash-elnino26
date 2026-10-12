"""Tests for src/run_hypotheses.py on synthetic tables shaped like the
pinned inputs (same regions, years and gaps), with planted effects. No
pinned input and no fire data is read."""
import numpy as np
import pandas as pd
import pytest

from src import pin_inputs, run_guard, run_hypotheses as rh, stats
from src.config import (CLIMATE_FIRST_YEAR, EL_NINO_THRESHOLD, FIRE_FIRST_YEAR,
                        FIRE_LAST_YEAR_BY_REGION, H1_VALUE, LA_NINA_THRESHOLD, TEST_DIRECTIONS)

DRAWS = {"n_perm": 200, "n_boot": 200}
PLANTED = {"PNW": 1.0, "BC": -1.0}  # enso_djf slope on log_burn; 0 elsewhere
FORCED = {1987: 1.46, 1992: 1.6, 1998: 2.2, 2010: 1.44, 2016: 2.4}  # strong and near-threshold
ZERO = ("SoCal", 2014)


def winters_table(seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = np.arange(CLIMATE_FIRST_YEAR + 1, 2027)
    enso = np.round(rng.normal(0, 0.8, len(years)).clip(-1.3, 1.3), 2)  # strong only if forced
    for year, value in FORCED.items():
        enso[years == year] = value
    phase = np.where(enso >= EL_NINO_THRESHOLD, "el_nino",
                     np.where(enso <= LA_NINA_THRESHOLD, "la_nina", "neutral"))
    return pd.DataFrame({"year": years, "enso_djf": enso, "phase": phase})


def synthetic_tables(seed: int = 1) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winters = winters_table(seed)
    controls, swe, spei, fire = [], [], [], []
    for region, last in FIRE_LAST_YEAR_BY_REGION.items():
        c = winters.copy()
        n = len(c)
        c.insert(0, "region", region)
        c["temp_jja"] = 290 + rng.normal(0, 1, n)
        c.loc[c["year"] == 2026, "temp_jja"] = np.nan
        c[H1_VALUE] = 300 + 0.2 * (c["year"] - 1990) + rng.normal(0, 40, n)
        c["precip_anom_lag0"] = rng.normal(0, 1, n)
        c["precip_anom_lag1"] = c["precip_anom_lag0"].shift(1)
        controls.append(c)
        s = c[["region", "year"]].copy()
        s["era5_swe_z"] = np.nan if region == "SoCal" else rng.normal(0, 1, n)
        s["station_swe_z"] = rng.normal(0, 1, n)
        if region in ("NorCal", "SoCal"):
            s["station_swe_z"] = np.nan
        if region == "AB":
            s.loc[(s["year"] < 1963) | (s["year"] > 2025), "station_swe_z"] = np.nan
        swe.append(s)
        w = c[["region", "year"]].copy()
        w["spei3_djf"] = rng.normal(0, 1, n)
        spei.append(w)
        f = c.loc[(c["year"] >= FIRE_FIRST_YEAR) & (c["year"] <= last),
                  ["region", "year", "enso_djf", "phase"]].copy()
        f["log_burn"] = (10 + 0.03 * (f["year"] - 2000) + PLANTED.get(region, 0.0) * f["enso_djf"]
                         + rng.normal(0, 0.3, len(f)))
        f["zero_fire"] = False
        if region == ZERO[0]:
            hit = f["year"] == ZERO[1]
            f.loc[hit, "log_burn"] = 0.0
            f.loc[hit, "zero_fire"] = True
        fire.append(f)
    fire = pd.concat(fire, ignore_index=True)
    return {"fire": fire, "frozen": fire.copy(), "parks": fire.copy(),
            "controls": pd.concat(controls, ignore_index=True),
            "swe": pd.concat(swe, ignore_index=True), "spei": pd.concat(spei, ignore_index=True)}


@pytest.fixture(scope="module")
def tables():
    return synthetic_tables()


@pytest.fixture(scope="module")
def results(tables):
    return rh.compute_all(tables, winters_table(seed=2), **DRAWS)


# --- the registered table ---------------------------------------------------------

def test_registered_table_holds_the_52_tests_in_plan_order(results):
    reg = results["registered_tests.csv"]
    assert len(reg) == 52 and (reg["run_kind"] == "registered").all()
    order = [rh.PLAN_ORDER.index(t) for t in reg["test"]]
    assert order == sorted(order)
    sizes = reg.groupby("family").size().to_dict()
    assert sizes == {"H1": 5, "H2": 5, "H3a": 5, "H3b": 5, "H4": 1, "H5": 10, "H6": 9,
                     "north_H2": 2, "north_H3a": 2, "north_H3b": 2, "C1": 3, "C2": 3}
    assert reg[["estimate", "ci_low", "ci_high", "p", "p_holm", "p_bh"]].notna().all().all()
    assert ((reg["ci_low"] <= reg["estimate"]) & (reg["estimate"] <= reg["ci_high"])).all()
    assert (reg["p_holm"] >= reg["p"] - 1e-12).all()
    assert (reg["significant"] == (reg["p_holm"] < 0.05)).all()


def test_effect_sizes_and_cis_come_before_p_values():
    cols = rh.COLUMNS
    assert cols.index("estimate") < cols.index("ci_low") < cols.index("pct_change") < cols.index("p")
    assert cols.index("p") < cols.index("p_holm") < cols.index("size") < cols.index("plain_ols_p")


def test_each_row_carries_its_registered_direction_and_size_label(results):
    reg = results["registered_tests.csv"]
    for _, row in reg[reg["test"] != "H4"].iterrows():
        assert row["alternative"] == TEST_DIRECTIONS[row["test"]][row["region"]]
        shape = run_guard.size_shape(row["test"], row["region"])
        if shape is None:  # H1, H2: permutation tests carry no label
            assert pd.isna(row["size"]) and pd.isna(row["plain_ols_p"])
            continue
        assert row["size_shape"] == shape and row["size"] == run_guard.size_label(shape)["size"]
        plain = run_guard.plain_ols_shape(row["test"], row["region"])
        assert pd.isna(row["plain_ols_p"]) == (plain is None)
        if plain is not None:
            assert row["plain_ols_size"] == run_guard.size_label(plain)["size"]
    h4 = reg[reg["test"] == "H4"].iloc[0]
    assert h4["size_shape"] == "H4 contrast, DK" and h4["method"] == "Driscoll-Kraay"
    assert h4["years"] == "1984-2024" and h4["n"] == 5 * 41 and h4["df"] == 40


def test_planted_effects_are_recovered_and_the_wrong_sign_gives_p_above_half(results, tables):
    reg = results["registered_tests.csv"].set_index(["test", "region"])
    pnw, bc = reg.loc[("H3a", "PNW")], reg.loc[("H3a", "BC")]
    assert abs(pnw["estimate"] - 1.0) < 0.2 and pnw["p"] < 0.001 and pnw["significant"]
    assert abs(bc["estimate"] + 1.0) < 0.2 and bc["p"] > 0.5  # registered one-sided positive
    assert pnw["pct_change"] == pytest.approx(100 * (np.exp(pnw["estimate"]) - 1))
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    g = fire[fire["region"] == "PNW"]
    direct = stats.coef_test(stats.fit_ols_hac(rh.H3A_FORMULA, g), "enso_djf", "greater")
    assert pnw["estimate"] == pytest.approx(direct["estimate"]) and pnw["p"] == pytest.approx(direct["p"])
    plain = stats.coef_test(stats.fit_ols_plain(rh.H3A_FORMULA, g), "enso_djf", "greater")
    assert pnw["plain_ols_p"] == pytest.approx(plain["p"])
    h2 = reg.loc[("H2", "PNW")]
    detr = stats.detrend(g, "log_burn").to_numpy()
    perm = stats.permutation_test(detr, g["phase"] == "el_nino", n_perm=200, alternative="greater")
    assert h2["estimate"] == pytest.approx(perm["diff"]) and h2["p"] == pytest.approx(perm["p"])
    assert h2["n"] == 42 and h2["n_group"] == int((g["phase"] == "el_nino").sum())


def test_holm_is_taken_within_each_family(results):
    reg = results["registered_tests.csv"]
    for family, rows in reg.groupby("family"):
        assert np.allclose(rows["p_holm"], stats.adjust_pvalues(rows["p"], "holm"))
        assert np.allclose(rows["p_bh"], stats.adjust_pvalues(rows["p"], "fdr_bh"))


def test_c1_runs_on_the_climate_winters(results):
    c1 = results["registered_tests.csv"].query("test == 'C1'")
    assert (c1["years"] == "1951-2026").all() and (c1["n"] == 76).all()
    assert (c1["term"] == "enso_djf:year_c").all() and c1["pct_change"].isna().all()


# --- the runs reported beside -------------------------------------------------------

def test_reported_runs_cover_the_planned_tests_and_regions(results):
    beside = results["reported_beside.csv"]
    counts = beside.groupby("run_kind").size().to_dict()
    assert counts == {"oni_robustness": 33, "frozen_rules": 44, "parks_nbac": 9, "zero_fire": 7,
                      "station_z": 6, "strong_only": 24, "strong_flip": 24, "h4_secondary": 7,
                      "h6_combined": 8, "block_bootstrap": 14, "h3_gap": 7,
                      "lag1_autocorrelation": 22}
    assert beside[["p_holm", "p_bh", "significant"]].isna().all().all()  # uncorrected
    oni = beside[beside["run_kind"] == "oni_robustness"]
    assert set(oni["test"]) == {"H1", "H2", "H3a", "H3b", "H4", "C1", "C2"}
    assert (oni["enso_index"] == "ONI").all()
    parks = beside[beside["run_kind"] == "parks_nbac"]
    assert set(parks["region"]) == {"AB", rh.H4_REGION_LABEL}
    assert (parks["fire_table"] == "fire_region_year_parks_nbac.csv").all()
    zero = beside[beside["run_kind"] == "zero_fire"]
    assert set(zero["region"]) == {"SoCal", rh.H4_REGION_LABEL} and (zero["n_zero"] == 1).all()
    assert zero.set_index("test").loc["H2", "n"] == 41  # the zero season dropped
    station = beside[beside["run_kind"] == "station_z"].set_index(["test", "region"])
    assert ("H6_swe", "NorCal") not in station.index
    assert station.loc[("C1", "AB"), "years"] == "1963-2025"
    strong = beside[beside["run_kind"].isin(["strong_only", "strong_flip"])]
    assert (strong["alternative"] == "two-sided").all() and set(strong["enso_index"]) == {"RONI", "ONI"}


def test_oni_run_differs_from_the_registered_run_and_strong_flip_moves_the_group(results):
    reg = results["registered_tests.csv"].set_index(["test", "region"])
    beside = results["reported_beside.csv"]
    oni = beside[beside["run_kind"] == "oni_robustness"].set_index(["test", "region"])
    assert oni.loc[("H3a", "PNW"), "estimate"] != reg.loc[("H3a", "PNW"), "estimate"]
    roni = beside[(beside["enso_index"] == "RONI") & (beside["test"] == "H2")
                  & (beside["region"] == "PNW")].set_index("run_kind")
    # fire years: 1992, 1998, 2016 strong; the flip drops none and adds 1987 and 2010
    assert roni.loc["strong_only", "n_group"] == 3 and roni.loc["strong_flip", "n_group"] == 5


def test_zero_fire_regression_equals_the_fit_without_the_zero_season(results, tables):
    zero = results["reported_beside.csv"].query("run_kind == 'zero_fire'").set_index("test")
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    g = fire[(fire["region"] == "SoCal") & ~fire["zero_fire"]]
    without = stats.fit_ols_plain(rh.H3A_FORMULA, g).params["enso_djf"]
    assert zero.loc["H3a", "estimate"] == pytest.approx(without)


def test_h4_secondary_rows_and_the_bootstrap_statistics(results, tables):
    beside = results["reported_beside.csv"]
    h4 = beside[beside["run_kind"] == "h4_secondary"]
    assert list(h4["size_shape"].dropna()) == ["H4 joint F, DK", "H4 contrast, clustered",
                                               "H4 joint F, clustered"]
    assert (h4["note"] == "model with temp_jja").sum() == 4
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    g = fire[fire["region"] == "PNW"].reset_index(drop=True)
    assert rh._enso_h3a(g) == pytest.approx(stats.fit_ols_plain(rh.H3A_FORMULA, g).params["enso_djf"])
    h3b = stats.fit_ols_plain(rh.REGRESSIONS["H3b"][0], g).params["enso_djf"]
    assert rh._enso_h3b(g) == pytest.approx(h3b)
    gap = beside[(beside["run_kind"] == "h3_gap") & (beside["region"] == "PNW")].iloc[0]
    assert gap["estimate"] == pytest.approx(rh._enso_h3a(g) - h3b) and pd.isna(gap["p"])


def test_validation_table(results):
    val = results["validation.csv"]
    assert len(val) == 7 * 3 + 4 * 2 + 5 * 2
    forward = val[(val["method"] == "expanding window") & (val["model"] == "H3a")].set_index("region")
    assert forward.loc["PNW", "years"] == "2004-2025" and forward.loc["PNW", "n"] == 22
    assert forward.loc["BC", "years"] == "2004-2024" and forward.loc["BC", "n"] == 21
    assert forward.loc["PNW", "skill"] > 0.3  # the planted slope beats the trend-only model
    assert val["coverage"].between(0, 1).all() and (val["interval"] == "80%").all()


# --- pieces ---------------------------------------------------------------------------

def test_percent_change_left_empty_above_the_zero_share_limit(tables):
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    g = fire[fire["region"] == "NorCal"].reset_index(drop=True)
    assert not pd.isna(rh.coef_row("H3a", "NorCal", g)["pct_change"])
    g.loc[:4, ["log_burn", "zero_fire"]] = [0.0, True]  # 5 of 42 seasons, above 10%
    row = rh.coef_row("H3a", "NorCal", g)
    assert "pct_change" not in row and row["n_zero"] == 5


def test_with_index_swaps_the_index_and_refuses_a_missing_year(tables):
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    other = winters_table(seed=2)
    swapped = rh.with_index(fire, other)
    assert len(swapped) == len(fire) == 291
    assert swapped.loc[swapped["year"] == 2000, "enso_djf"].nunique() == 1
    assert swapped["enso_djf"].tolist() != fire["enso_djf"].tolist()
    with pytest.raises(ValueError, match="No index value"):
        rh.with_index(fire, other[other["year"] != 2000])
    rh.check_index(fire, winters_table(seed=1))
    with pytest.raises(ValueError, match="differs from the pinned raw index"):
        rh.check_index(fire, other)


def test_a_group_too_small_to_compare_is_refused(tables):
    fire = rh.fire_frame(tables["fire"], tables["controls"], tables["swe"], tables["spei"])
    g = fire[fire["region"] == "PNW"].reset_index(drop=True)
    with pytest.raises(ValueError, match="cannot be compared"):
        rh.diff_row(g, "log_burn", g["year"] == 1998, "two-sided", 50, 50)


def test_add_corrections_refuses_a_missing_or_repeated_test(results):
    rows = results["registered_tests.csv"].to_dict("records")
    with pytest.raises(ValueError):
        rh.add_corrections(rows[1:])
    with pytest.raises(ValueError, match="twice"):
        rh.add_corrections(rows + rows[:1])


# --- main: preflight first, pinned readers, guarded writes ---------------------------------

def test_main_runs_nothing_when_preflight_fails(monkeypatch):
    def fail():
        raise AssertionError("an input was opened after a failed preflight")

    def refuse(run=None):
        raise RuntimeError("Preflight failed; no hypothesis run")

    monkeypatch.setattr(run_guard, "preflight", refuse)
    monkeypatch.setattr(pin_inputs, "load_input", lambda *a, **k: fail())
    monkeypatch.setattr(pin_inputs, "enso_raw_path", lambda *a, **k: fail())
    monkeypatch.setattr(run_guard, "write_result", lambda *a, **k: fail())
    with pytest.raises(RuntimeError, match="Preflight failed"):
        rh.main("run1")
    with pytest.raises(SystemExit, match="run1, run2"):
        rh.main("results")


def test_main_reads_through_the_pinned_readers_and_writes_through_write_result(
        monkeypatch, tmp_path, tables, results):
    calls, written = [], {}
    for index, seed in (("RONI", 1), ("ONI", 2)):
        w = winters_table(seed)
        lines = ["SEAS  YR  ANOM"] + [f"DJF {y} {v:.2f}" for y, v in zip(w["year"], w["enso_djf"])]
        (tmp_path / f"{index.lower()}.txt").write_bytes(chr(10).join(lines).encode())

    def preflight(run=None):
        calls.append(("preflight", run))
        return {"commit": "abc123", "checked_utc": "now"}

    def load_input(name):
        calls.append(("load", name))
        return tables[{v: k for k, v in rh.INPUTS.items()}[name]]

    def write_result(table, name, run, inputs=(), commit=None):
        calls.append(("write", name))
        written[name] = (table, run, list(inputs), commit)
        return pin_inputs.ROOT / "results" / "tables" / run / name

    monkeypatch.setattr(run_guard, "preflight", preflight)
    monkeypatch.setattr(pin_inputs, "load_input", load_input)
    monkeypatch.setattr(pin_inputs, "enso_raw_path",
                        lambda index: (tmp_path / f"{index.lower()}.txt").resolve())
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(run_guard, "write_result", write_result)
    monkeypatch.setattr(rh, "compute_all", lambda t, w: rh_compute(t, w))
    rh.main("run9")
    assert calls[0] == ("preflight", "run9")
    assert [c[0] for c in calls[1:]] == ["load"] * 6 + ["write"] * 3
    assert set(written) == set(rh.OUTPUTS)
    table, run, inputs, commit = written["registered_tests.csv"]
    assert run == "run9" and commit == "abc123" and len(inputs) == 8
    pd.testing.assert_frame_equal(table, results["registered_tests.csv"])


rh_compute = lambda t, w, _f=rh.compute_all: _f(t, w, **DRAWS)  # noqa: E731


# --- the pinned ENSO reader (D82) -------------------------------------------------------

def test_enso_raw_path_checks_the_pin(monkeypatch, tmp_path):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    oni = raw / "oni.ascii.txt"
    oni.write_bytes(b"SEAS YR ANOM")
    pins = tmp_path / "pins.csv"
    monkeypatch.setattr(pin_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(pin_inputs, "ENSO_RAW", {"ONI": oni})
    monkeypatch.setattr(pin_inputs, "pinned_files", lambda: [oni])
    pd.DataFrame([{"path": "data/raw/oni.ascii.txt", "sha256": pin_inputs.sha256(oni)}]).to_csv(
        pins, index=False)
    assert pin_inputs.enso_raw_path("ONI", path=pins) == oni.resolve()
    with pytest.raises(pin_inputs.PinnedInputError, match="No pinned raw ENSO file"):
        pin_inputs.enso_raw_path("MEI", path=pins)
    oni.write_bytes(b"SEAS YR ANOM revised")
    with pytest.raises(pin_inputs.PinnedInputError, match="differs from its pin"):
        pin_inputs.enso_raw_path("ONI", path=pins)
