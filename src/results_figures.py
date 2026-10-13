"""Site charts for Headlines 1 to 4 (ACTION_PLAN Phase 4), from the registered run.

Writes to results/figures/:
  headline1_el_nino_vs_rest.png   H1 and H2: El Nino years against the rest,
      winter precipitation and burned area, per region
  headline2_enso_strength.png     H3a and H3b: burned area on the winter
      index, without and with summer temperature, per region
  headline3_north_vs_socal.png    H4: the pooled contrast, with the regional
      H3a slopes it summarises above it
  headline4_interval_coverage.png how often the H3a model's past prediction
      intervals held the real season

Reads only the committed tables of one run folder (RUN), never a polygon
and never data/. Nothing here is a test or changes a number: each mark is a
row of registered_tests.csv or validation.csv as written. Every registered
row of a hypothesis is drawn, null results at the same size.

Run:  python -m src.results_figures
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import figures, theme
from src.config import PREDICTION_ALPHA, REGIONS, RESULTS

RUN = "run1"
LOG_POINTS = "log points of burned area"


def _run_dir(run: str) -> Path:
    return RESULTS / "tables" / run


def _rows(reg: pd.DataFrame, test: str) -> pd.DataFrame:
    """The registered rows of one test, regions in display order."""
    rows = reg[reg["test"] == test]
    if rows.empty:
        raise ValueError(f"No registered rows for {test}.")
    order = {region: i for i, region in enumerate(REGIONS)}
    return rows.sort_values("region", key=lambda s: s.map(order).fillna(len(order)),
                            kind="stable").reset_index(drop=True)


def headline1(reg: pd.DataFrame, out_dir: Path, run: str, narrow: bool = False) -> Path:
    panels = [
        {"title": "H1 · Winter precipitation, El Niño winters minus the rest",
         "xlabel": "mm of December to February precipitation", "family": "water",
         "rows": _rows(reg, "H1")},
        {"title": "H2 · Burned area, seasons after El Niño minus the rest",
         "xlabel": LOG_POINTS, "family": "fire", "rows": _rows(reg, "H2")},
    ]
    return figures.interval_ledger(panels, out_dir / "headline1_el_nino_vs_rest.png", _note(run),
                                   narrow)


def headline2(reg: pd.DataFrame, out_dir: Path, run: str, narrow: bool = False) -> Path:
    panels = [
        {"title": "H3a · Burned area per 1 °C of the winter index, trend only",
         "xlabel": f"{LOG_POINTS} per 1 °C", "family": "fire", "rows": _rows(reg, "H3a")},
        {"title": "H3b · The same with summer temperature held fixed",
         "xlabel": f"{LOG_POINTS} per 1 °C", "family": "fire", "rows": _rows(reg, "H3b")},
    ]
    return figures.interval_ledger(panels, out_dir / "headline2_enso_strength.png", _note(run),
                                   narrow)


def headline3(reg: pd.DataFrame, out_dir: Path, run: str, narrow: bool = False) -> Path:
    """The H4 contrast under the H3a slopes of the regions it pools, on one
    scale. The H3a rows are per-region fits; the contrast comes from one
    pooled model, so it is not their arithmetic difference."""
    contrast = _rows(reg, "H4")
    pooled = [name.strip() for name in
              contrast["region"].iloc[0].replace(" minus ", "/").split("/")]
    slopes = _rows(reg, "H3a")
    slopes = slopes[slopes["region"].isin(pooled)]
    rows = pd.concat([slopes.assign(region=slopes["region"] + " (H3a slope)"),
                      contrast.assign(region="North minus SoCal (H4)")], ignore_index=True)
    panels = [{"title": "H4 · Does the north respond differently from Southern California?",
               "xlabel": f"{LOG_POINTS} per 1 °C of the winter index", "family": "fire",
               "rows": rows}]
    return figures.interval_ledger(panels, out_dir / "headline3_north_vs_socal.png", _note(run),
                                   narrow)


def headline4(val: pd.DataFrame, out_dir: Path, narrow: bool = False) -> Path:
    table = val[val["model"] == "H3a"]
    order = {region: i for i, region in enumerate(REGIONS)}
    table = table.sort_values("region", key=lambda s: s.map(order), kind="stable")
    return figures.coverage_dots(table, 1 - PREDICTION_ALPHA,
                                 out_dir / "headline4_interval_coverage.png", narrow)


def _note(run: str) -> str:
    return (f"Registered tests, {run}. Intervals are two-sided 95%; the verdict is the Holm "
            "correction within each hypothesis's family.")


def make_figures(run: str = RUN, out_dir: Path = figures.FIGURES) -> list[Path]:
    reg = pd.read_csv(_run_dir(run) / "registered_tests.csv")
    val = pd.read_csv(_run_dir(run) / "validation.csv")
    paths = []
    for name in theme.themes():  # one file per theme; the site shows the matching one
        with figures.themed(name):
            paths += [headline1(reg, out_dir, run), headline2(reg, out_dir, run),
                      headline3(reg, out_dir, run), headline4(val, out_dir)]
            # the phone's drawings: the three ledgers with panels stacked,
            # the coverage chart on a narrow canvas
            paths += [draw(reg, out_dir, run, narrow=True)
                      for draw in (headline1, headline2, headline3)]
            paths.append(headline4(val, out_dir, narrow=True))
    return paths


def main() -> None:
    for path in make_figures():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
