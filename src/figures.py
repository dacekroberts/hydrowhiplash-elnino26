"""Figures written to results/figures/ by code (never by hand).

Colours come from theme/tokens.json through src.theme (D86), drawn on the
`surface` ground: the light theme unless a figure is drawn inside
`themed("dark")`, which writes a second file beside the first for the
site's dark mode (owner, 2026-10-13). A bar takes the colour of what it measures
(`fire` burned area, `water` precipitation and winter moisture, `snow`
snowpack). Every season is drawn; a season after an El Nino winter gets an
`enso-soft` band and an `enso` tick, a strong one an `enso-strong` tick and
its year label, so identity never rests on colour alone. The
percent-of-normal map runs from dry earth to wet blue (`precip-dry-2` to
`precip-wet-2`); red is not used for dryness.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import patheffects
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

from src import theme
from src.config import EL_NINO_THRESHOLD, FIGURE_CREDIT, RESULTS, STRONG_THRESHOLD

FIGURES = RESULTS / "figures"
# Module constant to colour token. The values are set by _set_theme: the
# first theme (light) at import, another inside themed().
COLOUR_TOKENS = {"INK": "ink", "MUTED": "ink-muted", "GRID": "rule", "AXIS": "rule-strong",
                 "GROUND": "surface", "ENSO": "enso", "ENSO_STRONG": "enso-strong",
                 "ENSO_SOFT": "enso-soft", "VERDICT": "evergreen"}
# What a bar or an interval measures; one colour family per kind of data.
FAMILY_TOKENS = ("fire", "water", "snow")
THEME = theme.themes()[0]
FAMILIES: dict[str, str] = {}


def _set_theme(name: str) -> None:
    """Point every colour constant of this module, and matplotlib's
    defaults, at theme `name`. Drawing code reads the constants when it
    runs, so this takes effect for every figure drawn afterwards,
    src.interactive's included."""
    values = theme.colours(name)
    globals().update({const: values[token] for const, token in COLOUR_TOKENS.items()})
    FAMILIES.clear()
    FAMILIES.update({token: values[token] for token in FAMILY_TOKENS})
    globals()["THEME"] = name
    plt.rcParams.update({
        "axes.edgecolor": AXIS, "axes.labelcolor": INK, "xtick.color": MUTED,
        "ytick.color": MUTED, "axes.facecolor": GROUND, "figure.facecolor": GROUND,
        "text.color": INK,
    })


@contextmanager
def themed(name: str):
    """Draw in theme `name` inside the block, then return to the theme
    before it. A figure saved inside a block of any theme but the first is
    written beside the first's file (themed_path)."""
    before = THEME
    _set_theme(name)
    try:
        yield
    finally:
        _set_theme(before)


def themed_path(out: Path) -> Path:
    """`out` in the first theme; `<stem>_<theme><suffix>` in any other."""
    if THEME == theme.themes()[0]:
        return out
    return out.with_name(f"{out.stem}_{THEME}{out.suffix}")


# Diverging, for precipitation as a share of normal: dry earth, neutral at
# normal, wet blue. Red is kept for burned area.
DRY_WET = LinearSegmentedColormap.from_list(
    "dry_wet", [theme.colour(f"precip-{step}")
                for step in ("dry-2", "dry-1", "mid", "wet-1", "wet-2")])


def _font_stack(role: str) -> list[str]:
    """The design typeface of `role`, then the system sans fallbacks, keeping
    only faces whose font files are installed (matplotlib warns on every
    text draw for a missing one). DejaVu Sans ships with matplotlib."""
    from matplotlib import font_manager

    # The files bundled in site/fonts are variable fonts. Matplotlib draws a
    # variable font at its default weight only (Public Sans: thin), so they
    # are not registered here; a static Regular and Bold would be needed.
    design = theme.families()[role].split(",")[0].strip().strip('"')
    installed = {font.name for font in font_manager.fontManager.ttflist}
    return [name for name in (design, "Segoe UI", "Helvetica", "Arial")
            if name in installed] + ["DejaVu Sans"]


