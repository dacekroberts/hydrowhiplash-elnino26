"""Checks before a hypothesis run (audit 2026-10-08 round 5 S4): clean
working tree, every pinned input matching input_pins.csv (hashes 3.38 GB,
about a minute), the frozen plan text, and the statistics tests. The runner
calls src.run_guard.preflight itself; this is the same check by hand.

Run:  python scripts/preflight.py              (all checks)
      python scripts/preflight.py --no-tests   (skip pytest)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.run_guard import preflight  # noqa: E402


def main(args: list[str]) -> int:
    try:
        ok = preflight(run_tests="--no-tests" not in args)
    except RuntimeError as err:
        print(err)
        return 1
    print(f"preflight passed at commit {ok['commit']} ({ok['checked_utc']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
