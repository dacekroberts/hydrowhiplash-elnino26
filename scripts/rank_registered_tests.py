"""Rank the registered tests of a run from most to least significant.

Reads results/tables/<RUN>/registered_tests.csv and writes
results/tables/registered_tests_ranked.csv: the same rows and values, in a
new order, with a rank and a tier. Nothing is computed again and the run
folder is not written to. A presentation table, made after the results were
seen (D106): no test reads it and it changes no registered verdict.

Order: the Holm-adjusted p-value, the registered decision, smallest first;
ties by the registered p-value, then by test and region.

Tier, from columns the run already holds, with no cut-off chosen here:
  TIER_PASS    `significant` is true (Holm p below the registered level)
  TIER_CLOSE   not significant, and the stored 95% interval excludes zero
  TIER_SPANS   the stored 95% interval spans zero
The interval is two-sided in every row, also beside a one-sided test, so a
one-sided p below 0.05 can sit in TIER_SPANS.

Usage, from the repo root:
    python scripts/rank_registered_tests.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
RUN = "run1"
OUT = TABLES / "registered_tests_ranked.csv"
TIER_PASS = "passes Holm"
TIER_CLOSE = "interval excludes zero, did not pass Holm"
TIER_SPANS = "interval spans zero"
KEEP = ["family", "test", "region", "term", "outcome", "method", "alternative", "years", "n",
        "estimate", "ci_low", "ci_high", "pct_change", "pct_low", "pct_high",
        "p", "p_holm", "significant"]


def rank(registered: pd.DataFrame) -> pd.DataFrame:
    """`registered` in rank order, with `rank`, `tier` and `interval_excludes_zero`."""
    table = registered.sort_values(["p_holm", "p", "test", "region"], kind="stable")[KEEP].copy()
    excludes = (table["ci_low"] > 0) | (table["ci_high"] < 0)
    table["interval_excludes_zero"] = excludes
    table["tier"] = TIER_SPANS
    table.loc[excludes, "tier"] = TIER_CLOSE
    table.loc[table["significant"], "tier"] = TIER_PASS
    table.insert(0, "rank", range(1, len(table) + 1))
    table.insert(1, "run", RUN)
    return table.reset_index(drop=True)


def build() -> pd.DataFrame:
    return rank(pd.read_csv(TABLES / RUN / "registered_tests.csv"))


def main() -> None:
    table = build()
    OUT.write_bytes(table.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    print(f"wrote {OUT} ({len(table)} rows)")
    print(table["tier"].value_counts().to_string())


if __name__ == "__main__":
    main()