DISPLAY_FONT = _font_stack("display")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": _font_stack("sans"),
    "axes.spines.top": False, "axes.spines.right": False,
})
_set_theme(THEME)


def _family(name: str) -> str:
    if name not in FAMILIES:
        raise ValueError(f"No colour family {name!r}; choose from {sorted(FAMILIES)}.")
    return FAMILIES[name]


def _title(ax, text: str) -> None:
    ax.set_title(text, loc="left", fontsize=10, color=INK, fontweight="bold",
                 fontfamily=DISPLAY_FONT)


def _mark_enso(ax, g: pd.DataFrame) -> None:
    """Band and tick for each season after an El Nino winter: `enso-soft`
    behind the bar, a tick on the panel's top edge, darker and longer for a
    strong winter."""
    for _, r in g[g["phase"] == "el_nino"].iterrows():
        strong = bool(r["strong"])
        ax.axvspan(r["year"] - 0.5, r["year"] + 0.5, color=ENSO_SOFT, lw=0, zorder=0)
        ax.plot([r["year"]] * 2, [0.9 if strong else 0.94, 1.0],
                transform=ax.get_xaxis_transform(), color=ENSO_STRONG if strong else ENSO,
                lw=2.4 if strong else 1.6, solid_capstyle="butt", zorder=3, clip_on=False)


def _year_label(ax, text: str, x: float, y: float, below: bool) -> None:
    ax.annotate(text, (x, y), xytext=(0, -2 if below else 2), textcoords="offset points",
                ha="center", va="top" if below else "bottom", fontsize=7, color=INK, zorder=4,
                path_effects=[patheffects.withStroke(linewidth=1.5, foreground=GROUND)])


def _winter_label(year: int) -> str:
    return f"{year - 1}-{year % 100:02d}"


def _series_panel(ax, g: pd.DataFrame, value: str, ylabel: str, title: str,
                  signed: bool = False, family: str = "water") -> None:
    """Bars per winter in the colour of `family`. `signed` values (e.g. a
    standardised index) get a zero baseline and symmetric limits; labels sit
    beyond each bar's end."""
    _mark_enso(ax, g)
    ax.bar(g["year"], g[value], width=0.8, color=_family(family), linewidth=0, zorder=2)
    mean = g[value].mean()
    ax.axhline(mean, color=INK, lw=1, ls=(0, (4, 3)), zorder=3)
    if signed:
        ax.axhline(0, color=AXIS, lw=0.8)
    for _, r in g[g["strong"] & (g["phase"] == "el_nino")].iterrows():
        _year_label(ax, _winter_label(int(r["year"])), r["year"], r[value],
                    signed and r[value] < 0)
    _title(ax, title)
    ax.set_ylabel(ylabel, fontsize=8)
    if signed:
        lim = np.nanmax(np.abs(g[value])) * 1.2
        ax.set_ylim(-lim, lim)
    else:
        ax.set_ylim(0, g[value].max() * 1.15)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)


def _legend(fig, index: str, family: str = "water", every: str = "Every winter",
            nino: str = "El Niño", strong: str = "Strong El Niño",
            mean: str = "Mean of all winters") -> None:
    handles = [Patch(color=_family(family), label=every),
               Patch(facecolor=ENSO_SOFT, edgecolor=ENSO, lw=1.6,
                     label=f"{nino} (DJF {index} ≥ {EL_NINO_THRESHOLD}): band and tick"),
               Patch(facecolor=ENSO_SOFT, edgecolor=ENSO_STRONG, lw=2.4,
                     label=f"{strong} (≥ {STRONG_THRESHOLD}): darker tick, labelled"),
               plt.Line2D([], [], color=INK, lw=1, ls=(0, (4, 3)), label=mean)]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, 0.995))


