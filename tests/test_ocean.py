"""Winter sea-surface temperature for the map's ocean panels (D99): made-up
grids, no data/ and no network."""
import numpy as np
import pandas as pd
import xarray as xr

from src import download_ersst, ocean
from src.config import (CLIMATE_FIRST_YEAR, ERSST_LAST_WINTER, NINO34_BOX, SST_EDGES, SST_MONTHS,
                        SST_NORMAL_YEARS, SST_PANELS, SST_TOKENS, SST_TROPICS_LAT)


def write_month(folder, year, month, field):
    lat = np.arange(-88.0, 89.0, 2.0)
    lon = np.arange(0.0, 360.0, 2.0)
    data = np.broadcast_to(field(lat[:, None], lon[None, :]), (lat.size, lon.size))
    ds = xr.Dataset({"sst": (("time", "lev", "lat", "lon"), data[None, None].astype("float32"))},
                    coords={"time": [0.0], "lev": [0.0], "lat": lat, "lon": lon})
    ds.to_netcdf(folder / f"ersst.v6.{year}{month:02d}.nc")


def test_file_names_cover_every_winter_from_its_december():
    names = download_ersst.file_names()
    assert len(names) == 3 * (ERSST_LAST_WINTER - CLIMATE_FIRST_YEAR)
    assert names[0] == f"ersst.v6.{CLIMATE_FIRST_YEAR}12.nc"       # winter 1951 starts in 1950
    assert names[-1] == f"ersst.v6.{ERSST_LAST_WINTER}02.nc"
    assert SST_MONTHS == (12, 1, 2)


def test_relative_anomaly_removes_a_warming_of_the_whole_tropics(tmp_path, monkeypatch):
    monkeypatch.setattr(ocean, "CLIMATE_FIRST_YEAR", 1989)
    monkeypatch.setattr(ocean, "ERSST_LAST_WINTER", 2022)
    (b0, b1), (c0, c1) = NINO34_BOX

    def field(winter):
        def values(lat, lon):
            base = 20.0 + 0 * lat + 0 * lon
            warm = 0.5 if winter == 2022 else 0.0             # the whole ocean warms
            box = (lat >= b0) & (lat <= b1) & (lon >= c0) & (lon <= c1)
            return base + warm + np.where(box & (winter == 2022), 2.0, 0.0)
        return values

    for winter in range(1990, 2023):
        for month in SST_MONTHS:
            write_month(tmp_path, winter - 1 if month == 12 else winter, month, field(winter))
    fields = ocean.winter_anomalies(tmp_path)
    assert list(fields["year"].values) == list(range(1990, 2023))
    plain, relative = ocean.nino34(fields["anomaly"]), ocean.nino34(fields["relative"])
    assert abs(plain[2022] - 2.5) < 1e-4 and abs(plain[2000]) < 1e-4
    belt = ocean.box_mask(fields["anomaly"], SST_TROPICS_LAT, (0, 360))
    box = ocean.box_mask(fields["anomaly"], *NINO34_BOX)
    assert bool((box & ~belt).sum() == 0)                     # the box lies inside the belt
    assert 1.9 < relative[2022] < 2.0                          # 2.5 less the belt's mean, box included
    far = fields["relative"].sel(year=2022, lat=40, lon=200)
    assert -0.1 < float(far) < 0.0                             # elsewhere the warming is gone
    table = ocean.check_nino34(fields, pd.DataFrame({"year": [2022], "enso_djf": [2.1]}))
    assert table.loc[table["year"] == 2022, "enso_djf"].iloc[0] == 2.1
    assert table["enso_djf"].isna().sum() == len(table) - 1


def test_settings_describe_five_classes_and_boxes_inside_the_grid():
    assert len(SST_EDGES) == 4 and list(SST_EDGES) == sorted(SST_EDGES) and len(SST_TOKENS) == 5
    assert SST_NORMAL_YEARS == (1991, 2020)
    for (la0, la1), (lo0, lo1) in list(SST_PANELS.values()) + [NINO34_BOX]:
        assert -88 <= la0 < la1 <= 88 and 0 <= lo0 < lo1 <= 358
