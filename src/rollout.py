"""The rollout calendar: every arrival the site waits on, in one dated list.

Each item says when something is expected, what it changes on the site and
what has to be prepared for it. The list is built from src/config.py (the
tracker window, the data day, the fire-season months, the release windows)
and written to results/tables/rollout_calendar.json, because the Quarto site
reads only results/. The tracker page's timetable and the scheduled
reminders both read that file, so they cannot disagree (D87).

An item counts as done only when the committed file named in its evidence
exists; nothing is ticked by hand. Items whose output files do not exist yet
carry no evidence and stay open until the code that writes them is built.

Run:  python -m src.rollout
Rebuild after any change to the settings it reads; tests/test_rollout.py
fails if the committed file is stale.
"""
from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from pathlib import Path

from src import config

OUT = config.RESULTS / "tables" / "rollout_calendar.json"
RUN1_PROVENANCE = config.RESULTS / "tables" / "run1" / "registered_tests.csv.provenance.json"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
NORTH = "PNW, BC, AB, AK and YT"
CALIFORNIA = "NorCal and SoCal"


def _d(text: str) -> date:
    return date.fromisoformat(text)


def _short(day: date) -> str:
    return f"{day.day} {MONTHS[day.month - 1][:3]} {day.year}"


def when_text(start: date, end: date, precision: str) -> str:
    """The date as a reader sees it: "by 7 Nov 2026", "1 to 14 Mar 2027"."""
    if precision == "on":
        return _short(start)
    if precision in ("by", "about", "after"):
        return f"{precision} {_short(end)}"
    if precision != "window":
        raise ValueError(f"unknown precision {precision!r}")
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day} to {_short(end)}"
    first = MONTHS[start.month - 1][:3] + ("" if start.year == end.year else f" {start.year}")
    return f"{first} to {MONTHS[end.month - 1][:3]} {end.year}"


def _add_months(day: date, months: int) -> date:
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def tracker_months() -> list[tuple[int, int, date]]:
    """(year, month, expected arrival) for each month of data the tracker
    waits on: the months whose data arrives inside TRACKER_WINDOW, a month's
    data being expected by TRACKER_DATA_DAY of the next month."""
    start, end = (_d(text) for text in config.TRACKER_WINDOW)
    out, cursor = [], date(start.year, start.month, 1)
    while cursor <= end:
        arrival = _add_months(cursor, 1).replace(day=config.TRACKER_DATA_DAY)
        if arrival <= end:
            out.append((cursor.year, cursor.month, arrival))
        cursor = _add_months(cursor, 1)
    return out


def april1_swe_date() -> date:
    """1 April of the forecast year plus the hourly product's lag margin."""
    return date(config.FORECAST_YEAR, 4, 1) + timedelta(days=config.ERA5_HOURLY_LAG_DAYS)


def season_ends() -> dict[str, date]:
    """Last day of each region's fire season of FORECAST_YEAR. A window that
    ends before it starts runs into the next calendar year (D43)."""
    out = {}
    for region, (first, last) in config.FIRE_SEASON_MONTHS.items():
        year = config.FORECAST_YEAR + (1 if last < first else 0)
        out[region] = date(year, last, calendar.monthrange(year, last)[1])
    return out


def registered_run_date() -> date:
    """UTC date of run1, from its provenance record."""
    run_utc = json.loads(RUN1_PROVENANCE.read_text("utf-8"))["run_utc"]
    return _d(run_utc[:10])


def _item(key, kind, start, end, precision, title, site_change, prepare, basis, *,
          reader=True, own_reminder=True, checked_at=(), evidence=None, stage=None) -> dict:
    return {"id": key, "kind": kind, "start": start, "end": end, "precision": precision,
            "title": title, "site_change": site_change, "prepare": prepare, "basis": basis,
            "reader": reader, "own_reminder": own_reminder, "checked_at": list(checked_at),
            "evidence": evidence, "forecast_stage": stage}


def _monthly_items() -> list[dict]:
    months = tracker_months()
    out = []
    for position, (year, month, arrival) in enumerate(months):
        name = MONTHS[month - 1]
        key = f"era5_{year}_{month:02d}"
        site_change = f"{name}'s tile fills in on the tracker for each region."
        prepare = (f"Download {name} {year} to a stamped path, rebuild the tracker tables, "
                   "render the site. Record the day CPC posted this month's RONI value.")
        if position == 0:
            site_change = ("The tracker moves from its before-winter state to tracking: "
                           f"{name}'s tile fills in for each region.")
            prepare = ("The hard-line item (ACTION_PLAN Phase 5, D55): set ERA5_LAG_MONTHS "
                       "from 3 to 1, download every published 2026 month to a stamped path "
                       "(D73), refit SPEI (about 55 minutes), rebuild the tables and report "
                       "the changed numbers. Recheck TRACKER_DATA_DAY against the day "
                       f"{name} appeared. Needs the stamped download paths built first.")
        elif month == 2:
            site_change = ("February's tile fills in, so the December to February winter "
                           "the tests use is complete.")
        elif position == len(months) - 1:
            site_change = (f"{name}'s tile fills in, so the October to March precipitation "
                           "total is complete.")
        out.append(_item(key, "data", arrival, arrival, "by",
                         f"{name}'s ERA5-Land monthly data", site_change, prepare,
                         "TRACKER_WINDOW, TRACKER_DATA_DAY (D55)"))
    return out