def winter_series(table: pd.DataFrame, value: str, ylabel: str, index: str,
                  out: Path, signed: bool = False, xlabel: str | None = None,
                  family: str = "water") -> Path:
    """One panel per region, every winter shown, El Nino winters highlighted.

    `signed` for values centred on zero; `xlabel` replaces the default axis
    note (e.g. when the value spans winter and the following summer);
    `family` is what the bars measure ("water" or "snow")."""
    regions = list(dict.fromkeys(table["region"]))
    fig, axes = plt.subplots(len(regions), 1, figsize=(10, 2.1 * len(regions)), sharex=True)
    for ax, region in zip(axes, regions):
        g = table[table["region"] == region].sort_values("year")
        _series_panel(ax, g, value, ylabel, region, signed=signed, family=family)
    years = table["year"]
    ticks = range(int(np.ceil(years.min() / 10) * 10), int(years.max()) + 1, 10)
    axes[-1].set_xticks(list(ticks), [_winter_label(t) for t in ticks])
    axes[-1].set_xlabel(xlabel or "Winter (Dec-Feb); fire season paired with each winter is the "
                        "later year", fontsize=8)
    _legend(fig, index, family)
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
    ax.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor=theme.colour("page"), zorder=0)
    for pct in pcts:
        mesh = ax.pcolormesh(pct["longitude"], pct["latitude"], np.log2(pct / 100),
                             cmap=DRY_WET, vmin=-2, vmax=2, shading="nearest",
                             transform=ccrs.PlateCarree(), rasterized=True)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor=AXIS, lw=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), edgecolor=GRID, lw=0.4)
    ax.add_geometries(regions.geometry, crs=ccrs.PlateCarree(), facecolor="none",
                      edgecolor=INK, lw=1.0)
    for _, r in regions.iterrows():
        pt = r.geometry.representative_point()
        ax.text(pt.x, pt.y, f"{r['region']}\n{region_pct[r['region']]:.0f}%",
                transform=ccrs.PlateCarree(), ha="center", va="center", fontsize=9,
                color=INK, fontweight="bold",
                bbox={"boxstyle": "round,pad=0.25", "fc": GROUND, "ec": "none", "alpha": 0.85})
    cb = fig.colorbar(mesh, ax=ax, orientation="horizontal", fraction=0.04, pad=0.03,
                      ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_xticklabels(["25%", "50%", "100%", "200%", "400%"], fontsize=8)
    cb.set_label("Winter precipitation as % of the 1950-51 to 2025-26 mean "
                 "(region labels: regional totals)", fontsize=8)
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold",
                 fontfamily=DISPLAY_FONT)
    return _save(fig, out)


def winter_series_columns(table: pd.DataFrame, columns: dict[str, str], ylabel: str,
                          index: str, out: Path, xlabel: str | None = None,
                          family: str = "snow") -> Path:
    """Several series side by side per region on a shared y scale, e.g.
    station index | ERA5-Land; `columns` maps a column title to a value
    column. Winters with no value in a column are left blank there."""
    names = list(columns)
    regions = list(dict.fromkeys(table["region"]))
    fig, axes = plt.subplots(len(regions), len(names), figsize=(14, 2.1 * len(regions)),
                             sharex=True, sharey="row", squeeze=False)
    for i, region in enumerate(regions):
        g = table[table["region"] == region].sort_values("year")
        for j, name in enumerate(names):
            _series_panel(axes[i, j], g.dropna(subset=[columns[name]]), columns[name],
                          ylabel if j == 0 else "", f"{region} · {name}", family=family)
        top = np.nanmax(g[list(columns.values())].to_numpy()) * 1.15
        axes[i, 0].set_ylim(0, top)
    years = table["year"]
    ticks = range(int(np.ceil(years.min() / 10) * 10), int(years.max()) + 1, 10)
    for ax in axes[-1]:
        ax.set_xticks(list(ticks), [_winter_label(t) for t in ticks])
        ax.set_xlabel(xlabel or "Winter (Dec-Feb); April 1 of the later year", fontsize=8)
    _legend(fig, index, family)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return _save(fig, out)


