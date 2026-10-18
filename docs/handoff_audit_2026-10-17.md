# Handoff to the main account: the final audit of 2026-10-17

Written at the end of the 2026-10-17 session, run from the owner's second
Claude account in the main checkout. This note is for the next main-account
session: what the audit found, what changed, what went live, and what the
second account could not do (the data guide). The day's log,
`logs/2026-10-17.md`, has the timed account.

## In short

- A read-only audit of the whole project ran as a 12-agent workflow
  (2,017 s): no high findings, six medium, 29 low (2 of them hypotheses);
  2 findings were refuted by the skeptics. Nothing found can move a
  registered number, and `results/tables/run1/` was not touched.
- All six medium findings are settled (five fixed, one flagged as the
  owner's prose), and 20 of the 29 low ones are settled (X2 with the
  mediums, 18 later, and B2, the same as D1). Nine low findings stay open
  (listed below).
- Uploaded on the owner's word (sixteenth upload): commit 3fa841e,
  66 files, 36,089,105 bytes, deployment 3fc1677d, 17:44. Checked live in
  a browser.
- Not done here: the data guide refresh (the page belongs to the main
  account; this account gets "artifact not found"). What to change is in
  "Data guide" below.
- Next free deviation number: still D110. No `ANALYSIS_PLAN.md` row was
  added; the plan checks pass.

## How the audit ran

Workflow `wf_509e8f57-c08`, every agent read-only (no edits, no pipeline
modules, no downloads, no uploads, scratch files outside the repo):

- Four area finders at high effort: measurement and climate; fire and
  statistics; site, figures and scripts; records and hard-coded values.
- A number tracer: three headline numbers followed from the site's inline
  Python back to `results/`, the code and `src/config.py`.
- One check runner: pytest (476 passed), the em-dash and frozen-plan checks
  (passed); `check_site.py` not run because it renders the site. `git
  status` was the same before and after.
- One skeptic per area at xhigh effort, told to disprove each high and
  medium finding; unsure counted as disproved.
- A completeness critic, then one targeted round on its two high gaps:
  - The served films against run1: the counts (52, 4 of 52, 0 of 25), the
    7 H2 estimates and intervals, the 4 Holm passes and the 4 close results
    match to 3 decimals; the closing dates match `rollout_calendar.json`.
  - The four Holm passes re-derived outside `src/stats.py` (a hand-coded
    Newey-West estimator and a statsmodels cross-check): H5 and H6 match
    run1 within 1e-11, the H1 family's flags agree.

Labels: CONFIRMED means shown by code reading plus a test, a run or a
traced value; HYPOTHESIS means not verified, with what would settle it.

## Medium findings (all CONFIRMED)

| ID | Where | Finding | Outcome |
|---|---|---|---|
| X1 | the films, Scene 3, about 48-56 s | Motion added a note, "AK, YT and NorCal are filed separately for not fitting cleanly into either group.", which the brief excluded and the D109 record did not mention; the site's diagram gives a different reason (hypotheses not yet set) | owner: "x1 a approved as stands"; `DECISIONS.md` 2026-10-17 "Final audit" (55db3c2) |
| D1 | `docs/methods_register.md` | ten status cells still said "no run yet" or "tests planned (Phase 4)" after run1 | updated with run1's counts, old wording kept with its date (455f061) |
| D2 | `docs/methods_register.md:109` | "Provisional values" (RONI revisions) said Code "none", "not handled" | points at `RONI_REVISION_MONTHS`, the `roni_revisions_close` calendar item and the index stamp; status "built, not yet used" (455f061) |
| C2 | `site/_quarto.yml` | the link card's alt text described the old strip-chart banner; the card is the region map | new alt text and comment, owner-approved (e4eccdf) |
| C3 | `site/methods.qmd` | measured numbers typed by hand ("about 42 seasons", "Alberta in 2016 to 2019", the coverage figure's alt text) | the two numbers are inline Python; a setup-cell check stops the build if `validation.csv` no longer gives the alt text's 77-91, 57 and 95; header comment updated (e4eccdf) |
| C5 | `site/methods.qmd`, "In the north only Alberta is drier" | reads against the page's own H1 table: PNW -29.0 mm and BC -13.7 mm are drier as point estimates; only Alberta's interval excludes zero | flagged, left as written: the owner's prose |

Refuted by the skeptics: C1 (the deploy draft gate reads visible text
only; that is recorded and tested) and C4 (the film's place outside
`results/` is the recorded design, and the served files are committed).

## Low findings fixed

| ID | Fix | Commit |
|---|---|---|
| X2 | "The film in words" now holds Motion's three on-screen lines (the Scene 3 note, the winter-rain title and subtitle, the burned-area subtitle), read off frames of both films; `scripts/prepare_film.py` `ADDED` and `--transcript`; a test ties `results/film/*.json` to the code | 455f061 |
| A2, D5 | AK JJA mean 10.2 °C (was 10.3) in the register and data dictionary; station correlations re-read (z 0.77-0.95, percent 0.78-0.94) | eae989e |
| A3 | config comment: Alaska spans 52.86-71.41N after the clip | eae989e |
| A5 | register: the audit's SPEI refit re-measure (up to 0.0143 main, 0.0259 north, in May-Jul, Sep, Oct; Feb and Aug within 0.001) beside the 0.003 claim | eae989e |
| B1 | data dictionary: no fire-table row is "MTBS+WFIGS" | eae989e |
| B4 | data dictionary: `note` holds distinct bootstrap resamples, not permutations | eae989e |
| D4 | `DATA_SOURCES.md`: the Alaska divisions row no longer says nothing derived is published | eae989e |
| D6 | register rows for the MTBS-WFIGS pair comparison and the link-card map settings | eae989e |
| D11 | deviations log header: D32-D34 were never assigned | eae989e |
| D3 | `fit_driscoll_kraay` reads `POOLED_COV_TYPE` and `USE_T` (same values) | eae989e |
| D7 | `scripts/stats_size_check.py` reads its years and level from config (not rerun) | eae989e |
| C10 | `MIN_FIRE_HA` in the season-series label | eae989e |
| C12 | the coverage chart's axis widens below 40% (unchanged at today's values) | eae989e |
| C6 | the film caption rounds the length once (no "1 min 60 sec") | eae989e |
| C7 | `check_site.py` checks video posters (CSS `url()` targets still not) | eae989e |
| C8 | `plan_frozen_problems` checks the deviations log against every commit since the tag that changed the plan, not only HEAD; empty placeholder rows skipped | eae989e |
| A4, C11 | tests: NaN cells inside a mask in `regional_mean`; map legend labels against the `MAP_LAYERS` edges | eae989e |
| B2 | the same as D1 | 455f061 |

