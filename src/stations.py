"""Station April 1 snow water equivalent: one tidy station x year table.

Sources (raw files from the download scripts; licences in DATA_SOURCES.md):
NRCS SNOTEL pillows and snow courses (WA, OR, ID, AK), BC manual snow
courses, the Yukon snow survey network, and CanSWE v8 for Alberta and for
BC and Yukon pillows. Rules in src/config.py ("Station April 1 SWE
cleaning"); reasoning in DECISIONS.md 2026-10-05 "Station snowpack cleaning
rules"; measured effects in docs/methods_register.md.

  clean_nrcs()      drop QC flags NRCS_DROP_QC and negatives; inches to mm;
                    pillows read at the midnight opening 1 April; snow
                    courses inside the date window, placeholder 1 July dates
                    kept as date_unknown
  clean_bc()        Survey Period 01-Apr, inside the window, estimate codes
                    dropped; coordinates from CanSWE (the BC file has none)
  clean_yukon()     target_date 1 April, inside the window
  clean_canswe()    pillows: the daily value dated 1 April; manual: the
                    sample nearest 1 April inside the window
  combine()         provincial files win over CanSWE for the same station-year
  assign_regions()  point in polygon; Yukon network sites outside Yukon dropped
  dedupe_sites()    one site filed under two IDs (another network or a renamed
                    course) counted once: the lower-priority copy's shared
                    years are dropped
  station_index()   region x year: median % of each station's normal and mean
                    standardised anomaly, normals over STATION_NORMAL_YEARS
  compare_era5()    the index beside ERA5-Land April 1 SWE on the same scales
  agreement()       per region: correlations and the station / grid level ratio

Every clean_* function returns (table, counts), counts being the rows each
rule removed, for the methods register.

Run:  python -m src.stations   (writes data/processed/station_swe_apr1.csv,
                                data/processed/station_swe_region_year.csv
                                and its committed copy in results/tables/)

The committed copy holds values derived from NRCS (public domain), BC, Yukon
and CanSWE (Open Government Licences, attribution notices 4, 5 and 7 in
DATA_SOURCES.md) and ERA5-Land (CC-BY 4.0); they stay under those terms
(LICENSE-CONTENT).
"""
from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

from src.config import (BC_DROP_CODES, BC_SNOW_RAW, CANSWE_FILES, CANSWE_PILLOW_TYPE,
                        CANSWE_PREFIXES, CANSWE_RAW, CLIMATE_FIRST_YEAR, CRS_GEOGRAPHIC,
                        DATA_PROCESSED, ERA5_SWE_MIN_NORMAL_MM, FOOT_M, INCH_MM, NRCS_DROP_QC,
                        NRCS_PLACEHOLDER_DATE,
                        NRCS_SNOW_RAW, REGIONS, RESULTS, STATION_INDEX_TABLE,
                        STATION_MIN_PER_REGION_YEAR, STATION_NORMAL_MIN_YEARS,
                        STATION_NORMAL_YEARS, STATION_PCT_MIN_NORMAL_MM, STATION_TABLE,
                        SITE_DUP_MAX_KM, SITE_DUP_MIN_SHARE, SITE_DUP_MIN_YEARS,
                        SITE_DUP_TOL_MM, SITE_SOURCE_PRIORITY, STATION_WINDOW_DAYS,
                        YUKON_NETWORK_REGION, YUKON_SNOW_RAW)

COLUMNS = ["station_id", "source", "network", "method", "lat", "lon", "elevation",
           "year", "swe_apr1_mm", "sample_date", "flags"]
ERA5_SWE = DATA_PROCESSED / "swe_april1_region_year.csv"   # python -m src.snow
COMMITTED_INDEX = RESULTS / "tables" / STATION_INDEX_TABLE.name
CANSWE_PROVINCE = {"ALE": "Alberta", "BCE": "BC", "YT": "Yukon"}
YUKON_PREFIX = "YT-"


def april1(year: pd.Series) -> pd.Series:
    return pd.to_datetime(pd.DataFrame({"year": year, "month": 4, "day": 1}))