def season_anomaly(table: pd.DataFrame, value: str = "log_burn",
                   flag: str = "zero_fire") -> pd.DataFrame:
    """`table` with `anomaly`: `value` minus the region's mean over its
    seasons with a counted fire. Raw values, not detrended (trend rule:
    raw values in figures). Zero-fire seasons get NaN: log(1 + 0) = 0 sits
    about 10 log points under any season with a fire and is drawn as a
    marker instead of a bar."""
    out = table.copy()
    burned = ~out[flag].astype(bool)
    means = out[burned].groupby("region")[value].mean()
    out["anomaly"] = (out[value] - out["region"].map(means)).where(burned)
    return out


def fire_season_series(table: pd.DataFrame, index: str, out: Path) -> Path:
    """One panel per region, every fire season shown as its departure from
    the region's mean log burned area, seasons after an El Nino winter
    highlighted. The right axis gives the same departure as a multiple of
    the region's typical (geometric mean) burned area."""
    table = season_anomaly(table)
    regions = list(dict.fromkeys(table["region"]))
    fig, axes = plt.subplots(len(regions), 1, figsize=(10, 2.1 * len(regions)), sharex=True)
    for ax, region in zip(axes, regions):
        g = table[table["region"] == region].sort_values("year")
        _mark_enso(ax, g)
        ax.bar(g["year"], g["anomaly"], width=0.8, color=_family("fire"), linewidth=0, zorder=2)
        ax.axhline(0, color=INK, lw=1, ls=(0, (4, 3)), zorder=3)
        lim = np.nanmax(np.abs(g["anomaly"])) * 1.25
        ax.set_ylim(-lim, lim)
        for _, r in g[g["strong"] & (g["phase"] == "el_nino") & g["anomaly"].notna()].iterrows():
            _year_label(ax, str(int(r["year"])), r["year"], r["anomaly"], r["anomaly"] < 0)
        for _, r in g[g["anomaly"].isna()].iterrows():
            ax.plot(r["year"], -lim * 0.9, marker="v", color=MUTED, ms=5, zorder=4)
            ax.annotate("no fire of 405 ha or more", (r["year"], -lim * 0.9), xytext=(6, 0),
                        textcoords="offset points", va="center", fontsize=7, color=MUTED)
        typical = np.expm1(g.loc[g["anomaly"].notna(), "log_burn"].mean())
        _title(ax, f"{region} · typical season {typical:,.0f} ha")
        ax.set_ylabel("log burned area,\ndeparture from mean", fontsize=8)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=8)
        right = ax.secondary_yaxis("right", functions=(lambda v: v / np.log(10),
                                                       lambda v: v * np.log(10)))
        decades = range(int(np.ceil(-lim / np.log(10))), int(np.floor(lim / np.log(10))) + 1)
        right.set_yticks(list(decades), [f"×{10.0 ** d:g}" for d in decades])
        right.tick_params(labelsize=7, colors=MUTED)
        right.spines["right"].set_visible(False)
    axes[-1].set_xlabel("Fire season (paired with the winter that ends in the same year; "
                        "California seasons run June to January)", fontsize=8)
    _legend(fig, index, "fire", every="Every fire season", nino="After an El Niño winter",
            strong="After a strong one", mean="Region's mean")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return _save(fig, out)


