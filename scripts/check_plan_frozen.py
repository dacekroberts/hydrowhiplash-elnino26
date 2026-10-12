"""Fail if ANALYSIS_PLAN.md differs from the tag analysis-plan-frozen above
its "## Deviations log" heading (audit 2026-10-08 round 5 S4). Rows below
the heading are the log and may be added.

Run:  python scripts/check_plan_frozen.py    (before every commit)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.run_guard import FROZEN_TAG, plan_frozen_problems  # noqa: E402


def main() -> int:
    problems = plan_frozen_problems()
    for line in problems:
        print(line)
    if not problems:
        print(f"frozen plan text matches {FROZEN_TAG}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
