# Session 10 kickoff: Phase 4, after run1

Written at the end of session 9 (2026-10-12). Part 1 is the handoff; Part 2
is the prompt to paste into a new Claude Code session in the main checkout.

## Part 1 · Handoff

**Where things stand.**

- **The registered runs are made and committed**, 25 days before the
  D73 deadline: `results/tables/run1/`, commit 4951e41, tag
  `registered-run1` (`DECISIONS.md` 2026-10-12 "run1: the first
  registered runs"). `registered_tests.csv` (52 rows, 12 Holm families),
  `reported_beside.csv` (205 rows), `validation.csv` (39 rows), a
  provenance file beside each, `conda_list_explicit.txt`.
- **Nothing in `run1/` is edited, renamed or deleted.** Any change that
  can move a registered number follows `docs/post_results_protocol.md`:
  a deviations-log row saying "decided after results were seen" and what
  had been seen, a rerun in `run2/`, and `changes_from_run1.csv`.
- After Holm at 0.05, 4 of 52 are significant: H1 SoCal (El Niño
  winters wetter), H5 lag 0 AB (a wetter winter, less burned area the
  same year), H5 lag 1 NorCal (a wetter winter, more burned area the
  next year), H6 SWE NorCal (more snow, less burned area). No test of
  ENSO on burned area (H2, H3a, H3b, H4, C2) and no C1 test is
  significant. The nulls are reported, not dropped. The owner has not
  written any interpretation yet; that prose is the owner's.
- The runner is `src/run_hypotheses.py` (`--run runN`; refuses a run
  folder that already holds an output). ONI is read through
  `pin_inputs.enso_raw_path` (D82).
- A results page format exists: `scripts/build_results_page.py --run
  run1 --out <file>` fills `scripts/results_page/template.html` from the
  run folder, no number typed. Published privately at
  https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk. It was
  syntax-checked, not viewed in a browser; the owner has not reviewed
  it. `NOTES` in the script holds the owner's reading per hypothesis and
  is empty.

**Owner's answers on 2026-10-12, after reading the results page and the
methods draft** (`DECISIONS.md` 2026-10-12 "Prediction model is next"):

- "looks good for starters. i think we will totally redesign the look of
  final site with design system in session 10, but the content is good."
  Session 10 is design-focused.
- The open choices below are put to the owner at the start of session
  10, each with a recommendation.
- The rollout timetable lives on the tracker page.
- Pings are scheduled tasks, a few days ahead of each date; arrivals
  with no fixed date are folded into the reminder nearest to when they
  are best checked.
- The prediction model is next (D83): scoped with the owner first, then
  built beside session 10 as a side session. Part 3.

**Open, for the owner to decide (raised 2026-10-12):**

- A design system so the site, the results page, the data guide and the
  roadmap share one theme. The three artifacts already share Archivo,
  IBM Plex Sans and IBM Plex Mono and a blue and ember palette. A good
  moment is the start of session 10, before any site page is written.
- Hosting: Streamlit, or the owner's own domain with Cloudflare R2. The
  project rule today is a Quarto site that only reads `results/`; a
  Streamlit app would be a scope change to log.
- A site page idea from the owner (2026-10-12): a map of all seven
  regions with a toggle per dataset (fire, snowpack, rainfall,
  temperature) and a legend drawn for each that shows the general trend
  in that sphere. A scope addition to the site plan, not started; it
  would read the committed region x year tables and the region
  polygons, and belongs with the design system choice.
- The results page states each registered hypothesis and its predicted
  direction above its results (owner's request); keep that for every
  later run's page.
- **A rollout calendar and pings (owner, 2026-10-12):** "session 10
  might need to scaffold exactly what the site is waiting for and when,
  setting up pings for me in advance so i can prepare the site for the
  changes." To build with the owner: one dated list of every arrival
  the site waits on and what each one changes on the site (each
  month's ERA5-Land data by the 7th, `TRACKER_DATA_DAY`; the hard-line
  item in early November; the DJF 2027 index and full winter in early
  March 2027; the 1 April snowpack about 8 April; the forecast stages
  of D76; CanSWE v9 around March 2027; CNFDB 2025 when released; the
  2027 fire season and its fall check, California after January 2028),
  kept in one place the code can read, then reminders ahead of each
  date. How far ahead, and through what (scheduled tasks, calendar),
  is the owner's choice; nothing is scheduled yet.
- **A page or site feature on the rollout timetable (owner,
  2026-10-12):** "some sort of page or site feature dedicated to
  informing readers about the rollout timetable." A scope addition to
  the site plan, not started. It should read the same dated list as the
  pings, so the public timetable and the reminders cannot disagree. The
  tracker page already has three states and a countdown (PRs #18, #19);
  decide whether the timetable lives there or on its own page.
- `ACTION_PLAN.md` Headlines 1 to 4 and the "Supporting" item (lag
  test, block bootstrap, Holm/BH) were ticked on 2026-10-12 on the
  owner's word; all were computed in `run1`. The full-record view is
  built (`results/figures/burned_area_anomaly_series_roni.png`). Open in
  Phase 4: the Methods and limitations section. A full draft is in
  `site/methods.qmd`, marked as a draft (private reading copy:
  https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf); it waits on the owner's edit
  and approval, on committed tables for the eight numbers marked with a
  dagger, and on the notices being confirmed with the read-licence
  skill (`DECISIONS.md` 2026-10-12 "Full-record burned-area view").

**Next work, in order:**

1. Later downloads to stamped paths (D73, audit round 5 S1): owner,
   2026-10-12: "built after the registered runs are committed and
   before the hard-line item". Not built yet.
2. The hard-line item (early November 2026, ACTION_PLAN Phase 5, D55):
   lag setting 3 to 1 month, download every published 2026 month, refit
   SPEI, rebuild, report the changed numbers. Never over a pinned file.
3. D77, after the runs: the delegated-build pilot (the pin report after
   `--rebuild`) and the methods-page line on where DeepSeek was used.
   Each DeepSeek call needs its own yes; flash at peak hours, pro
   off-peak (memory note).
4. The full-record view and the charts for Headlines 1 to 4; the Methods
   and limitations section, every null included.
5. From the portfolio review: three methods-page items as one scope
   addition (next free deviation number).

**Open, low:** pins walk one folder level (review F3); two tests need
the tag `analysis-plan-frozen` in the clone; one needs `data/`.

**Carried over, unchanged:** no task goes to the DeepSeek worker until
the owner says so; `data/` stays out of reach of every DeepSeek plan;
ask before any run that reads polygons (shared machine memory); the
going-public question is a leaning, not a decision.

**Next free deviation number: D84.** The frozen plan's deviations log is
at row 19.

## Part 2 · Prompt for session 10

```text
Session 10 for hydrowhiplash-elnino26: Phase 4, after run1.

1. Orient: read CLAUDE.md, docs/session10_kickoff.md (Part 1),
   logs/2026-10-12.md, the top of DECISIONS.md (2026-10-12 entries),
   docs/plan_deviations.md D77-D82, docs/post_results_protocol.md,
   docs/data_dictionary.md section 8a, ANALYSIS_PLAN.md (frozen: never
   edit above the deviations log) and ACTION_PLAN.md Phases 4 and 5.
   Read the roadmap artifact with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   and the results page: https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D84. This session is design-focused; the prediction
   model runs beside it as a side session (Part 3).

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is early November or later, read the hard-line item in Part 1
   before anything else.

5. Bring me the open choices in Part 1 (design system, hosting, the
   Headline boxes, the map page, the rollout timetable page) with a
   recommendation for each. Then scaffold the rollout calendar with me:
   every date the site is waiting on, what changes on the site at each,
   and the pings I want ahead of each. Ask before scheduling anything.
   Nothing is adopted without my yes.

6. Then the work list in Part 1, in order, starting with the stamped
   download paths. Ask me before any run that reads polygons, and before
   every DeepSeek call.

7. My interpretation of the results is mine to write. Discuss the
   numbers, flag stale or inconsistent wording, and suggest; don't
   rewrite.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   commit and push; refresh the data guide artifact
   (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild the
   results page if a new run exists, and offer to update the roadmap
   artifact; write the next kickoff the same way.
```

## Part 3 · Prediction model side session (D83)

Runs in a worktree beside session 10. It needs no `data/`: it reads only
committed tables in `results/tables/`. Side-session rules apply: no edits
to `logs/`, the session block goes in the PR description, new deviations
use a placeholder number.

**Scope proposed to the owner on 2026-10-12, not yet agreed:**

- *Version 1, the registered-style model.* Outcome: log burned area per
  region and season. Predictors known before the fire season: the winter
  index, October to March precipitation, 1 April snowpack, winter
  SPEI-3, and a year trend. One pooled linear model across the seven
  regions with region terms (291 region-seasons instead of about 42 per
  region), with shrinkage (ridge) so correlated predictors do not blow
  up. Scored only on seasons it has not seen: expanding window from 20
  training seasons, every region predicted for the same year at once.
  Baseline: the year trend alone. Reported: skill against the baseline
  with an interval, and how often its 80% interval held the real value.
  The 2027 season is the first real test.
- *Version 2, machine learning, only if version 1 beats the trend.* A
  small tree ensemble (gradient boosting or a random forest) on the same
  inputs and the same scoring, to ask one question: do interactions and
  thresholds (for example, snowpack mattering only in warm summers) add
  anything a linear model misses? With 291 rows it can easily memorise,
  so it is judged only on the unseen years, against version 1.
- *Not in either version:* summer weather as a predictor (not known in
  spring), anything trained on El Niño years only, and any claim that
  replaces a registered test.
- *Open for the owner:* whether the outcome stays total burned area or
  also asks a yes or no question ("a season in the top third?"), which
  is often easier to predict and easier to explain; whether Alaska and
  Yukon are pooled with the rest; whether summer temperature is added
  in a separate, clearly labelled "hindsight" run to show how much of
  the missing skill is summer.

```text
Side session for hydrowhiplash-elnino26: the seasonal-outlook prediction
model (D83), exploratory, in a worktree.

1. Orient: read CLAUDE.md, docs/session10_kickoff.md (Parts 1 and 3),
   docs/plan_deviations.md D83, DECISIONS.md 2026-10-12 "Prediction model
   is next", docs/post_results_protocol.md section 2, ACTION_PLAN.md
   "Later extensions", docs/data_dictionary.md section 8a, and
   results/tables/run1/validation.csv. Tell me in 3-4 lines what this
   session covers.

2. This analysis was planned after run1 was seen. It is exploratory,
   uncorrected and reported apart from the registered tests; it never
   replaces one, and the registered 2027 forecast stays the H3a model.
   Nothing in results/tables/run1/ is edited.

3. Before fitting anything, settle the scope in Part 3 with me and
   commit it as a one-page spec: the outcome, the predictors (only what
   is known before the fire season), the model, how it is scored on
   years it has not seen, the trend-only baseline, what would count as
   skill, and the rule for whether a machine-learning version 2 is
   tried. Explain each concept as it comes up. Nothing is adopted
   without my yes.

4. Then build version 1 in src/ as plain functions with tests on
   synthetic data, read tables only from results/tables/, and write its
   outputs to their own folder under results/tables/ with a provenance
   record. Report skill with intervals, and say plainly if the model
   does not beat the trend.

5. End: checks (pytest, check_no_em_dashes.py, check_plan_frozen.py),
   open a PR with the session block in its description. Do not edit
   logs/.
```
