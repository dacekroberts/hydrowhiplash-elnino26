"""Smoke tests for src/figures.py helpers added after Phase 1."""
import pandas as pd

from src import figures


def test_winter_series_columns_writes_png(tmp_path):
    years = list(range(2000, 2006))
    table = pd.DataFrame({"region": "R", "year": years,
                          "phase": ["el_nino", "neutral"] * 3, "strong": [True] + [False] * 5,
                          "a": [90.0, 100, 110, None, 95, 105], "b": [80.0, 100, 120, 90, 95, 105]})
    out = figures.winter_series_columns(table, {"Stations": "a", "Grid": "b"}, "% of normal",
                                        "ONI", tmp_path / "x.png")
    assert out.exists() and out.stat().st_size > 0


def test_no_colour_is_typed_in_the_figure_code():
    """Every figure colour comes from theme/tokens.json."""
    import re
    from pathlib import Path

    source = Path(figures.__file__).read_text("utf-8")
    assert re.findall(r"#[0-9a-fA-F]{6}\b", source) == []
    assert '"white"' not in source
    assert figures.FAMILIES["fire"] == figures.theme.colour("fire")


def test_interval_ledger_and_coverage_write_png(tmp_path):
    rows = pd.DataFrame({"region": ["A", "B"], "estimate": [0.2, -0.5],
                         "ci_low": [-0.1, -0.9], "ci_high": [0.5, -0.1],
                         "significant": [False, True]})
    out = figures.interval_ledger([{"title": "T", "xlabel": "x", "family": "fire", "rows": rows}],
                                  tmp_path / "l.png", note="n")
    assert out.exists() and out.stat().st_size > 0
    cov = pd.DataFrame({"region": ["A", "B"] * 2, "method": ["one"] * 2 + ["two"] * 2,
                        "coverage": [0.8, 0.7, 0.9, 0.6], "n": [40, 41, 20, 21]})
    out = figures.coverage_dots(cov, 0.8, tmp_path / "c.png")
    assert out.exists() and out.stat().st_size > 0


def test_headline_figures_draw_every_registered_row(tmp_path):
    """Synthetic run tables: each headline figure is written, and the rows
    handed to the ledger are all the registered rows of the test."""
    from src import results_figures as rf

    regions = ["PNW", "BC", "AB", "NorCal", "SoCal"]
    def block(test, names):
        return pd.DataFrame({"test": test, "region": names, "estimate": 0.1, "ci_low": -0.2,
                             "ci_high": 0.4, "significant": False})
    reg = pd.concat([block(t, regions[::-1]) for t in ("H1", "H2", "H3a", "H3b")]
                    + [block("H4", ["PNW/BC/AB minus SoCal"])], ignore_index=True)
    assert list(rf._rows(reg, "H3a")["region"]) == regions  # display order, none dropped
    val = pd.DataFrame({"model": "H3a", "region": regions * 2,
                        "method": ["leave-one-year-out"] * 5 + ["expanding window"] * 5,
                        "coverage": 0.8, "n": 40})
    for path in [rf.headline1(reg, tmp_path, "runX"), rf.headline2(reg, tmp_path, "runX"),
                 rf.headline3(reg, tmp_path, "runX"), rf.headline4(val, tmp_path)]:
        assert path.exists() and path.stat().st_size > 0


def test_history_html_is_one_fragment_with_every_season(tmp_path):
    from src import fire_figures
    from src.config import FIRE_LAST_YEAR_BY_REGION, FORECAST_YEAR

    rows = []
    for region in ("PNW", "BC"):
        for year in range(2000, 2006):
            rows.append({"region": region, "year": year, "phase": "el_nino" if year % 2 else "neutral",
                         "strong": year == 2001, "log_burn": 0.0 if year == 2002 else 10.0 + year % 3,
                         "burn_ha": 0.0 if year == 2002 else 5000.0, "enso_djf": 0.6,
                         "zero_fire": year == 2002})
    assert max(FIRE_LAST_YEAR_BY_REGION.values()) < FORECAST_YEAR  # the 2027 slot stays empty
    out = fire_figures.history_html(pd.DataFrame(rows), tmp_path)
    text = out.read_text("utf-8")
    assert text.lstrip().startswith("<div") and "<html" not in text
    assert 'id="season-history"' in text
    # plotly escapes < and > inside its JSON
    assert text.count("\\u003e2003\\u003c") == 2 and "no fire of" in text
    assert b"\r\n" not in out.read_bytes()