def items() -> list[dict]:
    """Every arrival, in date order, with its reminder date."""
    windows = {key: (_d(a), _d(b)) for key, (a, b) in config.ROLLOUT_WINDOWS.items()}
    monthly = _monthly_items()
    month_key = {(item["start"].year, item["start"].month): item["id"] for item in monthly}
    frozen = _d(config.TRACKER_FREEZE_DATE)
    run1 = registered_run_date()
    swe = april1_swe_date()
    ends = season_ends()
    north_end = max(day for day in ends.values() if day.year == config.FORECAST_YEAR)
    california_end = max(ends.values())
    djf_start, djf_end = windows["djf_index"]
    revised_by = _add_months(djf_end, config.RONI_REVISION_MONTHS)

    out = [
        _item("plan_frozen", "record", frozen, frozen, "on",
              "Analysis plan frozen",
              "Every page states this date: the tests were fixed before any fire data "
              "was opened.",
              "None.", "TRACKER_FREEZE_DATE; tag analysis-plan-frozen",
              own_reminder=False, evidence="tables/site_settings.json"),
        _item("registered_runs", "record", run1, run1, "on",
              "Registered tests run once and committed",
              "The results and the methods pages read run1.",
              "None.", "results/tables/run1 provenance; tag registered-run1",
              own_reminder=False, evidence="tables/run1/registered_tests.csv"),
        *monthly,
        _item("cnfdb_2025", "release", *windows["cnfdb_2025"], "window",
              "CNFDB 2025 fire polygons (no fixed date)",
              "The 2025 seasons of BC, AB and YT are reported beside the results; the "
              "registered tests keep 1984 to 2024.",
              "Check the CNFDB release folder for new file dates. If released: download "
              "to a stamped path (D73), read the release notes, report beside (D57). "
              "Reads polygons: ask the owner first.",
              "ROLLOUT_WINDOWS; frozen plan deviations log (D57): about January 2027",
              reader=False, own_reminder=False,
              checked_at=[month_key[(2027, 1)], month_key[(2027, 2)], month_key[(2027, 3)]]),
        _item("season_2026_closes", "season", date(2027, 1, 31), date(2027, 1, 31), "after",
              "California's 2026 fire season closes",
              "The 2026 season can be shown complete for every US region, still "
              "provisional (WFIGS) and outside the tests.",
              "Download WFIGS again to a stamped path and redraw the 2026 season for "
              "PNW, AK, NorCal and SoCal: described only, provisional, outside the "
              "tests (owner, 2026-10-12; D95). Reads polygons: ask the owner first.",
              "FIRE_SEASON_MONTHS (D43); ANALYSIS_PLAN Execution details: 2026 is "
              "described only; D95",
              reader=False, own_reminder=False, checked_at=[month_key[(2027, 2)]]),
        _item("canswe_v9", "release", *windows["canswe_v9"], "window",
              "CanSWE v9 station snow data (no fixed date)",
              "The station snow check beside the ERA5-Land snowpack gains April 2026 "
              "for Alberta.",
              "Check the Zenodo concept record for a v9. If released: read its terms "
              "(read-licence), download to a stamped path, rebuild the station index.",
              "ROLLOUT_WINDOWS; docs/alberta_swe_sources.md release record",
              reader=False, own_reminder=False,
              checked_at=[month_key[(2027, 2)], "djf_index", month_key[(2027, 4)]]),
        _item("djf_index", "index", djf_start, djf_end, "window",
              "The December to February El Niño index (RONI), first release",
              "The winter is classed as El Niño, strong El Niño or neither, and the "
              "first forecast stage is published from the registered model.",
              "Fetch CPC's first RONI release after February to a stamped path the day "
              "it appears and record the retrieval date: the frozen plan fixes that "
              "release as the forecast's input. Then run the 2027 forecast from the H3a "
              "model for all seven regions with 80% intervals.",
              "ROLLOUT_WINDOWS; ANALYSIS_PLAN Execution details, The 2027 forecast",
              stage="first"),
        _item("swe_april1", "data", swe, swe, "about",
              "Snowpack on 1 April (ERA5-Land)",
              "The final forecast stage is published, with the two snowpack and winter "
              "moisture forecasts beside it, and the tracker becomes the record of what "
              "arrived when.",
              "Download the 1 April hourly field to a stamped path, rebuild the "
              "snowpack table, run the secondary H6 forecasts, move the tracker to its "
              "final state.",
              "FORECAST_YEAR, ERA5_HOURLY_LAG_DAYS; DECISIONS 2026-10-05 SWE source",
              own_reminder=False, checked_at=[month_key[(2027, 4)]], stage="final"),
        _item("roni_revisions_close", "index", revised_by, revised_by, "about",
              "Revisions to the December to February index end",
              "Any revision is reported beside the forecast; the forecast keeps the "
              "first release.",
              "Fetch RONI again to a stamped path, compare the December to February "
              "value with the first release, report the difference.",
              "RONI_REVISION_MONTHS; ANALYSIS_PLAN: later revisions are reported, not "
              "substituted",
              reader=False, checked_at=[month_key[(2027, 4)]]),
        _item("verify_north", "verification", north_end, north_end, "after",
              f"The 2027 fire season ends in {NORTH}",
              "The verification panel sets what burned against the forecast for PNW and "
              "AK, from WFIGS and marked provisional. BC, AB and YT follow when NBAC "
              "holds 2027.",
              "Download WFIGS to a stamped path and measure 2027 for PNW and AK "
              "(provisional). BC, AB and YT wait: their registered source, CNFDB, "
              "arrives about January 2029 on its release record, and NBAC stands in as "
              "a provisional source from about May 2028 (D93). Reads polygons: ask the "
              "owner first.",
              "FIRE_SEASON_MONTHS, FORECAST_YEAR (D46); D93"),
        _item("verify_california", "verification", california_end, california_end, "after",
              f"The 2027 fire season ends in {CALIFORNIA}",
              "The verification panel is completed for California.",
              "As for the fall check. Also look for CNFDB 2026 and, in February or "
              "March, CanSWE v10 (April 2027 station values).",
              "FIRE_SEASON_MONTHS, FORECAST_YEAR (D43, D46)"),
        _item("cnfdb_2026", "release", *windows["cnfdb_2026"], "window",
              "CNFDB 2026 fire polygons (no fixed date)",
              "The 2026 seasons of BC, AB and YT are reported beside the results.",
              "As for CNFDB 2025.", "ROLLOUT_WINDOWS; CNFDB release record (D56)",
              reader=False, own_reminder=False, checked_at=["verify_california"]),
        _item("canswe_v10", "release", *windows["canswe_v10"], "window",
              "CanSWE v10 station snow data (no fixed date)",
              "The station snow check gains April 2027, the forecast's own spring.",
              "As for CanSWE v9.", "ROLLOUT_WINDOWS; docs/alberta_swe_sources.md",
              reader=False, own_reminder=False, checked_at=["verify_california"]),
        _item("nbac_2027", "release", *windows["nbac_2027"], "window",
              "NBAC burned-area polygons for 2027 (no fixed date)",
              "The verification panel gains BC, AB and YT, measured from NBAC and marked "
              "provisional.",
              "Check the NBAC download folder for a release holding 2027. If released: "
              "download to a stamped path, measure the 2027 season of BC, AB and YT "
              "under the fire rules, and report it as provisional: the registered "
              "series is CNFDB, and NBAC maps fires CNFDB does not hold (2.0% to 3.1% "
              "of its area, 1984 to 2024). Reads polygons: ask the owner first.",
              "ROLLOUT_WINDOWS; NBAC release record (v20260513 held 2025); D93"),
        _item("cnfdb_2027", "release", *windows["cnfdb_2027"], "window",
              "CNFDB 2027 fire polygons (no fixed date)",
              "The registered source's 2027 figures for BC, AB and YT are set beside "
              "the provisional NBAC ones, and the difference is reported.",
              "Check the CNFDB release folder for 2027. If released: download to a "
              "stamped path, measure BC, AB and YT, and report beside the NBAC figures "
              "already published; neither replaces the other without a note. Reads "
              "polygons: ask the owner first.",
              "ROLLOUT_WINDOWS; CNFDB release record (D56); D93"),
    ]
    lead = timedelta(days=config.ROLLOUT_REMINDER_LEAD_DAYS)
    for item in out:
        item["remind_on"] = item["start"] - lead if item["own_reminder"] else None
        item["when"] = when_text(item["start"], item["end"], item["precision"])
        evidence = item["evidence"]
        item["done"] = bool(evidence) and (config.RESULTS / Path(evidence)).exists()
    return sorted(out, key=lambda item: (item["start"], item["end"]))


def reminders(rows: list[dict] | None = None) -> list[dict]:
    """One reminder per item that has its own, with the undated arrivals
    checked at the same time folded in."""
    rows = items() if rows is None else rows
    out = []
    for item in rows:
        if item["remind_on"] is None:
            continue
        folded = [other["id"] for other in rows if item["id"] in other["checked_at"]]
        out.append({"date": item["remind_on"], "for": item["id"], "also_check": folded})
    return sorted(out, key=lambda row: row["date"])


def calendar_data() -> dict:
    rows = items()
    return {"lead_days": config.ROLLOUT_REMINDER_LEAD_DAYS, "items": rows,
            "reminders": reminders(rows)}


def text() -> str:
    return json.dumps(calendar_data(), indent=2, ensure_ascii=False,
                      default=lambda value: value.isoformat()) + "\n"


def main(out: Path = OUT) -> None:
    out.write_bytes(text().encode("utf-8"))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
