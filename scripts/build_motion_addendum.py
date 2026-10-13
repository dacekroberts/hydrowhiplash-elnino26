"""Build addendum 1 to the Motion handoff: the results that came close.

The first bundle (scripts/build_motion_handoff.py) had gone to the Motion
session when the owner asked for one more beat in Scene 7: the registered
tests whose 95% interval excludes zero but which did not pass the Holm
correction (D106). This writes a small flat folder to upload into the same
Motion chat:

  addendum1.md                            what changes, the rules, the line, the prompt
  addendum1_close_tests.json              the rows, cut from the run by rule
  addendum1_ref_passed_and_close_dark.png the two tiers drawn the site's way

Every value is read from results/tables/<RUN>/registered_tests.csv, which the
first bundle already carried whole as tests.csv; the tier rule is the one in
scripts/rank_registered_tests.py. No polygon is opened and nothing under
results/ is written.

Usage, from the repo root:
    python scripts/build_motion_addendum.py
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_dashboard  # noqa: E402  (needs scripts/ on the path)
import build_motion_handoff as handoff  # noqa: E402
import rank_registered_tests as ranking  # noqa: E402
from src import figures  # noqa: E402
from src.results_figures import LOG_POINTS  # noqa: E402

OUT = ROOT / "motion_handoff_addendum1"
SCENE = 7
FILM_THEME = "dark"  # the film is built dark first (owner, 2026-10-13)
REFERENCE = "addendum1_ref_passed_and_close.png"
# Label and description of a test that is close but has no wording among the
# results that pass (build_dashboard.SURVIVED). A draft for the owner to word.
CLOSE_ONLY = {
    "H6_spei": ("H6 (winter water balance and burned area)",
                "burned area that year, when the winter's water balance (SPEI) is wetter by "
                "one standard deviation", ""),  # draft
}
# Short row labels for the reference picture, by test.
ROW = {"H5_lag0": "winter rain, same year", "H5_lag1": "winter rain, year after",
       "H6_swe": "1 April snowpack", "H6_spei": "winter water balance", "H1": ""}
# The beat's line: a suggestion for the owner to word in the Motion chat.
LINE = ("{close} more have an interval clear of zero but did not pass the correction. "
        "{alberta} of them are in Alberta.")
RULES = (
    "The beat sits inside Scene {scene}, after the results that pass. The film stays at "
    "{max_seconds} s at most and the pace constant is not raised to fit it. If it does not fit, "
    "say so in the return notes and build Scene {scene} as approved.",
    "'Significant' still means only the {significant} of {tests} tests that pass the Holm "
    "correction. The {close} in this beat are never called significant, nearly significant, borderline, "
    "marginal or a trend. Their name on screen is the rule: 'interval clear of zero; did not "
    "pass the correction'.",
    "They are drawn below the results that pass and lighter: the same interval bar, a hollow "
    "mark where a passing result has a filled one, text in the muted ink. The reference "
    "picture shows the two forms as the site draws them.",
    "Each shows its region, its label and description as written in "
    "addendum1_close_tests.json, then its estimate and interval. No p-value is needed; if one "
    "is shown it is p_holm.",
    "A row marked draft carries wording the owner has not approved; show it as written and "
    "list it in the return notes.",
    "Associations, not causes, as for the rest of the film. None of the {close} sets El Niño "
    "against burned area, so card line 6 stands unchanged.",
    "The beat carries Scene {scene}'s credits (credits.md in the first bundle).",
)
RETURNS = (
    "Scene {scene}'s new start time and length, and the start time of the beat.",
    "Every figure on screen in the beat, and the wording shown with it.",
    "Whether the beat fitted without changing the pace constant or another scene's length.",
)
PROMPT = (
    "Addendum 1 to the bundle you already hold: three files, addendum1.md, "
    "addendum1_close_tests.json and addendum1_ref_passed_and_close_dark.png.",
    "Add one supporting beat at the end of Scene {scene}, as addendum1.md describes. Take every "
    "figure from addendum1_close_tests.json and keep the rules in addendum1.md, above all the "
    "one on the word 'significant'.",
    "Change nothing else in the film. Send back what addendum1.md lists under 'What comes "
    "back'.",
)


def close_rows() -> tuple[list[dict], dict]:
    """The close tier's rows worded for the film, and the counts beside them."""
    table = ranking.build()
    close = table[table["tier"] == ranking.TIER_CLOSE]
    wording = {**build_dashboard.SURVIVED, **CLOSE_ONLY}
    unworded = sorted(set(close["test"]) - set(wording))
    if unworded:
        raise ValueError(f"No wording for {unworded}.")
    rows = build_dashboard._rows(close, ["rank", "test", "region", "estimate", "ci_low",
                                         "ci_high", "pct_change", "pct_low", "pct_high",
                                         "p_holm", "significant", "alternative"])
    for row in rows:
        row["label"], row["what"], row["note"] = wording[row["test"]]
        row["draft"] = row["test"] in CLOSE_ONLY
        row["name"] = build_dashboard.REGION_NAMES[row["region"]]
        row["unit"] = "mm" if row["test"] == "H1" else "log points per 1 SD"
    counts = {"tests": len(table), "significant": int(table["significant"].sum()),
              "close": len(close),
              "interval_excludes_zero": int(table["interval_excludes_zero"].sum()),
              "close_in_alberta": int((close["region"] == "AB").sum()),
              "close_enso_burn": int(close["test"].isin(build_dashboard.ENSO_BURN_TESTS).sum())}
    return rows, counts