def nearest_in_window(df: pd.DataFrame, key: str, date: str, year: str,
                      window: int = STATION_WINDOW_DAYS) -> pd.DataFrame:
    """One row per (key, year): the row whose `date` is nearest 1 April of
    `year`, dropping rows more than `window` days away. Ties go to the later
    date. The offset is measured from the labelled year, so a record filed
    under year Y but dated a year off falls outside the window. Rows with no
    date raise: callers drop and count them first (drop_missing_dates), so a
    missing date is never counted as outside the window."""
    if df[date].isna().any():
        raise ValueError(f"{int(df[date].isna().sum())} row(s) with no {date}; "
                         f"drop them with drop_missing_dates first.")
    off = (df[date] - april1(df[year])).dt.days
    inside = df[off.abs() <= window].assign(_abs=off.abs())
    inside = inside.sort_values(["_abs", date], ascending=[True, False])
    return inside.drop_duplicates([key, year]).drop(columns="_abs")


def drop_missing_dates(df: pd.DataFrame, date: str, counts: dict) -> pd.DataFrame:
    """Rows with a `date`; the others are counted as "missing date"."""
    missing = df[date].isna()
    counts["missing date"] = int(missing.sum())
    return df[~missing]


def join_flags(*parts: pd.Series) -> pd.Series:
    """Semicolon-joined flag strings; empty parts skipped."""
    frame = pd.concat([p.fillna("").astype(str) for p in parts], axis=1)
    return frame.apply(lambda r: ";".join(v for v in r if v), axis=1)


def prefixed(values: pd.Series, prefix: str, skip: tuple = ("",)) -> pd.Series:
    """`prefix` + each value; values in `skip` (and missing values) become ''."""
    v = values.fillna("").astype(str).str.strip()
    return (prefix + v).mask(v.isin(skip), "")


