# Protocol for changes after results exist (S6)

Written 2026-10-11 (session 8), before any hypothesis test has run on fire
data and before the runner exists (audit round 5 S6; D73). Approved by
the owner on 2026-10-11; from here it changes only by a dated note at the
bottom.

D62 fixes what may change before the first test (bug fixes only). This
page says what happens from the first run onward.

## 1. The first results are never edited

- The first run writes to `results/tables/run1/`. Nothing in that folder is
  edited, renamed or deleted afterwards, by hand or by code.
- `src.run_guard.write_result` is the runner's only way to write a result.
  It refuses to overwrite an existing file, so a second run cannot replace
  the first.
- The commit holding `run1/` is tagged `registered-run1`, and `DECISIONS.md`
  records its commit and time (audit round 5 S5).
- A rerun for any reason goes beside it: `run2/`, `run3/`, each with its
  own provenance files. The site reads the latest run and says which.

## 2. What counts as a change, and what each one needs

| Change after `run1` exists | Needs |
|---|---|
| Code or rule change that can move a registered estimate, CI, p-value or Holm verdict (a bug fix included) | A row in the frozen plan's deviations log that says "decided after results were seen" and what had been seen; a `docs/plan_deviations.md` entry; a `DECISIONS.md` entry; a rerun in a new run folder; an old-vs-new table (section 3) |
| A pinned input changes (re-pin) | `python -m src.pin_inputs --repin "<reason>"`, which appends to `results/tables/input_pins_log.csv`; then as the row above if any value a registered test reads changed |
| A new analysis not in the plan | Labelled exploratory, uncorrected, reported apart from the registered tests; a `docs/plan_deviations.md` entry saying it was added after results; never replaces a registered test |
| Wording, figures or layout that read the same result tables | No rerun; the usual records |

Nothing is dropped: a registered test that was run stays reported, null
results included, even where a later run supersedes its numbers. Both runs
are shown.

## 3. The old-vs-new table

Any rerun that follows a code, rule or input change commits
`results/tables/<new run>/changes_from_<old run>.csv`: one row per
registered test (hypothesis, region), with the estimate, the 95% CI, the
registered p-value, the Holm-adjusted p-value and the Holm verdict from
each run, and the differences. Rows that did not move are kept, so the
table shows the whole set, not only what changed.

## 4. Size labels and plain OLS checks

- The size label beside every Newey-West, Driscoll-Kraay and joint-F
  p-value, and the size of each plain OLS check (D66, D68), are read from
  `results/tables/test_size.csv` by `src.run_guard.size_label`, never typed.
- Only rows with `label_scenario` true are labels. Each registered test
  maps to exactly one label row; a test enforces this
  (`tests/test_run_guard.py`).
- `test_size.csv` is not rebuilt after `run1` unless section 2's first row
  applies; its sha256 is in every provenance file.

## 5. Before every run

The runner calls `src.run_guard.preflight` first and stops on any problem:
a clean working tree, every pinned input matching `input_pins.csv`, the
frozen plan text identical to the tag `analysis-plan-frozen` above the
deviations log, and the statistics tests passing. Tables are opened only
through `src.pin_inputs.load_input`. Every result file gets a provenance
file beside it (commit, hashes of the pins and the size table, UTC time,
seed, package versions). The full environment (`conda list --explicit`) is
saved by hand into the run folder at the first run; no code writes it.

## 6. What this page does not cover

It does not decide whether a change is justified; that stays the owner's
call, logged as above. It cannot stop a result from being seen before a
change is proposed, so every post-result row says what had been seen.
