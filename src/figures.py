"""Figures written to results/figures/ by code (never by hand).

Colours: other winters are neutral context; El Nino winters orange, strong
ones a darker orange step with a year label, so identity never rests on
colour alone. Palette checked with the dataviz validator (2026-10-04):
orange pair CVD delta E 16.8, normal-vision 20.4.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import patheffects
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

from src.config import EL_NINO_THRESHOLD, RESULTS, STRONG_THRESHOLD

FIGURES = RESULTS / "figures"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
OTHER, NINO, STRONG = "#c3c2b7", "#eb6834", "#9a3412"
# Diverging: dry red, neutral grey at normal, wet blue.
DRY_WET = LinearSegmentedColormap.from_list(
    "dry_wet", ["#a8302f", "#e34948", "#f0efec", "#2a78d6", "#1c4f91"])

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
})


def _bar_colours(g: pd.DataFrame) -> list[str]:
    return [STRONG if s else NINO if p == "el_nino" else OTHER
            for p, s in zip(g["phase"], g["strong"])]


def _winter_label(year: int) -> str:
    return f"{year - 1}-{year % 100:02d}"


def _series_panel(ax, g: pd.DataFrame, value: str, ylabel: str, title: str,
                  signed: bool = False) -> None:
    """Bars per winter. `signed` values (e.g. a standardised index) get a
    zero baseline and symmetric limits; labels sit beyond each bar's end."""
    ax.bar(g["year"], g[value], width=0.8, color=_bar_colours(g), linewidth=0)
    mean = g[value].mean()
    ax.axhline(mean, color=INK, lw=1, ls=(0, (4, 3)))
    if signed:
        ax.axhline(0, color=MUTED, lw=0.8)
    for _, r in g[g["strong"] & (g["phase"] == "el_nino")].iterrows():
        below = signed and r[value] < 0
        ax.annotate(_winter_label(int(r["year"])), (r["year"], r[value]),
                    xytext=(0, -2 if below else 2), textcoords="offset points", ha="center",
                    va="top" if below else "bottom", fontsize=7, color=INK, zorder=4,
                    path_effects=[patheffects.withStroke(linewidth=1.5, foreground="white")])
    ax.set_title(title, loc="left", fontsize=10, color=INK, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=8)
    if signed:
        lim = np.nanmax(np.abs(g[value])) * 1.2
        ax.set_ylim(-lim, lim)
    else:
        ax.set_ylim(0, g[value].max() * 1.15)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)


def _legend(fig, index: str) -> None:
    handles = [Patch(color=OTHER, label="Other winters"),
               Patch(color=NINO, label=f"El Niño (DJF {index} ≥ {EL_NINO_THRESHOLD})"),
               Patch(color=STRONG, label=f"Strong El Niño (≥ {STRONG_THRESHOLD}), labelled"),
               plt.Line2D([], [], color=INK, lw=1, ls=(0, (4, 3)), label="Mean of all winters")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, 0.995))


def winter_series(table: pd.DataFrame, value: str, ylabel: str, index: str,
                  out: Path, signed: bool = False, xlabel: str | None = None) -> Path:
    """One panel per region, every winter shown, El Nino winters highlighted.

    `signed` for values centred on zero; `xlabel` replaces the default axis
    note (e.g. when the value spans winter and the following summer)."""
    regions = list(dict.fromkeys(table["region"]))
    fig, axes = plt.subplots(len(regions), 1, figsize=(10, 2.1 * len(regions)), sharex=True)
    for ax, region in zip(axes, regions):
        g = table[table["region"] == region].sort_values("year")
        _series_panel(ax, g, value, ylabel, region, signed=signed)
    years = table["year"]
    ticks = range(int(np.ceil(years.min() / 10) * 10), int(years.max()) + 1, 10)
    axes[-1].set_xticks(list(ticks), [_winter_label(t) for t in ticks])
    axes[-1].set_xlabel(xlabel or "Winter (Dec-Feb); fire season paired with each winter is the "
                        "later year", fontsize=8)
    _legend(fig, index)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return _save(fig, out)


def winter_series_two_indices(tables: dict[str, pd.DataFrame], value: str, ylabel: str,
                              out: Path) -> Path:
    """Same series classified by two ENSO indices, side by side per region."""
    names = list(tables)
    first = tables[names[0]]
    regions = list(dict.fromkeys(first["region"]))
    fig, axes = plt.subplots(len(regions), len(names), figsize=(14, 2.1 * len(regions)),
                             sharex=True, sharey="row")
    for i, region in enumerate(regions):
        for j, name in enumerate(names):
            g = tables[name]
            g = g[g["region"] == region].sort_values("year")
            _series_panel(axes[i, j], g, value, ylabel if j == 0 else "",
                          f"{region} · classified by {name}")
    years = first["year"]
    ticks = range(int(np.ceil(years.min() / 10) * 10), int(years.max()) + 1, 10)
    for ax in axes[-1]:
        ax.set_xticks(list(ticks), [_winter_label(t) for t in ticks])
    _legend(fig, " / ".join(names))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return _save(fig, out)


def percent_of_normal_map(pcts: list[xr.DataArray], regions: gpd.GeoDataFrame,
                          region_pct: pd.Series, title: str, out: Path,
                          extent: tuple[float, float, float, float] = (-169, -109, 32, 71.5)
                          ) -> Path:
    """Map of one winter's precipitation as % of the baseline mean.

    `pcts` holds one grid per download domain; overlapping cells hold the same
    values, so drawing order doesn't matter. Colours are on a log2 scale so
    50% and 200% sit equally far from 100%. `extent` is (W, E, S, N).
    """
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    west, east, south, north = extent
    proj = ccrs.LambertConformal(central_longitude=(west + east) / 2,
                                 standard_parallels=(south + 8, north - 8))
    fig = plt.figure(figsize=(9, 8.6))
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    ax.set_extent(list(extent), crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor="#f7f7f5", zorder=0)
    for pct in pcts:
        mesh = ax.pcolormesh(pct["longitude"], pct["latitude"], np.log2(pct / 100),
                             cmap=DRY_WET, vmin=-2, vmax=2, shading="nearest",
                             transform=ccrs.PlateCarree(), rasterized=True)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor=MUTED, lw=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), edgecolor=GRID, lw=0.4)
    ax.add_geometries(regions.geometry, crs=ccrs.PlateCarree(), facecolor="none",
                      edgecolor=INK, lw=1.0)
    for _, r in regions.iterrows():
        pt = r.geometry.representative_point()
        ax.text(pt.x, pt.y, f"{r['region']}\n{region_pct[r['region']]:.0f}%",
                transform=ccrs.PlateCarree(), ha="center", va="center", fontsize=9,
                color=INK, fontweight="bold",
                bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none", "alpha": 0.8})
    cb = fig.colorbar(mesh, ax=ax, orientation="horizontal", fraction=0.04, pad=0.03,
                      ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_xticklabels(["25%", "50%", "100%", "200%", "400%"], fontsize=8)
    cb.set_label("Winter precipitation as % of the 1950-51 to 2025-26 mean "
                 "(region labels: regional totals)", fontsize=8)
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    return _save(fig, out)


def _save(fig, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out
