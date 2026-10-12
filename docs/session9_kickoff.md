# Session 9 kickoff: Phase 4, plan the first hypothesis runs

Written at the end of session 8 (2026-10-12). Part 1 is the handoff; Part 2
is the prompt to paste into a new Claude Code session in the main checkout.

## Part 1 · Handoff

**Where things stand.**

- Both items that had to be settled before any hypothesis test are
  settled (owner): the Interior Alaska check is measured and reported as
  a descriptive limitation (D79, frozen plan's deviations log row 17);
  there is no NBAC re-run, and the per-fire coverage split is reported as
  a limitation beside the BC, AB and YT results (D81, row 19). Numbers in
  `DECISIONS.md` 2026-10-11 "Session 8: owner decisions before the first
  test" and 2026-10-12 "No NBAC re-run".
- The runner safeguards are built, tested and cold-checked (D73;
  `DECISIONS.md` 2026-10-11 "Runner safeguards built (session 8)"):
  `docs/post_results_protocol.md` (owner-approved), `src/pin_inputs.py`
  (`guard_write`, `guard_folder`, `repin`, `load_input`, `copy_pinned`),
  `src/run_guard.py` (`preflight`, `size_shape`, `plain_ols_shape`,
  `size_label`, `provenance`, `write_result`),
  `scripts/check_plan_frozen.py`, `scripts/preflight.py`,
  `tests/test_run_guard.py`. The offline copy of the 30 pinned inputs is
  in `pinned_inputs_copy/` (git-ignored; `python -m src.pin_inputs --copy`).
- The plain OLS check beside H3a and H3b takes the sidedness of its
  registered test (D80, row 18); `results/tables/test_size.csv` has 71
  rows.
- The Claude Code Project is not used for the registered runs (D78): one
  runner in the main checkout makes them in one commit. It is taken up
  again for the site pages after the runs.
- The site methods flowchart is merged (PR #23, D74). Its caption and alt
  text in `site/methods.qmd` are drafts for the owner to word, and the
  `ACTION_PLAN.md` "Methods flowchart" item stays unticked until then.
- **The runner itself is not written. No hypothesis test has run on fire
  data, and no view has set burned area beside ENSO.**

**First in session 9: plan the first hypothesis runs with the owner,**
then write the runner. Fixed already:

- The runner calls `run_guard.preflight(run="run1")` first, opens tables
  only through `pin_inputs.load_input`, takes every size label from
  `run_guard.size_label` (never typed), and writes every result through
  `run_guard.write_result` to `results/tables/run1/` with its provenance
  file. Results are never overwritten; a rerun goes in `run2` with a
  `changes_from_run1.csv` (`docs/post_results_protocol.md`).
- Save `conda list --explicit` by hand at the first run (protocol).
- Effect sizes and CIs before p-values; null results reported.
- Size labels read so far (label rows of `test_size.csv`): H3a
  Newey-West one-sided 0.068, two-sided 0.065; plain OLS check 0.048 and
  0.041. H3b 0.071 and 0.082; plain OLS 0.056 and 0.050. H1 and H2 are
  permutation tests and carry no label. H4, H5, H6, C1 and C2 labels are
  in the table and were not listed in session 8.
- To decide with the owner: which tests go in the first registered run
  and in what order; whether the runs reported beside them (ONI
  robustness, frozen-rules, Parks Canada sensitivity, strong-only; D75)
  are written by the same runner pass; the layout of the result tables.
- After the runner is written and before it runs: the DeepSeek read-only
  review of the safeguard code and the runner (D77), each call with the
  owner's yes, in an off-peak hour.
- Tag `registered-run1` on the commit that holds the runs.

**Deadline: the registered runs, and the runs reported beside them,
committed by Friday 2026-11-06** (D73, D75), the day before October's
ERA5-Land data is expected (`TRACKER_DATA_DAY` 7).

**Open from the session 8 cold check (none blocks a run):**

- Later downloads to stamped paths (D73, audit round 5 S1) are not built.
- The downloaders print no pin diff after `--rebuild`; this is the
  delegated-build pilot of D77, after the runs.
- Two tests in `tests/test_run_guard.py` need the tag
  `analysis-plan-frozen` in the clone.
- `tests/test_run_guard.py::test_real_builders_refuse_to_overwrite_their_pinned_tables`
  needs `data/`, so it fails in a worktree.

**Hard-line item (early November 2026, ACTION_PLAN Phase 5, D55):** lag
setting 3 to 1 month, download every published 2026 month, refit SPEI,
rebuild, report the changed numbers. Do it first if the date has come,
but never before the registered runs are committed unless the deadline
was missed (then see the Phase 5 item).

**Carried over, unchanged (session 8 kickoff, "Portfolio review
handoff"):** nothing from the portfolio review starts before the runs
are committed; after them, three methods-page items as one scope
addition (next free deviation number). No task goes to the DeepSeek
worker until the owner says so. Ask before any run that reads polygons
(shared machine memory). The going-public question is a leaning, not a
decision.

**Next free deviation number: D82.** The frozen plan's deviations log is
at row 19.

**Known limits, recorded (register):** as in the session 8 kickoff, plus
the NBAC per-fire split (provincial-label area in fires missing from
CNFDB: AB 2.7%, BC 2.0%, YT 3.1%; seasons over 10%: AB 6, BC 9, YT 3 of
41; not checked whether CNFDB files those fires under a neighbouring
year) and the Interior Alaska numbers (D79).

## Part 2 · Prompt for session 9

```text
Session 9 for hydrowhiplash-elnino26: Phase 4, plan the first hypothesis
runs and write the runner.

1. Orient: read CLAUDE.md, docs/session9_kickoff.md (Part 1),
   logs/2026-10-12.md, the top of DECISIONS.md (2026-10-11 and 2026-10-12
   entries), docs/plan_deviations.md D77-D81, docs/post_results_protocol.md,
   src/run_guard.py, ANALYSIS_PLAN.md (frozen: never edit above the
   deviations log) and ACTION_PLAN.md Phase 4. Read the roadmap artifact
   with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D82.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. If it is early November or later, read the hard-line item in Part 1
   before anything else.

4. Plan the first hypothesis runs with me before writing any runner code:
   bring a table of every registered test (region, sidedness, size label
   from results/tables/test_size.csv through run_guard.size_label, plain
   OLS check where one is reported), then the open choices in Part 1.
   Nothing is adopted without my yes.

5. Write the runner: preflight first, tables only through
   pin_inputs.load_input, results only through run_guard.write_result to
   results/tables/run1/, effect sizes and CIs before p-values. Tests on
   synthetic data. No hypothesis test runs on fire data until I say so.

6. Before the first run: the DeepSeek read-only review (D77), each call
   with my yes; ask me before any run that reads polygons.

7. Deadline: registered runs, and the runs reported beside them,
   committed by Friday 2026-11-06 (D73, D75), tag registered-run1.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   commit and push; refresh the data guide artifact
   (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and offer to update
   the roadmap artifact; write the next kickoff the same way.
```
