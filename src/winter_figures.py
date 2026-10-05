"""Regenerate the Phase 1 winter-precipitation figures without the notebook.

Writes to results/figures/, exactly as notebook 01 (cells 7-13) does:
  djf_precip_series_<index>.png      every winter per region, ENSO_INDEX
  djf_precip_series_oni_vs_roni.png  the same series classified by each index
  djf_precip_1997_98_pct_normal.png  winter 1997-98 as % of the all-winter mean

so results/ can be rebuilt from scratch by code alone (Phase 1 audit,
finding 7). Notebook 01 calls the same functions, one per figure, so the
figure code has one copy. Needs the ERA5-Land files, data/processed/regions.geojson and
data/processed/el_nino_winters.csv; the RONI table is downloaded once if it
is missing (download_oni.load_winters).

The map's extent and title wording follow notebook 01 unchanged; both are
open as D28.

Run:  python -m src.winter_figures
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import xarray as xr

from src import era5, figures
from src.config import DATA_PROCESSED, ENSO_INDEX, ENSO_INDEX_URLS

VALUE = "precip_djf_mm"
YLABEL = "DJF precipitation (mm)"
# The winter shown on the map: 1997-98, a strong El Niño (notebook 01, cell 10).
MAP_WINTER = 1998
MAP_TITLE = "Winter 1997-98 (Dec-Feb) precipitation, % of the 1950-2026 mean"
MAP_FILE = "djf_precip_1997_98_pct_normal.png"


def series_by_index(table: pd.DataFrame, winters: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """The precipitation table re-classified by each ENSO index (notebook cell 12)."""
    precip = table[["region", "year", "winter", VALUE]]
    return {name: precip.merge(w.drop(columns="winter"), on="year", how="left")
            for name, w in winters.items()}


def map_inputs(table: pd.DataFrame, datasets: dict[str, xr.Dataset],
               winter: int = MAP_WINTER) -> tuple[list[xr.DataArray], pd.Series]:
    """Per-domain grids and per-region values of one winter as % of the mean.

    Grids: each cell's winter total over its own all-winter mean. Regions:
    the regional (cos(latitude)-weighted) totals from `table`, same ratio.
    """
    pcts = []
    for ds in datasets.values():
        djf = era5.winter_total(ds["tp"]).compute()
        pcts.append(djf.sel(year=winter) / djf.mean("year") * 100)
    by_region = table.pivot(index="year", columns="region", values=VALUE)
    return pcts, by_region.loc[winter] / by_region.mean() * 100


def series_figure(table: pd.DataFrame, out_dir: Path = figures.FIGURES) -> Path:
    """Every winter per region, classified by ENSO_INDEX (notebook cell 8)."""
    return figures.winter_series(table, VALUE, YLABEL, ENSO_INDEX,
                                 out_dir / f"djf_precip_series_{ENSO_INDEX.lower()}.png")


def map_figure(table: pd.DataFrame, datasets: dict[str, xr.Dataset],
               regions: gpd.GeoDataFrame, out_dir: Path = figures.FIGURES
               ) -> tuple[Path, pd.Series]:
    """Winter MAP_WINTER as % of the mean (notebook cell 10); also returns the
    regional percentages shown on the map."""
    pcts, region_pct = map_inputs(table, datasets)
    out = figures.percent_of_normal_map(pcts, regions, region_pct, MAP_TITLE,
                                        out_dir / MAP_FILE)
    return out, region_pct


def comparison_figure(tables: dict[str, pd.DataFrame],
                      out_dir: Path = figures.FIGURES) -> Path:
    """The series classified by each index side by side (notebook cell 13);
    `tables` from series_by_index."""
    names = "_vs_".join(name.lower() for name in tables)
    return figures.winter_series_two_indices(tables, VALUE, YLABEL,
                                             out_dir / f"djf_precip_series_{names}.png")


def make_figures(regions: gpd.GeoDataFrame, datasets: dict[str, xr.Dataset],
                 winters: pd.DataFrame, by_index: dict[str, pd.DataFrame],
                 out_dir: Path = figures.FIGURES) -> list[Path]:
    """Build the three Phase 1 figures.

    `winters` is the ENSO_INDEX classification (data/processed/
    el_nino_winters.csv) behind the main table, the series and the map;
    `by_index` maps each index name to its classification for the
    comparison figure, in order (notebook cells 7 and 12).
    """
    table, _ = era5.build_winter_precip_table(regions, winters, datasets)
    return [series_figure(table, out_dir),
            map_figure(table, datasets, regions, out_dir)[0],
            comparison_figure(series_by_index(table, by_index), out_dir)]


def main() -> None:
    from src.download_oni import load_winters
    from src.regions import load_regions

    regions = load_regions()
    datasets = era5.open_domains(sorted(set(era5.assign_domains(regions)),
                                        key=list(era5.ERA5_DOMAINS).index))
    winters = pd.read_csv(DATA_PROCESSED / "el_nino_winters.csv")
    by_index = {name: load_winters(name) for name in ENSO_INDEX_URLS}
    for path in make_figures(regions, datasets, winters, by_index):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
