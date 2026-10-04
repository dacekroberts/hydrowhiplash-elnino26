"""Spatial helpers that enforce the project's measurement rules.

Two rules, both easy to break silently:
  1. Burned area is measured in an equal-area CRS, never in EPSG:4326.
  2. Regional means of gridded climate data are weighted by cos(latitude),
     because a 0.1 degree cell at 60N covers about half the area of one at 32N.
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import xarray as xr

from src.config import CRS_EQUAL_AREA, M2_PER_HA


def area_ha(gdf: gpd.GeoDataFrame) -> "pd.Series":
    """Polygon area in hectares, computed in the equal-area CRS.

    Recomputed from geometry rather than taken from each source's own area
    field, so US and Canadian records use identical arithmetic.
    """
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS; set it before measuring area.")
    return gdf.to_crs(CRS_EQUAL_AREA).geometry.area / M2_PER_HA


def latitude_weights(da: xr.DataArray, lat: str = "latitude") -> xr.DataArray:
    """cos(latitude) weights for a regular lat/lon grid."""
    return np.cos(np.deg2rad(da[lat]))


def regional_mean(da: xr.DataArray, mask: xr.DataArray,
                  lat: str = "latitude", lon: str = "longitude") -> xr.DataArray:
    """Area-weighted mean of `da` over cells where `mask` is True.

    `mask` is a boolean grid on the same lat/lon coordinates, e.g. from
    regionmask. Returns a series over the remaining dimensions (usually time).
    """
    weights = latitude_weights(da, lat).broadcast_like(mask).where(mask, 0)
    return da.weighted(weights.fillna(0)).mean(dim=[lat, lon])
