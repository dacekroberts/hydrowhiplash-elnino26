# Hand-off to the main-checkout session: the start-month split branch

Written 2026-10-13 by the worktree session on `claude/sharp-jemison-a79067`.
Owner, 2026-10-13: the table is accepted; no push and no PR for now. This
note lists what is left for the main checkout, in order. Nothing below was
done from the worktree.

## What the branch holds

Commits on top of main at `4e68d63`, local only, and one local tag,
`after-date-split-frozen` at `3285b23` (annotated, not pushed):

| Commit | Holds |
|---|---|
| `05c4622` | `src/fire_after_date.py`, its tests, three settings in `src/config.py` |
| `3285b23` | the split as one function over named region-seasons; **the version frozen for scoring**, and the commit the table was built at |
| `c9f2708` | the table, its provenance record, and the records |
| `c33459d` and the commit after it | the rollout calendar's open item, the tag and NBAC decisions, and this note |

Table: `results/tables/after_issue_date/fire_after_issue_date_region_year.csv`,
873 rows, sha256
`2978e3169917f65443063c003014c36f75d28cc93729579f5cf9a56cb19b137d`.

## Steps, in order

1. **Keep the branch.** The commits are reachable only through the local
   branch `claude/sharp-jemison-a79067`. Removing the worktree does not
   delete a branch, but `git branch -D` would. After any worktree clean-up,
   confirm with `git branch --contains 3285b23`.

2. **`3285b23` stays reachable through the tag `after-date-split-frozen`**
   (owner, 2026-10-13: tag locally, then the usual squash). `merge-side-pr`
   step 6 squashes, which leaves `3285b23` and `c9f2708` off main; the
   sibling and the table's provenance record both name `3285b23`, so the
   tag must not be deleted. It is local: pushing it (`git push origin
   after-date-split-frozen`) needs the owner's yes, and until it is pushed
   it exists on this machine only. Check with `git rev-parse
   after-date-split-frozen^{}`.

3. **Merge, when the owner says so.** `CLAUDE.md` prescribes
   `merge-side-pr`, which works on a pull request, so it needs the push the
   owner has not given yet. Until then the branch waits. When it runs,
   step 2's flags to expect: none under `data/`, none in `logs/`, the
   frozen plan untouched.

4. **Number the deviations** (`merge-side-pr` step 5,
   `scripts/merge_append_only.py`). Two placeholders: D?a (the table, a
   scope addition) and D?b (a worktree session read the main checkout's
   fire files). With main still at D102 they become D103 and D104; take
   the numbers the script prints. References sit in `DECISIONS.md`,
   `docs/plan_deviations.md`, `docs/methods_register.md`,
   `docs/data_dictionary.md`, `src/config.py` and the first lines of
   `src/fire_after_date.py`.
   **Note for the sibling:** the renumbering edits one token in the
   docstring of `src/fire_after_date.py`, after the frozen commit. The
   decision entry says a change to that module after `3285b23` is logged
   and told to the sibling before the next scoring day. The owner agreed
   (2026-10-13) that this is fine as a logged change: log it as a
   comment-only change (no line of code differs), and **report to the
   owner the commit on main that holds it** (the squash commit, or the
   renumbering commit if separate), so the sibling can record it.

5. **Checks after the merge**, from the main checkout: `python -m pytest`
   (472 passed on the branch), `python scripts/check_no_em_dashes.py`,
   `python scripts/check_plan_frozen.py`, `python -m src.pin_inputs
   --verify`, and the table's sha256 against the value above. The table
   is written once: do not rerun `python -m src.fire_after_date`
   (`run_guard.write_result` refuses, by design).

6. **Daily log** (`merge-side-pr` step 8): fold the session block below
   into the log of the day of the merge, placeholders replaced by the
   assigned numbers.

7. **Data guide artifact** (`CLAUDE.md`, end of every main-checkout
   session): add the new table and its columns
   (`docs/data_dictionary.md`, "Start-month split table"), the three
   settings (`AFTER_DATE_ISSUE_MONTHS`, `AFTER_DATE_RUN`,
   `AFTER_DATE_TABLE`) and the register row "Start-month split (sibling
   table)". No headline number: no split value is recorded on this side
   until the sibling has set its rules.

8. **The hand-over read in the sibling** is the owner's to approve there:
   the file, its sha256 and commit `3285b23`, with the sources' terms
   (MTBS, WFIGS, CNFDB; `DATA_SOURCES.md` notices 8 to 10).

## Open items

- **Scoring-day reading of a later retrieval's fire files.** Not built.
  `src.fire` reads the pinned downloads only; on a scoring day the
  outcome rebuild has to turn a stamped retrieval into pieces and pass
  them to `split_table(pieces, seasons, scoring_day_seasons=seasons)`.
  Tracked in the `prepare` text of `cnfdb_2025`, `season_2026_closes`,
  `verify_north` and `cnfdb_2027` on the rollout calendar.
- **NBAC: settled, nothing to build** (owner, 2026-10-13). NBAC has no
  ignition date; the sibling's rule names CNFDB polygons as the outcome
  source for BC, AB and YT, so a season's split arrives with its CNFDB
  outcome (2027 with CNFDB 2027, stated in the `cnfdb_2027` item).
- **Held-back seasons.** No figure for one was produced, printed or
  written. `scoring_day_seasons` has been used on made-up pieces only.

## Session block

```
### 13:30-15:20 · Claude Code (worktree: claude/sharp-jemison-a79067)
- Built results/tables/after_issue_date/fire_after_issue_date_region_year.csv
  for the sibling (D?a): 873 rows, five checks passed, sha256
  2978e316...9b137d, built at 3285b23 on a clean tree.
- New module src/fire_after_date.py and tests/test_fire_after_date.py (10
  tests; suite 472 passed). Scoring-day path fixed: held-back seasons are
  refused unless named in scoring_day_seasons; 3285b23 frozen for scoring.
- Read the main checkout's pinned fire downloads read-only through
  --data-root (D?b); nothing under data/ written.
- Records: DECISIONS.md, plan_deviations (D?a, D?b), methods register, data
  dictionary; open item added to four rollout calendar items; hand-off
  note docs/handoff_after_date_merge.md.
- Tagged 3285b23 locally as after-date-split-frozen (owner's yes); nothing
  pushed or merged. No held-back figure produced.
```