def interval_ledger(panels: list[dict], out: Path, note: str | None = None) -> Path:
    """A hypothesis as a ledger: one row per region, the estimate and its 95%
    interval on a scale shared within the panel, a line at no effect.

    Each panel is a dict: `title`, `xlabel`, `family` (what the outcome
    measures) and `rows`, a table with `region`, `estimate`, `ci_low`,
    `ci_high` and `significant` (the Holm verdict). The verdict is carried
    by form as well as colour: a filled dot for significant after Holm, a
    hollow one for not. Null results are drawn at the same size."""
    n_rows = max(len(p["rows"]) for p in panels)
    fig, axes = plt.subplots(1, len(panels), figsize=(4.9 * len(panels), 0.42 * n_rows + 1.7),
                             squeeze=False)
    for ax, panel in zip(axes[0], panels):
        rows = panel["rows"].reset_index(drop=True)
        colour = _family(panel["family"])
        ax.axvline(0, color=AXIS, lw=1.2, zorder=1)
        for i, r in rows.iterrows():
            ax.plot([r["ci_low"], r["ci_high"]], [i, i], color=colour, lw=4,
                    solid_capstyle="butt", zorder=2)
            passed = r["significant"] == True  # noqa: E712  (the column may hold NaN)
            ax.plot(r["estimate"], i, marker="o", ms=7.5, mew=1.6, zorder=3,
                    mfc=VERDICT if passed else GROUND, mec=VERDICT if passed else INK)
        ax.set_yticks(range(len(rows)), rows["region"], fontsize=9, color=INK)
        ax.set_ylim(len(rows) - 0.4, -0.6)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", labelsize=8)
        ax.spines["left"].set_visible(False)
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.set_xlabel(panel["xlabel"], fontsize=8)
        _title(ax, panel["title"])
    handles = [plt.Line2D([], [], color=MUTED, lw=4, label="95% interval"),
               plt.Line2D([], [], ls="", marker="o", ms=7.5, mew=1.6, mfc=VERDICT, mec=VERDICT,
                          label="Estimate, significant after Holm"),
               plt.Line2D([], [], ls="", marker="o", ms=7.5, mew=1.6, mfc=GROUND, mec=INK,
                          label="Estimate, not significant"),
               plt.Line2D([], [], color=AXIS, lw=1.2, label="No effect")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, 1.0))
    if note:
        fig.text(0.01, 0.0, note, fontsize=7.5, color=MUTED, va="bottom", ha="left")
    fig.tight_layout(rect=(0, 0.04 if note else 0, 1, 0.92))
    return _save(fig, out)


def coverage_dots(table: pd.DataFrame, target: float, out: Path) -> Path:
    """How often past prediction intervals held the real season. One row per
    region, one marker per `method` in `table` (columns `region`, `method`,
    `coverage`, `n`), a line at the `target` share."""
    regions = list(dict.fromkeys(table["region"]))
    methods = list(dict.fromkeys(table["method"]))
    markers = ["o", "D", "s"]
    fig, ax = plt.subplots(figsize=(7.2, 0.42 * len(regions) + 1.7))
    ax.axvline(100 * target, color=AXIS, lw=1.2, zorder=1)
    for j, method in enumerate(methods):
        g = table[table["method"] == method].set_index("region").reindex(regions)
        ax.plot(100 * g["coverage"], range(len(regions)), ls="", marker=markers[j], ms=7.5,
                mew=1.6, mfc=_family("fire") if j == 0 else GROUND, mec=_family("fire"),
                zorder=3, label=f"{method.capitalize()} ({int(g['n'].min())} to "
                                f"{int(g['n'].max())} seasons predicted)")
    ax.plot([], [], color=AXIS, lw=1.2, label=f"Target: {100 * target:.0f}%")
    ax.set_yticks(range(len(regions)), regions, fontsize=9, color=INK)
    ax.set_ylim(len(regions) - 0.4, -0.6)
    ax.set_xlim(40, 100)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel(f"Seasons whose burned area fell inside the {100 * target:.0f}% prediction "
                  "interval (%)", fontsize=8)
    fig.legend(loc="upper center", ncol=1, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.84))
    return _save(fig, out)


def credit(fig, y: float = -0.005, va: str = "top") -> None:
    """FIGURE_CREDIT in the figure's lower right corner. By default just
    under the canvas, where a tight bounding box takes it in; a figure saved
    at its full canvas passes a y inside it."""
    fig.text(0.995, y, FIGURE_CREDIT, ha="right", va=va, fontsize=6.5, color=MUTED)


def _save(fig, out: Path) -> Path:
    out = themed_path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    credit(fig)
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=GROUND)
    plt.close(fig)
    return out