def reference(out: Path) -> Path:
    """Both tiers as the site's interval ledger: burned-area tests on one
    scale, the two winter precipitation tests on another."""
    table = ranking.build()
    shown = table[table["tier"] != ranking.TIER_SPANS].copy()
    shown["region"] = [f"{r} · {ROW[t]}" if ROW[t] else r
                       for r, t in zip(shown["region"], shown["test"])]
    rain = shown["test"] == "H1"
    panels = [
        {"title": "Burned area per 1 SD of the winter measure",
         "xlabel": f"{LOG_POINTS} per 1 SD", "family": "fire", "rows": shown[~rain]},
        {"title": "Winter precipitation in El Niño winters",
         "xlabel": "mm, December to February, El Niño winters minus the rest",
         "family": "water",
         "rows": shown[rain]},
    ]
    note = (f"Registered tests, {ranking.RUN}: every test whose two-sided 95% interval excludes "
            "zero. A filled mark passed the Holm correction; a hollow one did not.")
    with figures.themed(FILM_THEME):
        return figures.interval_ledger(panels, out / REFERENCE, note)


def brief(rows: list[dict], counts: dict, picture: str) -> str:
    film = {**handoff.FILM, **counts, "scene": SCENE}
    lines = ["# Addendum 1: the results that came close", "",
             f"For the film already in this chat. One supporting beat is added to Scene {SCENE}; "
             "nothing else changes. The beat's line and any row marked draft are suggestions "
             "for the owner to word.", "",
             "## What the beat shows", "",
             f"{counts['interval_excludes_zero']} of the {counts['tests']} registered tests have a "
             f"two-sided 95% interval that excludes zero. {counts['significant']} of them pass "
             f"the Holm correction and are in Scene {SCENE} already. The other {counts['close']} "
             "are this beat. The rule picks them: no cut-off was chosen by eye.", "",
             "| Rank of 52 | Region | Test | Estimate | 95% interval | Holm p | Wording |",
             "|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['rank']} | {row['name']} | {row['label']} | {row['estimate']} | "
                     f"{row['ci_low']} to {row['ci_high']} | {row['p_holm']} | "
                     f"{'draft' if row['draft'] else 'approved 2026-10-13'} |")
    lines += ["", "Units and the percent changes are in addendum1_close_tests.json. A burned-area "
              "row is in log points per one standard deviation of the winter measure; "
              "pct_change is the same figure as a percent.", "",
              "## Suggested line", "", LINE.format(close=counts["close"],
                                                   alberta=counts["close_in_alberta"]), "",
              "## Rules for the beat", ""]
    lines += [f"- {rule.format(**film)}" for rule in RULES]
    lines += ["", "## What comes back", ""] + [f"- {item.format(**film)}" for item in RETURNS]
    lines += ["", "## Prompt to paste", ""] + [line.format(**film) + "\n" for line in PROMPT]
    lines += ["## Files and why each may leave the repository", "",
              "| File | Why |", "|---|---|",
              f"| `addendum1.md` | this note; {handoff.SAFE['tests']} |",
              f"| `addendum1_close_tests.json` | rows of the same table, cut by rule; "
              f"{handoff.SAFE['tests']} |",
              f"| `{picture}` | drawn by code from the same table; (c) Dace Roberts |"]
    return "\n".join(lines) + "\n"


def build(out: Path) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    rows, counts = close_rows()
    picture = reference(out).name
    numbers = {"run": ranking.RUN, "rule": ranking.TIER_CLOSE, "counts": counts, "close": rows}
    (out / "addendum1_close_tests.json").write_bytes(
        json.dumps(numbers, ensure_ascii=False, indent=1).encode("utf-8"))
    (out / "addendum1.md").write_bytes(brief(rows, counts, picture).encode("utf-8"))
    names = sorted(path.name for path in out.iterdir())
    for name in names:
        if (out / name).is_dir() or any(mark in name for mark in "@[]()"):
            raise ValueError(f"{name} would not survive the upload.")
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    for name in build(args.out):
        print(f"wrote {args.out / name}")


if __name__ == "__main__":
    main()
