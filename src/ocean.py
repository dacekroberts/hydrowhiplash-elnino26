"""Winter sea-surface temperature for the map page's ocean panels (D99).
Visualisation only: nothing here feeds a registered test, a reported run or
the forecast, and the ERSST files are not pinned inputs.

For each winter (December Y-1 to February Y, labelled Y like everything
else): the mean of the three months' anomalies against each cell's
SST_NORMAL_YEARS winters, then the same with the tropical mean anomaly
(SST_TROPICS_LAT, every longitude) subtracted, as NOAA's relative index
does, so a warming ocean does not make every recent winter look like an
El Nino. NOAA's RONI is further rescaled to the variance of the plain
index; that step is not applied here, so the Nino 3.4 mean of these maps
tracks RONI without equalling it. check_nino34 measures how closely.

  winter_anomalies(folder)  DataArrays `anomaly` and `relative` (year, lat, lon)
  nino34(field)             the Nino 3.4 box mean per winter
  check_nino34(...)         the box mean beside the project's DJF index values

Run:  python -m src.ocean      writes results/tables/sst_nino34_check.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from src import geo
from src.config import (CLIMATE_FIRST_YEAR, ENSO_INDEX, ERSST_LAST_WINTER, ERSST_RAW, NINO34_BOX,
                        RESULTS, SST_MONTHS, SST_NORMAL_YEARS, SST_TROPICS_LAT)

CHECK_TABLE = RESULTS / "tables" / "sst_nino34_check.csv"


def monthly(folder: Path = ERSST_RAW) -> xr.DataArray:
    """sst in degrees Celsius with dimensions (year, month, lat, lon), year
    being the winter's label."""
    winters = range(CLIMATE_FIRST_YEAR + 1, ERSST_LAST_WINTER + 1)
    rows = []
    for winter in winters:
        months = []
        for month in SST_MONTHS:
            year = winter - 1 if month == 12 else winter
            with xr.open_dataset(folder / f"ersst.v6.{year}{month:02d}.nc",
                                 decode_times=False) as ds:
                months.append(ds["sst"].isel(time=0, lev=0).load().drop_vars(["time", "lev"]))
        rows.append(xr.concat(months, dim=pd.Index(list(SST_MONTHS), name="month")))
    return xr.concat(rows, dim=pd.Index(list(winters), name="year"))


def box_mask(field: xr.DataArray, lat: tuple[float, float], lon: tuple[float, float]) -> xr.DataArray:
    """True for cells whose centre lies in the box (lon in degrees east)."""
    return ((field["lat"] >= lat[0]) & (field["lat"] <= lat[1])
            & (field["lon"] >= lon[0]) & (field["lon"] <= lon[1]))


def winter_anomalies(folder: Path = ERSST_RAW) -> xr.Dataset:
    sst = monthly(folder)
    n0, n1 = SST_NORMAL_YEARS
    normal = sst.sel(year=slice(n0, n1)).mean("year")
    anomaly = (sst - normal).mean("month")
    tropics = box_mask(anomaly, SST_TROPICS_LAT, (0, 360))
    belt = geo.regional_mean(anomaly, tropics, lat="lat", lon="lon")
    return xr.Dataset({"anomaly": anomaly, "relative": anomaly - belt})


def nino34(field: xr.DataArray) -> pd.Series:
    mask = box_mask(field, NINO34_BOX[0], NINO34_BOX[1])
    return geo.regional_mean(field, mask, lat="lat", lon="lon").to_series()


def check_nino34(fields: xr.Dataset, winters: pd.DataFrame) -> pd.DataFrame:
    """Per winter: the Nino 3.4 means of the two fields and the project's
    DJF index value (`winters`: year, enso_djf)."""
    table = pd.DataFrame({"sst_anomaly_nino34": nino34(fields["anomaly"]),
                          "sst_relative_nino34": nino34(fields["relative"])}).reset_index()
    return table.merge(winters[["year", "enso_djf"]], on="year", how="left").round(3)


def main() -> None:
    from src import pin_inputs

    fields = winter_anomalies()
    index = pin_inputs.load_input("climate_controls_region_year.csv")
    index = index[index["region"] == index["region"].iloc[0]]
    table = check_nino34(fields, index)
    CHECK_TABLE.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(CHECK_TABLE, index=False, lineterminator="\n")
    both = table.dropna()
    gap = both["sst_relative_nino34"] - both["enso_djf"]
    print(f"wrote {CHECK_TABLE}: {len(table)} winters")
    print(f"relative Nino 3.4 mean against DJF {ENSO_INDEX}: r = "
          f"{np.corrcoef(both['sst_relative_nino34'], both['enso_djf'])[0, 1]:.3f}, "
          f"RMSE {np.sqrt((gap ** 2).mean()):.2f} C, largest gap {gap.abs().max():.2f} C")


if __name__ == "__main__":
    main()
