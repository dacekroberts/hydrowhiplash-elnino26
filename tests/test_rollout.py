"""The rollout calendar: built from src/config.py, committed copy current."""
import json
from datetime import date, timedelta

from src import config, rollout


def test_committed_file_matches_config():
    committed = json.loads(rollout.OUT.read_text("utf-8"))
    assert committed == json.loads(rollout.text()), "rerun python -m src.rollout"


def test_tracker_months_are_october_to_march():
    months = rollout.tracker_months()
    assert [(y, m) for y, m, _ in months] == [(2026, 10), (2026, 11), (2026, 12),
                                              (2027, 1), (2027, 2), (2027, 3)]
    assert months[0][2] == date(2026, 11, config.TRACKER_DATA_DAY)
    assert months[-1][2] == date(2027, 4, config.TRACKER_DATA_DAY)


def test_dates_derived_from_settings():
    assert rollout.april1_swe_date() == date(2027, 4, 8)
    ends = rollout.season_ends()
    assert ends["AK"] == date(2027, 9, 30) and ends["PNW"] == date(2027, 10, 31)
    assert ends["NorCal"] == ends["SoCal"] == date(2028, 1, 31)


def test_items_are_unique_ordered_and_complete():
    rows = rollout.items()
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert [row["start"] for row in rows] == sorted(row["start"] for row in rows)
    for row in rows:
        assert row["start"] <= row["end"], row["id"]
        assert row["title"] and row["site_change"] and row["prepare"] and row["basis"], row["id"]
        assert set(row["checked_at"]) <= set(ids), row["id"]


def test_every_open_item_is_covered_by_a_reminder():
    rows = rollout.items()
    reminders = rollout.reminders(rows)
    covered = {r["for"] for r in reminders} | {i for r in reminders for i in r["also_check"]}
    assert {row["id"] for row in rows if not row["done"]} <= covered
    lead = timedelta(days=config.ROLLOUT_REMINDER_LEAD_DAYS)
    by_id = {row["id"]: row for row in rows}
    for reminder in reminders:
        assert reminder["date"] == by_id[reminder["for"]]["start"] - lead


def test_a_folded_arrival_is_checked_inside_or_after_its_window():
    rows = rollout.items()
    by_id = {row["id"]: row for row in rows}
    for row in rows:
        if row["own_reminder"] or row["done"]:
            continue
        checks = [by_id[key]["remind_on"] for key in row["checked_at"]]
        assert checks and max(checks) >= row["start"] - timedelta(days=7), row["id"]


def test_done_needs_committed_evidence():
    for row in rollout.items():
        if row["done"]:
            assert (config.RESULTS / row["evidence"]).exists()
    assert not next(r for r in rollout.items() if r["id"] == "era5_2026_10")["done"]


def test_when_text():
    assert rollout.when_text(date(2026, 11, 7), date(2026, 11, 7), "by") == "by 7 Nov 2026"
    assert rollout.when_text(date(2027, 3, 1), date(2027, 3, 14), "window") == "1 to 14 Mar 2027"
    assert rollout.when_text(date(2027, 1, 1), date(2027, 2, 28), "window") == "Jan to Feb 2027"