def finish(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = df["year"].astype(int)
    if "flags" not in df:
        df["flags"] = ""
    return df[COLUMNS].sort_values(["station_id", "year"]).reset_index(drop=True)


# ---------------------------------------------------------------- NRCS

def read_nrcs(raw: Path = NRCS_SNOW_RAW) -> tuple[pd.DataFrame, pd.DataFrame]:
    """April 1 values (SNTL month 4; snow courses month 4, part 1) and station
    metadata from the AWDB JSON files."""
    rows = []
    for f in sorted(raw.glob("data_*.json")):
        for st in json.loads(f.read_text(encoding="utf-8")):
            for block in st.get("data", []):
                for v in block.get("values", []):
                    if v.get("month") != 4 or v.get("monthPart", "1") != "1":
                        continue
                    rows.append({"triplet": st["stationTriplet"], "year": v["year"],
                                 "value_in": v.get("value"), "qc": v.get("qcFlag"),
                                 "qa": v.get("qaFlag"), "collection": v.get("collectionDate")})
    values = pd.DataFrame(rows, columns=["triplet", "year", "value_in", "qc", "qa", "collection"])
    meta = []
    for f in sorted(raw.glob("stations_*.json")):
        meta += json.loads(f.read_text(encoding="utf-8"))
    meta = pd.DataFrame(meta).rename(columns={"stationTriplet": "triplet", "latitude": "lat",
                                              "longitude": "lon", "elevation": "elevation_ft"})
    return values, meta[["triplet", "lat", "lon", "elevation_ft"]]


def clean_nrcs(values: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    counts = {"rows": len(values)}
    df = values.dropna(subset=["value_in"])
    counts["missing value"] = counts["rows"] - len(df)
    for flag in NRCS_DROP_QC:
        n = len(df)
        df = df[df["qc"] != flag]
        counts[f"qc {flag}"] = n - len(df)
    n = len(df)
    df = df[df["value_in"] >= 0]
    counts["negative"] = n - len(df)
    df = df.assign(network_code=df["triplet"].str.split(":").str[2])

    pillow = df[df["network_code"] == "SNTL"].assign(
        sample_date=lambda d: april1(d["year"]), method="pillow", network="SNOTEL", date_flag="")
    course = df[df["network_code"] == "SNOW"].copy()
    course["sample_date"] = pd.to_datetime(course["collection"])
    month, day = NRCS_PLACEHOLDER_DATE
    placeholder = (course["sample_date"].dt.month == month) & (course["sample_date"].dt.day == day)
    unknown = course[placeholder].assign(sample_date=pd.NaT, date_flag="date_unknown")
    dated = drop_missing_dates(course[~placeholder], "sample_date", counts)
    windowed = nearest_in_window(dated, "triplet", "sample_date", "year")
    counts["outside window"] = len(dated) - len(windowed)
    counts["date_unknown (kept)"] = len(unknown)
    course = pd.concat([windowed.assign(date_flag=""), unknown]).assign(
        method="manual", network="NRCS snow course")

    out = pd.concat([pillow, course]).merge(meta, on="triplet", how="inner")
    out["flags"] = join_flags(prefixed(out["qc"], "nrcs_qc:", skip=("", "V")),
                              prefixed(out["qa"], "nrcs_qa:"), out["date_flag"])
    out = out.assign(station_id=out["triplet"], source="nrcs",
                     swe_apr1_mm=out["value_in"] * INCH_MM,
                     elevation=out["elevation_ft"] * FOOT_M)
    counts["kept"] = len(out)
    return finish(out), counts


# ---------------------------------------------------------------- BC

def read_bc(raw: Path = BC_SNOW_RAW) -> pd.DataFrame:
    """Archive and current-season manual surveys, headers stripped; rows
    repeated across the two files (same course, date and SWE) kept once."""
    frames = []
    for name in ("allmss_archive.csv", "allmss_current.csv"):
        d = pd.read_csv(raw / name, skipinitialspace=True, dtype={"Number": str})
        d.columns = [c.strip() for c in d.columns]
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(["Number", "Date of Survey", "Water Equiv. mm"])


def clean_bc(raw: pd.DataFrame, coords: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """`coords`: station_id, lat, lon (CanSWE ids BCE-<Number>)."""
    df = raw[raw["Survey Period"].astype(str).str.strip() == "01-Apr"].copy()
    counts = {"rows": len(df)}
    df["swe"] = pd.to_numeric(df["Water Equiv. mm"], errors="coerce")
    df = df.dropna(subset=["swe"])
    counts["missing value"] = counts["rows"] - len(df)
    df["code"] = df["Survey Code"].fillna("").astype(str).str.strip()
    n = len(df)
    df = df[~df["code"].isin(BC_DROP_CODES)]
    counts["estimate codes"] = n - len(df)
    df["sample_date"] = pd.to_datetime(df["Date of Survey"], format="%Y/%m/%d",
                                       errors="coerce")  # malformed: counted as missing
    df = drop_missing_dates(df, "sample_date", counts)
    df["year"] = df["sample_date"].dt.year
    df["station_id"] = "BCE-" + df["Number"].astype(str).str.strip()
    n = len(df)
    df = nearest_in_window(df, "station_id", "sample_date", "year")
    counts["outside window or repeat"] = n - len(df)
    n = len(df)
    df = df.merge(coords[["station_id", "lat", "lon"]], on="station_id", how="inner")
    counts["no coordinates"] = n - len(df)
    df = df.assign(source="bc", network="BC snow course", method="manual",
                   elevation=pd.to_numeric(df["Elev. metres"], errors="coerce"),
                   swe_apr1_mm=df["swe"], flags=prefixed(df["code"], "bc:"))
    counts["kept"] = len(df)
    return finish(df), counts


# ---------------------------------------------------------------- Yukon

def read_yukon_csv(path: Path) -> pd.DataFrame:
    """Yukon API CSV: quoted '#' comment lines precede the header."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("location_code"))
    return pd.read_csv(StringIO("\n".join(lines[start:])))


def clean_yukon(data: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    target = pd.to_datetime(data["target_date"])
    df = data[(data["parameter"] == "snow water equivalent")
              & (target.dt.month == 4) & (target.dt.day == 1)].copy()
    counts = {"rows": len(df)}
    df = df.dropna(subset=["result"])
    counts["missing value"] = counts["rows"] - len(df)
    df["sample_date"] = pd.to_datetime(df["sample_date"])
    df = drop_missing_dates(df, "sample_date", counts)
    df["station_id"] = YUKON_PREFIX + df["location_code"]
    n = len(df)
    df = nearest_in_window(df, "station_id", "sample_date", "year")
    counts["outside window"] = n - len(df)
    m = meta.assign(station_id=YUKON_PREFIX + meta["location_code"]).rename(
        columns={"latitude": "lat", "longitude": "lon", "elevation_m": "elevation"})
    df = df.merge(m[["station_id", "lat", "lon", "elevation"]], on="station_id", how="inner")
    flags = df["flag"].map({"Estimated SWE": "yukon:estimated"}).fillna("")
    df = df.assign(source="yukon", network="Yukon snow course", method="manual",
                   swe_apr1_mm=df["result"].astype(float), flags=flags)
    counts["estimated (kept)"] = int((flags != "").sum())
    counts["kept"] = len(df)
    return finish(df), counts


# ---------------------------------------------------------------- CanSWE

def read_canswe(path: Path = CANSWE_RAW / CANSWE_FILES[0],
                prefixes: tuple = CANSWE_PREFIXES,
                window: int = STATION_WINDOW_DAYS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Station table and the SWE values within `window` days of 1 April for
    stations whose id prefix is in `prefixes` (so Hydro-Quebec, HQ-, is never
    read). Values come back with the agency flag decoded."""
    ds = xr.open_dataset(path)
    ids = ds["station_id"].values.astype(str)
    keep = [i for i in ids if i.split("-")[0] in prefixes]
    ds = ds.sel(station_id=keep)
    time = pd.to_datetime(ds["time"].values)
    off = (time - april1(pd.Series(time.year)).values).days
    idx = np.where((np.abs(off) <= window) & (time.year >= CLIMATE_FIRST_YEAR))[0]
    stations = pd.DataFrame({"station_id": keep, "lat": ds["lat"].values,
                             "lon": ds["lon"].values, "elevation": ds["elevation"].values,
                             "type_mes": ds["type_mes"].values})
    sub = ds[["snw", "data_flag_snw"]].isel(time=idx).load()
    obs = sub.to_dataframe().reset_index().dropna(subset=["snw"])
    obs["data_flag_snw"] = obs["data_flag_snw"].map(
        lambda b: b.decode("ascii") if isinstance(b, bytes) else str(b)).str.strip()
    ds.close()
    return stations, obs.rename(columns={"time": "sample_date"})


def clean_canswe(stations: pd.DataFrame, obs: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = obs.merge(stations, on="station_id", how="inner")
    counts = {"rows": len(df)}
    n = len(df)
    df = df[df["snw"] >= 0]
    counts["negative"] = n - len(df)
    df["year"] = df["sample_date"].dt.year
    is_pillow = df["type_mes"] == CANSWE_PILLOW_TYPE
    pillow = df[is_pillow & (df["sample_date"] == april1(df["year"]))]
    manual = nearest_in_window(df[~is_pillow], "station_id", "sample_date", "year")
    out = pd.concat([pillow.assign(method="pillow"), manual.assign(method="manual")])
    province = out["station_id"].str.split("-").str[0].map(CANSWE_PROVINCE)
    kind = out["method"].map({"pillow": "pillow", "manual": "snow course"})
    out = out.assign(source="canswe", network=province + " " + kind,
                     swe_apr1_mm=out["snw"].astype(float),
                     flags=prefixed(out["data_flag_snw"], "canswe:"))
    counts["kept"] = len(out)
    return finish(out), counts


# ---------------------------------------------------------------- combine

def combine(provincial: pd.DataFrame, canswe: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Provincial (and NRCS) rows plus CanSWE rows for station-years the
    provincial files do not hold."""
    have = pd.MultiIndex.from_frame(provincial[["station_id", "year"]])
    dup = pd.MultiIndex.from_frame(canswe[["station_id", "year"]]).isin(have)
    out = pd.concat([provincial, canswe[~dup]], ignore_index=True)
    return finish(out), {"canswe rows replaced by provincial": int(dup.sum()),
                         "canswe rows added": int((~dup).sum())}


def assign_regions(table: pd.DataFrame, regions: gpd.GeoDataFrame) -> tuple[pd.DataFrame, dict]:
    """Add `region` by point in polygon (no areas measured); drop stations in
    no region and Yukon network sites outside YUKON_NETWORK_REGION."""
    sites = table.drop_duplicates("station_id")[["station_id", "lat", "lon"]]
    points = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites["lon"], sites["lat"]),
                              crs=CRS_GEOGRAPHIC)
    joined = gpd.sjoin(points, regions[["region", "geometry"]].to_crs(CRS_GEOGRAPHIC),
                       how="left", predicate="within")
    region = joined.drop_duplicates("station_id").set_index("station_id")["region"]
    out = table.assign(region=table["station_id"].map(region))
    yukon_out = out["station_id"].str.startswith(YUKON_PREFIX) & (out["region"] != YUKON_NETWORK_REGION)
    counts = {"stations in no region": int(region.isna().sum()),
              "rows in no region": int(out["region"].isna().sum()),
              "yukon network stations outside Yukon": int(
                  out.loc[yukon_out & out["region"].notna(), "station_id"].nunique()),
              "yukon network rows outside Yukon": int((yukon_out & out["region"].notna()).sum())}
    out = out[out["region"].notna() & ~yukon_out]
    return out.reset_index(drop=True), counts


def dedupe_sites(table: pd.DataFrame, max_km: float = SITE_DUP_MAX_KM,
                 tol_mm: float = SITE_DUP_TOL_MM, min_share: float = SITE_DUP_MIN_SHARE,
                 min_years: int = SITE_DUP_MIN_YEARS) -> tuple[pd.DataFrame, dict]:
    """Count a site once when two station IDs hold the same record.

    Two stations are one site when they lie within `max_km` (geodesic
    distance on the WGS84 ellipsoid) and, over at least `min_years` shared
    years with snow at either site (a value above `tol_mm`), at least
    `min_share` of their April 1 values agree within `tol_mm`; bare-ground
    years don't count as agreement (pre-freeze audit 2026-10-07, P4). The
    lower-priority copy loses all its shared years and keeps the rest.
    Priority: SITE_SOURCE_PRIORITY (NRCS for US sites, the provincial file
    for Canadian ones, CanSWE last), read from each copy's rows in the shared
    years, then more values, then station_id. An ID can mix sources: CanSWE
    files Yukon course 09CA-SC04's 1978-84 values under SC05, the course that
    replaced it 15 km away, so SC05's shared rows are CanSWE copies and SC05
    loses them; ranking a whole ID by its first row (5 provincial IDs ranked
    as CanSWE) or by its best row (SC05 kept SC04's record) gets mixed IDs
    wrong (fix review 2026-10-07, F1).
    Found by the pre-freeze audits (2026-10-06): e.g. NRCS 19A01:WA:SNOW and
    BC's BCE-WA07 (51 identical years), Yukon 09BA-SC02 and SC02A.
    """
    from pyproj import Geod

    ranked = table.assign(
        rank=table["source"].map(SITE_SOURCE_PRIORITY).fillna(len(SITE_SOURCE_PRIORITY)))
    sites = (ranked.groupby("station_id")
             .agg(rank=("rank", "min"), lat=("lat", "first"), lon=("lon", "first"),
                  n=("year", "size")).reset_index())
    sites = sites.sort_values(["rank", "n", "station_id"], ascending=[True, False, True])
    sites = sites.reset_index(drop=True)
    # Coarse degree box first, then the geodesic distance for the candidates.
    lat, lon = sites["lat"].to_numpy(), sites["lon"].to_numpy()
    lat_box = max_km / 100           # degrees; 1 degree of latitude is about 111 km
    lon_box = max_km / (111 * 0.30)  # 1 degree of longitude is over 33 km south of 72N
    i, j = np.nonzero(np.triu((np.abs(lat[:, None] - lat[None, :]) < lat_box)
                              & (np.abs(lon[:, None] - lon[None, :]) < lon_box), k=1))
    _, _, dist_m = Geod(ellps="WGS84").inv(lon[i], lat[i], lon[j], lat[j])
    near = dist_m <= max_km * 1000
    values = table.pivot_table(index="year", columns="station_id", values="swe_apr1_mm")
    row_rank = ranked.pivot_table(index="year", columns="station_id", values="rank",
                                  aggfunc="min")
    drop, pairs = set(), []
    for a, b in zip(i[near], j[near]):  # a ranks above b (sites is sorted)
        keep_id, lose_id = sites.at[a, "station_id"], sites.at[b, "station_id"]
        both = values[[keep_id, lose_id]].dropna()
        # Agreement counts only in years with snow at either site (a value
        # above tol_mm): two bare low sites agree every year without being
        # one record (pre-freeze audit P4: 23G12/23G13:OR, 22F28/22F27:OR,
        # 945:OR:SNTL/21G04:OR).
        snowy = both[(both > tol_mm).any(axis=1)]
        if len(snowy) < min_years:
            continue
        if ((snowy[keep_id] - snowy[lose_id]).abs() <= tol_mm).mean() >= min_share:
            shared_rank = row_rank.loc[both.index, [keep_id, lose_id]].min()
            if shared_rank[lose_id] < shared_rank[keep_id]:
                keep_id, lose_id = lose_id, keep_id
            drop.update((lose_id, int(y)) for y in both.index)
            pairs.append((keep_id, lose_id))
    key = pd.MultiIndex.from_frame(table[["station_id", "year"]].astype({"year": int}))
    lost = key.isin(list(drop))
    out = table[~lost].reset_index(drop=True)
    counts = {"duplicate site pairs": len(pairs), "rows dropped": int(lost.sum()),
              "rows dropped by region": table.loc[lost, "region"].value_counts().to_dict()}
    return out, counts


# ---------------------------------------------------------------- regional index

def station_normals(table: pd.DataFrame, years: tuple[int, int] = STATION_NORMAL_YEARS,
                    min_years: int = STATION_NORMAL_MIN_YEARS) -> pd.DataFrame:
    """Per station: count, mean and SD of April 1 SWE over `years` (inclusive);
    only stations with at least `min_years` values there."""
    first, last = years
    inside = table[table["year"].between(first, last)]
    stats = inside.groupby("station_id")["swe_apr1_mm"].agg(
        n_normal="size", normal_mm="mean", normal_sd="std").reset_index()
    return stats[stats["n_normal"] >= min_years].reset_index(drop=True)


def station_index(table: pd.DataFrame, normals: pd.DataFrame,
                  min_stations: int = STATION_MIN_PER_REGION_YEAR,
                  min_normal_mm: float = STATION_PCT_MIN_NORMAL_MM) -> pd.DataFrame:
    """Region x year index from stations with a normal.

    station_swe_pct: median across stations of SWE / normal x 100, over
    stations whose normal is at least `min_normal_mm` (n_stations_pct).
    station_swe_z: mean across stations of (SWE - normal) / SD, over stations
    with SD > 0 (n_stations). Each is left empty where its station count is
    below `min_stations`; the counts stay in the table."""
    df = table.merge(normals, on="station_id", how="inner")
    df["pct"] = (100 * df["swe_apr1_mm"] / df["normal_mm"]).where(df["normal_mm"] >= min_normal_mm)
    df["z"] = ((df["swe_apr1_mm"] - df["normal_mm"]) / df["normal_sd"]).where(df["normal_sd"] > 0)
    out = df.groupby(["region", "year"]).agg(
        n_stations=("z", "count"), station_swe_z=("z", "mean"),
        n_stations_pct=("pct", "count"), station_swe_pct=("pct", "median")).reset_index()
    out.loc[out["n_stations"] < min_stations, "station_swe_z"] = np.nan
    out.loc[out["n_stations_pct"] < min_stations, "station_swe_pct"] = np.nan
    return out


def anomalies(values: pd.Series, years: pd.Series,
              normal_years: tuple[int, int] = STATION_NORMAL_YEARS) -> tuple[pd.Series, pd.Series]:
    """% of the mean and standardised anomaly against `normal_years`, for one
    regional series (used to put ERA5-Land on the station index's scale).
    Raises when fewer than 2 values fall in `normal_years` (no SD)."""
    inside = values[years.between(*normal_years)]
    if inside.count() < 2:
        raise ValueError(f"{int(inside.count())} value(s) in {normal_years[0]}-"
                         f"{normal_years[1]}; at least 2 are needed for a normal and SD.")
    return 100 * values / inside.mean(), (values - inside.mean()) / inside.std(ddof=1)


def swe_normal_ok(swe_mm: pd.Series, years: pd.Series,
                  min_normal_mm: float = ERA5_SWE_MIN_NORMAL_MM) -> bool:
    """True when a region's April 1 SWE normal (mean over STATION_NORMAL_YEARS)
    is at least `min_normal_mm`; below it (SoCal, 0.06 mm) % and z are not
    meaningful. One rule for compare_era5 and src.phase2_figures."""
    normal = swe_mm[years.between(*STATION_NORMAL_YEARS)].mean()
    return bool(normal >= min_normal_mm)  # False for a NaN normal


def compare_era5(index: pd.DataFrame, era5: pd.DataFrame) -> pd.DataFrame:
    """Region x year: the station index next to ERA5-Land April 1 SWE (glacier
    cells excluded) on the same scales, plus the ENSO columns from `era5`."""
    era5 = era5.copy()
    parts = []
    for region, g in era5.groupby("region", sort=False):
        pct, z = anomalies(g["swe_apr1_mm"], g["year"])
        if not swe_normal_ok(g["swe_apr1_mm"], g["year"]):
            pct, z = pct * np.nan, z * np.nan
        parts.append(g.assign(era5_swe_pct=pct, era5_swe_z=z))
    era5 = pd.concat(parts)
    cols = ["region", "year", "winter", "swe_apr1_mm", "era5_swe_pct", "era5_swe_z",
            "enso_index", "enso_djf", "phase", "strong"]
    out = era5[cols].rename(columns={"swe_apr1_mm": "era5_swe_apr1_mm"}).merge(
        index, on=["region", "year"], how="left", validate="one_to_one")
    for c in ("n_stations", "n_stations_pct"):
        out[c] = out[c].fillna(0).astype(int)
    lead = ["region", "year", "winter", "station_swe_pct", "station_swe_z", "n_stations",
            "n_stations_pct", "era5_swe_apr1_mm", "era5_swe_pct", "era5_swe_z"]
    return out[lead + [c for c in out.columns if c not in lead]]


def agreement(table: pd.DataFrame, normals: pd.DataFrame, stations_table: pd.DataFrame) -> pd.DataFrame:
    """Per region, over years with a station index: correlation of station and
    ERA5-Land series (% and z), and the level ratio = median station normal /
    ERA5-Land regional mean over the normal period (both mm)."""
    first, last = STATION_NORMAL_YEARS
    site_region = stations_table.drop_duplicates("station_id").set_index("station_id")["region"]
    norm = normals.assign(region=normals["station_id"].map(site_region))
    rows = []
    for region, g in table.groupby("region", sort=False):
        both = g.dropna(subset=["station_swe_pct", "era5_swe_pct"])
        if both.empty:
            continue
        era5_normal = g.loc[g["year"].between(first, last), "era5_swe_apr1_mm"].mean()
        station_normal = norm.loc[norm["region"] == region, "normal_mm"].median()
        rows.append({"region": region, "n_years": len(both),
                     "first_year": int(both["year"].min()), "last_year": int(both["year"].max()),
                     "corr_pct": both["station_swe_pct"].corr(both["era5_swe_pct"]),
                     "corr_z": both["station_swe_z"].corr(both["era5_swe_z"]),
                     "station_normal_median_mm": station_normal,
                     "era5_normal_mm": era5_normal,
                     "level_ratio": station_normal / era5_normal})
    return pd.DataFrame(rows)


def effects_by_group(table: pd.DataFrame, normals: pd.DataFrame, enso: pd.DataFrame,
                     column: str = "elevation", groups: int = 3,
                     min_normal_mm: float = STATION_PCT_MIN_NORMAL_MM) -> pd.DataFrame:
    """Per region, stations split into `groups` equal-count groups by
    `column` (a station attribute such as elevation): El Nino minus neutral
    and strong El Nino minus all winters, in points of the median % of
    normal. `enso`: year, phase, strong. Descriptive. Stations with no
    `column` value (e.g. no elevation) are left out of the groups."""
    df = table.merge(normals, on="station_id", how="inner")
    df = df[df["normal_mm"] >= min_normal_mm]
    df = df.assign(pct=100 * df["swe_apr1_mm"] / df["normal_mm"])
    e = enso.drop_duplicates("year").set_index("year")
    rows = []
    for region, d in df.groupby("region", sort=False):
        site = d.drop_duplicates("station_id").set_index("station_id")[column].dropna()
        if site.empty:
            continue
        labels = pd.qcut(site, groups, labels=False, duplicates="drop")
        for k in sorted(labels.unique()):
            ids = labels.index[labels == k]
            s = d[d["station_id"].isin(ids)].groupby("year")["pct"].median()
            s = s[s.index.isin(e.index)]
            ph = e.loc[s.index]
            nino = ph["phase"] == "el_nino"
            rows.append({"region": region, "group": int(k) + 1,
                         f"{column}_min": site[ids].min(), f"{column}_max": site[ids].max(),
                         "stations": len(ids),
                         "nino_minus_neutral": s[nino].mean() - s[ph["phase"] == "neutral"].mean(),
                         "strong_minus_all": s[nino & ph["strong"]].mean() - s.mean()})
    return pd.DataFrame(rows)


def build() -> tuple[pd.DataFrame, dict]:
    from src.regions import load_regions

    report = {}
    canswe_stations, canswe_obs = read_canswe()
    coords = canswe_stations[canswe_stations["type_mes"] != CANSWE_PILLOW_TYPE]
    nrcs, report["nrcs"] = clean_nrcs(*read_nrcs())
    bc, report["bc"] = clean_bc(read_bc(), coords)
    yt, report["yukon"] = clean_yukon(read_yukon_csv(YUKON_SNOW_RAW / "snow_survey_data.csv"),
                                      read_yukon_csv(YUKON_SNOW_RAW / "snow_survey_metadata.csv"))
    canswe, report["canswe"] = clean_canswe(canswe_stations, canswe_obs)
    table, report["combine"] = combine(pd.concat([nrcs, bc, yt], ignore_index=True), canswe)
    table = table[table["year"] >= CLIMATE_FIRST_YEAR]
    table, report["regions"] = assign_regions(table, load_regions())
    table, report["duplicate sites"] = dedupe_sites(table)
    return table, report


def main() -> None:
    table, report = build()
    STATION_TABLE.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(STATION_TABLE, index=False, date_format="%Y-%m-%d", lineterminator="\n")
    for step, counts in report.items():
        print(step, counts)
    print(f"{len(table):,} station-years, {table['station_id'].nunique():,} stations -> {STATION_TABLE}")
    print(table.groupby(["region", "source", "method"]).agg(
        stations=("station_id", "nunique"), values=("year", "size"),
        first=("year", "min"), last=("year", "max")))

    normals = station_normals(table)
    index = station_index(table, normals)
    era5 = pd.read_csv(ERA5_SWE)
    region_year = compare_era5(index, era5)
    region_year["region"] = pd.Categorical(region_year["region"], categories=list(REGIONS),
                                           ordered=True)
    region_year = region_year.sort_values(["region", "year"]).reset_index(drop=True)
    region_year["region"] = region_year["region"].astype(str)
    for path in (STATION_INDEX_TABLE, COMMITTED_INDEX):
        path.parent.mkdir(parents=True, exist_ok=True)
        region_year.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {path}: {len(region_year)} rows")
    print(f"{len(normals)} stations with a {STATION_NORMAL_YEARS} normal")
    print(agreement(region_year, normals, table).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
