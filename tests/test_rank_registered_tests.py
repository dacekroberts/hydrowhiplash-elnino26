"""The ranked copy of the registered tests (scripts/rank_registered_tests.py)."""
import sys

import pandas as pd

from src.config import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import rank_registered_tests as ranking  # noqa: E402


def test_ranking_keeps_every_row_and_value_of_the_run():
    registered = pd.read_csv(ranking.TABLES / ranking.RUN / "registered_tests.csv")
    table = ranking.build()
    assert list(table["rank"]) == list(range(1, len(registered) + 1))
    assert table["p_holm"].is_monotonic_increasing
    key = ["test", "region"]
    merged = table.merge(registered, on=key, suffixes=("", "_run"), validate="one_to_one")
    assert len(merged) == len(registered)
    for column in ("estimate", "ci_low", "ci_high", "p", "p_holm"):
        assert (merged[column] == merged[f"{column}_run"]).all()


def test_tiers_follow_the_run_columns():
    table = ranking.build()
    passed = table["tier"] == ranking.TIER_PASS
    close = table["tier"] == ranking.TIER_CLOSE
    assert (passed == table["significant"]).all()
    assert (close == (~table["significant"] & table["interval_excludes_zero"])).all()
    # Every passing row ranks above every row that does not pass.
    assert table.loc[passed, "rank"].max() < table.loc[~passed, "rank"].min()


def test_committed_copy_matches_a_rebuild(tmp_path):
    rebuilt = tmp_path / "ranked.csv"
    rebuilt.write_bytes(ranking.build().to_csv(index=False, lineterminator="\n").encode("utf-8"))
    pd.testing.assert_frame_equal(pd.read_csv(ranking.OUT), pd.read_csv(rebuilt))