def _fire_table():
    years = list(range(2000, 2006))
    return pd.DataFrame({"region": "R", "year": years,
                         "phase": ["el_nino", "neutral"] * 3, "strong": [True] + [False] * 5,
                         "log_burn": [10.0, 12.0, 0.0, 11.0, 9.0, 13.0],
                         "zero_fire": [False, False, True, False, False, False]})


def test_season_anomaly_is_centred_on_seasons_with_fire():
    out = figures.season_anomaly(_fire_table())
    assert pd.isna(out.loc[2, "anomaly"])  # the zero-fire season is a marker, not a bar
    assert abs(out["anomaly"].sum()) < 1e-9  # mean of the 5 seasons with fire is 11
    assert out.loc[0, "anomaly"] == -1.0 and out.loc[5, "anomaly"] == 2.0


def test_fire_season_series_writes_png(tmp_path):
    out = figures.fire_season_series(pd.concat([_fire_table(), _fire_table().assign(region="S")]),
                                     "RONI", tmp_path / "f.png")
    assert out.exists() and out.stat().st_size > 0


def test_themed_switches_every_colour_and_returns(tmp_path):
    """Inside themed("dark") the constants, the families and the saved file's
    name are the dark theme's; afterwards everything is the first theme's."""
    light, dark = figures.theme.colours("light"), figures.theme.colours("dark")
    out = tmp_path / "c.png"
    cov = pd.DataFrame({"region": ["A", "B"], "method": "leave-one-year-out",
                        "coverage": 0.8, "n": 40})
    with figures.themed("dark"):
        assert (figures.INK, figures.GROUND) == (dark["ink"], dark["surface"])
        assert figures.FAMILIES["fire"] == dark["fire"]
        assert figures.themed_path(out).name == "c_dark.png"
        assert figures.coverage_dots(cov, 0.8, out).name == "c_dark.png"
    assert (figures.INK, figures.GROUND) == (light["ink"], light["surface"])
    assert figures.FAMILIES["fire"] == light["fire"]
    assert figures.themed_path(out) == out and not out.exists()
    assert (tmp_path / "c_dark.png").stat().st_size > 0


def test_narrow_ledger_stacks_its_panels_on_a_phone_wide_canvas(tmp_path):
    from matplotlib.image import imread

    rows = pd.DataFrame({"region": ["PNW", "BC"], "estimate": [0.1, -0.2], "ci_low": [-0.3, -0.6],
                         "ci_high": [0.5, 0.2], "significant": [True, False]})
    panels = [{"title": "A long title that has to wrap on a phone", "xlabel": "x", "family": f,
               "rows": rows} for f in ("water", "fire")]
    wide = figures.interval_ledger(panels, tmp_path / "t.png", "note")
    thin = figures.interval_ledger(panels, tmp_path / "t.png", "note", narrow=True)
    assert thin.name == "t_narrow.png" and wide.name == "t.png"
    (wh, ww), (th, tw) = imread(wide).shape[:2], imread(thin).shape[:2]
    assert tw < 0.45 * ww and th > wh           # under half the width, and taller: stacked
    assert tw <= figures.NARROW_WIDTH_IN * 200 * 1.15


def test_narrow_coverage_chart_is_drawn_on_a_phone_wide_canvas(tmp_path):
    from PIL import Image
    table = pd.DataFrame({"region": ["A", "B", "A", "B"], "coverage": [0.8, 0.7, 0.9, 0.6],
                          "method": ["leave-one-year-out"] * 2 + ["expanding window"] * 2,
                          "n": [40, 40, 20, 20]})
    wide = figures.coverage_dots(table, 0.8, tmp_path / "c.png")
    thin = figures.coverage_dots(table, 0.8, tmp_path / "c.png", narrow=True)
    assert thin.name == "c_narrow.png" and wide.name == "c.png"
    with Image.open(thin) as a, Image.open(wide) as b:
        assert a.width < 0.6 * b.width

