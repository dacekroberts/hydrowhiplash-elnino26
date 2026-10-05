"""Download the ENSO index (ONI or RONI) and classify every winter.

The index is chosen by ENSO_INDEX in src/config.py; record the choice in
ANALYSIS_PLAN.md before freezing.

Writes:
  data/raw/<index>.ascii.txt          raw index table
  data/processed/enso_index.csv       tidy: season, year, anom
  data/processed/el_nino_winters.csv  one row per winter (all phases):
                                      year, winter, enso_djf, phase, strong

Year convention: the DJF value labelled with year Y is the winter of
(Y-1)-Y, which affects the fire season of year Y.

Run:  python -m src.download_oni
"""
from pathlib import Path

import pandas as pd
import requests

from src.config import (CLIMATE_FIRST_YEAR, DATA_PROCESSED, DATA_RAW,
                        EL_NINO_THRESHOLD, ENSO_INDEX, ENSO_INDEX_URLS,
                        LA_NINA_THRESHOLD, STRONG_THRESHOLD)


def download(index: str = ENSO_INDEX, refresh: bool = True) -> Path:
    """Fetch the raw table for `index` ("ONI" or "RONI") to data/raw/.

    With refresh=False an existing file is reused (for exploration of the
    index not selected in config, e.g. RONI next to ONI before the freeze).
    """
    url = ENSO_INDEX_URLS[index]
    if not url:
        raise SystemExit(f"No URL set for index {index!r} in src/config.py.")
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out = DATA_RAW / f"{index.lower()}.ascii.txt"
    if out.exists() and not refresh:
        return out
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out.write_text(resp.text)
    return out


def load_winters(index: str = ENSO_INDEX, refresh: bool = False) -> pd.DataFrame:
    """Classified winters for any index, without writing data/processed/."""
    return classify_winters(parse(download(index, refresh=refresh)))


def parse(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+")
    df.columns = [c.lower() for c in df.columns]  # seas, yr, total, anom
    return df.rename(columns={"seas": "season", "yr": "year"})


def classify_winters(index: pd.DataFrame) -> pd.DataFrame:
    """One row per winter, every phase kept, so all years stay analysable."""
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
    return djf[["year", "winter", "enso_djf", "phase", "strong"]].reset_index(drop=True)


def main() -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    index = parse(download())
    index.to_csv(DATA_PROCESSED / "enso_index.csv", index=False)

    winters = classify_winters(index)
    winters.to_csv(DATA_PROCESSED / "el_nino_winters.csv", index=False)

    nino = winters[winters["phase"] == "el_nino"]
    print(f"El Nino winters since {CLIMATE_FIRST_YEAR}-{CLIMATE_FIRST_YEAR + 1 - 1900:02d} "
          f"(DJF {ENSO_INDEX} >= {EL_NINO_THRESHOLD}):")
    for _, r in nino.iterrows():
        tag = "  STRONG" if r["strong"] else ""
        print(f"  {r['winter']}  {ENSO_INDEX} {r['enso_djf']:+.1f}{tag}")
    counts = winters["phase"].value_counts()
    print(f"\nTotals: {counts.to_dict()}")


if __name__ == "__main__":
    main()
