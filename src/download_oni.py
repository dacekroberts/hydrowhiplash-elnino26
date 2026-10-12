"""Download the ENSO index (ONI or RONI) and classify every winter.

The index is chosen by ENSO_INDEX in src/config.py; record the choice in
ANALYSIS_PLAN.md before freezing.

Writes:
  data/raw/<index>.ascii.txt          raw index table
  data/processed/enso_index.csv       tidy: season, year, anom
  data/processed/el_nino_winters.csv  one row per winter (all phases):
                                      year, winter, enso_index, enso_djf,
                                      phase, strong

Year convention: the DJF value labelled with year Y is the winter of
(Y-1)-Y, which affects the fire season of year Y.

Run:  python -m src.download_oni
      python -m src.download_oni --stamp [YYYY-MM-DD]   a later retrieval (D73):
          both raw index files go to data/raw/later/<stamp>/enso/ with a
          retrieval record; data/raw and data/processed are not touched.
          parse() and classify_winters() read a stamped file like any other.
"""
from pathlib import Path

import pandas as pd
import requests

from src import later, pin_inputs
from src.config import (CLIMATE_FIRST_YEAR, DATA_PROCESSED, DATA_RAW,
                        EL_NINO_THRESHOLD, ENSO_INDEX, ENSO_INDEX_URLS,
                        LA_NINA_THRESHOLD, STRONG_THRESHOLD)


def download(index: str = ENSO_INDEX, refresh: bool = True, rebuild: bool = False) -> Path:
    """Fetch the raw table for `index` ("ONI" or "RONI") to data/raw/.

    With refresh=False an existing file is reused (for exploration of the
    index not selected in config, e.g. RONI next to ONI before the freeze).
    The raw files are pinned inputs and CPC revises past values monthly, so
    a refresh over an existing file is refused without `rebuild` (audit
    2026-10-08 round 5 S1, S2).
    """
    url = ENSO_INDEX_URLS[index]
    if not url:
        raise SystemExit(f"No URL set for index {index!r} in src/config.py.")
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out = DATA_RAW / f"{index.lower()}.ascii.txt"
    if out.exists() and not refresh:
        return out
    pin_inputs.guard_write([out], rebuild)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out.write_text(resp.text)
    return out


def load_winters(index: str = ENSO_INDEX, refresh: bool = False) -> pd.DataFrame:
    """Classified winters for any index, without writing data/processed/."""
    return classify_winters(parse(download(index, refresh=refresh)), index)


def parse(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+")
    df.columns = [c.lower() for c in df.columns]  # seas, yr, total, anom
    return df.rename(columns={"seas": "season", "yr": "year"})


def classify_winters(index: pd.DataFrame, name: str) -> pd.DataFrame:
    """One row per winter, every phase kept, so all years stay analysable.
    `name` is the index the values come from, written to `enso_index` like
    every other table's ENSO columns."""
    # DJF labelled Y = winter (Y-1)-Y. ERA5-Land starts in Jan 1950, so the
    # first complete winter is 1950-51 (year = CLIMATE_FIRST_YEAR + 1).
    djf = index[(index["season"] == "DJF")
                & (index["year"] >= CLIMATE_FIRST_YEAR + 1)].copy()
    djf["winter"] = (djf["year"] - 1).astype(str) + "-" + djf["year"].astype(str)
    djf = djf.rename(columns={"anom": "enso_djf"})
    djf["phase"] = "neutral"
    djf.loc[djf["enso_djf"] >= EL_NINO_THRESHOLD, "phase"] = "el_nino"
    djf.loc[djf["enso_djf"] <= LA_NINA_THRESHOLD, "phase"] = "la_nina"
    djf["strong"] = djf["enso_djf"] >= STRONG_THRESHOLD
    djf["enso_index"] = name
    return djf[["year", "winter", "enso_index", "enso_djf", "phase",
                "strong"]].reset_index(drop=True)


def download_stamped(stamp: str) -> Path:
    """Fetch every index in ENSO_INDEX_URLS to its stamped folder and close
    it. CPC revises recent values, and the 2027 forecast reads the first
    release that holds DJF 2027 (ANALYSIS_PLAN "Execution details"), so each
    retrieval is kept as its own dated record. Returns the folder."""
    out = later.open_folder(DATA_RAW / "enso", stamp)
    for index, url in ENSO_INDEX_URLS.items():
        if not url:
            continue
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        (out / f"{index.lower()}.ascii.txt").write_bytes(resp.content)
        print(f"{index} <- {url}")
    later.record(out, stamp, ", ".join(u for u in ENSO_INDEX_URLS.values() if u))
    return out


def main(rebuild: bool = False) -> None:
    pin_inputs.guard_write([DATA_RAW / f"{ENSO_INDEX.lower()}.ascii.txt",
                            DATA_PROCESSED / "enso_index.csv",
                            DATA_PROCESSED / "el_nino_winters.csv"], rebuild)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    index = parse(download(rebuild=rebuild))
    index.to_csv(DATA_PROCESSED / "enso_index.csv", index=False, lineterminator="\n")

    winters = classify_winters(index, ENSO_INDEX)
    winters.to_csv(DATA_PROCESSED / "el_nino_winters.csv", index=False, lineterminator="\n")

    nino = winters[winters["phase"] == "el_nino"]
    print(f"El Nino winters since {CLIMATE_FIRST_YEAR}-{CLIMATE_FIRST_YEAR + 1 - 1900:02d} "
          f"(DJF {ENSO_INDEX} >= {EL_NINO_THRESHOLD}):")
    for _, r in nino.iterrows():
        tag = "  STRONG" if r["strong"] else ""
        print(f"  {r['winter']}  {ENSO_INDEX} {r['enso_djf']:+.1f}{tag}")
    counts = winters["phase"].value_counts()
    print(f"\nTotals: {counts.to_dict()}")


if __name__ == "__main__":
    import sys

    argv = sys.argv[1:]
    stamp = later.take_stamp(argv)
    if stamp:
        download_stamped(stamp)
    else:
        main(rebuild="--rebuild" in argv)