After these: 481 tests pass; `check_site.py`: 5 pages, all links resolve.

## Low findings still open

| ID | Where | Finding | Why left |
|---|---|---|---|
| A1 | `src/whiplash.py:374` | the per-cell SPEI cache is reused without checking it covers the data's months, cells or settings | **settle before the 4 November item**, which adds months; not a small change |
| D8 | `src/rollout.py:176` | the 2026 season close (31 Jan 2027) and some month keys are typed, not derived | a code change to the calendar and its test |
| D10 | `src/regions.py:36` | region polygons read from a live Natural Earth URL, with no saved raw copy or pin | needs a download script and a pin |
| B5 | `src/stats.py` `loyo_prediction` | rows with a missing predictor are dropped silently | a missing outcome is allowed on purpose, so a blanket check would break it; needs a predictors-only check |
| E4 | `scripts/build_dashboard.py:116` | BC's typical season is rounded twice: 39,776 ha on the dashboard and in the Motion data, 39,775 on the site | rebuilds the dashboard and the Motion data |
| E2 | `site/methods.qmd:651` | the page says each test's size is printed beside it; its results table has no size column | owner's call: add the column or reword |
| C9 | `site/index.qmd:36` | the home page's "next to arrive" is fixed at build time; the tracker uses the visitor's date | site behaviour; owner's call |
| B3 | `scripts/stats_size_check.py:10` | the size simulation's predictor persistence (0.27) is below one real predictor's (PNW precip_anom_lag1, 0.286) | needs a new simulation; the effect is well under a point of size |
| D9 | `src/config.py:729` | config says ONI is built from ERSST v6; the data dictionary says v5 (HYPOTHESIS) | read CPC's ONI page to settle |

E1, the number tracer's copy of C5, was merged with it.

## Found along the way

- **The Map page carries no Natural Earth credit** (none in its HTML on
  the live site, 2026-10-17). The deploy skill's domain rules ask for a
  credit wherever a map appears; Natural Earth itself requires none. Not
  new today. Owner's wording to add.
- No log exists for 2026-10-14; a short account of that day is in
  `logs/2026-10-17.md` (from git and `DECISIONS.md`).
- `docs/plan_deviations.md` D109 still says "Actual: to come"; the film
  went live on 2026-10-14. Needs a superseding entry (D110 is free).
- The `site` preview in `.claude/launch.json` serves `site/_site/`, an old
  render, not the staged `dist/site/`.
- Claude Code's permission check refused `scripts/deploy_site.py` (even
  without `--upload`) as a "Production Deploy" until the owner gave
  permission in chat.

## Data guide (for the main account)

https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P could not be read from
the second account. Refresh it in the next main-account session from
`docs/data_dictionary.md`, `src/config.py`, `docs/methods_register.md` and
`results/tables/`, and set the snapshot commit to 3fa841e or later. What
changed on 2026-10-17:

- **RONI revisions:** now a handled control. `RONI_REVISION_MONTHS = 2`,
  read by the `roni_revisions_close` calendar item (from 2027-05-14), with
  the index stamp that keeps a rebuild on the retrieval the forecast read.
  Status: built, not yet used.
- **Film transcript (`results/film/film_<theme>.json`):** 11 lines now,
  the 8 approved card lines plus Motion's 3 on-screen lines. Approved by
  the owner as they stand.
- **Alaska's summer mean:** 10.2 °C for JJA 1951-2025 (it was given as
  10.3).
- **The `note` column of the result tables:** for H1, H2 and the
  strong-only rows, the number of distinct bootstrap resamples of the El
  Niño group (10 for 3 winters), not a permutation count.
- **Fire table `source`:** "MTBS+WFIGS" is a possible value but no
  committed row has it.
- **SPEI per-cell refit:** reproducible to about 0.03 SD per cell in May
  to October; February and August within 0.001, so the registered DJF and
  JJA values are unaffected.
- **Two settings now in the register:** the MTBS-WFIGS pair comparison
  (`SOURCE_PAIR_YEARS` 2021-2024, one-to-one pairs only; WFIGS over MTBS
  0.9587 to 0.9862) and the link-card map (`CARD_MAP_*`: 2 km, 100 km2,
  15 km inland, 150 km runs; display only).
- **Headline numbers:** unchanged (52 tests, 4 significant after Holm,
  0 of the 25 that set El Niño against burned area).

## Commits

55db3c2, 455f061, e4eccdf, 84f1c57, eae989e, 3fa841e, all pushed to
origin `main`; this note and the upload's log line come after.
