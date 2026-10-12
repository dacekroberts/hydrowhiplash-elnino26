# Session 10 kickoff: design system, rollout calendar, after run1

Written at the end of session 9 (2026-10-12). Part 1 is the handoff; Part 2
is the prompt to paste into a new Claude Code session in the main checkout;
Part 3 is the prediction-model side session that runs beside it.

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
  significant. The nulls are reported, not dropped.
- The runner is `src/run_hypotheses.py` (`--run runN`; refuses a run
  folder that already holds an output). ONI is read through
  `pin_inputs.enso_raw_path` (D82).
- `ACTION_PLAN.md` Phase 4: Headlines 1 to 4, the supporting item and
  the full-record view are ticked
  (`results/figures/burned_area_anomaly_series_roni.png`,
  `python -m src.fire_figures`). One box is open: Methods and
  limitations.
- **Three private pages, all read by the owner on 2026-10-12** ("looks
  good for starters ... the content is good"):
  - Results page, https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk:
    built by `scripts/build_results_page.py --run run1 --out <file>`
    from `scripts/results_page/template.html`, no number typed. Each
    section states its registered hypothesis and predicted direction;
    keep that for every later run. `NOTES` in the script holds the
    owner's reading per hypothesis and is empty.
  - Methods draft, https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf:
    a reading copy of `site/methods.qmd`, which is marked as a draft.
    Result numbers are read at render time from `run1`; settings come
    from `results/tables/site_settings.json` (`python -m
    src.site_settings`; a test fails if it is stale).
  - Roadmap and data guide (URLs in Part 2), both current.
  Neither new page has been viewed in a browser by Claude.
- **The methods draft is not publishable yet.** Eight numbers marked
  with a dagger are typed from `DECISIONS.md` and the methods register
  and need a committed table each. The fire and snow-station notices
  were copied from `DATA_SOURCES.md` and need confirming with the
  read-licence skill; the ERA5-Land hourly entry, the CanSWE paper
  citation and notice 13 are missing. The wording is the owner's to
  sign off (`DECISIONS.md` 2026-10-12 "Full-record burned-area view").
- **Flag, nothing changed:** the frozen plan says the 2027 forecast
  comes from the H3a model, and H3a showed no skill over a trend-only
  model in `run1` (-0.03 to +0.01). Any move away from it goes through
  the post-results protocol.

**Decided by the owner on 2026-10-12** (`DECISIONS.md` 2026-10-12
"Prediction model is next" and "Prediction model scope agreed"):

- Session 10 is design-focused: "i think we will totally redesign the
  look of final site with design system in session 10, but the content
  is good."
- The rollout timetable for readers lives on the tracker page.
- Pings are scheduled tasks, a few days ahead of each date; arrivals
  with no fixed date are folded into the reminder nearest to when they
  are best checked. Nothing is scheduled yet.
- The prediction model is the next analysis (D83), scope agreed, built
  beside session 10 as a side session on branch
  `side/prediction-model`. Part 3.

**To put to the owner at the start of session 10, each with a
recommendation:**

- **Design system.** One set of fonts, colours and components for the
  site, the results page, the methods page, the data guide and the
  roadmap. The private pages already share Archivo, IBM Plex Sans and
  IBM Plex Mono and a blue and ember palette; the owner expects a full
  redesign, not a tidy-up. The owner has two design systems of their
  own from other projects ("Link Station Commercial: Night Line",
  "Storefronts Near Transit") as reference for how they like these
  built.
- **Hosting.** Streamlit, or the owner's own domain with Cloudflare R2.
  The project rule today is a static Quarto site that only reads
  `results/`, which fits the second; a Streamlit app would be a scope
  change to log.
- **Map page** (owner's idea): all seven regions with a toggle per
  dataset (fire, snowpack, rainfall, temperature) and a legend drawn
  for each that shows the general trend in that sphere. A scope
  addition, not started; it would read the committed region x year
  tables and the region polygons.

**To build with the owner in session 10: the rollout calendar.** Owner:
"session 10 might need to scaffold exactly what the site is waiting for
and when, setting up pings for me in advance so i can prepare the site
for the changes." One dated list, kept where the code can read it, of
every arrival the site waits on and what each one changes on the site.
The tracker page's timetable and the scheduled reminders both read that
list, so they cannot disagree. Dates the project already has:

- each month's ERA5-Land data by the 7th (`TRACKER_DATA_DAY`);
- the hard-line item in early November 2026;
- the full winter and the DJF 2027 index in early March 2027;
- the 1 April snowpack about 8 April 2027;
- the dated forecast stages (D76);
- CanSWE v9 around March 2027; CNFDB 2025 when released (no date);
- the 2027 fire season and its fall check; California after January
  2028.

**Next work, in order, after the choices and the calendar:**

1. Later downloads to stamped paths (D73, audit round 5 S1): owner,
   2026-10-12: "built after the registered runs are committed and
   before the hard-line item". Not built yet.
2. The hard-line item (early November 2026, ACTION_PLAN Phase 5, D55):
   lag setting 3 to 1 month, download every published 2026 month, refit
   SPEI, rebuild, report the changed numbers. Never over a pinned file.
3. Committed tables for the eight typed numbers in the methods draft,
   and the notices confirmed.
4. D77, after the runs: the delegated-build pilot (the pin report after
   `--rebuild`) and the methods-page line on where DeepSeek was used.
   Each DeepSeek call needs its own yes; flash at peak hours, pro
   off-peak (memory note).
5. The site charts for Headlines 1 to 4, in the new design.
6. From the portfolio review: three methods-page items as one scope
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
Session 10 for hydrowhiplash-elnino26: design system, hosting and the
rollout calendar, after run1.

1. Orient: read CLAUDE.md, docs/session10_kickoff.md (Part 1),
   logs/2026-10-12.md, the top of DECISIONS.md (2026-10-12 entries),
   docs/plan_deviations.md D77-D83, docs/post_results_protocol.md,
   docs/data_dictionary.md sections 8a and 8b, site/methods.qmd,
   ANALYSIS_PLAN.md (frozen: never edit above the deviations log) and
   ACTION_PLAN.md Phases 4 and 5. Read with the Artifact tool (action
   "read"):
   the roadmap, https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   the results page, https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk
   the methods draft, https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D84. The prediction model runs beside this session
   as a side session (Part 3); don't build it here.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is early November or later, read the hard-line item in Part 1
   before anything else.

5. Bring me the three choices in Part 1 (design system, hosting, the
   map page), each with a recommendation. I expect a full redesign of
   the site's look; the content of the results page and the methods
   draft stands. Nothing is adopted without my yes.

6. Build the design system with me, then apply it to the site, the
   results page template and the methods page so they share one theme.

7. Scaffold the rollout calendar with me: every date the site is
   waiting on and what changes on the site at each, in one list the
   code can read. Put the timetable for readers on the tracker page,
   read from that list. Then set up the pings as scheduled tasks a few
   days ahead of each date, folding undated arrivals into the nearest
   sensible check. Show me the list of reminders and ask before
   scheduling anything.

8. Then the work list in Part 1, in order, starting with the stamped
   download paths. Ask me before any run that reads polygons, and before
   every DeepSeek call.

9. My interpretation of the results is mine to write. Discuss the
   numbers, flag stale or inconsistent wording, and suggest; don't
   rewrite.

10. End of session: daily-log skill, python scripts/log.py list,
    python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
    python scripts/check_site.py, commit and push; merge the
    prediction-model PR with the merge-side-pr skill if it is ready;
    refresh the data guide artifact
    (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild the
    results page and the methods reading copy if they changed, and offer
    to update the roadmap artifact; write the next kickoff the same way.
```

## Part 3 · Prediction model side session (D83)

Runs beside session 10 in a named worktree, not an auto-named one:
branch `side/prediction-model`, created from `main` at the start
(owner: "started in a proper worktree (not random)"). It needs no
`data/`: it reads only committed tables in `results/tables/`.
Side-session rules apply: no edits to `logs/`, the session block goes
in the PR description, new deviations use a placeholder number.

**Scope agreed by the owner on 2026-10-12** ("i agree with proposed
scope"; `DECISIONS.md` 2026-10-12 "Prediction model scope agreed"). The
side session writes it up as a one-page spec and commits that before
any fit:

- *Version 1, a pooled linear model.* Predictors known before the fire
  season: the winter index, October to March precipitation, 1 April
  snowpack, winter SPEI-3, and a year trend. One model across the seven
  regions with region terms (291 region-seasons instead of about 42 per
  region), with shrinkage (ridge) so correlated predictors do not blow
  up. Scored only on seasons it has not seen: expanding window from 20
  training seasons, every region predicted for the same year at once.
  Baseline: the year trend alone. Reported: skill against the baseline
  with an interval, and how often its 80% interval held the real value.
  The 2027 season is the first real test.
- *Outcome, two forms (owner: "add yes no"):* total log burned area,
  and a yes or no outcome, whether the season falls in the top third of
  that region's seasons. The cut for the top third is taken from the
  training seasons only at each step, so the unseen year never sets its
  own bar. Scored against the base rate (one in three).
- *Hindsight run (owner: "yes"):* the same model with June to August
  temperature added, in a separate, clearly labelled run. It cannot be
  used to forecast; it shows how much of the missing skill is summer
  weather.
- *Alaska and Yukon (owner: "pool them report skill separately"):* in
  the one pooled model with the other five regions; skill is reported
  per region and for the two groups apart.
- *Version 2, machine learning, only if version 1 beats the trend.* A
  small tree ensemble (gradient boosting or a random forest) on the same
  inputs and the same scoring, to ask one question: do interactions and
  thresholds add anything a linear model misses? With 291 rows it can
  easily memorise, so it is judged only on the unseen years, against
  version 1.
- *Not in either version:* summer weather as a forecasting predictor
  (not known in spring; the hindsight run is labelled apart), anything
  trained on El Niño years only, and any claim that replaces a
  registered test.
- *Still to fix in the spec, before any fit:* the shrinkage setting and
  how it is chosen inside the training seasons only; the exact skill
  measure for the yes or no outcome; the rule that decides whether
  version 2 is tried.

Expectation to state up front: in `run1` the single-predictor models
beat the trend by at most 0.06 on unseen years, so a small gain or none
is the likely outcome, and either is reported plainly.

```text
Side session for hydrowhiplash-elnino26: the seasonal-outlook prediction
model (D83), exploratory.

1. Work on branch side/prediction-model in its own worktree, created
   from main. Do not use an auto-named worktree. This session needs no
   data/: it reads only committed tables in results/tables/.

2. Orient: read CLAUDE.md, docs/session10_kickoff.md (Parts 1 and 3),
   docs/plan_deviations.md D83, DECISIONS.md 2026-10-12 "Prediction model
   is next" and "Prediction model scope agreed",
   docs/post_results_protocol.md section 2, ACTION_PLAN.md "Later
   extensions", docs/data_dictionary.md section 8a, and
   results/tables/run1/validation.csv. Tell me in 3-4 lines what this
   session covers.

3. This analysis was planned after run1 was seen. It is exploratory,
   uncorrected and reported apart from the registered tests; it never
   replaces one, and the registered 2027 forecast stays the H3a model.
   Nothing in results/tables/run1/ is edited.

4. Before fitting anything, write the scope I agreed in Part 3 as a
   one-page spec and commit it, then bring me the three points still to
   fix (the shrinkage setting, the skill measure for the yes or no
   outcome, the rule for trying version 2), each with a recommendation.
   Explain each concept as it comes up. Nothing is adopted without my
   yes.

5. Then build version 1 (both outcomes, the hindsight run, skill per
   region and for Alaska and Yukon apart) in src/ as plain functions
   with tests on synthetic data. Read tables only from results/tables/
   and write the outputs to their own folder under results/tables/ with
   a provenance record. Report skill with intervals, and say plainly if
   the model does not beat the trend. Try version 2 only if the agreed
   rule says so.

6. Side-session rules: do not edit logs/; a new deviation gets a
   placeholder number (D\?a), never a real one.

7. End: python -m pytest, python scripts/check_no_em_dashes.py,
   python scripts/check_plan_frozen.py, then open a PR with the session
   block in its description.
```
