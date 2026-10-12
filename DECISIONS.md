# Decisions

Judgment calls, with the reasoning and the alternatives rejected. Newest
first. Never edit an old entry: add a new one that supersedes it and links
back. Changes to pre-registered tests go in the deviations log in
`ANALYSIS_PLAN.md` instead.

**Entry format:** one bullet per decision. A bold one-sentence statement, then
prose with real numbers, rejected alternatives and affected files. Neutral
past tense ("Decided", "Found", "Dropped"), no first person.

**What qualifies:** judgment calls with rejected alternatives, scope
changes, data sources added or ruled out, bug fixes with numeric
consequences (old and new numbers), superseded decisions, verification runs
with counts. **Not:** copy edits, routine mechanics, open work (that's
`ACTION_PLAN.md`).

## Changes

### 2026-10-12 - Stamped paths: one parallel tree

- **Decided (owner, "option a"): everything fetched or rebuilt after
  run1 goes into one parallel tree, and no pinned file is written
  (D73, D88).** Downloads: `data/raw/later/<stamp>/<source folder>/`,
  the stamp being the retrieval date. Rebuilt tables:
  `results/tables/tracker/<stamp>/`. Rejected stamped downloads with
  tables rebuilt in place under a logged re-pin: less code, but
  `results/tables/` would then hold files run1 did not read. Rejected a
  release stamp in each file name (as NBAC's own names carry): only NBAC
  publishes one, and a folder per retrieval keeps each source's file
  names unchanged for the readers.
- **Built `src/later.py` and a `--stamp` option on eleven download
  scripts** (the index, ERA5-Land monthly and 1 April, MTBS, WFIGS,
  CNFDB, NBAC, CanSWE, NRCS, BC and Yukon snow). A stamped folder is
  closed by `retrieval.json` (size and sha256 of each file) and is never
  written again; an interrupted run leaves no record and can be re-run
  under the same stamp. Without the flag every script behaves as
  before, including the refusal to overwrite a pinned file. The Alaska
  climate-division boundaries were left without the flag: fixed
  polygons, no later release expected.
- **Decided that a stamped index retrieval fetches both RONI and ONI
  and writes nothing to `data/processed/`**, where the classified
  winters are pinned. The frozen plan's "DJF 2027 value in CPC's first
  release after February 2027, with its retrieval date recorded" is
  then the stamped folder itself.
- **Decided that a stamped ERA5-Land run requests only the years with
  no full-year file on disk** (today: 2026) and leaves the existing
  partial file in place, so the pinned climate tables stay rebuildable
  from the files they were made from.
- **Not built, left for the hard-line item:** the builders (`era5`,
  `climate_vars`, `snow`, `whiplash`) do not yet read a stamped folder
  on top of `data/raw` or write to `tables_dir(stamp)`. Tested on
  made-up files only (9 tests); no download was run and no polygon was
  read. Files: `src/later.py`, `src/config.py`, the eleven
  `src/download_*.py`, `tests/test_later.py`.

### 2026-10-12 - Session 10: rollout calendar

- **Decided to keep the rollout calendar as a list built in code from
  the settings in `src/config.py`, written to
  `results/tables/rollout_calendar.json` (D87).** `src/rollout.py`
  derives every date a setting already fixes: the six monthly ERA5-Land
  arrivals (October to March, by the 7th of the next month), the 1 April
  snowpack (1 April plus `ERA5_HOURLY_LAG_DAYS`, 8 April 2027) and the
  two verification dates (after 31 October 2027 for PNW, BC, AB, AK and
  YT; after 31 January 2028 for NorCal and SoCal). Five arrivals with no
  fixed date get an expected window in `ROLLOUT_WINDOWS`. Rejected a
  hand-written YAML or JSON list: it would repeat dates the config
  already holds, and the site reads only `results/`. Rejected typing the
  list into `config.py` itself: 18 items with prose would bury the
  settings. Files: `src/rollout.py`, `src/config.py`,
  `tests/test_rollout.py`, `site/tracker.qmd`, `src/theme.py`.
- **Decided that an item is marked done only when a committed file under
  `results/` shows it**, in keeping with "the page picks its state from
  what the pipeline has written to `results/`, so nobody flips it by
  hand" (2026-10-05). Two items are done (the freeze, run1). The other
  16 carry no evidence file yet, because the tracker tables that would
  show a month's arrival are not built; each gets its evidence when its
  code is written. The "next" mark is set in the visitor's browser from
  the date.
- **Found while listing the arrivals, none of it changed:** (1) the
  frozen plan fixes the forecast's input as "the DJF 2027 value in CPC's
  first release after February 2027, with its retrieval date recorded",
  so that release has to be fetched to a stamped path the day it
  appears; CPC's posting day has not been measured, and the window
  1 to 14 March 2027 is an expectation. (2) RONI values may be revised
  for two months, so the December to February value can move until
  about 14 May 2027; revisions are reported, not substituted. (3) On its
  release record (2024 data in files dated 28 January 2026) CNFDB 2027
  would arrive about January 2029, so BC, AB and YT have no registered
  burned-area source for the fall 2027 verification; open, the owner's
  to decide before October 2027. (4) No plan says whether the 2026
  season is redrawn once California's closes at the end of January
  2027; listed as an item with no task. (5) D76 sets no number of
  forecast stages; the list marks two, as a proposal.
- **Built the tracker page as a timetable only** (`site/tracker.qmd`,
  marked draft; its sentences and the wording of each row are drafts
  for the owner). The region x month tiles and the countdowns wait for
  the hard-line item. Twelve of the 18 items are shown to readers; the
  six left off are the undated releases, the 2026 season's close and
  the end of the index revisions.

- **Decided (owner): the 2027 forecast is published in two stages
  (D76, D87).** The first at CPC's first RONI release after February
  2027 (expected 1 to 14 March), from the registered H3a model; the
  final after the 1 April snowpack (about 8 April 2027), adding the two
  secondary single-predictor H6 forecasts. Rejected one stage in April:
  the H3a forecast needs only the index, and a dated March statement is
  the earlier record. Open for the first stage's wording: H3a showed no
  gain over a trend-only model in run1 (-0.03 to +0.01).
- **Decided (owner): ten reminders scheduled as one-time tasks, three
  days ahead of each date at 9:00 local, look and report only.** Each
  reads its item from `rollout_calendar.json` by id, quotes it, and
  reads the publishers' public pages (CNFDB folder, CanSWE record, CPC
  index file) for the undated arrivals; none downloads, edits, commits
  or reads polygons. Dates: 2026-11-04, 2026-12-04, 2027-01-04,
  2027-02-04, 2027-02-26 (the index), 2027-03-04, 2027-04-04 (with the
  snowpack), 2027-05-11 (index revisions), 2027-10-28, 2028-01-28. Task
  ids start `whiplash-rollout-`; they live in the owner's
  `~/.claude/scheduled-tasks/`, outside the repository, and run only
  while the desktop app is open (a missed one runs at the next launch).
  If a date in the calendar changes, the matching task has to be moved
  by hand: the tasks read the items, not their own run dates.

### 2026-10-12 - Session 10: design system, hosting and the map page

- **Decided (owner, session 10): a new design system for this project,
  kept as a Design System artifact with one tokens file in the
  repository that the site, the results page template, the methods page
  and the figures read (D86).** Owner's direction: "integrate color
  green as essential (ecosystems) with a natural earth vibe. pop colors
  are the red and blue for fire/rainfall data". Rejected adapting Night
  Line or Storefronts Near Transit (both built for transit subjects) and
  a tokens file with no browsable reference. Nothing in the look is
  adopted until the owner has seen a draft.
- **Decided (owner): the site is hosted as the static Quarto build on
  the owner's own domain through Cloudflare, not on GitHub Pages and not
  as a Streamlit app (D84).** Rejected Streamlit: it needs a running
  Python server and would replace the Quarto build that reads only
  `results/`. Cloudflare's documentation (read 2026-10-12) recommends
  Workers static assets over Pages for new static sites, and requires
  the domain's nameservers to be on Cloudflare; no R2 page read states
  that a bucket serves `index.html` for a folder URL, so R2 is kept for
  large files only, if the map page needs them. The exact setup is
  settled when the first piece is ready to publish; nothing is deployed.
  A direct upload of the built site leaves the repository private.
- **Decided (owner): the map page is taken up as a scope addition, built
  after the stamped download paths and the hard-line item (D85).** All
  seven regions with a toggle per dataset (fire, snowpack, rainfall,
  temperature). It shows each year's values from the committed region x
  year tables; no new trend statistic is computed, so nothing is added
  to the analyses made after `run1`. Its colour ramps are designed into
  the design system now. Rejected trend legends for now: a trend per
  region and dataset would be a new analysis after results were seen
  (`docs/post_results_protocol.md` section 2). Stated limit: one shade
  per region repeats the limitation that wet coasts sit inside the
  regional mean.
- **Adopted (owner, session 10: "love the winter to fire, looks great"):
  the design system "Hydrowhiplash: Winter to Fire".** A pale lichen
  ground and an evergreen for the frame; red only for burned area, blue
  only for precipitation, teal for snowpack, amber for seasons after an
  El Niño winter, a violet reserved for La Niña; National Park, Public
  Sans and JetBrains Mono. `theme/tokens.json` is the master copy and
  the artifact mirrors it; `src/theme.py` reads it and writes the Quarto
  theme (`site/theme/`), and the results page and the methods reading
  copy take their CSS variables from it (`scripts/build_results_page.py`,
  `scripts/build_methods_copy.py`, new). Tests hold the text colours to
  4.5:1 on their grounds in both themes and fail if `site/theme/` is
  stale. Three calls made in the draft and left standing by the owner's
  yes: "significant after Holm" is a filled evergreen dot with the word
  (it was ember orange, and red now means fire); green is never a data
  series beside red; the typefaces.
- **Redrew the mechanism diagram and the methods flowchart from the
  tokens** (`python -m src.diagrams`; owner: "yes regenerate the
  flowchart"). The flowchart's boxes stay neutral. In the mechanism
  diagram the north pathway moved from orange to the snow colour and the
  south stays blue (the water colour): orange read as fire under the new
  system, and both pathways end in fire. Supersedes the colour choice in
  2026-10-04 "Mechanism diagram"; the wording, layout and footnotes are
  unchanged. Not restyled yet: the data figures drawn by
  `src/figures.py` (they need `data/`, and one reads polygons); they
  follow with the site charts for Headlines 1 to 4. The diagrams keep
  DejaVu Sans so their SVGs stay byte-identical between machines.
- **Noted (owner, session 10): "if at all necessary invoke deepseek".**
  Read as leave to call the DeepSeek worker where a task needs it,
  reported when used; `data/` stays out of reach of every DeepSeek plan.

### 2026-10-12 - Prediction model scope agreed

- **Decided (owner, after `run1` was seen, before any model is fitted;
  D83): the scope proposed for the prediction model.** Version 1: one
  pooled linear model with shrinkage across all seven regions, region
  terms, predictors known before the fire season (winter index, October
  to March precipitation, 1 April snowpack, winter SPEI-3, year trend),
  scored only on unseen seasons by expanding window from 20 training
  seasons against a trend-only baseline. Two outcomes: log burned area,
  and a yes or no for a season in the top third of the region's seasons
  (owner: "add yes no"), the cut taken from the training seasons only.
  A separate hindsight run adds June to August temperature to show how
  much of the missing skill is summer weather (owner: "yes"). Alaska and
  Yukon are pooled with the other five regions and their skill reported
  apart (owner: "pool them report skill separately"). Version 2, a small
  tree ensemble, is tried only if version 1 beats the trend. It is built
  in a named worktree, branch `side/prediction-model`, beside session
  10. Left for the written spec, before any fit: the shrinkage setting,
  the skill measure for the yes or no outcome, the rule for version 2.
  Rejected one model per region: about 42 seasons each, where `run1`
  already showed single predictors gaining at most 0.06 over the trend.
  Exploratory throughout; the registered 2027 forecast stays the H3a
  model.

### 2026-10-12 - Prediction model is next; owner's answers at the end of session 9

- **Decided (owner, after `run1` was seen): the seasonal-outlook
  prediction model is the next analysis, moved up from "Later
  extensions", scoped first and then built as a side session beside the
  design-focused session 10 (D83).** Owner: "try training it on the past
  years and have it try on years not yet seen", and asked to scope its
  extent, its training, and whether machine learning would be a second
  version. It reads only committed region x year tables, so a worktree
  session can do it without `data/`; it touches `src/` and `results/`,
  while session 10 touches the site. It is exploratory and reported
  apart from the registered tests, never in place of one; the registered
  2027 forecast stays the H3a model. Because every result has been seen,
  the predictors, the scoring on unseen years (expanding window, as in
  `validation.csv`), the trend-only baseline and what counts as skill
  are written down and agreed before any model is fitted. Rejected
  starting it inside session 10: the two would compete for one session's
  attention. Scope proposed to the owner the same day (a pooled linear
  model first; machine learning as a second version only if the first
  beats the trend); not yet agreed, nothing built.
- **Decided (owner): the rollout timetable for readers lives on the
  tracker page**, not on a page of its own.
- **Decided (owner): reminders ahead of each rollout date are scheduled
  tasks, a few days in advance; arrivals with no fixed date are folded
  into the reminder nearest to when they are best checked.** Set up in
  session 10; nothing is scheduled yet.
- **Decided (owner): the site's look is redesigned with a design system
  in session 10.** The results page and the methods draft were read
  ("looks good for starters ... the content is good"); the open choices
  (design system, hosting, the map page) are put to the owner at the
  start of session 10 with a recommendation each. The methods wording is
  not yet signed off line by line, so the `ACTION_PLAN.md` Methods item
  stays open with its typed numbers and notices.

### 2026-10-12 - Full-record burned-area view; methods and limitations draft

- **Built the full-record view of burned area as each season's departure
  from the region's mean log burned area, raw and not detrended**
  (`src/fire_figures.py`, `figures.fire_season_series`;
  `results/figures/burned_area_anomaly_series_roni.png`). Seven panels,
  seasons 1984 to each region's last test year, read from the pinned
  `fire_region_year.csv`; seasons after an El Nino winter highlighted,
  strong ones labelled; a right-hand axis reads the departure as a
  multiple of the region's typical (geometric mean) season. Raw values
  follow the trend rule (detrended in tests, raw in figures). The one
  zero-fire season (SoCal 2014) is drawn as a marker and left out of the
  mean: log(1 + 0) sits about 10 log points under any season with a fire
  and would flatten the panel. Rejected hectares on a log axis: a zero
  cannot be drawn and bars have no natural baseline. First view to set
  burned area beside ENSO, made after the registered runs were committed
  (D62).
- **Drafted the whole methods and limitations page for the owner to
  edit; nothing in it is approved** (`site/methods.qmd`, marked as a
  draft at the top). Every result number is read at render time from
  `results/tables/run1/`; settings quoted in prose come from a new
  `results/tables/site_settings.json`, written from `src/config.py` by
  `src/site_settings.py` with a test that fails if it is stale, because
  the site cannot import `src`. Eight numbers are still typed from this
  file and the methods register (marked with a dagger on the page: the
  127,000 ha overlap, 17 of 76 winters, the MTBS to WFIGS ratio, the NBAC
  missing share, the Parks Canada years, the defence-land share, the
  station correlation, the Interior Alaska correlations); each needs a
  committed table before the page is public. Notices 8 to 12 and the
  snow-station notices were copied from `DATA_SOURCES.md` and are to be
  confirmed with the read-licence skill before publication; the ERA5-Land
  hourly entry, the CanSWE paper citation and notice 13 are not on the
  page yet. The `ACTION_PLAN.md` Methods item stays open until the owner
  approves the wording.
- **Fixed a test, not the runner:**
  `test_main_runs_nothing_when_preflight_fails` called `main("run1")`
  and failed once `results/tables/run1/` existed, because `main` refuses
  a filled run folder before it reaches preflight. The test now points
  `RESULTS` at an empty folder. No result changed; 341 tests pass.

### 2026-10-12 - run1: the first registered runs

- **Ran the registered tests once, on the owner's go ("start run1"), and
  committed them: `results/tables/run1/`, commit 4951e41, tag
  `registered-run1`, both pushed.** `python -m src.run_hypotheses --run
  run1` on commit 777eafd with a clean tree; started 2026-10-12 09:41:27
  UTC, results written 09:44:33 UTC; preflight passed (30 pinned inputs,
  the frozen plan text, the statistics tests). Run commit made
  2026-10-12 02:45 local (09:45 UTC), 25 days before the D73 deadline of
  Friday 2026-11-06. Three tables, each with a provenance file:
  `registered_tests.csv` (52 rows, 12 Holm families),
  `reported_beside.csv` (205 rows: ONI robustness 33, frozen rules 44,
  Parks Canada 9, zero-fire 7, station z 6, strong-only 24, strong-flip
  24, H4 secondary 7, H6 combined 8, block bootstrap 14, H3a minus H3b
  gap 7, lag-1 autocorrelation 22) and `validation.csv` (39 rows).
  `conda_list_explicit.txt` (356 lines) was saved into the folder by
  hand before the commit, as `docs/post_results_protocol.md` section 5
  requires. Nothing in `run1/` is edited, renamed or deleted from here
  on; any rerun goes to `run2/` under the protocol.
- **Found, registered tests after Holm at 0.05: 4 of 52 significant.**
  H1 SoCal (El Niño winters wetter: +64.4 mm DJF, 95% CI 31.0 to 99.6);
  H5 lag 0 AB (a wetter winter, less burned area the same year: slope
  -0.687, CI -1.099 to -0.276, about -50% per unit); H5 lag 1 NorCal
  (a wetter winter, more burned area the next year: +0.388, CI 0.188 to
  0.589, about +47%); H6 SWE NorCal (more snow, less burned area:
  -0.377, CI -0.616 to -0.138, about -31%). No ENSO-on-burned-area test
  (H2, H3a, H3b, H4, C2) and no C1 test was significant, before or
  after correction; every H3a interval spans 0. These are reported as
  nulls, not dropped.
- **Built a results page format on the owner's request, filled from the
  run folder by a script** (`scripts/build_results_page.py`,
  `scripts/results_page/template.html`), so the look is settled before
  the site pages are written. Per hypothesis: every region's estimate
  and 95% interval on one scale, Holm verdict by colour, the
  reported-beside runs as an overlay, then the other side runs and the
  validation table. No number is typed; a rerun gets its own page.
  Published privately as an artifact, not part of the Quarto site and
  not in `results/`. Rejected a hand-written page: its numbers could
  drift from `run1/`. A scope addition outside the plans; no test,
  input or result changed. Left open by the owner: a shared design
  system for the site, and hosting (Streamlit, or the owner's domain
  with Cloudflare R2).

### 2026-10-12 - DeepSeek review of the safeguards and the runner (D77)

- **Ran the D77 read-only review once, with the owner's yes: 8 findings,
  2 fixed as bugs, 6 checked and not taken.** `deepseek-flash` at `max`
  effort, 2026-10-12 09:15-09:18 UTC (peak hours; owner: no need to wait
  for a cheap call), on staged copies of `src/run_guard.py`,
  `src/pin_inputs.py`, `src/run_hypotheses.py`, `scripts/preflight.py`
  and `scripts/check_plan_frozen.py` in a temporary folder outside the
  repository (1,080 lines; 40,160 input and 32,599 output tokens). The
  worker read those five files and nothing else. It found no path by
  which `main()` starts or writes without preflight passing.
- **Fixed, F1 (medium): `write_result` wrote the provenance file and
  then the table under their final names**, so an interrupted write
  could leave a truncated table beside a provenance file stating the
  full hash, in a folder the runner then refuses to write again. Both
  files are now written under `.tmp` names and renamed once both are
  complete; `main` also refuses a run folder that holds only a
  provenance file. **Fixed, F7 (low): H1 and C1 rows carried
  `fire_table` = `fire_region_year.csv`** though they read no fire
  table; the column is now empty for every row whose outcome is not
  `log_burn`. No estimate, p-value or rule changed. Tests: 337 collected
  in the suite (2 added in `tests/test_run_guard.py` and
  `tests/test_run_hypotheses.py`, one assertion extended).
- **Not taken, each checked against the code:** F2 (the size table is
  read without a pin check): it is a committed script output, preflight
  refuses an unclean tree, and its sha256 is in every provenance file.
  F4 (a missing predictor would shorten a fit silently) and F6 (H4's
  panel could be unbalanced): `stats.fit_ols_hac`, `fit_driscoll_kraay`
  and `expanding_window` raise on a dropped row or an unbalanced panel;
  the reviewer could not see `src/stats.py`. F5 (a region missing from
  `FIRE_LAST_YEAR_BY_REGION` would vanish): all seven are there and
  `add_corrections` raises before anything is written. F3 (pins walk
  one folder level): the four download folders are flat, 30 files
  pinned; left as a low open point. F8 (a BOM or cp1252 save of
  `ANALYSIS_PLAN.md` fails preflight): it fails closed, with no run.

### 2026-10-12 - First hypothesis runs planned; runner written

- **Decided (owner, 2026-10-12, session 9, before any test): the first
  registered run holds all 52 registered tests in one pass, in the plan's
  order** (H1, H2, H3a, H3b, H4, H5, H6, C1, C2), Holm and BH per family
  at the end; nothing computed is printed, the run reports file names and
  row counts. Rejected running hypothesis by hypothesis: an early result
  could colour a later choice.
- **Decided (owner): the runs reported beside the tests are made in the
  same pass** (D75: ONI robustness, frozen-rules, Parks Canada
  sensitivity, strong-only), **and so is every other reported piece the
  frozen plan asks for:** zero-fire sensitivity, station-z repeats of H6
  SWE and C1, the block bootstrap check on H3a and H3b, the H3a minus
  H3b gap CI, H4 with `temp_jja` and with year-clustered errors and its
  joint F, the H6 combined model, lag-1 autocorrelation, leave-one-year-
  out and expanding-window validation. The 2027 forecast intervals are
  left out: the DJF 2027 RONI value does not exist yet.
- **Decided (owner): three result tables in `results/tables/run1/`:**
  `registered_tests.csv` (52 rows), `reported_beside.csv` (a `run_kind`
  column) and `validation.csv`; columns run estimate, CI, percent change,
  then p, Holm p, BH p, verdict, size label, plain OLS p.
- **Decided (owner): a second pinned reader for the raw ENSO files**
  (D82): `pin_inputs.enso_raw_path`. Every committed table holds RONI
  only; ONI sits in the pinned `data/raw/oni.ascii.txt`, which
  `load_input` refuses. Rejected building a committed ONI table: it
  needs a re-pin, a row in the re-pin log before any result exists.
- **Built: `src/run_hypotheses.py` and `tests/test_run_hypotheses.py`**
  (18 tests on synthetic tables shaped like the inputs; 335 tests pass).
  Not run on fire data. Size labels read through `run_guard.size_label`
  for the planning table: H3a 0.0675 one-sided and 0.0650 two-sided
  (plain OLS 0.0475, 0.0410); H3b 0.0715 and 0.0815 (0.0560, 0.0495);
  H4 contrast 0.0780; H5 and H6 0.0790 one-sided, 0.0965 two-sided; C1
  0.0705 (0.0460); C2 0.1020 (0.0490).
- **Points the frozen plan leaves to the code, as built (for the owner
  to confirm before the run):** the El Nino group of H1 and H2 is
  `phase` el_nino against all other years. Percent change is filled for
  regression coefficients and the H4 contrast on `log_burn`, not for
  H2's difference in detrended means. Zero-fire rows are written only
  where a zero-fire season exists (main table: SoCal 2014, so SoCal's
  tests and H4). The Parks Canada run holds AB's tests and H4. The ONI,
  frozen-rules, Parks and zero-fire runs carry the H4 contrast only; the
  joint F, the year-clustered fit and the `temp_jja` model are run on
  the main table. H4 with `temp_jja` carries no size label (none was
  measured for that model). Lag-1 autocorrelation covers `log_burn` and
  its detrended residuals (7 regions), detrended DJF precipitation (5)
  and the C1 snowpack z (3). Leave-one-year-out rows also give RMSE and
  MAE. A comparison group under 2 years stops the run before anything
  is written. `validation.csv` holds summaries, not per-year
  predictions.

### 2026-10-12 - No NBAC re-run; the per-fire coverage split is a reported limitation

- **Decided (owner, 2026-10-12, before any test): no exploratory NBAC
  re-run of the Canadian tests; the per-fire coverage split is reported
  beside the BC, AB and YT results as a measured limitation** (D81;
  frozen plan's deviations log, row 19). With the Interior Alaska check
  (D79) this settles both items that had to be decided before the first
  hypothesis test. Measured 2026-10-11 to 12
  (`scripts/nbac_coverage.py`, 88 minutes;
  `data/processed/nbac_coverage_fires.csv`, 3,035 fire-by-label rows,
  2,892 NBAC fires of 405 ha or more, 1984-2024; the regenerated season
  table equals the 2026-10-08 one in all 264 rows). NBAC area with no
  same-YEAR CNFDB polygon under it, split at an uncovered share of 0.5
  (`NBAC_MISSING_SHARE`) into fires missing from CNFDB and rim
  disagreement: AB 547,394 ha missing (103 fires) and 265,694 rim, of
  10,523,204; BC 173,688 (85) and 336,563, of 8,239,696; YT 194,517 (89)
  and 238,196, of 6,306,203. Of the 297 missing rows, 213 are wholly
  uncovered (690,395 ha). AB's missing area by land: defence 109,773 ha
  (D71), national parks 217,386 (Wood Buffalo; D69 covers 2016-2019),
  provincial and other labels 219,900. Provincial-label missing area as
  a share of that NBAC area: AB 2.7%, BC 2.0% (166,800 ha), YT 3.1%
  (193,555 ha). Rim on provincial labels: AB 2.2%, BC 4.2%, YT 3.9%,
  above the 0.3-1.2% floor of audit round 5 L6 (three AB seasons), so
  the 0.5 cut leaves partly covered fires in the rim class. Seasons
  where provincial-label missing fires exceed 10% of the season's NBAC
  area: AB 6 of 41 (1986, 2000, 2001, 2005, 2006, 2024), BC 9 (1985,
  1987, 1989, 1991, 1992, 1996, 1998, 1999, 2000), YT 3 (1986, 2000,
  2019); the large recent ones AB 2024 (105,541 ha, 14.7%, one fire of
  81,134 ha with no CNFDB polygon), YT 2019 (70,493 ha, 26.4%, 19 fires)
  and AB 2006 (41,677 ha, 27.9%). Not checked: whether CNFDB files any
  of these fires under a neighbouring YEAR. Reasons for no re-run: the
  provincial missing area is 2-3%, the log series correlate at 0.990
  (BC), 0.994 (AB) and 0.997 (YT), parks and defence lands are already
  handled (D69, D71), and a re-run needs its own date rule (NBAC has no
  ignition date) and another fire build before 2026-11-06. Rejected the
  re-run as the direct check of the 18 region-seasons over 10%; rejected
  deciding after results. No fire total was set beside ENSO.
- **Record check closed (session 8 kickoff): the register's "Union
  area" figures agree.** WFIGS overlap left out is 79,443 ha over every
  season built and 52,834 ha inside the table's 291 seasons; the other
  26,609 ha is the unfinished 2026 season (PNW 24,243, NorCal 2,367),
  built but outside the table. Sentence added to the register row.

### 2026-10-12 - Plain OLS check takes the registered test's sidedness

- **Decided (owner, option chosen 2026-10-11, sizes accepted 2026-10-12,
  before any test): the plain OLS check beside H3a and H3b in PNW, BC and
  AB is one-sided, like the registered test it sits beside** (D80; frozen
  plan's deviations log, row 18). D66 kept the check only where its
  measured size is near 5%, and its size had been measured two-sided only
  (cold check 2026-10-11, low 10). Measured one-sided
  (`scripts/stats_size_check.py`, 1,000 datasets per scenario, label row
  2,000): H3a 4.75%, H3b 5.60% (Monte Carlo SE 0.49%); across the three
  scenarios 4.2-5.5% and 5.0-6.2%. Kept. NorCal, SoCal, AK and YT are
  registered two-sided and keep the two-sided rows (4.1%, 4.95%); C1 was
  already one-sided, C2 two-sided. Rejected a two-sided check beside a
  one-sided test: with the estimate in the expected direction its p is
  double by construction, so it would read as a failed check (the D68
  reasoning); rejected printing both (a third number per row). Registered
  p-values and Holm verdicts unchanged.
- **`results/tables/test_size.csv` rebuilt, 63 to 71 rows.** The two new
  shapes draw nothing from the random stream, and all 63 earlier rows
  reproduced exactly; the script stamps every row with the run date, so
  their `measured` column now reads 2026-10-11 for values first measured
  on 2026-10-08. `run_guard.plain_ols_shape(test, region)` returns the
  check's row in the test's own sidedness. Tests: 317 passed.
- **Offline copy of the 30 pinned inputs** (owner, 2026-10-11: a folder
  of its own inside the repository): `pinned_inputs_copy/` (3.2 GB,
  git-ignored), written by `python -m src.pin_inputs --copy`, each file
  checked against its pin (`PINNED_COPY_DIR`; audit round 5 S1c). It
  guards against an overwrite, not against loss of the disk.

### 2026-10-11 - Session 8: owner decisions before the first test

- **Decided (owner, 2026-10-11, before any test): the Interior Alaska
  numbers are reported beside the Alaska results as a descriptive
  limitation** (D79; frozen plan's deviations log, row 17). Alaska stays
  one region in every test. Measured the same day, climate only, no fire
  table read (`scripts/interior_alaska_check.py`): the Interior (NOAA NCEI
  climate divisions 3, 4, 5, Central, Northeast and Southeast Interior,
  clipped to the AK polygon) is 41.8% of the polygon's area, 11,772 of
  27,711 ERA5-Land cells. Interior against whole-AK series, 1951-2026:
  correlation 0.982 (`temp_jja`), 0.976 (`temp_mam`), 0.793
  (`precip_djf_mm`), 0.823 (`precip_octmar_mm`); mean DJF precipitation
  88.9 against 182.7 mm. El Nino minus other winters (26 of 76), in SD of
  each series: DJF precipitation -0.366 against -0.183, Oct-Mar -0.250
  against -0.035, `temp_mam` +0.452 against +0.373, `temp_jja` +0.107
  against +0.171. Descriptive differences, no test. The plan's stated
  limitation (climate means include wet coasts) holds for precipitation
  and is small for temperature; AK's registered tests (H2, H3a, H3b) use
  the ENSO index and `temp_jja`, not precipitation. Rejected leaving the
  limitation unmeasured; rejected deciding after results (it would look
  chosen to fit them).
- **Read the terms of the NOAA NCEI Alaska climate divisions**
  (`DATA_SOURCES.md` row and notice 13): no licence named; the dataset
  record asks for a citation and carries warranty disclaimers, with no
  restriction on use. Verdict PERMITTED WITH CONDITIONS. The "public
  domain" sentence the 2026-10-05 probe quoted was not found again; the
  in-zip metadata was not read. Downloaded 2026-10-11 (391,385 bytes;
  `src/download_ak_divisions.py`).
- **Decided (owner): the Claude Code Project is not used for the
  registered runs or the runs reported beside them** (D78; settles D63).
  One runner in the main checkout makes them in one commit. Each run is
  seconds of compute, the preflight verifies 30 pinned inputs of which 23
  sit under `data/`, and the protocol wants one run folder written once.
  The Project is taken up again for site pages after the runs.
- **Approved (owner): `docs/post_results_protocol.md`**, including the
  run folder `results/tables/run1/` and the tag `registered-run1`.
- **Added (owner): `python scripts/check_plan_frozen.py` to `CLAUDE.md`'s
  "Checks".**
- **Housekeeping:** `side/nbac-probe` (c4981de, patch-identical to main)
  and `side/fire-licence-reads` (31c7cc0; PR #21 squash-merged 2026-10-07,
  its `D?a` now D56, its three ledger rows revised in main since) deleted
  after the comparison was reported. PR #23 (site methods flowchart, D74)
  merged with the owner's yes, squash commit 2fb0e37.
- **Added to `scripts/nbac_coverage.py`: a per-fire output and split**
  (`NBAC_MISSING_SHARE` 0.5; audit round 5 L6), run with the owner's yes
  for a polygon read. Its numbers and the NBAC re-run decision follow in
  their own entry.
- **Fixed:** `phase2.main` read `data/processed/` before its guard after
  the cold-check fix moved the guard into `write_tables`, so
  `test_real_builders_refuse_to_overwrite_their_pinned_tables` failed in a
  worktree without `data/` (found by the flowchart side session); the
  guard runs first again, and in `write_tables` too.

### 2026-10-11 - Site methods flowchart built (side session)

- **Built the methods flowchart decided on 2026-10-08 ("Site methods
  flowchart", D74) as `src.diagrams.methods_flowchart`**, writing
  `results/figures/methods_flow.*` (9 in wide) and `methods_flow_narrow.*`
  (4.6 in wide), included under "Method" in `site/methods.qmd` with a
  draft caption and draft alt text. No data was read and no fire table was
  opened. The two mechanism SVGs are byte-identical after the shared
  helpers gained an optional line style.
- **Decided to draw every box in the neutral colours and leave the orange
  and blue unused.** On the home page orange means the north pathway and
  blue the south; a second meaning on the methods page (climate against
  fire, say) would be read as the first. Rejected tinting the three
  columns by kind of source.
- **Decided to draw arrows per group, not per source.** Three columns
  (ENSO index; climate; fire), each a group of sources above the variables
  made from that group, with one arrow per column. Rejected
  one arrow per source and
  variable pair (eight crossing arrows at phone width).
- **Decided (owner, 2026-10-11) to print a two-line note under the
  chart:** "Arrows show groups, not single sources. Snow stations are
  used only to check the ERA5-Land snowpack." The second sentence follows
  `ANALYSIS_PLAN.md` H6 ("ERA5-Land April 1 SWE z (station z as the
  check)"). Printed in the figure, as the mechanism diagram's framing
  line is, so it travels with the image. Rejected the page caption alone.
- **Decided to put NBAC beside the pre-registered tests, dashed, not among
  the sources.** Among the sources it would read as part of the main
  burned-area series. Rejected a footnote (the 2026-10-08 entry names it
  as a source to show).
- **Added one box the 2026-10-08 entry does not list: "ENSO index per
  winter"**, so that ONI and RONI lead to a variable like every other
  source. No scope change; the label is the owner's to reword or drop.
- **Left `ACTION_PLAN.md` "Methods flowchart" unticked**, as the mechanism
  diagram item is: the labels, caption and alt text await the owner.
  Files: `src/diagrams.py`, `tests/test_diagrams.py`,
  `site/methods.qmd`, `results/figures/methods_flow*`.

### 2026-10-11 - DeepSeek: the repo's source may be sent

- **Decided (owner, on a recommendation): the repo's source may go to
  DeepSeek, and every review runs on staged copies.** The files under
  review are copied to a temporary folder outside the repo and reviewed
  there, so `data/`, the logs and `DECISIONS.md` are not beside them.
  Downsides weighed: the code leaves the machine for an outside service
  whose retention and training terms were not read; the code is MIT and
  the repo is likely to go public, so the exposure is early rather than
  extra; no result exists yet to leak. Rejected reviewing in the main
  checkout: the prompt's "read only these files" is an instruction, not
  a lock. Closes the open point in the entry below. Each call still
  needs its own yes.

### 2026-10-11 - DeepSeek delegation: what is taken up, and when

- **Decided (owner, 2026-10-11, before any test): a DeepSeek read-only
  review of the safeguard code is added as an extra read outside the
  pre-results gate, not as a sixth audit round** (D77). The gate closed
  on round 5 by the owner's standard (tag `pre-results-gate-closed`) and
  stays closed; the review covers `src/run_guard.py`,
  `src/pin_inputs.py`, `scripts/preflight.py` and
  `scripts/check_plan_frozen.py` (484 lines, read so far by one short
  cold check), and the runner once it is written. Each finding is
  checked before it counts, and only a bug fix may follow. Rejected
  calling it round 6: that would reopen a gate whose closing rule was
  met.
- **Decided (owner, on a recommendation): no delegated build before the
  registered runs are committed (2026-11-06).** The handoff
  (`docs/deepseek_handoff_2026-10-11.md`) proposed building the runner
  safeguards S2 to S6 with DeepSeek, one per run, as a harder pilot
  before 2026-10-25; commit cdbf687 already held them when the handoff
  was read. The replacement pilot (the pin report after `--rebuild` in
  the modules that guard a pinned write without calling
  `pin_inputs.report_rebuild`) waits until after the runs, in line with
  "no new scope before the runs" (entry "Portfolio review handoff: what
  is taken up, and when"). Rejected an exception for one small build:
  the 2026-11-06 date does not need it.
- **Decided (owner): the methods page says where DeepSeek was used, in
  the owner's words: "DeepSeek helper agents contributed here".** Placed
  with the other methods-page items, after the runs.
- **Decided (owner): the DeepSeek worker may read the committed tables
  in `results/tables/`.** They are derived region x year tables already
  committed, from sources whose ledger verdicts permit derived outputs.
  `data/` stays out of reach of every plan and prompt.
- **Open:** whether the repo's source may go to DeepSeek at all (the
  `deepseek-delegate` skill asks once per project); the owner asked for
  the downsides first. No DeepSeek call is made until it is answered.

### 2026-10-11 - Runner safeguards built (session 8)

- **Built the runner safeguards S2-S5 and the size-label lookup, after the
  protocol for changes after results (S6) was written first** (D73; audit
  round 5; `docs/post_results_protocol.md`, a draft until the owner
  approves it). No hypothesis test has run, no polygon file was read and
  no pinned input changed (`pin_inputs --verify`: all match). S2: every
  builder and downloader whose output is a pinned input calls
  `pin_inputs.guard_write` first and refuses without `--rebuild`; a re-pin
  needs `--repin "<reason>"` and appends to
  `results/tables/input_pins_log.csv` (`INPUT_PINS_LOG`); the bare
  `python -m src.pin_inputs` no longer writes pins. S3:
  `pin_inputs.load_input(name)` opens only a pinned table in
  `results/tables/` whose sha256 equals its pin. S4:
  `scripts/check_plan_frozen.py` and `scripts/preflight.py`
  (`src/run_guard.py`). S5: `run_guard.write_result` writes a provenance
  file beside each result and never overwrites one. Size labels:
  `run_guard.size_shape` and `size_label`; each of the 39 registered
  regression tests and the four H4 shapes maps to exactly one label row of
  `test_size.csv`. Tests: 311 passed.
- **Wider than the audit's list, by the same rule:** the audit named
  `src.fire`, `src.parks_gap`, `src.climate_vars` and `pin()`. The guard
  also covers `src.phase2`, `src.snow_soil`, `src.stations` (each writes a
  pinned table), `src.download_oni` (its default overwrote the pinned RONI
  file) and the four fire downloaders (each run rewrote the pinned listing
  and manifest, with or without `--refresh`). Rejected leaving the
  downloaders to S1's stamped paths alone: until those exist, one run
  would break `--verify`.
- **Short cold check (Fable 5.1 subagent, read-only, on the uncommitted
  tree): no high, 4 medium, 8 low; fixed before the commit.** M1, the
  guard sat in `main()` only, so the notebook 02 cell calling
  `phase2.write_tables` could still overwrite a pinned table: the guard
  moved into `write_tables` in `src/phase2.py` and `src/fire.py`. M2,
  `write_result` wrote the table before its provenance record: the record
  is now built first. M3, the run folder's own untracked files marked
  every later result dirty and failed a second preflight: the folder being
  written is left out of the clean-tree check. M4, the frozen-text check
  trusted a movable local tag: the tag must point at `FROZEN_PLAN_COMMIT`
  (acf7a80). Lows fixed: `load_input` refuses a path outside
  `results/tables/`; a deviations-log row edited or removed against HEAD
  is reported; a clearer error for a wrong H4 shape; the protocol no
  longer claims an environment file no code writes; UTF-8 for the
  preflight's pytest output.
- **Left open, for the owner:** S1's release- or retrieval-stamped
  download paths and the offline copy of the 30 pinned inputs (3.38 GB)
  are not built; the downloaders print no pin diff after `--rebuild`. The
  plain OLS check for H3a and H3b was measured two-sided only, while PNW,
  BC and AB are registered one-sided: which plain OLS p is reported there
  is undecided. `scripts/check_plan_frozen.py` is not yet in `CLAUDE.md`'s
  "Checks". Two tests need the tag `analysis-plan-frozen`, so a clone
  without tags fails them.

### 2026-10-11 - Portfolio review follow-up

- **Decided (owner, 2026-10-11, before any test): the commit due by
  2026-11-06 also holds the runs reported beside the registered tests**
  (the ONI robustness check, the frozen-rules run, the Parks Canada
  sensitivity run, the strong-only results), since they read the same
  pinned inputs. Rejected running them after the first tracker update
  (D75; frozen plan's deviations log, row 16).
- **Decided (owner, 2026-10-11): the site is published on a rolling
  basis**, each piece when it is ready, and the 2027 forecast in dated
  stages as the winter data arrive. A piece is ready when the licences of
  its sources are read and, for anything setting burned area beside ENSO,
  the registered runs are committed. Supersedes the single "publish" step
  in spring 2027 as the only publication point (D76).
- **Kept (owner asked for a recommendation): the three methods-page items
  enter ACTION_PLAN after the runs are committed**, as in the entry
  below. None depends on a result, but each is the owner's prose to word
  and the site plan says not to design ahead of results; a worktree
  session can draft them at any time after the date with no data.
- **Checked the licence ledger for commercial-use terms** (owner: before
  the runs; for a possible tip link). `DATA_SOURCES.md` holds 14 verdicts:
  13 PERMITTED or PERMITTED WITH CONDITIONS, none of those barring
  commercial use; 1 AMBIGUOUS, the Alberta snow portal (non-commercial,
  unmodified copies only), which was never downloaded (CanSWE is used
  for Alberta). CanSWE's ReadMe carves out Hydro-Quebec data under CC
  BY-NC-SA; the project reads Alberta stations only. A ledger check, not
  a fresh licence read. Where a tip link goes stays the owner's call (own
  domain or GitHub profile as the fallback).
- **Noted:** the owner runs expanded-heatmap's batch first, so the NBAC
  per-fire split waits for it or for the owner's word.

### 2026-10-11 - Portfolio review handoff: what is taken up, and when

- **Decided (owner, 2026-10-11): nothing from the portfolio review handoff
  is started before the registered runs are committed (Friday 2026-11-06,
  D73).** The handoff (`hydrowhiplash-elnino26_PORTFOLIO_REVIEW_NOTES.md`,
  from the owner's portfolio review session, read 2026-10-11, read-only
  first pass) agrees with ACTION_PLAN Phase 4 on the order of work. Taken
  up after the runs, as one scope addition with its own deviation number
  and `[mid-project]` markers in ACTION_PLAN's "Second goal": three
  methods-page items, each a draft for the owner to word (why regression
  and not a trained ML model; a responsibility statement saying who the
  forecast is for; a statement of where coverage is thin). Later, when the
  owner brings them: the tone guide from link-station (suggestions on
  drafted prose only), a "system map" section in `CLAUDE.md`, the glossary
  export for the interview catalogue, and the results-page boxes, talk
  track, motion opener and hub card. Rejected adding the methods-page
  items to ACTION_PLAN now (new scope ahead of the deadline) and drafting
  the plain-words result sentence before results exist (it would set a
  direction and a framing ahead of the numbers). Shared machine memory
  (32 GB, expanded-heatmap's batch in the week of 2026-10-12): the owner
  handles it as needed. The DeepSeek worker takes no task until the owner
  says its integration is finished.
- **Found the handoff stale against the repo in these places** (for any
  prose that reuses it): "210 passing tests" (the 2026-10-08 log records
  278 to 289 passed); "about 5 strong events" (3 strong winters in the
  1984-2025 fire record under RONI, 7 in 1951-2026; the ACTION_PLAN
  Pitfalls wording was already flagged in D9); a headline sentence shaped
  as strong winters against the rest (strong-only results are exploratory;
  the registered burned-area regressions use the continuous index on
  `log_burn`); the method list omits Driscoll-Kraay errors, the
  expanding-window validation and the measured test sizes; the safeguard
  list omits S1, the S6-first order and the cold check; the
  before-any-test list omits the Claude Code Project go/no-go (D63);
  "five audit rounds" are the pre-results rounds, with four more audits
  before the freeze; the frozen plan's deviations log holds 15 rows,
  several decided after fire data was opened; and ACTION_PLAN publishes
  the forecast in spring 2027, with the final winter data, not right
  after the runs.

### 2026-10-08 - Site methods flowchart

- **Decided (owner, 2026-10-08) to add a methods flowchart to the public
  site** (`site/methods.qmd`, "Method"): sources (ERA5-Land, snow
  stations, MTBS and WFIGS, CNFDB, ONI and RONI; NBAC as a sensitivity
  source), the variables made from them (winter precipitation, whiplash,
  snowpack, burned area per region and season), the tidy region x year
  table, the pre-registered tests and the site's charts. Built like the
  mechanism diagram (2026-10-04 "Mechanism diagram"): drawn in code in
  `src/diagrams.py`, written to `results/figures/`, byte-identical between
  runs and tested, wide and phone layouts, the same palette. Structure
  only: burned area and ENSO appear as boxes, never as numbers side by
  side. Rejected reusing the private notebooks doc's diagram (it shows
  where the notebooks sit, which a reader does not need) and a Mermaid
  block in the page (the figure would live outside `results/`). Needs no
  data, so a worktree session can build it. Scope addition (D74).

### 2026-10-08 - Audit round 5 settled; pre-results gate closed

- **Settled (owner, yes on every recommendation): the pre-results audit
  round 5** (`docs/audit_2026-10-08_preresults_round5.md`, Fable 5.1,
  read-only, at c6ac758; no high, no medium, 6 low, and 7 forward
  safeguards from a second pass the owner asked for). Independent code
  reproduced every number the round 4 fix put in the records from the
  pinned zips (union-to-union agreement, the 25 / 6 / 11 season counts,
  Wood Buffalo 95.67%, defence lands 109,773 ha, the D71 polygon facts,
  the parks table to every printed digit), and the whole gate recomputed
  by hand on synthetic data. The owner's standard (a cold round with no
  high and no medium findings) is met, so **the gate closed on round 5**:
  the commit that records this entry carries the tag
  `pre-results-gate-closed` (round 5 S5). Rejected a round 6: the standard
  was set before round 5 ran.
- **L1-L6:** L1, the "most large seasons" sentence now quotes all nine AB
  seasons with CNFDB Parks Canada area of 50,000 ha or more (five below
  NBAC 0.68-0.90, three near at 0.99-1.11, one above at 1.92), so F3's
  "more likely low than high" stands, less strongly (register,
  `src/parks_gap.py`; the round 4 entry above is left as written). L2,
  the defence-land parts are 60 for 1984-2024 (63 with 2025), 58 undated;
  L3, they are 1% of AB's counted burned area, not of AB's area (D72, plan
  log row 14). L4, the parks table's `burn_ha` differs from the main
  table's in the last digit in 7 seasons (CSV round trip, at most 4.7e-10
  ha): stated in the data dictionary; rejected rebuilding a pinned table at
  closure for it. L5, `assert_pinned` and the two measurement CSVs named
  in the register and data dictionary. L6, F1's number holds both missing
  fires and rim disagreement; the rims alone were 0.3-1.2% of a season in
  the AB years the auditor probed; the floor is stated beside F1's numbers
  and a per-fire split (uncovered share above 0.5 as missing) is the first
  step of the session 8 NBAC decision.
- **F1 measured** (`scripts/nbac_coverage.py`, 2026-10-08, about 90
  minutes): NBAC fire area (whole fire at or above 405 ha) with no CNFDB
  polygon of the same calendar YEAR under it, 1984-2024: AB 7.7%, BC 6.2%,
  YT 6.9%; under the provincial labels AB 393,140 ha (4.8%), BC 501,894
  (6.1%), YT 430,841 (6.8%); Wood Buffalo 303,904 of 2,078,447 ha (14.6%,
  about 175,000 of it the 2016-2019 gap); defence lands 109,773 ha (100%).
  AB's provincial 4.8% is well above the rim floor, so some seasons
  (likely 2005-2007) may hold whole fires CNFDB lacks. Nothing adopted:
  input to the session 8 decision.
- **S1-S7 (forward safeguards; none a defect today):** S1, the later
  downloads (the November ERA5-Land update, D55; the March 2027 RONI
  value; CNFDB 2025) would land on pinned paths: the registered runs are
  computed and committed by Friday 2026-11-06, before October's ERA5-Land
  data is expected (`TRACKER_DATA_DAY` 7); every later download gets a
  release- or retrieval-stamped path, built before the tracker code; if
  the runs miss the date, only the climate tables are re-pinned, logged,
  and only if every value a registered test reads is identical (D73, plan
  log row 15); an offline copy of the 30 pinned inputs (3.38 GB). S2
  (builders refuse to overwrite a pinned file without `--rebuild`; every
  re-pin logs its reason), S3 (`pin_inputs.load_input(name)`, the runner's
  only way to open a table), S4 (`scripts/check_plan_frozen.py` and a
  preflight the runner calls first) and S5 (a provenance record beside
  every result: commit, pin and size-table hashes, seed, package versions)
  are built in session 8 with tests, before the first run, then a short
  cold check of that code. S6, a protocol for changes after results
  exist, is written at the start of session 8, before any result. S7, the
  session 7 log block, written tonight.

### 2026-10-08 - Audit round 4 settled

- **Settled (owner, yes on every finding): the pre-results audit round 4**
  (`docs/audit_2026-10-08_preresults_round4.md`, Fable 5.1, read-only, at
  46534b1; no high, 2 medium, 8 low, 3 follow-ups). An independent NBAC
  rebuild reproduced the Parks Canada sensitivity table to the decimal.
  M1: "CNFDB holds no Parks Canada polygon for 2016-2021" was false as
  written; rechecked: none at all 2018-2020, Nahanni only 2016-2017 (5 and
  8 polygons, none in the study regions), 2021 small fires only (28 in the
  study regions, largest 65 ha), none at or above 405 ha in BC, AB or YT
  2016-2021; flag and tables unchanged; live wording corrected, D71
  supersedes D69's sentence. M2: fires on Department of National Defence
  land in AB (CFB Wainwright, Suffield; 109,773 ha over 1984-2024, 0.98% of
  AB, up to 59% of AB 1991) are in no CNFDB polygon in any year; owner
  chose a stated limitation, not added to the sensitivity table, because
  NBAC gives every part cause "Undetermined", satellite-only, 58 of 63
  undated, so they cannot be told from range burning (D71).
- **L1-L8 as suggested:** agreement figures re-measured union to union
  (NBAC 1.3% above CNFDB over AB 1984-2017; 6 of 25 seasons within 5%,
  ratio 0.45-2.08) and Wood Buffalo recomputed (2.08 of 2.17 Mha, 95.7%),
  both by `python -m src.parks_gap --measure`, now in the repository
  (process point); D70's label range 4.1-5.0% (D71); size labels "decided,
  applied in the hypothesis runs"; DATA_SOURCES lists the frozen-rules and
  parks tables; `pin_inputs.assert_pinned` for the hypothesis loaders;
  pin comments dated; `double_ha` rounded to a microhectare and clipped at
  0 (86 seasons held float noise down to -4.2e-9 ha; fire tables rebuilt,
  no other value changed, events file byte-identical).
- **F1-F3:** F2 (AB 2020 and 1991 as leverage seasons) and F3 (NBAC park
  area more likely low than high: ratios 0.68-0.84 in the large seasons
  2003, 2004, 2012) recorded in the register. F1 (NBAC area with no CNFDB
  polygon under it, by season and NBAC label) is `scripts/nbac_coverage.py`;
  its first run reported every hectare uncovered because pyogrio returns
  no rows, silently, when a `where` filter names a field missing from
  `columns`; fixed (the field read, an empty year raises), the rest of
  `src/` checked (unaffected). Its numbers go to the session 8 decision on
  the NBAC re-run.
- **Gate standard (owner, 2026-10-08):** the gate closes on a cold round
  with no high and no medium findings, ideally a few lows. Round 5 next,
  on Fable 5.1.

### 2026-10-08 - Audit round 3 settled

- **Settled (owner, yes on every finding): the pre-results audit round 3**
  (`docs/audit_2026-10-08_preresults_round3.md`, Fable 5.1, read-only, at
  309de6a; no high, 1 medium, 7 low). An independent rebuild of BC, AB and
  YT from the raw CNFDB download reproduced the committed tables at
  6e79757, 32e8d42 and 309de6a in every row. M1: `pin_inputs` pinned the
  whole `results/tables/` folder, so `--verify` would refuse once a
  hypothesis run writes a table there; now the input tables are pinned by
  name (`PINNED_RESULT_TABLES`, 7 tables; `test_size.csv`, a script
  output, unpinned), the download folders by folder, NBAC's included.
  L1: the fire build re-run with its output saved to
  `data/processed/fire_run.log` and `fire_frozen_rules_run.log`. L2, L6, L7:
  dictionary and register wording (309 prescribed polygons; a fire_id can
  name more than one fire, e.g. BC 1994-K50087; merged-fire attribute
  counts). L3, L5: D70. L4: the per-region size labels use the two AR(1)
  0.3 scenarios pooled (2,000 datasets), with each row's Monte Carlo SE.
- **Parks Canada gap: B + C (owner, 2026-10-08; D69).** AB 2016-2019
  flagged `parks_gap`; a reported sensitivity run on the main table with
  NBAC's park area added for those seasons (`src/parks_gap.py`). Rejected:
  a limitation only (AB 2017 is 39% short), filling the main table with
  NBAC (mixes sources; single seasons disagree with CNFDB by up to 2x).
  Found while measuring: the gap is 2016-2021 in CNFDB, not 2018-2020 as
  its update log says; NBAC has no park fire in 2020 or 2021.
- **Deferred to session 8, to be decided before the first hypothesis test
  (owner, 2026-10-08):** the exploratory NBAC re-run of the Canadian tests
  and the NOAA NCEI Interior Alaska check. Adopting either after results
  are visible would look chosen to fit them. NBAC vs CNFDB, 1986-2024
  (NBAC by calendar year, CNFDB by season window): log-series correlation
  BC 0.990, AB 0.994, YT 0.997; NBAC totals 84%, 94%, 91% of CNFDB;
  seasons differing by more than 0.25 in log_burn BC 11, AB 9, YT 4 of
  39. A re-run would need its own date rule (NBAC has no ignition date).
- **Gate:** round 4, a cold review of the round 3 fixes and the Parks
  Canada code, follows (D64); the gate closes when a round finds nothing
  high and the owner agrees.

### 2026-10-08 - Audit round 2 settled

- **Settled (owner, 2026-10-08): the pre-results audit round 2**
  (`docs/audit_2026-10-08_preresults_round2.md`, Fable 5.1, read-only, at
  32e8d42; 1 high, 1 medium, 7 low). H1 (high): the round 1 CNFDB
  dissolve merged different fires sharing a reused FIRE_ID; fixed by
  merging only parts within 1 km, chained (D67). BC 1998 back to
  60,120.5 ha and 22 fires (was 61,135.5 and 24 after round 1), BC 1994
  back to 11 fires; the other six changed seasons kept; 58 merged fires
  from 121 polygons, 10 among the counted pieces, all within 0.5 km.
  Rejected: reverting to per polygon (loses the 10 sound merges); the NFDB
  points file as a check (new download; the 25 km gap decides it).
- **M1: plain OLS check dropped for the H4 contrast** (D68; size 0.7%,
  power about half the registered test's), recorded internally only;
  kept for H3a, H3b, C1, C2.
- **L1-L7 as the report suggested:** `scripts/stats_size_check.py`
  writes `results/tables/test_size.csv` with the tests each shape labels,
  adding the H3b, persistent-predictor, C2 and C1 shapes (new: the C2
  Newey-West interaction test measures 10.0-10.4%, its plain OLS check
  4.6-5.2%; the bootstrap behind `--bootstrap`) (L1); register counts
  for wildfire types, country assignment and the null sweep corrected
  (L2, L4, L7); `n_parts` and `cnfdb_year` documented, ACTION_PLAN
  progress line updated (L3); `lag1_autocorrelation` now the sample ACF
  (one mean), predictors' values recomputed, largest change 0.01 (L5);
  the H4 multi-seed test uses 200 panels with bound 26 (catches a
  doubling 86% of the time; 18 rejections here), the bootstrap agreement
  test 5 seeds with both outcomes, and a dissolve test with parts 25 km
  apart, a 3-part chain and the 1 km edge (L6). A stale config comment
  corrected while counting L2: the prescribed flags mark 309 CNFDB
  polygons since 1984 (Parks Canada 297, AB 7, Ontario 5), not "304 in
  BC, AB, YT and Parks Canada".
- **NBAC downloaded (owner's yes, 2026-10-08) for the Parks Canada gap
  and the NBAC vs CNFDB comparison:** `src/download_nbac.py`, release
  v20260513; exploratory, not an input to any registered test, not in the
  input pins. Findings go to the owner before anything is adopted.

### 2026-10-08 - Audit round 1 settled

- **Settled (owner, yes on every finding): the pre-results audit round 1**
  (`docs/audit_2026-10-08_preresults_round1.md`, Fable 5.1, read-only, at
  6e79757; no high, 4 medium, 11 low). M1 (robust tests oversized): (a)
  measured size printed beside every robust p, (c) joint F kept as
  reported with its size, (b) a size check kept only where its own size
  is near 5% (D66): plain OLS p for the ENSO tests (H3a, H3b, H4
  contrast, C1, C2), not for H5 and H6 (7-9% at their predictors' lag-1
  autocorrelation up to 0.27), the year-block bootstrap p dropped
  (6-9%). Rejected: the bootstrap as the check (owner's condition: kept
  only if near 5%). The H4 Driscoll-Kraay contrast with regions
  correlated 0.5 measured 8.2% from 3,000 datasets, between the audit's
  10.0% (500) and session 7's 6.3% (1,000).
- **M2 recorded, no rule change:** 104 CNFDB polygons with no year
  (YT 85, Parks Canada 19), outside the read; AB about 8% of 1984-89 area,
  YT about 2% of 1984-99; a stated limitation.
- **M3 fixed (a defect a check found, under D62's firm line): CNFDB
  polygons sharing agency, YEAR and FIRE_ID are merged before the floor**
  (`dissolve_cnfdb`). Owner chose the dissolve over recording the
  per-polygon rule. Before and after: 8 seasons change, all Canadian,
  every US season identical; BC 1998 +1,015 ha (n_fires 22 to 24), BC
  2003 +645 ha (56 to 57), BC 2006 +33 ha, AB 2012 +40 ha; BC 1994, BC
  2004, YT 1990, YT 1995, AB 2012 one fire fewer. CNFDB fires at the
  floor 10,774 polygons to 10,751 fires; overlap left out CNFDB 46,012 to
  46,248 ha. Merged parts disagree on date in some groups; BC
  1998-N40188 joins a 16 May human-caused part and a 6 August lightning
  part (459 ha, 0.8% of BC 1998), kept merged under the rule and flagged
  to the owner. The frozen-rules table rebuilt from the new pieces (YT
  undated 104 to 103; ratios unchanged to 3 decimals).
- **M4 fixed:** `precip_djf_mm` added to the climate controls table
  (identical to `djf_precip_region_year.csv`, 532 of 532 rows, difference
  0), so H1's input is committed and pinned.
- **L1-L11 as recommended:** register and dictionary wording (L1 piece
  counts with a 1 ha tolerance, L2 WFIGS id uniqueness, L3 ERA5 lag, L4
  Daily perimeter shares, L7 zero-indicator SEs, L8 strict inequality, L9
  Idaho time zone, L11 n_fires counts pieces); `loyo_prediction` refuses
  repeated years (L5); helpers `strong_flags`, `center_year`,
  `percent_change`, `lag1_autocorrelation`, `ols_prediction` with
  known-answer tests (L6); tests for several seeds, one-sided contrasts,
  `wald_f_test` alone and every config default (L10).
- **Null and placeholder sweep (owner's request): nothing beyond M2.**
  Counts in the register's "Null and placeholder sweep" row; the round 2
  cold review rechecks it.

### 2026-10-08 - Pre-results gate code built (session 7)

- **Built and tested on synthetic data: every piece of the D51 gate**
  (`src/stats.py`, `src/climate_vars.py`, `src/fire.py`,
  `src/pin_inputs.py`; tests 232 to 264). One-sided p (`t_pvalue`,
  `coef_test`, `permutation_test(alternative=...)`); `use_t` and the D65
  correction in `fit_ols_hac`; `fit_driscoll_kraay` with `inference_df` =
  years - 1 and every p from scipy (`coef_test`, `contrast_test`,
  `wald_f_test`); `h4_test` (contrast and F(4, 40)) on a formula written
  once with SoCal as reference; `with_zero_indicators`;
  `expanding_window`, `validation_summary`, `forecast_skill`;
  `family_tests` and `run_family`; `detrend` (burn_detr); `zscore`
  (ddof 1). Known answers: Newey-West and Driscoll-Kraay covariances
  rebuilt by hand, the H4 contrast equal to per-region OLS slope
  differences, F by hand, Holm and BH by hand, zero indicators equal to
  dropping the years, first expanding-window prediction 2004 (22 or 21).
  All eleven traps of the session 7 kickoff handled in code or recorded
  as methods notes (`docs/methods_register.md` "Statistics").
- **Changed: `fit_pooled` and `fit_ols_hac` refuse a row with a missing
  value** (trap 4). Until now `fit_pooled` dropped such rows (a 2026-10-05
  audit choice, its test replaced) and `fit_ols_hac` accepted a missing
  value at either end of the series, which shortened it silently while
  staying contiguous. Rejected: dropping rows with a warning (H4's panel
  must stay balanced; D57).
- **Built: `temp_jja`, `temp_mam` and `precip_anom`** (climate data only),
  `results/tables/climate_controls_region_year.csv`, 532 rows; numbers in
  the register. Built: the D62 frozen-rules fire table from
  `fire_events.csv` (no new geometry), 291 rows; burned area 93.2% (AB)
  to 100.1% (BC) of the main table; AB 1997 and YT 2022 become zero-fire
  seasons because every fire in them is undated (YT 2022: 97 fires,
  233,108 ha). Printed by region over all seasons, no ENSO column.
- **Found (flagged for the owner, not acted on): the robust tests reject
  a true null more often than 5% on synthetic data**
  (`scripts/stats_size_check.py`, 1,000 datasets, errors independent /
  AR(1) rho 0.3): H4 contrast Driscoll-Kraay 0.062 / 0.081, H4 joint F
  0.175 / 0.192, per-region Newey-West two-sided 0.075 / 0.092, one-sided
  0.061 / 0.078. The registered methods are frozen; options go to the
  owner with the first audit round.
- **Pinned: the 25 input files** (`results/tables/input_pins.csv`, sha256,
  2.12 GB; trap 7). RONI's file is the download of 2026-10-06, ONI's of
  2026-10-04.

### 2026-10-08 - Small-sample correction on in every robust fit

- **Decided (owner, before any result): the robust covariances are
  corrected for the parameters the fit used, in every fit** (D65). Read
  from the statsmodels 0.15.0 source: `cov_type="HAC"` defaults to no
  correction (`use_correction=False`), `"hac-groupsum"` (Driscoll-Kraay)
  to the cluster factor G/(G - 1) x (N - 1)/(N - K), `"cluster"` to the
  same factor. Leaving the defaults would have corrected H4 but not the
  per-region tests. Chosen: n/(n - k) for Newey-West, the cluster factor
  for Driscoll-Kraay and year clustering (`ROBUST_SMALL_SAMPLE_CORRECTION`
  = True; `src.stats`). Effect on SEs (arithmetic): H3a sqrt(42/39) =
  +3.8%, H3b sqrt(42/38) = +5.1%, H4 Driscoll-Kraay (41 years, 205 rows,
  15 parameters) +4.9%; estimates unchanged. Rejected: off everywhere (the
  kickoff's lean, matching Stata's xtscc per the statsmodels docstring;
  needs an override of the Driscoll-Kraay default) and the software
  defaults (two rules in one analysis). Frozen plan deviations log, row 7.

### 2026-10-08 - Pre-results audit in repeated rounds

- **Decided (owner): the pre-results audit runs in rounds until a round
  finds nothing high** (D64), as before the freeze (a targeted audit and
  two fix reviews, 2026-10-07). Round 1 is a cold read-only audit of the
  statistics code, the new variables, the frozen-rules fire table and the
  fire build (D51, D62); its findings are settled with the owner and
  fixed; each later round is a fresh cold read-only review of the fix diff
  and the whole gate. The gate closes when a round finds nothing high and
  the owner agrees; that close is D62's firm line. Each report is saved
  unchanged as `docs/audit_YYYY-MM-DD_*.md`. Owner's reason: "I want to be
  extra certain we have a solid foundation before the following steps."
  Rejected: one audit round (the D51 wording); a fixed number of rounds
  (the pre-freeze series needed three before nothing high remained).
  The Claude Code Project is decided after the last round (D63).

### 2026-10-08 - Claude Code Project decided after the audits

- **Decided (owner): the Claude Code Project go/no-go waits until the
  pre-results audit (D51, extended by D62) is settled** (D63). The shared
  statistics code, the missing variables and the frozen-rules fire table
  are built in the main session; the decision on parallel threads is made
  for the hypothesis runs that follow the audit. Why: the gate's pieces
  share `src/stats.py` and depend on each other, so threads would mostly
  wait on one another and add PR review while the code is still in flux;
  the hypothesis runs (H1-H6, C1-C2) are separate tasks that need only the
  committed tables. Rejected: setting the Project up at the start of
  session 7 (the reminder's original timing, and `ACTION_PLAN.md` Phase 4
  "Before starting"). `docs/session7_kickoff.md` and the memory note
  updated.

### 2026-10-07 - D60 re-run on 2023: pass, frozen years stand

- **Found: the source-agreement rule passes on 2023 in all four US
  regions, so the fire tests keep the frozen years** (US 1984-2025,
  Canada 1984-2024; D61's rule). Union area of 2023 ignitions in each
  region's 2023 window, d = log(1 + ha_WFIGS) - log(1 + ha_MTBS): PNW
  162,501 vs 158,812 ha, d = -0.023; AK 116,540 vs 114,425, -0.018;
  NorCal 80,397 vs 81,276, +0.011; SoCal 45,158 vs 43,737, -0.032; all
  under 0.10. NorCal's +0.234 (summed) was the overlapping WFIGS polygons.
  No year changes, so no new row in `ANALYSIS_PLAN.md`'s deviations log.

### 2026-10-07 - Frozen-rules robustness run; firm line on fire rules

- **Decided (owner, 20:17 UTC-07:00): every burned-area test is also run
  on a fire table built under the rules as frozen** (D62, scope addition):
  H2, H3a, H3b, H4, H5, H6 and C2, reported in one table beside the main
  results, uncorrected (as the ONI runs). The variant reverses each
  post-freeze fire rule that the frozen text still lets be built: summed
  clipped area instead of union (D61), MTBS "Other" dropped (the frozen
  list names Wildfire, Wildland Fire Use and Unknown; D58), CNFDB fires
  without month dropped (the frozen text assigns by ignition date; D59),
  the frozen years (US 1984-2025, Canada 1984-2024) whatever the D61
  re-run gives. The 2024-01-01 cutover is the same in both: it is the
  frozen rule ("MTBS for every year it holds complete") applied. If the
  two disagree, the difference is reported as a limitation of the main
  analysis. Why: six rules changed after the freeze (D55, D57-D61), four
  after fire data was opened; the variant shows whether they matter
  instead of asking the reader to trust them. Rejected: headline tests
  only (the code is shared, the cost small).
- **Decided (owner): the firm line on fire record rules is the end of the
  pre-results audit (D51), extended to the fire build.** Until that
  read-only audit closes, a rule may change only for a defect a check
  finds, logged with before-and-after numbers and what had been seen;
  after it, before the first registered test, bug fixes only. No view
  that sets burned area beside ENSO until Phase 4 (the committed table
  holds both; a 2023-2025 printout on 2026-10-07 showed them together
  once). Rejected: the line at this commit (the audit could still find a
  rule defect) and at the first test without extending the audit.
  `ACTION_PLAN.md` Phase 4, marked `[mid-project: D62]`.

### 2026-10-07 - MTBS complete through 2023; cutover, union area, D60 re-run

- **Decided (owner, 20:03 UTC-07:00, before the re-run was computed):
  the MTBS-to-WFIGS cutover moves to 2024-01-01; each region-season's
  burned area is the union of its counted fire pieces; D60's rule is
  re-run on 2023** (D61; supersedes the 2025-01-01 cutover and D60's
  outcome, both below). The D60 check as computed (2024 ignitions) gave
  d = +0.27 (PNW), +0.90 (AK), +0.24 (NorCal), +0.23 (SoCal), all above
  0.10. A fire-by-fire match (each WFIGS fire against the MTBS polygons
  it intersects, 2021-2024) showed the cause: MTBS has not yet mapped
  114 WFIGS fires of 2024 (537,228 ha; McDonald AK 62,212 ha, Lone Rock
  OR 55,532, Wapiti ID 52,230), 22-58% of each US region's WFIGS area,
  against 0-0.1% in 2021-2022 and 0-4.2% in 2023. On fires both hold,
  the products agree: one-to-one pairs WFIGS/MTBS area median 0.959,
  0.982, 0.980, 0.983 and total 0.967, 0.972, 0.974, 0.986 (2021-2024;
  108, 192, 85, 127 pairs). D60's premise ("the window both sources hold
  complete") failed for 2024, so its d measured MTBS's mapping backlog,
  not a product difference. The one outlier, NorCal 2023 (d = +0.234),
  is WFIGS overlap: "BLOCK" (6,504 ha) lies over Elliot, Ufish and Head,
  also listed, and Mosquito is three overlapping polygons (13,836, 5,668,
  1,929 ha) against MTBS's one (14,616 ha). The build's overlap check
  found area counted twice in every source (CNFDB 46,012 ha, WFIGS
  38,439, MTBS 1,767 over all region-seasons; largest AB 2012 24,692 ha,
  PNW 2026 WFIGS 24,243, BC 2015 14,147, NorCal 2025 WFIGS 10,349).
  Cutover 2024-01-01: MTBS for ignitions through 2023, WFIGS from 2024
  (`MTBS_WFIGS_CUTOVER`). Union area: overlapping polygons of one
  region, season and source count once; fire counts and the whole-fire
  floor unchanged. D60 re-run, fixed before computing: d = log(1 +
  union ha WFIGS) - log(1 + union ha MTBS) for 2023 ignitions in each
  region's 2023 window, threshold 0.10 (`SOURCE_CHECK_YEAR` 2023). Pass
  in all four US regions: the frozen years stand (US 1984-2025, Canada
  1984-2024). Fail in any: PNW, AK, NorCal and SoCal end at 2023 (MTBS
  only, no WFIGS in any test), Canada stays at 2024. Rejected: keeping
  the 2025 cutover (US 2024 from an MTBS year missing 22-58%), ending
  every region at 2023 outright, and D60's literal outcome (all end at
  2024, which would still need WFIGS for 2024).

### 2026-10-07 - CNFDB terms re-read at download (session 6)

- **Found: the CNFDB release carries two terms the first read did not
  cover; neither stops the committed table, one adds a notice.** (1) The
  update log says the BC polygons are "Licensed under Open Government
  License - British Columbia"; OGL-BC 2.0 permits any lawful use with its
  attribution statement, now notice 12 in `DATA_SOURCES.md`. (2) The
  release's documentation PDF says "an End-User Agreement is required",
  linking a page that returns 404; the agreement it names (found by web
  search; its Datamart page also 404) is the older access contract,
  internal use only, no distribution without Canada's consent, with "Her
  Majesty the Queen" as party (before September 2022). The live catalogue
  record (checked in a browser 2026-10-07) and the release's ISO 19115
  record name only the Open Government Licence - Canada, so the OGL-C is
  read as governing and the PDF sentence as stale (its citation is dated
  2021 too). Left open for the publish decision: confirm with CWFIS only
  if the catalogue licence changes. The repository is private, so the
  committed `results/tables/fire_region_year.csv` is not a publication.

### 2026-10-07 - Fire record rules settled at download (session 6)

- **Decided (owner, 16:40 UTC-07:00, before the comparison was computed):
  the last fire season of every region is set by a fixed source-agreement
  rule on the 2024 MTBS-WFIGS overlap** (D60). For PNW, AK, NorCal and
  SoCal, burned area of fires ignited in calendar 2024 (the window both
  sources hold complete; California's January 2025 fires left out because
  MTBS lacks Border 2) is built twice under identical rules, once from
  MTBS only and once from WFIGS only, and d = log(1 + ha_WFIGS) -
  log(1 + ha_MTBS). If |d| >= 0.10 in any of the four regions, every
  region's fire tests end at 2024 (one perimeter product per country in
  every tested season, a balanced panel); otherwise the frozen plan's 2025
  stands for the US regions. Threshold from D57: NBAC's 11-17% area gap
  (a log step of 0.12 to 0.19) was judged too large to splice into the
  last season. Fire data had been opened when this was set (attribute
  profiles, MTBS fire counts and acres by state and year); nothing had
  been joined to ENSO. Owner's question was whether a project-wide 2024
  end is the better call; rejected: ending at 2024 outright (gives up a
  season without evidence that the splice harms it) and keeping 2025
  without a rule. Either outcome is a dated row in `ANALYSIS_PLAN.md`'s
  deviations log only if the years change.
- **Decided (owner): MTBS incident type "Other" is the plan's "Unknown"**
  (D58): kept, counted and reported separately. The release of 2026-10-07
  holds Wildfire 16,779, Prescribed Fire 9,639, Other 4,311 and Wildland
  Fire Use 203 polygons and no "Unknown"; its own metadata documents the
  fourth type as "Unknown" (UNK). In WA, OR, ID, CA and AK, Other is 128
  fires and 1.04 M acres (1.0% of Wildfire acres), peaking June-September,
  including wildfires such as KAN 7 (AK 1990, 367,541 acres) and Bear
  Wallow Complex (CA 2008). Rejected: dropping Other. `MTBS_KEEP_TYPES`.
- **Decided (owner): the MTBS-to-WFIGS cutover is by ignition date, on
  2025-01-01**: MTBS for fires ignited through 2024-12-31, WFIGS from
  2025-01-01. MTBS holds 2023 and 2024 at their usual counts and only 14
  fires from 2025 in the five states (none in AK or WA); its January 2025
  holds Palisades, Eaton and Hughes but not Border 2. Cutting by season
  year would have taken California's season-2024 January fires from an
  incomplete MTBS year. California's season 2024 therefore takes its
  January 2025 fires from WFIGS. `MTBS_WFIGS_CUTOVER`.
- **Decided (owner): CNFDB fires with a year but no month or day count for
  season YEAR** (D59), flagged, and are left out of season length. Large
  fires (>= 405 ha, CFS area, 1984-2024, by agency): YT 102 undated of
  1,038 (97 in 2022; 3.4% of area), AB 39 of 648 (5.0%), BC 0 of 1,140.
  Among dated fires the area outside the season window is 0.04% (BC),
  0.9% (AB) and 0.01% (YT), so an undated fire is almost surely in season.
  Rejected: dropping them (YT 2022 would lose 97 fires).
- **Decided: each region takes fires only from its own country's sources**:
  PNW, AK, NorCal and SoCal from MTBS and WFIGS, BC, AB and YT from CNFDB.
  A cross-border fire's whole polygon in its source sets the 405 ha floor;
  the part across the border is counted from the other country's record,
  so no area is counted twice. Rejected: clipping every source to every
  region (double counts border fires such as those on the WA-BC line).

### 2026-10-07 - Canadian fire series end at 2024

- **Decided (owner): BC, AB and YT fire tests use seasons 1984-2024; PNW,
  AK, NorCal and SoCal keep 1984-2025** (D57; settles D56), before any
  fire data was downloaded or opened. CNFDB polygons end in 2024. A
  documentation-only NBAC probe (PR #22) found NBAC holds 2025 but its
  area runs 11-17% below CNFDB on average (method papers), it has no true
  ignition date (agency start date or first hotspot; 82% of polygons
  dated, 1986-2020), splits events at boundaries and remaps past years
  each release. A 2025-only fill-in would build a step of about -0.12 to
  -0.19 in `log_burn` into the last season, the size of the effects under
  test. H4's pooled model uses 1984-2024 for all five regions (balanced,
  Driscoll-Kraay df 40); expanding-window predictions 2004-2024 for the
  Canadian regions; the Canadian 2027 forecasts are trained to 2024. CNFDB
  2025, when released (about January 2027), is reported beside the
  results, not substituted (as later RONI revisions are). Rejected:
  waiting for that release, NBAC for 2025 only, NBAC for the whole
  Canadian series (a post-freeze swap of the named source with new
  handling rules), the NFDB points (agency-reported areas, against the
  project's own-measurement rule). `CNFDB_LAST_YEAR`,
  `FIRE_LAST_YEAR_BY_REGION`, `POOLED_LAST_YEAR`; second row of the
  frozen plan's deviations log.
- **Merged PR #21 (fire licence reads) and PR #22 (NBAC probe)** after
  clean pre-screens and the owner's yes; NBAC's ledger row and notice 11
  stay for reference (notice 11 applies only if NBAC is used).

### 2026-10-07 - NBAC documentation probe for D56 (side session)

- **Read the NBAC documentation and licence, without opening any data,
  so the owner can choose among the D56 options (2), (3a) and (3b) before
  any Canadian fire numbers are seen; no option chosen.** Found:
  - release v20260513 covers 1972-2025, but no document says whether
    the 2025 BC, AB and YT polygons rest on agency perimeters or on
    satellite mapping alone;
  - polygons are grouped into fire events (`NFIREID`, `GID`) but split
    at provincial, territorial and park boundaries;
  - there is no true ignition date: `AG_SDATE` (agency start, recorded
    or detection date) and `HS_SDATE` (first hotspot, from 1989 only);
  - a `PRESCRIBED` flag exists, from agency reports;
  - NBAC replaces many agency (CNFDB) polygons with Landsat mapping, and
    the method papers document NBAC area as mostly lower than CNFDB's,
    by about 11-17% on average;
  - how 1984-1985 were built is undocumented;
  - past years are revised between releases.
  Licence: Open Government Licence - Canada 2.0, PERMITTED WITH
  CONDITIONS (provider's citation, licence link; no act owed). Answers
  and sources: `docs/nbac_probe.md`. Files: `docs/nbac_probe.md`,
  `DATA_SOURCES.md`.

### 2026-10-07 - Fire perimeter licences read (side session)

- **Found MTBS burned-area boundaries public domain, with acknowledgement
  the only condition (PERMITTED WITH CONDITIONS).** Read with the
  `read-licence` skill after the freeze (acf7a80), terms only, no data
  fetched. The ScienceBase release (ver. 12.0, April 2025, 1984-2024) is
  marked CC0, and both FGDC records say "There are no restrictions on use,
  except for reasonable and proper acknowledgement of information
  sources." Derived region x year tables can be committed and shown on the
  site with the citation and credit line (`DATA_SOURCES.md` notice 8); no
  act is owed. Direct Download serves a newer quarterly-updated file than
  the citable release, so the release name and download date are recorded
  at download. Files: `DATA_SOURCES.md`.
- **Found WFIGS Interagency Fire Perimeters usable with its disclaimer
  carried along (PERMITTED WITH CONDITIONS), with no licence named.** The
  item's Terms of Use field is a liability and warranty disclaimer only;
  permission rests on the WFIGS site ("Public Data is freely accessible to
  anyone that wishes to use it"), the ArcGIS Online grant for public items
  (use, reproduce, derivative works, distribute) and federal public
  domain. Chose the all-years item (5e72b169..., `NIFC_Authoritative`) for
  recent seasons; rejected the year-to-date item (rolls over each
  January) and a 2025 copy owned by an unrelated account (no terms).
  WFIGS holds perimeters "starting in 2021", so the MTBS-to-WFIGS cutover
  cannot fall earlier. Footer copyright and non-federal contributors leave
  a low, open risk. Files: `DATA_SOURCES.md`.
- **Found the CNFDB fire polygons under the Open Government Licence -
  Canada (PERMITTED WITH CONDITIONS), and found they end in 2024.** The
  CWFIS catalogue record and the ISO metadata both name OGL-Canada 2.0;
  the provider's citation and a licence link are the conditions
  (`DATA_SOURCES.md` notice 10), no act is owed. The polygons cover BC,
  AB and YT through 2024 only, so the frozen plan's 2025 fire season has
  no Canadian polygons yet (deviation D56). Not decided here: waiting for
  the next release, ending the Canadian series at 2024, or using the NFDB
  points or NBAC (1972-2025, same licence, a satellite-based composite and
  so a different method from the agency polygons) for 2025; each is a
  change to a pre-registered setting or source and is the owner's call.
  Files: `DATA_SOURCES.md`, `docs/plan_deviations.md`.

### 2026-10-07 - Tracker data arrival measured

- **Probed CDS for ERA5-Land monthly means (owner's go-ahead)**: one cell,
  2 m temperature, July, August and September 2026, all published on
  2026-10-07 (41-54 s per request; probe files in the session scratchpad,
  not kept). Monthly means arrive within about a week of the month's end,
  so the live tracker runs as PR #19 planned. Supersedes the arrival claim
  in "Freeze and tracker" below (D55 supersedes D54): the "measured
  3-month lag" was the pre-start review's download margin
  (`ERA5_LAG_MONTHS`), and the July end of the data followed from it.
  Rejected building monthly totals from hourly ERA5-Land (not needed).
- **Set `TRACKER_DATA_DAY` = 7** (the day observed; September's exact
  release day unknown, rechecked at the first update).
- **Decided (owner) to change `ERA5_LAG_MONTHS` from 3 to 1 at the first
  tracker update (early November 2026), as a hard-line item**, not now: it
  needs a SPEI refit (about 55 min), and the October download is due then
  anyway. Logged today as the first row of the frozen plan's deviations
  table, so the decision is dated before any fire data was downloaded or
  opened, in keeping with the freeze. Its effect: 2026's summer values
  (JJA SPEI, whiplash, soil moisture; descriptive) fill in; no registered
  test changes (fire tests end with 2025, climate tests use DJF through
  2026, calibration 1951-2020).

### 2026-10-07 - Freeze and tracker

- **Froze `ANALYSIS_PLAN.md` (owner's explicit yes)**: commit acf7a80,
  2026-10-07 13:35:38 UTC-07:00, tag `analysis-plan-frozen` (annotated,
  pushed), building on 96a1908; the "Frozen on" line gives the minute
  (owner's request). No fire data had been downloaded or opened anywhere.
  Three audit rounds that day (one prefreeze audit, two fix reviews, the
  last on a whole-plan read) found nothing high by the end.
- **Decided (owner) to keep the Claude Code Project on standby and decide
  when the Phase 4 statistics code starts** (the D51 gate), and to send the
  three fire licence reads (MTBS, WFIGS/NIFC, CNFDB) to the standing side
  session. Rejected setting the Project up at the freeze: its draft
  instructions predate the frozen plan, and the licence reads fit the side
  session's existing rules. The reminder note moved to the statistics
  code.
- **Added the settled tracker settings to `src/config.py`**
  (`TRACKER_WINDOW` 2026-10-01 to 2027-04-30, `TRACKER_FREEZE_DATE`),
  from PR #19's table; verification dates follow `FIRE_SEASON_MONTHS`.
  **Left out the data-arrival dates** (D54): PR #19 assumed monthly data by
  the 6th of the next month (October's data in early November) and flagged
  it as an assumption to measure; the project's own measured lag
  (`ERA5_LAG_MONTHS` = 3) has ERA5-Land monthly means ending in July 2026
  on 2026-10-07, so October would arrive about January. Owner's decision
  pending.

### 2026-10-07 - Second fix review settled

- **Ran a second read-only review in a fresh cold session** (owner's
  choice, "one more just to be safe"; the first review session retired),
  of ee9503d..b9153a4 and the whole `ANALYSIS_PLAN.md` as it would be
  frozen. Report: `docs/audit_2026-10-07_fixreview2.md` (the session's own
  file, line endings normalised). Nothing high; one medium-low open choice,
  eight low items. It confirmed the station outputs byte-identical to
  ee9503d, that each new test fails under the rule it guards against
  (the SC04/SC05 test under the rejected best-row rule), every plan
  setting against `config.py`, and the four dedupe variants' dry-run
  numbers. The owner accepted every recommendation below.
- **Decided (owner) that the ONI robustness runs use ONI's own strong set
  and near-threshold band** (finding 1; D53), by the same rules: within
  0.06 of 1.5 after rounding, 1972-73 1.55, 1991-92 1.54, 2009-10 1.47
  (checked from the cached ONI file); ONI's strong set adds 2023-24 and
  drops 1965-66. Rejected flipping RONI's three winters under ONI (1.24,
  1.18, 1.47 there) and no flip under ONI.
- **Decided (owner) on the strong-only scope** (finding 8): the regions of
  the parent test (H1 the five main regions, H2 all seven), every test
  two-sided and uncorrected, exploratory. Rejected carrying H2's one-sided
  directions to 3 strong seasons.
- **Decided (owner) to report leave-one-year-out coverage for the two
  single-predictor H6 forecasts too** (finding 9), as for H3a.
- **Closed the zero-fire wording gap** (finding 2): a dated pointer on the
  2026-10-05 "Zero-fire years" note to "Execution details", and the
  `ZERO_YEAR_PCT_LIMIT` comment in `config.py`. The precedence sentence
  covers original text against a dated note, not two dated notes.
- **Records** (findings 3-7): the `dedupe_sites` docstring now states the
  tie-break the code uses (shared-row rank, then the ID's best rank, then
  values, then ID) and that site coordinates come from an ID's first row,
  a known limitation left unchanged at the freeze (checking every
  coordinate could find new pairs); register: YT first has 3 stations in
  1968, not 1965 (2 in 1965-67); the strong-only row carries D52 and D53;
  "every headline test" replaced in the register, dictionary and
  `config.py` by every registered test that uses the index.
- **Corrected** "Fix review findings settled" (this date): restricting the
  ONI runs to the four headline methods would have left C1 and C2 without
  the index check, not "C1, C2 and H4's contrast" (H4 is headline method
  3). Season length's dating (ignition) is in the data dictionary, not the
  plan; left (descriptive).

### 2026-10-07 - Fix review findings settled

- **Ran a read-only review of the pre-freeze fixes (97663e5..ee9503d) in a
  cold session with a neutral prompt, on a different model (Fable 5.1)**
  (owner's choice). Report saved as `docs/audit_2026-10-07_fixreview.md`
  (the session's own file, unchanged but for line endings). Nothing high or
  medium; every number recorded at ee9503d reproduced, the SPEI cache again
  the ML optimum, the three D49 claims confirmed against the R source. The
  owner accepted every recommendation below.
- **Fixed the duplicate-site priority for station IDs that mix sources**
  (F1). The review found the priority read from an ID's first row (5
  provincial IDs ranked as CanSWE) and proposed the best source present.
  That rule changed the table: CanSWE files Yukon course 09CA-SC04's
  1978-84 values under SC05, the course that replaced it 15 km away, so
  SC05 ranked as Yukon-file, kept the CanSWE copies and SC04 vanished
  (2,167 stations; the index changed). Decided instead to read priority
  from each copy's rows in the shared years: the copy holding the
  lower-priority rows there loses them. Output byte-identical to ee9503d
  (18 pairs, 509 station-years, 2,168 stations). Tests for the shared-row
  rule and the SC04/SC05 pattern, and for the snowy-years case the first
  test missed (F2: 21 shared years, 3 snowy, all disagreeing).
- **Corrected two records of 2026-10-07** (F3, Info): one of the six pairs
  no longer merged (22F05/710:OR:SNTL) agreed in its single snowy year and
  dropped out for having fewer than 3, not for disagreeing ("Pre-freeze
  audit findings settled" says all six disagree); and the offset
  near-duplicates under the snowy-years rule number 5, not 11. Register:
  933 stations with a normal (YT 54).
- **Decided (owner) on four plan clarifications** (F4, F5; D52): the R
  SPEI note covers only its three points (the fit stays ML, heat index and
  calibration 1951-2020); one-sided permutation p is (count + 1) / (n + 1);
  zero-fire indicator fits have slightly different HAC and Driscoll-Kraay
  standard errors from a fit without those years (accepted); the
  near-threshold flip is one run with all three winters flipped together;
  ONI robustness runs cover every registered test that uses the ENSO index
  (H1, H2, H3a, H3b, H4, C1, C2, strong-only), not H5 and H6. Rejected the
  four headline methods only (would leave C1, C2 and H4's contrast
  without the index check).
- **Recorded, not changed** (G1-G3): no test checks Thornthwaite against an
  independently published worked example (R not installed; no PET values
  written from memory; constants confirmed against the R source by two
  sessions). The per-cell change statistics of the refit (0.03 and 0.01
  SD, largest 0.77) come from the refit session's comparison with a scratch
  backup of the old cache, not kept in the repo. Notebooks 02-03 were
  re-executed with nbconvert in ee9503d (the review compared their outputs
  but did not run them).

### 2026-10-07 - Pre-freeze audit findings settled

- **Ran a targeted read-only audit in a separate cold session with a neutral
  prompt** (owner's choice; Part 3 of `docs/session5_kickoff.md`) over
  every change since bfbc802 and the plan's executability. Report saved
  unchanged as `docs/audit_2026-10-07_prefreeze.md` (eeebbe5). Nothing high:
  every committed table and every recorded refit number reproduced
  independently, and a multi-start optimiser found no better SPEI fit than
  the cache. Findings P1-P6 (medium to low), stale records (R), two info
  items. The owner accepted every recommendation below.
- **Decided (owner) that the zero-fire sensitivity keeps every row in the
  regressions and gives each zero region-year its own 0/1 indicator**
  (P1; D50): one dummy per year fits that year exactly, so the coefficients
  and residual df equal a fit without it, while the series stays one row
  per year for the HAC and Driscoll-Kraay lags (`fit_ols_hac` refuses
  gaps, as decided 2026-10-06). Permutation tests (H2) drop the zero years.
  Rejected the longest gap-free run (could discard many years) and HAC
  across gaps (the fault removed on 2026-10-06).
- **Decided (owner) on a precedence sentence under "Frozen on"** in
  `ANALYSIS_PLAN.md` (P2; owner's wording): where the original text and a
  dated decided note or "Execution details" disagree, the dated note
  governs, with the deviations listed. Rejected rewriting the stale
  passages (owner's prose).
- **Decided (owner) on six open execution choices** (P3; "Execution
  details"): regression one-sided p is the tail in the stated direction (an
  opposite-sign estimate gives p above 0.5); the 2027 intervals are OLS
  prediction intervals from the full training fit, with LOYO and
  expanding-window coverage reported; expanding-window validation covers
  H3a and the two single-predictor H6 models, error as RMSE and MAE of
  `log_burn`; the H4 joint Wald test is F(4, years - 1), matching `use_t`
  and the frozen df (chi-square rejected as large-sample); `temp_jja`,
  `temp_mam`, `precip_anom` and `precip_djf_mm` use all land cells, glacier
  cells included (only SWE and SPEI exclude them); strong-only exploratory
  results cover H1 and H2 and their near-threshold flip. Also clarified
  (owner) that Holm decides significance at α = 0.05 after correction,
  BH reported alongside (the Inference note; "Reporting rules" did not
  name the correction).
- **Decided (owner) to add a trend-only baseline to the expanding-window
  validation** (scope addition, before any fire data; D50): RMSE and MAE
  of `log_burn ~ year` per region, and a skill score 1 - RMSE(model) /
  RMSE(trend-only) for H3a and the two single-predictor H6 models;
  descriptive, no significance test. A significant H3a slope shows El
  Niño relates to burned area; the skill score shows whether it improves
  the forecast over the region's trend, which is the 2027 forecast's
  claim. Registered now so either outcome is clean. Rejected adding it
  later as exploratory (a baseline chosen after the results) and a
  Diebold-Mariano test (22 held-out seasons give it little power).
- **Decided (owner) that duplicate station sites must agree in years with
  snow** (P4): agreement within 2.6 mm counts only where either site holds
  more than 2.6 mm, at least 3 such years. Two bare low sites had agreed
  every snow-free year. Dry run: 18 pairs instead of 24, 509 station-years
  dropped instead of 576, 71,250 rows and 2,168 stations; all 6 pairs no
  longer merged are low Oregon sites with 0-3 snowy shared years that
  disagree in them (the audit named 3; the rule found 3 more of the same
  kind); station z changes by at most 0.016 (PNW). The 11 near-identical
  pairs 3-12 km apart stay unmerged, recorded as a known gap (no effect on
  the index today). Rejected a wider distance threshold (one more arbitrary
  cut).
- **Decided (owner) that PET and SPEI follow the SPEI reference
  implementation (R package SPEI)** (P5, P6; D49): exponent constant
  0.01792 (xclim's 0.01791 changed PET by at most 0.14%); the power law at
  every temperature, as `SPEI::thornthwaite` does (Thornthwaite's 1948
  table for monthly means at or above 26.5 °C is not used; the R source was
  read 2026-10-07); the 3-month window sums monthly amounts of P - PET in mm
  (the code averaged daily rates, so February counted as a full month).
  xclim accepts `mm/month` input; its rolling mean of three amounts is
  their sum / 3, which standardises identically (6e-6 in a 60-year test).
  Rejected rewording only (the freeze is the last cheap refit) and the
  hot-range formula (departs from the SPEI reference). Measured (full
  refit of both domains, 2026-10-07; main 1,586 s, north 1,618 s):
  per-cell mean change 0.03 SD in February, 0.01 in August, largest 0.77;
  regional series against the 2026-10-06 values over 1951-2025, DJF
  SPEI-3 r 0.9990-0.9995 (largest change 0.15, AB), JJA r 0.9999 (0.05),
  whiplash r 0.9994-0.9997 (0.16); El Niño minus neutral moves by at most
  0.02 (PNW whiplash +0.60 to +0.58, PNW DJF -0.42 to -0.40, BC JJA +0.33
  to +0.34); DJF 2026 SoCal -0.72 to -0.70 (cells at the clip 9.9% to
  9.0%), NorCal +0.17 to +0.15, AK +0.75 to +0.69, YT +2.16 to +2.10;
  calibration mean -0.0069/-0.0076, SD 0.985; fitted cells unchanged
  (33,867 main, 33,850 north). Station index after the dedupe change:
  PNW z by at most 0.016 (one station in one year), other regions
  unchanged. Tables, Phase 2 figures and notebooks 02-03 rebuilt; of the
  figures only `whiplash_series_roni.png` changed (the rest byte-identical).
- **Decided (owner) on two checks for the gaps the audits leave**: a short
  read-only review of this session's fix diff by a fresh session or agent
  with a neutral prompt before the freeze; and a pre-results audit gate in
  Phase 4 (D51): the statistics code and variables not yet built are
  tested on synthetic data and audited before anything runs on the fire
  table. Rejected freezing on self-review of the fixes alone (the bias the
  cold sessions exist to avoid).
- **Fixed the stale records the audit listed** (R): data dictionary station
  counts, BC summer SPEI, PET and SPEI wording; `config.py` comments
  (`PET_METHOD`, `SPEI_SCALE`, station minimum frozen at 5); every
  `file.py:line` reference in `docs/methods_register.md` replaced by a
  function name. Recorded the log-logistic shape running to about 1e7-1e8
  in some cell-months (no finite optimum, effectively a logistic; values
  stable to 0.003) in the register.

- **Decided (owner) to compute Thornthwaite PET as Thornthwaite (1948)
  defined it: a climatological heat index per cell from its 1951-2020
  monthly mean temperatures, the N/30 month-length factor, PET 0 at or below
  0 °C** (`pet_thornthwaite`, `PET_HEAT_INDEX_YEARS`; D47). Supersedes the
  PET part of 2026-10-04 "SPEI settings" (xclim TW48). xclim recomputes the
  index from each calendar year: in the incomplete 2026 it was about half
  size and PET 1.5-2.1 times too high in January-April; the 2027 forecast
  input (January-February only) would have been worse; years with no month
  above 0 °C gave 0/0 = NaN (the 46 icefield cells with no February value,
  22 AK and 24 YT); and a per-year index damps PET's warming response
  (independent audit: JJA sensitivity 0.14 vs 0.22 mm/day per °C). Found by
  the re-audit and the independent audit, missed by the first audit.
  Rejected the climatological index without N/30 and complete-year indices.
- **Decided (owner) to leave glacier cells out of SPEI**, as out of the SWE
  means (`GLACIER_SPEI_EXCLUDED`): main 33,867 and north 33,850 fitted cells.
- **Measured (full refit, 2026-10-06):** correlation with the old regional
  series over 1951-2025, DJF SPEI-3 0.992 (SoCal) to 1.000, JJA 0.947 (AK)
  to 0.998, whiplash 0.973 to 0.998. El Niño minus neutral: DJF within 0.04
  of before (SoCal +0.93 to +0.89); JJA smaller by 0.01-0.08 (PNW +0.21 to
  +0.18, BC +0.41 to +0.33, AB +0.48 to +0.44, AK -0.11 to -0.18); whiplash
  PNW +0.63 to +0.60, BC +0.96 to +0.89, AB +1.08 to +1.03, SoCal -0.99 to
  -0.96. DJF 2026: SoCal -1.37 to -0.72, NorCal -0.02 to +0.17, PNW -0.32
  to -0.26. Calibration mean -0.007 and -0.008, SD 0.985 in both domains; no
  fitted cell lacks a February value. SoCal's 2025-26 winter was 3.0 °C
  above its 1951-2020 DJF mean (12.6 vs 9.6 °C), so its DJF 2026 SPEI ranks
  58 of 76 though its precipitation ranks 20, with 9.9% of cells at the
  clip (0% in 2015 and 1998): real warmth, amplified by Thornthwaite's
  temperature sensitivity, a known limitation to state with the 2027
  forecast input. Station index after the dedupe: YT z changed by at most
  0.070, PNW 0.016, others unchanged.

### 2026-10-06 - Plan gaps closed

- **Decided (owner) on the execution details the audits found open, as one
  package** (`ANALYSIS_PLAN.md` "Execution details"): fire tests on seasons
  1984-2025 (`FIRE_LAST_YEAR`; CNFDB 2026 not out in time, WFIGS 2026
  provisional, California's 2026 season closes February 2027), 2027
  (`FORECAST_YEAR`) never in training, expanding-window predictions
  2004-2025 (22, correcting "about 23" in "Inference"); one-sided p = the
  tail in the stated direction, CIs always two-sided 95%; H4's registered
  model without `temp_jja`, its joint Wald test with the same Driscoll-Kraay
  errors; the 2027 forecast from H3a for all seven regions, H6
  single-predictor forecasts secondary, RONI input from CPC's first release
  after February 2027 with the retrieval date, revisions reported; the H3a
  minus H3b gap CI by moving-block bootstrap (3 years, 10,000 draws); the
  block bootstrap checks the `enso_djf` coefficients of H3a and H3b;
  zero-year sensitivity over every burned-area test with `burn_detr`
  re-detrended; station minimum frozen at 5 (no widening for AB or YT);
  `temp_jja`, `temp_mam` via `src.geo.regional_mean`, z-scores with ddof 1;
  strong-only runs against all other years. Rejected going through each
  item separately (owner's choice). Sources: the plan-versus-config re-audit
  and the independent audit (`docs/audit_2026-10-06_climate.md` s.3).
- **Decided (owner): HAC fits use contiguous runs of years only**, and
  `stats.fit_ols_hac` raises otherwise. The fire tests are contiguous
  (1984-2025); station-z checks use each region's contiguous record (AK
  1960+, AB 1963-2025, YT 1975+). Rejected allowing gaps (HAC would treat
  the years either side of a gap as neighbours).
- **Fixed the near-threshold band comparison**: distances to 1.5 are rounded
  to the index's 2 published decimals before comparing (`ENSO_DECIMALS`);
  abs(1.44 - 1.5) is 0.06000000000000005, so 2009-10 would have dropped out
  of the band the plan names (independent audit F7). The earlier config test
  had hidden this with a `+1e-9` tolerance; it now checks the rounded rule.

### 2026-10-06 - Duplicate station sites

- **Decided (owner) to count one site once when two station IDs hold the
  same record:** within 3 km (geodesic, WGS84) and at least 80% of at least
  3 shared years within 2.6 mm (0.1 inch); the lower-priority copy (NRCS,
  then provincial files, then CanSWE; then more values) loses its shared
  years and keeps the rest (`src.stations.dedupe_sites`). Dry run on the
  current table: 24 pairs, 576 station-years dropped (PNW 419, YT 123, AK
  34), 71,759 to 71,183 rows; e.g. NRCS 19A01:WA:SNOW and BC's BCE-WA07 (51
  identical years), Yukon 09BA-SC02 and SC02A. Rejected the narrower rule
  first chosen (same coordinates within about 100 m, identical values):
  the independent audit showed most duplicates sit across networks with
  slightly different coordinates. Affects only the station index (the
  robustness check). `SITE_DUP_*`, `SITE_SOURCE_PRIORITY`.

### 2026-10-06 - stats.py guards

- **Fixed (owner's choice, before Phase 4) four latent faults the
  independent audit found:** `permutation_test` returned the smallest
  possible p (1/(n + 1)) for a NaN difference, now raises on a missing value
  (as `bootstrap_ci_diff` and `adjust_pvalues`, where a NaN counted in the
  Holm family size); `fit_ols_hac` depended on row order (an SE moved from
  0.320 to 0.290 when rows were shuffled) and treated gaps as adjacent, now
  raises unless the rows used are consecutive years in order; `fit_pooled`
  broke on repeated index labels from `pd.concat`, now resets the index.
  Rejected leaving them to Phase 4. Tests added.

### 2026-10-06 - PR #20 review fixes

- **Fixed the six review findings on PR #20 in the main session**, after
  merging it (owner's choice): `join_enso` keeps years after the last
  published ENSO winter with empty ENSO columns (a missing year inside the
  record still raises), so a monthly tracker run before CPC posts DJF 2027
  doesn't stop; `classify_winters` needs the index name (no default that
  could label ONI values RONI); `effects_by_group` skips a region with no
  elevations; malformed BC survey dates are counted as missing, not fatal;
  one SWE-normal rule (`stations.swe_normal_ok`) for `compare_era5` and the
  figures; notebooks 02 and 03 call `src.phase2_figures`, one generator per
  figure. Rejected sending them back to the side session.

### 2026-10-06 - Independent audit and re-audits

- **Ran two re-audits from the main session and an independent audit in a
  separate session with a neutral prompt (owner's choice, for less bias),
  then compared.** Reports: `docs/audit_2026-10-06_climate.md` (independent,
  commit bfbc802) and the follow-up section of
  `docs/audit_2026-10-05_phase2.md`. All three agreed on the high finding
  (the per-year heat index); only the independent audit found the damped
  warming response, the float band fault and the `stats.py` NaN p-value;
  the first audit had missed the heat index and the duplicates. Its claim
  that the 46 cells were all in AK was wrong (22 AK, 24 YT); their cause is
  the 0/0 heat index.

### 2026-10-06 - Phase 2 audit fixes (side session)

- **Fixed the low-severity code findings of the pre-freeze audit in a side
  PR, code only, each with a test** (owner's choice, relayed by the main
  session; `docs/audit_2026-10-05_phase2.md` findings 5, 6, 8, 9, 11-15).
  `snow.glacier_mask` uses complete years only; `whiplash.restandardise`
  sorts by year and raises below 2 calibration values; `stations.anomalies`
  raises below 2 normal years; `stations.effects_by_group` leaves out
  stations with no elevation instead of crashing in `qcut`;
  `el_nino_winters.csv` gains `enso_index`; the `data/processed/` writers in
  `era5`, `snow`, `download_oni` and `stations` write LF; the em-dash check
  scans notebook code cells; `python -m src.phase2_figures` rebuilds the
  five Phase 2 figures from `results/tables/`. Expected effect after the
  re-runs: values unchanged; line endings and the new column differ. Files:
  `src/era5.py`, `src/snow.py`, `src/snow_soil.py`, `src/whiplash.py`,
  `src/stations.py`, `src/download_oni.py`, `src/phase2_figures.py`,
  `scripts/check_no_em_dashes.py`, tests.

- **Decided one ENSO join for every region x year table
  (`era5.join_enso`).** A left join validated many-to-one; years before the
  first ENSO winter are dropped (April 1 1950 and soil moisture 1950 have no
  December 1949 before them, which the inner joins dropped without saying
  so); any later year with no ENSO value raises. `winters`' own
  `enso_index` must name `ENSO_INDEX`, and the table keeps one such column,
  so the new column can't duplicate in a merge. Applied to
  `era5.winter_precip_table` as well as the three tables named in the
  audit, so all four follow one rule. Rejected raising on 1950 too: those
  rows are expected and every table already starts in 1951.

- **Decided that a survey with no date is counted as "missing date", never
  as "outside window".** `stations.nearest_in_window` now refuses undated
  rows, so every caller has to drop and count them first
  (`drop_missing_dates`: NRCS snow courses, BC, Yukon). CanSWE dates come
  from the file's time axis and can't be missing. Rejected counting inside
  `nearest_in_window`, which returns only rows and would need a second
  return value at every call.

- **Decided that `src.phase2_figures` picks regions by rule, not by name.**
  The SWE series leaves out regions whose ERA5-Land April 1 normal is below
  `ERA5_SWE_MIN_NORMAL_MM` (the rule `compare_era5` already uses; SoCal
  0.06 mm), and the station comparison shows regions with a station index.
  Same regions as notebooks 02 and 03 today; the notebooks' own literals
  (finding 10) are left for the main session.

- **Left for the main session:** the whiplash table's CSV writer sits in
  `whiplash.main`, outside this PR's boundary, so it still writes CRLF on
  Windows (one argument, `lineterminator="\n"`); findings 7 and 16 (in
  `stations.compare_era5` and `stations.combine`) and 10 (notebooks) were
  not part of this task. `figures.winter_series` fails with a single region
  (`plt.subplots` returns one Axes); not changed.

### 2026-10-06 - Tracker window and verification dates follow the pre-freeze decisions

- **Decided (owner) to start the season timeline in October and to split
  the verification date by region.** Deviation D46; supersedes the November
  start in "Season timeline page for the live tracker" (2026-10-05, D44).
  H5's `precip_anom` as the October-March total was decided before the
  freeze (DECISIONS.md 2026-10-05 "Hypotheses"), so October 2026 is an
  input: the first countdown now targets October's data (expected about
  6 November, an assumed lag) instead of November's (about 6 December).
  With the California fire windows running June to January of Y+1 (D43),
  the 2027 forecast can be checked in fall 2027 for PNW, BC, AB, AK and YT,
  and for NorCal and SoCal only after January 2028; the page shows both
  dates rather than holding the whole verification panel until 2028.
  Files: `ACTION_PLAN.md`.

### 2026-10-06 - Pre-freeze audit

- **Decided (owner) to audit the climate data and the Phase 2 code before
  the freeze, read-only, by two research agents** (data in the main
  checkout, code against the rules; D35's phase-boundary audit).
  Report: `docs/audit_2026-10-05_phase2.md` (commit audited 5386222). Data
  largely clean: ENSO columns, SPEI standardisation, whiplash, SWE z and the
  station index all recomputed exactly; the 111 unfitted north cells are
  glacier icefields.
- **Fixed (owner's choice): Thornthwaite PET in polar day and night.**
  xclim's TW48 leaves day length NaN there, so north of about 68N every DJF
  and JJA SPEI-3 was missing and regional means skipped those cells (AK
  15.1% and 17.4% of its weight, YT 5.1% and 6.3%). `pet_thornthwaite` now
  repeats xclim's TW48 steps with `infill_polar_days` (24 h and 0 h); main
  domain PET identical (largest difference 3e-15 mm/day), so only the north
  SPEI was refit (1,947 s). Only the AK and YT SPEI and whiplash columns
  changed (largest change 0.62 in whiplash; correlation with the old series
  AK 0.989 DJF, 0.979 JJA; YT 0.999, 0.998). AK El Niño minus neutral
  whiplash -0.01 to -0.08, YT +0.24 to +0.23 (RONI). No pre-registered test
  uses these (AK and YT SPEI and whiplash are descriptive). 46 north cells
  (59-63N, Alaska Range, Wrangell-St Elias) still have no February value;
  they predate the fix, cause open. Rejected disclosing the gap only and
  deferring the fix. Tests added.
- **Fixed (owner's choice): ERA5-Land SWE % and z empty where a region's
  1991-2020 normal is under 10 mm** (`ERA5_SWE_MIN_NORMAL_MM`), the station
  index's floor. Only SoCal is affected (normal 0.06 mm; z had reached 4.69,
  % 1,787); H6 already excluded SoCal from the SWE test.
- **Decided (owner) to pre-register the Driscoll-Kraay t degrees of freedom
  as years minus 1** (`POOLED_DF_YEARS_MINUS`): statsmodels counts them from
  row order (df 0, 4 or 100 for one dataset sorted three ways, standard error
  0.10722 in all). Removes a choice that would otherwise be made after the
  fire data.
- **Decided (owner): the low-severity findings (12 code and data items) go
  to a side-session PR**, with a main-session re-run after merging; stale
  register and dictionary wording fixed in the main session. A second,
  independent audit follows: a separate session with a neutral prompt, plus
  fresh agents from the main session, compared (owner's choice, for less
  bias).

### 2026-10-05 - H1 months and the CLAUDE.md fire window

- **Decided (owner): H1 compares DJF precipitation totals (`precip_djf_mm`),
  detrended per region.** The plan named only a "winter precipitation
  anomaly"; DJF matches the hypothesis wording and the Phase 1 values
  already shown. Rejected Oct-Mar (H5's months). `config.H1_VALUE`.
- **Decided (owner) to update `CLAUDE.md`'s fire-season window line to the
  windows chosen in D43**, since sessions follow it as an instruction;
  marked `[mid-project: D43]`.

### 2026-10-05 - Inference

- **Decided (owner): t critical values (`use_t=True`) in every HAC and
  pooled fit, and Driscoll-Kraay errors (maxlags 2) for the pooled H4
  model, with year-clustered errors reported alongside.** About 42 fire
  seasons give about 42 clusters, where normal critical values overstate
  precision; year clustering allows regions in one year to correlate but
  ignores each region's correlation with its own nearby years, which
  Driscoll-Kraay covers. Rejected `use_t` alone. `USE_T`, `POOLED_COV_TYPE`
  (statsmodels `hac-groupsum`); `src/stats.py` applies neither yet. D45.
- **Decided (owner) to add expanding-window validation: fit on 1984 to
  Y-1, predict Y, from 20 training seasons (first prediction 2004, about 23
  predictions), for H3a and the H6 models**, with coverage and error beside
  leave-one-year-out. Leave-one-year-out lets each fit see later years; the
  2027 forecast cannot. Rejected a 15-season start (shakier early fits) and
  leave-one-year-out alone. `FORWARD_MIN_TRAIN_YEARS`.
- **Decided (owner) on the correction families: one Holm family per
  hypothesis across the main regions, BH alongside** (H1 5 tests, H2 5, H3a
  5, H3b 5, H5 10, H6 9; H4 a single test; AK and YT H2, H3a, H3b 2 each;
  C1 and C2 3 each; ONI and station-z robustness runs uncorrected). H3a and
  H3b kept apart: the same coefficient estimated with and without
  `temp_jja`, so a shared family would penalise one question twice.
  Rejected H3a and H3b shared. `CORRECTION_FAMILIES`; tests check that
  every tested cell sits in exactly one family.

### 2026-10-05 - Season timeline page for the live tracker

- **Decided (owner) to build the live 2026-27 tracker as one site page in
  three states: before winter, tracking and final.** Deviation D44. The
  owner proposed a countdown page if the build finishes before November,
  kept through the winter and then replaced by the results; adopted in the
  form of a November-April season timeline, which holds both countdowns
  (to the first month of data, then to the April 1 snowpack) and becomes
  the results page's record of what arrived when. Rejected a standalone
  countdown page, deleted at the end: a bare countdown reads as a launch
  rather than a study, and the completed timeline is the evidence that the
  forecast was issued before the season, which the fall verification needs.
  The page states the freeze date, and has a state for an El Niño that comes
  in below strong. Mockup (private, example values):
  https://claude.ai/artifact/PirV1BadszhJwgQBHCtYdq. Files:
  `ACTION_PLAN.md`.

- **Decided that the countdowns target expected data arrival, not calendar
  dates.** The test season is Dec-Feb and ERA5-Land publishes each month
  after it ends, so "tracking begins" means the first month's data landing
  (November's, early December) and tracking ends when April 1 snowpack
  arrives. Counting to 1 November would show "tracking started" with nothing
  on the page. The arrival lag is an assumption until measured; the dates
  go in `src/config.py` (main session, after the freeze), and the page
  picks its state from what the pipeline has written to `results/`, so
  nobody flips it by hand.

### 2026-10-05 - Alaska stays one region

- **Decided (owner) to keep Alaska as one region (east of 169W) and state
  the coast-interior limitation for AK, BC and PNW together.** Supersedes
  the conditional in "Hypotheses" below (one region unless a probe found a
  licensed boundary). A research agent found one (read-only, no fire pages
  opened): NOAA NCEI Alaska climate divisions (Bieniek et al. 2012, 13
  polygons, 391 KB, https://www.ncei.noaa.gov/pub/data/cirs/climdiv/AK_climate_divisions.zip;
  NOAA: "in the public domain"), Interior = divisions 3, 4, 5; coastline
  from Alaska DNR, terms not read. Fallbacks EPA Level III ecoregions ("Use
  constraints: None") and USGS Unified Ecoregions (public domain). Kept one
  region because every region is a whole state or province, and BC and PNW
  share the mismatch (wet coasts that rarely burn); splitting only Alaska
  would treat one region differently, and consistency would mean splitting
  BC too. The tested predictors are standardised, which limits how much the
  coast's large totals weigh. Cost: AK predictors partly describe places
  that don't burn, likely diluting an El Niño signal toward zero; an AK
  null is read with that in mind. A descriptive check with the NCEI
  Interior boundary in Phase 4 stays a flagged option (scope), not decided.

### 2026-10-05 - Data rules

No fire data seen; choices rest on the sources and fire regimes. General
knowledge of large California fires outside June-October (Thomas, Dec 2017;
Camp and Woolsey, Nov 2018; the Los Angeles fires of January 2025) informed
the window.

- **Decided (owner) on fire windows: NorCal and SoCal June to January of the
  next year, BC April-October, PNW June-October, AB April-October, AK and YT
  April-September (no longer provisional).** A January Y+1 fire counts for
  season Y, paired with winter (Y-1)-Y. Rejected June-December (January
  fires would fall outside every season) and keeping June-October. Cost:
  California season Y closes in February Y+1, so the fall 2027 check is
  preliminary for California. `FIRE_SEASON_MONTHS` now allows a wrapping
  window ((6, 1)). D43.
- **Decided (owner) on the fire record rules:** MTBS Wildfire, Wildland Fire
  Use and Unknown kept (Unknown counted), Prescribed Fire dropped, Canadian
  prescribed burns dropped where flagged; the 405 ha floor on each fire's
  whole `area_ha`, then clipped to each region; ignition date; MTBS then
  WFIGS with the cutover recorded at download and the overlap year compared;
  CNFDB date completeness reported by decade. Rejected the floor on the
  clipped part (a large fire crossing a border would drop out of a region).
  `MTBS_KEEP_TYPES`.
- **Decided (owner): zero-fire region-years kept, counted and excluded in a
  sensitivity run; no percent change where they exceed 10% of seasons**
  (`ZERO_YEAR_PCT_LIMIT`). Rejected excluding them from the main analysis
  (drops the quietest seasons, biasing burned area up).
- **Decided (owner): near-threshold winters get a flip-flag sensitivity run
  for the strong-only (exploratory) results, no exclusion**
  (`STRONG_SENSITIVITY_BAND` 0.06; RONI 1965-66 1.53, 1986-87 1.46, 2009-10
  1.44). Rejected excluding them and doing nothing extra.

### 2026-10-05 - Hypotheses

Numbers below: El Niño minus neutral under RONI (SPEI in SPEI units, SWE as
z), 1951-2026, descriptive; no fire data seen.

- **Decided (owner) to add H6, "low April 1 snowpack and a dry winter
  predict more burned area", and keep whiplash descriptive** (option D of
  `docs/prefreeze_options.md`). `log_burn ~ swe_z + year` and
  `log_burn ~ spei3_djf + year` per region, each alone; both together
  reported, not tested (correlation PNW 0.61, BC 0.67, AB 0.65). Both are
  known by 1 April in every region, so they can feed the 2027 forecast, and
  they separate the dry-winter path (winter SPEI-3 PNW -0.42, BC -0.55, AB
  -0.60) from the warm-winter path (SWE z -0.41, -0.56, -0.69). Whiplash
  (JJA - DJF) mixes a dry winter with a wetter summer in the north (summer
  SPEI-3 +0.21, +0.41, +0.48), so its sign for fire is unclear; kept as a
  descriptive mechanism variable. Rejected whiplash as the only core
  variable, a winter-to-spring whiplash (still inside the April fire
  windows), and no new hypothesis.
- **Decided (owner): season length, snowfall fraction and summer soil
  moisture are descriptive only.** Season length is undefined with 0-1
  counted fires and CNFDB date completeness is unchecked; snowfall fraction
  and soil moisture are shown beside H6 as mechanism checks. Rejected testing
  season length and soil moisture as an H3b-style control.
- **Decided (owner) on directions and sidedness for every test**
  (`ANALYSIS_PLAN.md` "Directions and sidedness"; `config.TEST_DIRECTIONS`).
  PNW, BC, AB one-sided where theory and precursors agree (H2 higher, H3a
  and H3b positive, H5 lag0 negative, H6 negative); NorCal and SoCal
  two-sided except SoCal H5 lag1 (positive, the fuel build-up); H1
  two-sided and labelled a check, since winter precipitation was seen
  before the freeze (SoCal +62.9%, PNW -10.7%); the H3a minus H3b gap
  reported with a CI, not tested. Rejected H1 descriptive and all
  two-sided.
- **Decided (owner): H4 is one contrast, the mean `enso_djf` slope of PNW,
  BC and AB minus SoCal's, two-sided**, with the joint Wald test of the four
  interaction terms as secondary; AK and YT out of the pooled model.
  Rejected the joint Wald test as primary (four degrees of freedom for a
  one-number question).
- **Decided (owner): H5's `precip_anom` is the October-March total as a
  z-score against the region's 1991-2020 normal.** Covers California's
  autumn and March storms that DJF misses and ends before every fire window.
  Signs: north lag0 negative one-sided, lag1 two-sided; SoCal lag0
  two-sided (grass grows but a wet winter can delay the season), lag1
  positive one-sided; NorCal two-sided. Rejected DJF.
- **Decided (owner) on Alaska and Yukon as their own family (option B):**
  H2, H3a, H3b two-sided (expected higher, positive); H1 and H6
  descriptive; H4 and H5 not extended; MAM temperature as a descriptive
  spring variable. Under RONI an average El Niño barely moves AK (SWE z
  -0.11, DJF precipitation -0.1%) though strong winters do (SWE z -0.42),
  so no one-sided claim. Alaska stays one region unless a short probe finds
  a boundary with clear terms; if none is found, the skews are disclosed. Rejected
  descriptive only and one-sided (option C). D42.

### 2026-10-05 - Trend and climate change

- **Decided (owner) that the climate variables follow the burned-area
  one-method trend rule.** Permutation and bootstrap comparisons use
  residuals from `value ~ year` per region; regressions carry a `year`
  term; figures stay raw. Measured on the RONI tables (2026-10-05): trends
  are large (ERA5-Land April 1 SWE z PNW -0.21, BC -0.16 SD per decade, -1.55
  and -1.19 SD over 1951-2026; snowfall fraction -0.11 to -0.15 SD per decade
  everywhere but YT), but detrending moves the El Niño minus other-years
  differences by 0.04 SD at most (e.g. PNW SWE -0.47 to -0.51), since RONI is
  nearly unrelated to the trend. Rejected raw comparisons (two methods in
  one plan).
- **Decided (owner) to pre-register two secondary compounding tests in their
  own family:** C1 `swe_z ~ enso_djf + year_c + enso_djf:year_c` (PNW, BC,
  AB; 1951-2026; interaction expected negative, one-sided; repeated on the
  station z) and C2 the same on `log_burn` (1984+; expected positive,
  two-sided for low power). Early and late halves as a figure only.
  Rejected exploratory only (a real signal could never count as confirmed)
  and the snowpack test alone. The El Niño x year interaction was not
  computed before registering; the session 3 elevation finding (low-third
  stations -42, high third +3 points of normal) hints at C1, so the plan
  says it is only partly blind. `config.COMPOUNDING_REGIONS`.
- **Decided (owner) to report RONI as the trend-adjusted index for these
  tests, ONI as the check.** Closes the open decision in D38.

### 2026-10-05 - SWE source for the tests

- **Decided (owner) that every SWE test and the 2027 forecast use ERA5-Land
  April 1 SWE, with the station index as a named robustness check.**
  ERA5-Land covers 1951-2026 in all seven regions and is available about
  8 April 2027; the station index starts AK 1960, AB 1963, YT 1975, ends
  2025 in AB, has no NorCal series, and its sites sit high (PNW median
  station normal 3.1 times the grid mean), missing the low-elevation loss
  (strong winters: low third -42, high third +3 points of normal). Yearly z
  correlation with stations PNW 0.95, BC 0.84, AB 0.77, AK 0.80, YT 0.84.
  El Niño minus neutral under RONI (SD), ERA5-Land / stations: PNW -0.34 /
  -0.17, BC -0.53 / -0.48, AB -0.70 / -0.84. Rejected stations primary (no
  NorCal, no Alberta value until about March 2028) and both co-primary
  (doubles the SWE tests in every family). Agrees with
  `docs/alberta_swe_sources.md`.
- **Decided (owner) on the z-score against the 1991-2020 regional normal
  (`era5_swe_z`) as the predictor's unit.** Coefficients read per SD of
  snowpack, comparable across regions and with the station z. Rejected
  percent of normal (skewed; the PNW station median fell to 3.3% in 2015)
  and mm (not comparable across regions); percent stays for display.
  `config.SWE_TEST_COLUMN`, `SWE_CHECK_COLUMN`.

### 2026-10-05 - ENSO index: RONI

- **Decided (owner) on RONI as the ENSO index for every test, with ONI as
  the robustness check re-run for each headline test.** RONI is NOAA's
  official index (PIS 26-05), so the 2026-27 value the forecast uses and the
  index the models are trained on match, and it puts 1950s and 2020s winters
  on one scale. Measured 2026-10-05: correlation with ONI 0.96; 17 of 76
  winters change class; RONI 26 El Niño (7 strong), 26 neutral, 24 La Niña;
  fire record 14 El Niño (3 strong: 2023-24 falls to 1.13; 1965-66 becomes
  strong at 1.53), 9 neutral, 20 La Niña. Correlation with year: ONI -0.01,
  RONI -0.22 (1951+), -0.18 (1984+); the `year` term in the regressions
  covers this. The descriptive climate numbers point both ways (RONI widens
  El Niño minus neutral, e.g. AB SWE -0.56 to -0.70 SD, SoCal DJF
  precipitation +0.62 to +1.02 SD; ONI correlates more with northern SWE,
  PNW r -0.38 vs -0.29), so they were set aside as a reason. Rejected ONI
  primary and both co-primary (doubles the tests). Committed tables and
  figures rebuilt with RONI (figure names now end `_roni`). `ENSO_INDEX`,
  new `ENSO_ROBUSTNESS_INDEX` in `src/config.py`. D41.

### 2026-10-05 - Deviation numbers given at merge

- **Decided (owner, relayed by the main session) that side sessions write
  placeholder deviation numbers and the merge assigns the real ones.**
  Deviation D40. A new side-session entry is titled with a placeholder
  (D\?a, then D\?b, unique within the PR), used for every reference to it. When main is merged
  into the PR, `scripts/merge_append_only.py` gives each placeholder the
  next number after the highest real D on either side and rewrites the
  references in the files the PR changes; `scripts/prescreen_prs.py` does
  the same in its rehearsal, in queue order, and lists the numbers in its
  report so the owner approves the final ones. Replaces the per-session
  ranges (session 3: main D36-D39, side D40 onward). Rejected keeping ranges
  (agreed anew every session, with gaps when a range goes unused). The main
  session keeps numbering its own entries directly. Files:
  `scripts/merge_append_only.py`, `scripts/prescreen_prs.py`,
  `.claude/skills/merge-side-pr/SKILL.md`, both tests.

- **Decided to number a PR's placeholders oldest entry first, from the bottom
  of the deviations log up.** The log is newest first, so numbering in
  reading order would put D40 above D41 and break the descending order the
  log and the merge's ordering rely on. The request said "in order of
  appearance"; read here as the order the entries were written. Owner
  confirmed 2026-10-05.

- **Decided how the merge tells a placeholder from a mention of one.** The
  token is D, a question mark and lower-case letters, standing alone. In
  Markdown prose a backslash before the question mark makes a literal mention
  (it renders the same and is not numbered), as in the first bullet. The
  script, the pre-screen, their tests and the merge-side-pr skill describe
  the rule, so they are skipped, named one by one (`LITERAL_PLACEHOLDERS`,
  at the main session's request). The leftover check covers every other
  tracked file: a placeholder from main's side, or one a PR references
  without defining, stops the merge; tests show it for a `src/` comment, a
  notebook cell and a Markdown plan file. Rejected matching only inside the
  two logs, which would miss `[mid-project: ...]` markers and code comments.

- **Decided to check the day's log separately after a session block is
  folded in (`merge_append_only.py --check-log`).** The block lives in the
  PR description, which no tree check sees, and is folded into `logs/` by
  hand with the numbers the merge printed (merge-side-pr steps 8 and 10).
  Requested by the main session while the owner reviewed the risk of a
  missed reference.

### 2026-10-05 - Data guide page, refreshed every session

- **Decided (owner) to keep a private data guide page listing every data
  type, derived variable, setting and headline number, and to refresh it at
  the end of every main-checkout session.** Published 2026-10-05
  (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P, snapshot 6ad8666)
  after the owner asked for a summary of all data types and values from
  sessions 0-3, so the data set stays understandable as it grows. The repo
  stays the source of truth (data dictionary, config, methods register); the
  page is a readable snapshot. Rejected a committed Markdown copy, which
  would duplicate the data dictionary and go stale. Files: `CLAUDE.md`,
  `docs/session4_kickoff.md`.

### 2026-10-05 - Stations against ERA5-Land (verification)

- **Found that station April 1 SWE agrees with ERA5-Land on the direction
  of the El Niño difference in all five station regions, and on its size in
  BC and AB, while in PNW the station loss is smaller because the network
  sits high.** Correlation of the yearly series (% of 1991-2020 normal /
  standardised): PNW 0.94 / 0.95 (76 years), BC 0.79 / 0.84 (76), AB 0.84 /
  0.77 (63), AK 0.78 / 0.80 (67), YT 0.84 / 0.84 (52). Level ratio (median
  station normal / ERA5-Land regional mean, 1991-2020): PNW 3.10, BC 1.07,
  AB 1.26, AK 0.68, YT 0.88. Strong El Niño minus all winters, points of
  normal, stations / ERA5-Land on the same years: PNW -8.5 / -25.6, BC
  -14.3 / -13.0, AB -38.9 / -32.3, AK -4.1 / -5.0, YT -5.5 / -2.1. Checked
  before interpreting the PNW gap: units (the index is a ratio; normals
  plausible, PNW pillow median 456 mm), dates (exact-date pillows show -1.7,
  courses within 3 days of 1 April -15.1, so the ±10-day window does not
  hide a loss) and the glacier mask (no PNW cells). PNW stations split into
  elevation thirds: low (550-1,470 m) -42.3, mid -4.6, high (1,880-2,800 m)
  +3.0; BC low -20.9, high -10.9. The area-weighted grid mean is dominated
  by lower terrain. Also found: the median index collapses toward 0 in snow
  droughts (PNW 2015: 156 of 368 stations bare, median 3.3%; 2026: 153 of
  344, 4.7%) while ERA5-Land shows about 27% and 40%. Descriptive; no tests.
  An elevation-matched ERA5-Land comparison was flagged as a scope addition,
  not built. Files: `src/stations.py`, notebook 03.

### 2026-10-05 - Snowfall fraction and soil moisture columns

- **Decided (owner) to define the snowfall fraction over November-March as
  the ratio of regional totals, and summer soil moisture as the JJA mean of
  the depth-weighted 0-28 cm layer.** Nov-Mar is the accumulation season
  behind April 1 SWE (rejected: DJF, which misses November and March, when
  the rain-snow line matters most at mid elevations; Oct-Mar). Ratio of
  regional means (cos-latitude weighted, `src.geo.regional_mean`) rather
  than the mean of per-cell fractions, which is noisy in near-dry cells.
  JJA matches SPEI-3 JJA (rejected: each region's fire window, which mixes
  snowmelt-wet April-May soils into the northern means; both). Layers
  weighted 0.25 / 0.75 (7 and 21 cm thick) rather than layer 1 alone, which
  flickers with each shower. Means 1951-2026: snowfall fraction YT 0.99,
  AB 0.92, AK 0.83, BC 0.78, PNW 0.46, NorCal 0.31, SoCal 0.06; soil
  moisture 0.12 (SoCal) to 0.35 m³/m³ (AB). Descriptive unless
  `ANALYSIS_PLAN.md` adds them. Files: `src/config.py`, `src/snow_soil.py`,
  `results/tables/snow_soil_region_year.csv`.

### 2026-10-05 - Regional station index

- **Decided (owner) that the regional station index is the median across
  stations of April 1 SWE as % of each station's 1991-2020 mean, with the
  mean standardised anomaly as a second column.** Normals from stations
  with at least 20 of the 30 years (935 stations); the % column leaves out
  stations whose normal is under 10 mm, where percentages explode. A
  region-year needs 5 stations, else the index is left empty (the counts
  stay in the table); the owner may widen this for AB and YT if their
  analyses prove too short (a 3 was a misclick, corrected the same
  session). Rejected: one method only; 1951-2020 normals (more early
  stations, but normals from different parts of 70 trending years);
  1981-2010; 24 (WMO 80%) or 15 years; 3 or 10 stations. Resulting index
  starts: PNW and BC 1951, AK 1960, AB 1963, YT 1975; AB ends 2025 (CanSWE).
  Files: `src/config.py`, `src/stations.py`,
  `results/tables/station_swe_region_year.csv`.

### 2026-10-05 - Station snowpack cleaning rules

- **Decided (owner) the rules that turn the raw station files into one
  station x year table of April 1 SWE in mm**, every year kept (71,759
  station-years, 2,180 stations in five regions, 1950-2026). Measured on the
  raw files first; each rule's count is in `docs/methods_register.md`.
  - NRCS: dropped QC flags B (1,126 regression back-estimates that copy a
    snow course into a pillow record, so the course would count twice
    before 1980 and the swings are damped, SD 0.54 vs 0.61 of the station
    median) and S (9 values with data, all 8 April negatives among them).
    Kept E (minor adjustment for sensor noise; 27% of SNOTEL), K (estimate;
    782 snow-course values since 2009, median 1.00 of normal), V, N, C, X,
    with the flag in `flags`. Rejected dropping K too, or keeping B.
  - NRCS snow courses dated 1 July (2,163 values, 485 courses): kept with
    `sample_date` empty and flag `date_unknown`; their values look like
    April 1 surveys (median 0.92 of the station median vs 0.96).
  - Manual surveys, all sources: the sample nearest 1 April within ±10 days
    (98.3% of NRCS, 99.99% BC, 99.8% Yukon, 98.8% Alberta inside). Rejected
    ±7 and ±15. Pillows: SNOTEL's midnight value opening 1 April, CanSWE's
    daily value dated 1 April; each pillow is its own station.
  - BC: survey codes kept as flags except the estimates EST AREAL AVG and
    EST PILLOW (7 values); archive and current-season rows were identical
    (103) and are kept once; coordinates from CanSWE (the BC file has none),
    so 7 courses (84 values) without a CanSWE match are dropped.
  - Yukon: "Estimated SWE" kept and flagged (199 values; depth measured,
    density from history); network sites outside Yukon dropped (lowest
    licence risk; 8 stations, 315 values), as were 2 in NWT (no region).
  - CanSWE: provincial files win for the same station-year (15,373 CanSWE
    values replaced, 9,770 added: Alberta, BC and Yukon pillows, BC-run
    courses missing from the BC file). CanSWE flags kept in `flags`; flag Y
    does not occur in AB, BC or YT. Hydro-Québec is never read.
  - Regions by point in polygon, whatever the network: 15 BC-run courses in
    WA and ID count for PNW; 33 stations fall in no region (mostly Alberta-
    and BC-run sites in Montana, plus 3 Idaho stations on the edge and the 2
    NWT sites).
  - NRCS station elevations converted from feet (found while building).
  Files: `src/config.py`, `src/stations.py`, `tests/test_stations.py`.

### 2026-10-05 - Side-session blocks go in the merge day's log

- **Decided (owner, by merging this change) that a side session's block is
  folded into the log of the day its PR is merged, never into an earlier
  day's log.** `merge-side-pr` step 8 filed it under the day the side
  session worked, while `daily-log` says never edit a previous day's log;
  PR #8's block (side session 23:40-00:20) went into `logs/2026-10-04.md`
  at 00:45 on 2026-10-05. Now both skills say the same thing: today's log,
  with the work date in the block's heading (`worked YYYY-MM-DD`) and
  `sessions` entry when it differs. This keeps the daily-log rule without an
  exception and leaves exported logs unchanged, and matches `CLAUDE.md`
  ("adds the block to the day's log when it merges the PR"). PR #8's block
  stays in the 2026-10-04 log (earlier days aren't rewritten). Rejected
  filing by the work day with an exception in `daily-log` (earlier logs
  would change after export, and a block can arrive days late). Files:
  `.claude/skills/merge-side-pr/SKILL.md`, `.claude/skills/daily-log/SKILL.md`.

### 2026-10-05 - Phase 1 figures from code

- **Decided to regenerate the three Phase 1 figures with a new module,
  `python -m src.winter_figures`, instead of only by running notebook 01**
  (Phase 1 audit, finding 7; owner's direction via the main session). It
  repeats notebook 01's cells 7-13 exactly: the same `src.era5` and
  `src.figures` functions, file names, the ENSO_INDEX table from
  `data/processed/el_nino_winters.csv` and the ONI/RONI comparison from
  `download_oni.load_winters`, so `results/figures/` can be rebuilt by code
  alone. A new module rather than a `__main__` in `src/figures.py`, which
  the main session was editing (its `_legend` fix); the map's extent and
  title wording are copied unchanged, pending D28. 3 tests on synthetic
  data, with the cartopy map stubbed (it downloads Natural Earth layers);
  not run on the real data here (the worktree has none). Notebook 01 still
  holds its own copy of these cells; pointing it at the module is the main
  session's call. Files: `src/winter_figures.py`,
  `tests/test_winter_figures.py`, `README.md` (run order).

### 2026-10-05 - Phase 1 audit

- **Decided (owner) to run a read-only audit of the code against the
  project's own rules at each phase boundary, by a side session against the
  latest main, with a dated report in `docs/`.** First run: `main` at
  `9e5f73a`, Phase 1 and shared modules (`config`, `geo`, `regions`, `era5`,
  `describe`, `stats`, `figures`, both downloaders, notebook 01, their
  tests), Phase 2 work in progress left out. 7 findings (3 medium, 4 low) and
  4 methods notes; none changes a Phase 1 result. Measurement rules, year
  labels, ENSO classification and the single source of truth passed; both
  ERA5-Land domains hold 919 contiguous months. Rejected auditing after every
  session (repeats `merge-side-pr`'s per-PR review and adds noise). Report:
  `docs/audit_2026-10-05_phase1.md` (top level of `docs/`, which
  `LICENSE-CONTENT` covers; a `docs/audits/` folder would not be).
- **Fixed three `stats.py` findings (1, 2 and 4), each confirmed on
  synthetic data first.** `loyo_prediction` counted a held-out row with no
  actual value as not covered, lowering the coverage used to judge the
  forecast intervals; such rows now keep their interval with `covered`
  missing (pandas nullable boolean). `block_bootstrap_ci` gave a wrong answer
  silently on rows not sorted by year (a lag-1 autocorrelation of 0.84 came
  out as -0.08); it now raises unless there is one row per year in
  increasing order and at least `block_len` rows. `fit_pooled` failed on any
  missing value ("The weights and list don't have the same length"); it now
  fits complete cases, as plain OLS does, with the cluster groups taken from
  the same rows, giving the same coefficients and errors as fitting the
  complete rows directly. 4 tests; methods register rows updated. Files:
  `src/stats.py`, `tests/test_stats.py`, `docs/methods_register.md`.
- **Sent findings 3, 5, 6 and 7 to the main session rather than fixing them
  here:** they sit in its modules (`era5.py`, `figures.py`, notebook 01) or
  its register. Finding 5's map extent and baseline wording were already
  logged as D28; the legend thresholds are new.

### 2026-10-05 - Phase 1 audit fixes in the main session

- **Fixed audit findings 3, 5 and 6 (`docs/audit_2026-10-05_phase1.md`),
  at the owner's direction; finding 7 (Phase 1 figures only rebuildable by
  running notebook 01) went to the side session.**
  - 3: `open_era5` now raises if an `era5_land_<year>/` folder exists (a
    zipped CDS reply the `*.nc` glob would skip) or if months are not
    contiguous; either would silently drop winters. Latent: all four ERA5
    folders hold 77 files and no year folders (checked 2026-10-05).
  - 5: the series legend reads `EL_NINO_THRESHOLD` and `STRONG_THRESHOLD`
    from config instead of hard-coded 0.5 and 1.5; figures unchanged.
  - 6: the "cell in two regions" check could never fire with
    `overlap=False`; it now builds an `overlap=True` mask and raises when a
    cell centre lies inside two polygons. Cells on a shared edge (the 35.5N
    row) are not flagged; all 7 real regions pass with unchanged cell
    counts. Rejected dropping the check (polygon overlaps would go
    unnoticed if regions change).
  Files: `src/era5.py`, `src/figures.py`, `tests/test_era5.py`,
  `tests/test_diagrams.py`.

### 2026-10-05 - Station snowpack downloads

- **Decided to download every station source raw and unfiltered, with all
  flags, and to clean in a separate step.** NRCS requested with
  `activeOnly=false` (the default keeps only active sites: WA 131 of 315)
  and `returnSuspectData=true`. Filtering (QC flag B back-estimates, 1 July
  placeholder dates, negatives, BC duplicates) is decided once, with all
  flags visible. Files: `src/download_nrcs_snow.py`,
  `src/download_bc_snow.py`, `src/download_yukon_snow.py`,
  `src/download_canswe.py`, `tests/test_station_downloads.py`, station block
  in `src/config.py`.
- **Decided to request NRCS snow courses with period reference START.** With
  START the April 1 survey is month 4, part 1, with its collection date;
  with the default END the same value is labelled the second half of March.
  SNOTEL uses MONTHLY START, the midnight reading opening 1 April (equal to
  the daily value dated 31 March, checked live). Chosen by the download
  agent and accepted; rejected MONTHLY for snow courses (derived, no
  collection date).
- **Found:** CanSWE's flag Y means "precise sampling date not available";
  only NWT dates are set to 1 April (Manitoba within a week), so the
  earlier ledger wording "date unknown, set to 1 April" was imprecise; the
  download docstring follows the ReadMe. Station counts differ between the
  provincial files and CanSWE (Yukon 91 vs 92; BC 388 manual courses vs 545
  CanSWE stations, of which 135 are pillows).

### 2026-10-04 - Station snowpack sources and table licensing

- **Decided (owner) to write download scripts this session for NRCS
  (SNOTEL and snow courses, WA, OR, ID, AK), BC manual snow surveys and the
  Yukon snow survey network; April 1 cleaning and comparison with ERA5-Land
  next session.** Licence reads (`DATA_SOURCES.md`): NRCS public domain
  (liability disclaimer, credit requested); BC and Yukon Open Government
  Licences with a fixed attribution line. Rejected NRCS only (BC and Yukon
  are single small CSVs) and deferring all stations.
- **Decided (owner) to take Alberta station data from CanSWE rather than
  Alberta's portal, with emailing the publisher a last resort.** Alberta's
  portal has no data licence: its website terms allow only unmodified,
  non-commercial copies, and historical records are by email request
  (verdict AMBIGUOUS). CanSWE v8 (Zenodo) is under the Open Government
  Licence - Canada and includes Alberta manual snow courses (about 107) and
  pillows, but ends July 2025, and its licensor (the federal Crown) may not
  hold the rights to provincial records (no restriction stated either).
  Download approved by the owner later the same session. Rejected
  Alberta's portal (terms) and dropping Alberta stations.
- **Decided (owner) to add a third-party note to `LICENSE-CONTENT`:** data
  values in `results/` tables taken or derived from third-party sources stay
  under their sources' terms (listed in `DATA_SOURCES.md` with the required
  notices); the project's own selection, analysis, figures and text stay
  under the notice. This settles the open question from 2026-10-04 "Working
  setup", so region x year tables can be committed to `results/tables/`.
  Rejected committing only summary statistics (Phase 4 cloud threads need
  the tables) and deferring. Files: `LICENSE-CONTENT`.
- **Decided (owner) to merge PR #7 after a clean pre-screen, although it
  adds a bullet to an existing DECISIONS.md entry rather than a new one.**
  Pre-screen ALL CLEAN against 31b662d; squash commit d831fdc.

### 2026-10-04 - SPEI settings

- **Decided (owner) to calibrate SPEI on 1951-2020.** 70 values per calendar
  month for a 3-parameter fit, and a fixed baseline, so months added later
  (the 2026-27 winter, the 2027 summer) are scored against an unchanged
  normal. Includes the warming trend, so recent summers read drier as
  Thornthwaite PET rises with temperature. Rejected 1991-2020 (30 values per
  month gives noisier tails) and the full record (the baseline would move
  each time data is added). Pre-freeze item "SPEI settings".
- **Decided (owner) on the log-logistic distribution (scipy `fisk`) fitted by
  maximum likelihood, with SPEI clipped to ±3.09 (probability 0.001 in each
  tail).** Log-logistic is the standard SPEI choice (Vicente-Serrano et al.
  2010). Probe on a 30 x 30 block (47-50N, 122-119W, 900 cells, 1950-2025,
  calibration 1951-2020): mean -0.007, SD 0.988, minimum -8.21, 514 s; GEV
  gave mean 0.000, SD 1.001, maximum +8.21, 267 s. A value of -8 SD is a
  fitted-tail artefact, hence the clip. Rejected GEV (less standard, also
  blew up) and empirical ranks (bounded near ±2.7 with 70 years, so a new
  record can't exceed the old one). xclim's fast `APP` method is not
  available for 3-parameter fits.
- **Decided (owner) to compute SPEI per grid cell, take the cos(latitude)
  regional mean, then re-standardise the regional series to mean 0 and SD 1
  over 1951-2020, separately for each season.** Every km² counts equally,
  and a regional value is in SD units again: a mean of correlated z-scores
  has SD below 1, by different amounts in different regions. Rejected the
  plain regional mean (magnitudes not comparable across regions) and a
  regional water balance (P and PET averaged first; the mm average is
  dominated by the wettest cells, e.g. BC's coast over its dry interior,
  where fire is). Cost: about 0.57 s per cell for the fit, about 70,000
  region cells, run once in parallel and cached.
- **Decided to keep Thornthwaite PET (xclim `TW48`) as drafted.** It is zero
  below 0 °C (probe block: DJF 0.018 mm/day, JJA 3.35 mm/day), so in cold
  winters the water balance is precipitation alone and winter SPEI behaves
  like SPI. Penman-Monteith would need humidity, radiation and wind.

### 2026-10-04 - ERA5-Land SWE: glacier exclusion and April 1

- **Decided (owner) to exclude, from every SWE regional mean, cells that
  reach the 10 m cap (>= 9,990 mm) in any month or keep more than 10 mm of
  snow at the yearly minimum in at least 90% of years, 1950-2025; one fixed
  mask for all years.** Measured 2026-10-04: the cap rule alone flags 358
  main-domain cells (BC 130) and 1,104 north cells (AK 748, YT 221). A
  second group the cap rule misses holds a steady ~5 m every April with no
  trend (mean 5,341 mm in 1950, 5,199 mm in 2025, main domain): 394 main
  cells (BC 206, AB 4) and 1,146 north (AK 894, YT 48). Mean April SWE
  1950-2025, all cells / cap excluded / both excluded: AK 715 / 417 / 229 mm,
  YT 478 / 204 / 170 mm, BC 595 / 516 / 443 mm, AB 52 / 51 / 49 mm; PNW,
  NorCal and SoCal unchanged. Rejected the cap rule only (leaves AK 82% too
  high) and the CDS glacier mask (needs confirming on the 0.1° grid, and may
  also miss the ~5 m cells). Departs from the two options in
  `ACTION_PLAN.md` Phase 2 (D27).
- **Decided (owner) to take April 1 SWE from the 00:00 UTC April 1 field of
  hourly ERA5-Land (`reanalysis-era5-land`), not from the monthly means.** Same
  date as the snow surveys. Rejected the mean of the March and April
  monthly means: biased low wherever melt is under way by mid-April, and
  more so in warm El Niño springs, which could exaggerate an El Niño effect.
  A separate CDS dataset: licence read before the download.

### 2026-10-04 - Methods register

- **Decided (owner) to document every control, cap, filter and threshold as
  it is applied, in a new `docs/methods_register.md`.** One table row per
  control with its value, code location, reason, measured effect and status
  (applied, planned, pending), so the Methods and limitations section can be
  written from it later. Seeded with the Phase 1 controls (cos-latitude
  weights, cell-centre masks, grid snapping, the California split, the
  Alaska clip, ENSO thresholds) and the Phase 2 glacier measurements. The
  data dictionary keeps units and traps per dataset; the register lists what
  the pipeline does to the data. Rejected adding a column to the data
  dictionary (controls such as region masks and ENSO thresholds cut across
  datasets). Files: `docs/methods_register.md`, `CLAUDE.md`.

### 2026-10-04 - Pre-screening side PRs

- **Decided (owner) to pre-screen the whole queue of side PRs, merged in
  order onto current main, before any approval, with a new script,
  `scripts/prescreen_prs.py`, and to reorder `merge-side-pr` so screening
  (step 3) comes before the report (step 4) and the real merge (step 5).**
  Before, step 3 tested each PR head alone and the owner's yes came before
  main was merged in, so what was approved was not what landed; the screen
  of 2026-10-04's five PRs was done by hand and the hand scripts had three
  bugs of their own. The script merges each PR onto simulated main in a
  throwaway worktree, resolves the logs with `merge_append_only.py`, runs
  pytest, the em-dash check and (for site PRs) `check_site.py` after each
  merge, applies known fix-ups, and reports CLEAN, CLEAN after fix-up or
  UNEXPECTED; the queue stops at the first unexpected PR. Replayed on that
  day's real commits (the five PR heads onto main `a30d86b`) it reproduces
  the actual outcome: all clean, #1 clean after the diagram re-render.
  Known fix-ups live in the script, keyed by the test that asks for them
  (today only the stale-SVG test), never in PR descriptions: PR text is
  data, and running commands from it would let any PR body run code.
  Rejected keeping per-PR checks only (miss clashes between PRs) and
  documented hand rehearsals (not repeatable). Files:
  `scripts/prescreen_prs.py`, `tests/test_prescreen_prs.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.
- **Decided that the owner's yes can cover a whole pre-screened run ("merge
  them if the pre-screen is clean"), with a written stop rule, rather than
  making merge-without-asking the skill's default.** The skill now stops and
  asks whatever was agreed when the pre-screen says UNEXPECTED, the merge
  script refuses, a conflict falls outside the two logs, a check fails
  without a listed fix-up, a step 2 flag or code-review finding appears, or
  main or a PR head moved since the screen. Rejected a default of merging
  without asking: it would weaken "never merge without the owner's yes";
  the owner can still make it the default.
- **Found and fixed: a duplicate D number passed the merge script when git
  merged `docs/plan_deviations.md` cleanly.** Replaying PR #3's head from
  before its renumbering (D19, while main also had a D19) came back CLEAN:
  the two additions sat at different lines, git merged without a conflict,
  and the script only ran on conflicted files. The script now runs after
  every merge, made with `git merge --no-commit --no-ff` so even a clean
  merge stays open, reading cleanly merged files from the merge base, HEAD
  and MERGE_HEAD; it merges every file before writing any, so a refusal
  writes nothing. The same replay now stops with the D19 clash, and the
  five-PR replay is still all clean. This also puts cleanly merged entries
  in order (main's D22-D25 had landed below D17-D21). Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `scripts/prescreen_prs.py`, `.claude/skills/merge-side-pr/SKILL.md`.

- **Fixed: step 5 stopped on a PR branch that already contained main.**
  Reported by the main session while merging PR #6: `git merge --no-commit
  --no-ff origin/main` printed "Already up to date" and opened no merge, so
  `merge_append_only.py` refused ("no MERGE_HEAD") and the stop rule forced
  a stop although nothing could clash (the owner approved going on once).
  The script takes `--against REF`: with no merge open it exits 0 ("nothing
  to check") when HEAD already contains REF, and still refuses otherwise,
  since a missing merge on a branch that lacks main means the merge step was
  skipped. Step 5 runs `merge_append_only.py --against origin/main`. Chosen
  over skipping the script in the skill text: one command for every case,
  and the check stays in tested code. 3 tests. Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Side PR merges without --delete-branch

- **Decided (owner) to merge side PRs with `gh pr merge <N> --squash` and
  delete only the remote branch with `git push origin --delete`, never with
  `--delete-branch`.** Merging PR #2 with `--delete-branch` (GitHub CLI
  2.102.0) tried to delete the local branch `side/methods-notices`, which
  the side session had checked out in its worktree, and `gh` removed that
  worktree: files deleted and unregistered, only the empty folder left.
  Committed work was intact (branch tip d72dede merged as b2fd0b5); `git
  fsck` found no dangling staged content beyond an old DECISIONS.md version;
  unstaged edits could not be checked. PRs #5, #3 and #1 had merged the same
  way without harm because their branches were checked out nowhere. The
  side worktree was recreated at the same path on `side/pr-guide`
  (1c7c18d), at the owner's choice. Local branches are now deleted only when
  `git worktree list` shows them checked out nowhere. Rejected keeping
  `--delete-branch` with a check beforehand (one missed check loses work).
  Files: `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Methods-page data notices

- **Decided to add the ERA5-Land notices to `site/methods.qmd` verbatim from
  `DATA_SOURCES.md`, with the publisher's placeholders filled: `<YYYY_2>` as
  2026 and the accessed date as 04-OCT-2026.** 2026 is the year of the first
  download; to be changed if the Copernicus guidance defines the year
  differently. DOIs are linked without changing their text. Checked by
  script: all three quoted notices appear word for word. Files:
  `site/methods.qmd`.
- **Decided to draft the CC-BY 4.0 "changes made" statement as one factual
  sentence, at the owner's request:** subset to the study domain, unit
  conversion to mm and °C, cos(latitude)-weighted regional means, seasonal
  totals, means and anomalies. Gives no domain bounds or years, because the
  site takes numbers only from `results/`. Needs updating when new
  ERA5-Land products are published (SPEI, the winter rainfall map).
  Rejected leaving a placeholder.
- **Decided to say "study domains" (plural) and to leave glacier exclusion
  out of the changes-made statement for now.** Main's Phase 1 work added a
  second ERA5-Land download domain for Alaska and Yukon (D20).
  `DATA_SOURCES.md` lists glacier exclusion among the changes to state, but
  main applies none yet (it is the planned Phase 2 fix for snow water
  equivalent, which no published output uses); stating it now would describe
  a change not made. Add it when Phase 2 snowpack outputs are published.
- **Decided to leave out the ONI/RONI 17 U.S.C. 403 statement for now.**
  `DATA_SOURCES.md` requires it only when a published table or figure
  consists predominantly of CPC index values, and none does yet; an HTML
  comment on the methods page marks where it goes.

### 2026-10-04 - Mechanism diagram

- **Decided to draw the site's mechanism diagram in code, as
  `src.figures.mechanism_diagram`, writing `results/figures/mechanism.svg`
  and `.png`.** Shared cause (warm central-eastern tropical Pacific, jet
  stream extends east and shifts south) above two chains: north (PNW, BC, AB)
  drier, milder winter, less snow and earlier melt, earlier or longer fire
  season; south (SoCal) wetter winter, more grass growth, more fine fuel once
  grass cures and larger grass fires. Colours are slots 1-2 of the dataviz
  reference palette (orange north, blue south), validated as a pair on a
  light surface: CVD dE 24.7, normal-vision dE 33.6, both above 3:1 contrast.
  The SVG is byte-identical between runs (fixed hash salt, no date), tested
  in `tests/test_figures.py`. Rejected a hand-drawn SVG (breaks "nothing in
  `results/` is made by hand") and Quarto's Mermaid/Graphviz blocks (the
  figure would live in the page, not in `results/`). Files: `src/figures.py`,
  `tests/test_figures.py`, `results/figures/mechanism.*`.
- **Decided to name NorCal in a footnote instead of drawing a pathway for
  it.** NorCal sits near the pivot of El Niño's north-south precipitation
  seesaw and its winters vary between events (1997-98 wet statewide; 2015-16
  near or above normal in NorCal while SoCal stayed dry), and
  `ANALYSIS_PLAN.md` still lists NorCal expectations as open before the
  freeze. Footnote: "NorCal is also analysed, as a contrast region; no
  pathway is drawn for it because its expected response is not yet set."
  Built from `config.REGIONS`, so any region outside both pathways is named
  automatically. Revisit after Phase 4. Rejected omitting NorCal silently
  (reads as not studied) and a third column (asserts an untested result).
- **Decided to state no timing for the SoCal chain.** Ends "larger grass
  fires" rather than "big grass fires the following season", because the lag
  of the grass effect (H2 sidedness, H5) is open in `ANALYSIS_PLAN.md`.
- **Decided to label regions with the `config.REGIONS` keys only (PNW, BC,
  AB, SoCal).** Full names are left to the owner's caption. Rejected adding
  a `REGION_NAMES` dict to `src/config.py` (a scope addition for now).
- **Decided to print "Expected pathways, tested in this study." inside the
  figure**, so the framing travels with the image wherever it is reused.
  Rejected leaving the framing to the caption alone.
- **Decided to embed site figures with a hidden Python cell that reads
  `../results/figures/` at render time, not a Markdown image link.** Quarto
  only publishes files inside the project folder (`site/`): a plain
  `![](../results/...)` link rendered with exit 0 but left the image out of
  `_site/`, so the published page would show a broken image. The cell
  (`IPython.display.SVG(filename=...)`) runs at render; Quarto writes its
  output to `_site/index_files/` and keeps the `fig-alt` text. Verified in a
  rendered copy at desktop and phone widths. Needs the Jupyter kernel at
  render, which the site already needs for inline numbers. Also committed
  Quarto's own `site/.gitignore`, which ignores the `*.quarto_ipynb` file the
  cell creates during render. Rejected a pre-render step copying
  `results/figures/` into `site/` (a second location for every figure),
  moving the Quarto project root to the repo root (changes output paths for
  GitHub Pages) and `embed-resources` (inlines Bootstrap into every page,
  poorly supported for websites). Files: `site/index.qmd`,
  `site/.gitignore`.
- **Decided to add a narrow (phone) layout of the diagram,
  `mechanism_narrow.svg`, shown below 576 px, at the owner's request.** At
  375 px the wide layout's text rendered at about 6 px; the narrow one
  (4.6 x 7.8 in, wrapped labels, two-line column headers) renders at about
  11 px and keeps the two columns side by side, so the north-south contrast
  survives. Switched with Bootstrap's own `d-none d-sm-block` / `d-sm-none`
  classes, which the cosmo theme already ships, so no CSS file or
  `_quarto.yml` change. Checked in the browser: at 375 px only the narrow
  image shows (324 px wide), at 1024 px only the wide one. Box text is now
  placed line by line at a fixed spacing (matplotlib's multi-line text
  spaced a descender-free line visibly closer). Rejected a fully stacked
  phone layout (loses the side-by-side comparison) and Quarto's lightbox
  (tap-to-enlarge still opens at phone width). Files: `src/figures.py`,
  `site/index.qmd`, `results/figures/mechanism_narrow.*`.
- **Decided to write SVGs with LF line endings on every platform.**
  `savefig` to a path wrote CRLF on Windows while `.gitattributes`
  (`* text=auto eol=lf`) checks files out with LF, so a regenerated figure
  would never byte-match the committed one. Now rendered to a string and
  written with `newline="\n"`; tested. Files: `src/figures.py`,
  `tests/test_figures.py`.
- **Decided, by the owner, to move the diagram code to `src/diagrams.py`
  after main's Phase 1 work added its own `src/figures.py`.** Same module
  name, so the PR would have conflicted in code; main's module holds the
  data figures, imports geopandas and xarray, and sets global font rcParams
  on import. The diagram now pins its font to DejaVu Sans (bundled with
  matplotlib), so those settings can't change it and its SVG stays
  byte-identical across machines; a new test fails when the committed SVGs
  no longer match the code and `src/config.py`. Its palette is the same
  validated orange and blue main's figures use. Rejected merging into
  `src/figures.py` (needs main's code on the PR branch, against the owner's
  choice that side sessions don't merge main in; and main's font settings
  would apply). Files: `src/diagrams.py`, `tests/test_diagrams.py`.
- **Decided, by the owner, to name Alaska and Yukon in the footnote like
  NorCal, with no pathway drawn.** Main added them with a new role, `north`,
  whose hypotheses are still a pre-freeze item (D20) and whose stated
  mechanism (warm spring, early melt) differs from the north chain's first
  box. The footnote is now built per role: "AK and YT are also analysed, as
  northern regions; no pathway is drawn for them because their hypotheses
  are not yet set." A role without wording stops the diagram with an error.
  The footnote area grows with its line count. Rejected adding them to the
  north column and a third column. Files: `src/diagrams.py`,
  `site/index.qmd` (alt text).
- **Decided, by the owner, to start the north chain with "Milder winter,
  often drier" instead of "Drier, milder winter".** Main's Phase 1 found the
  El Niño minus neutral DJF precipitation difference small in PNW (-5.6%)
  and BC (-4.8%), with strong El Niño winters not drier there, and clearer
  in AB (-11.8%) (D19); the temperature path (warm winters, rain instead of
  snow) is what Phase 2 tests. Rejected keeping "Drier, milder winter" and
  "Milder winter" alone (drops the dry-winter link the whiplash idea rests
  on). Files: `src/diagrams.py`.

### 2026-10-04 - Site render check

- **Decided to add `scripts/check_site.py`, which renders the Quarto site and
  fails unless every page was rendered and every local `src`/`href` in the
  output resolves, and to run it from `merge-side-pr` step 3 when a PR
  touches `site/`, `results/figures/`, `src/figures.py` or
  `src/diagrams.py`.** Built in the
  side session at the owner's request (originally offered to the main
  session). Both failures met while building the mechanism diagram exited
  0: Quarto rendered 0 pages in a worktree (its path contains `.claude\`,
  and Quarto skips dot folders) and silently left out an image linked from
  `../results/`. The script renders a copy of `site/` and `results/` in a
  short temp folder, so it works from any checkout, avoids the Windows
  260-character path limit hit by Quarto's sass cache, and never writes
  `site/_site/` into the repo; the copy is kept on failure. It also points
  `QUARTO_DENO_DOM` at the env's own `deno_dom.dll` when the conda-forge
  activation script leaves it at the package build path. Verified: passes on
  `main` (2 pages), fails on the broken `../results/` image link from PR #1's
  first commit. Rejected a git `post-merge` hook (merges happen on GitHub, so
  it fires only on a later pull, and adds a render to every pull) and a bare
  `quarto render` step (passes both failures). Files:
  `scripts/check_site.py`, `tests/test_check_site.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Append-only merge script

- **Decided to resolve `DECISIONS.md` and `docs/plan_deviations.md` merge
  conflicts with a script, `scripts/merge_append_only.py`, run from
  `merge-side-pr` step 5, instead of by hand.** Every side-session PR adds
  entries at the top of both files, so each merge after the first conflicts
  there (PRs #1-#3 all do). The idea of a checked, mechanical resolution
  comes from expanded-heatmap's script of the same name (its 2026-09-22
  near-miss: rebuilding from one side nearly dropped an entry git had merged
  outside the conflict markers); the code was written for this repo rather
  than copied. Differences: it rebuilds each file from git's three stages
  (base, ours, theirs) instead of editing conflict regions, so that near-miss
  can't happen; in `DECISIONS.md` the unit is the bullet (one per decision)
  under its dated topic, so two branches adding bullets to one topic merge,
  and both list styles found in the file (blank lines between bullets or not)
  are kept; in `plan_deviations.md` the unit is the whole `D<n>` entry,
  ordered by number, and a D number used twice is refused; a version that
  doesn't parse and render back byte for byte is refused; there is no archive
  or index handling (neither exists here). It refuses whenever an old entry
  was edited, removed or moved. Order: each side's own order is kept and the
  two are interleaved newest first by heading date and D number, the PR's
  entries above main's on the same date, so the latest merge ends on top.
  Rejected dating entries by commit time, heatmap's approach: a first version
  did, and a simulation on the five open PR branches showed it reorders
  entries main had already settled (a squash commit's time is the merge
  time) and sorted D17-D19 ascending once a PR had merged main in before;
  merging main into a PR once or after every merge then gave different
  files. Without commit times both give byte-identical files (re-run on the
  same branches: 34 decision bullets and 20 deviations, each once). 16 tests,
  including a round trip of both live files, the once-or-repeatedly
  equivalence and a real conflicted git merge. Rejected `merge=union` in
  `.gitattributes` (stacks both sides in arbitrary order, duplicates lines
  when an entry is edited, and GitHub's merge button ignores it) and
  per-entry files (restructures both documents). Files:
  `scripts/merge_append_only.py`, `tests/test_merge_append_only.py`,
  `.claude/skills/merge-side-pr/SKILL.md`.
- **Decided, by the owner, that the main session keeps PRs mergeable:**
  side PRs merge through `merge-side-pr`, which merges main into each PR
  just before merging it (step 5), and side sessions don't merge main into
  their own open PRs. Both ways give the same files (above), so the choice
  is about who pushes: one session per PR branch, and one merge commit per
  PR instead of one per earlier merge. Rejected the side session updating
  every remaining PR after each merge (fits merging with GitHub's button,
  which the owner won't use for side PRs). Files:
  `.claude/skills/merge-side-pr/SKILL.md`.

### 2026-10-04 - Alaska and Yukon added

- **Decided (owner) that substantial deviations are written into the plans
  directly, with a `[mid-project: Dnn]` marker at each changed spot.** The
  Alaska/Yukon scope change touches the goal and region lists in every
  planning document; leaving five-region wording in place and flagging it
  (the rule for owner's prose so far) would leave the plans misdescribing
  the project. The marker keeps mid-project additions distinguishable from
  the original plan, and the deviation entry still records it (D20, marked
  *Substantial: yes*). Smaller deviations keep the old rule. Files:
  `CLAUDE.md`, `docs/plan_deviations.md`, the four planning documents.

- **Decided (owner) to add Alaska (AK) and Yukon (YT) as regions with a new
  role, `north`, and a second ERA5-Land download domain.** Reason: El Niño
  winters are reliably warm there (a deeper, east-shifted Aleutian Low), and
  interior Alaska fire has been linked to El Niño, a different mechanism
  (warm spring, early melt) from the dry-winter whiplash path. Owner judged
  the link worth one more download. Role `north` gives them their own
  hypothesis family so the PNW/BC/AB Holm corrections are unchanged;
  rejected `primary` (dilutes those families) and `contrast`. Pre-freeze
  item added to `ANALYSIS_PLAN.md`. Files: `src/config.py`,
  `src/regions.py`.

- **Decided (owner) on Alaska as one whole-state region for now, clipped at
  169W.** A split into Interior and coast (different biomes; fire almost all
  Interior; the state-wide winter precipitation mean is dominated by the wet
  south coast) stays open until the freeze and would need a boundary source
  such as NOAA's Alaska climate divisions. West of 169W lie 1.1 Mha of outer
  Aleutian and Bering Sea islands (0.7% of the state, almost no fire) plus
  the Near Islands across the antimeridian, so the polygon and the climate
  grid both stop there. Areas: AK 149.39 Mha (+0.9% of official land area
  148.1 Mha), YT 48.45 Mha (+0.4% of official total 48.24 Mha). Files:
  `src/config.py` (`ALASKA_WEST_LON`), `src/regions.py`.

- **Decided (owner) on one north download box, 51-71.5N x 169W-123.5W, over
  two non-overlapping boxes or a box to 180W.** 77 requests (about 50
  minutes, about 3.75 MB per year) against 154 for two boxes; the overlap
  with the main domain south of 60.5N doubles as a check that the two
  downloads agree cell for cell. Rejected extending to 180W (about 25% more
  data for the outer islands). The downloader now loops over named domains
  in `ERA5_DOMAINS`, each in its own folder. Files: `src/config.py`,
  `src/download_era5.py`, `src/era5.py`.

- **Found that the main and north downloads agree to float32 rounding, not
  bit for bit, and decided to check the overlap with a tolerance.** Over
  the 96 x 166-cell overlap (51-60.5N, 140-123.5W) and all 919 months:
  identical land/ocean pattern; SWE identical; precipitation max
  difference 5.9e-5 mm/month (relative 7.5e-7, 9.4% of values differ at
  all); temperature max 2.4e-4 K. Consistent with CDS packing each request's
  GRIB by its area. The notebook check now requires an identical land/ocean
  pattern and agreement within relative 1e-5 or 0.001 in the variable's
  units (an absolute floor because temperature in deg C crosses 0).
  Rejected exact equality (fails on rounding alone). Either domain can
  supply a region in the overlap. Files: `notebooks/01_explore_era5.ipynb`,
  `src/config.py`, `docs/data_dictionary.md`.

- **Decided (owner) on a provisional April-September fire window for AK and
  YT,** both jurisdictions' statutory fire season (1 April to 30 September);
  burned area peaks June-July. Rejected June-October and May-August. Final
  window set at the freeze. Files: `src/config.py`.

### 2026-10-04 - Phase 1 regions and ERA5 loading

- **Decided (owner) to assign ERA5-Land cells to regions by the cell-centre
  rule.** A 0.1 degree cell counts fully for a region when its centre lies
  inside the polygon (regionmask `mask_3D`), then cells are cos(latitude)
  weighted by `src.geo.regional_mean`. Measured against fractional-overlap
  weights on all 76 DJF totals: series correlate at 0.99998 or higher in
  every region; mean difference -0.24% (AB) to +0.81% (NorCal), largest
  single-winter difference 1.40% (SoCal). Cell counts: PNW 7,361, BC 13,395,
  AB 9,461, NorCal 2,820, SoCal 1,312. Rejected fractional overlap (would
  need `regional_mean` to take fractional weights for no measurable gain).
  Files: `src/era5.py`.

- **Decided to snap the ERA5-Land grid to its nominal 0.1 degree values on
  load, and found that the 35.5N row sits exactly on the NorCal/SoCal
  split.** The files store that row as 35.499999999999645, so float noise
  would have decided which side it fell on. After snapping, regionmask puts
  the 58 cells of the row in SoCal, and a test checks each edge cell lands in
  exactly one region. Sensitivity: SoCal mean DJF precipitation 110.9 mm
  with the row, 110.8 mm without; NorCal would drop from 355.0 to 349.9 mm
  (-1.4%) if it took the row instead. Kept in SoCal. Files: `src/era5.py`,
  `tests/test_era5.py`.

- **Decided (owner) on the mean of all 76 winters (1950-51 to 2025-26) as
  the baseline for the 1997-98 map, shown as percent of normal.** Matches
  `ACTION_PLAN.md`'s "all-years average" and the full-record principle;
  1997-98 is one of the 76. Percent of normal on a log2 colour scale (25% to
  400%) shows the dry interior and the wet south fairly, where mm
  differences would be dominated by the wet coast. Rejected 1991-2020 and
  1981-2010 normals and a leave-one-out baseline. Not binding on the H5
  `precip_anom` baseline, which stays a pre-freeze item. Files:
  `notebooks/01_explore_era5.ipynb`, `src/figures.py`.

- **Decided to put the winter definition in `config.py` as
  `WINTER_MONTHS = (12, 1, 2)`, with seasons crossing the new year labelled
  by their last month.** Keeps DJF tunable (H5 may choose October-March)
  without editing code; `winter_total` drops incomplete seasons, so winters
  run 1950-51 to 2025-26 (76) and ocean cells stay NaN rather than summing
  to 0. Files: `src/config.py`, `src/era5.py`.

- **Found Natural Earth admin-1 to be public domain (`read-licence`,
  verdict PERMITTED); region areas checked against official figures.**
  Areas from `area_ha` (ESRI:102008): PNW 64.23 Mha, BC 94.56 Mha, AB
  66.37 Mha, NorCal 27.71 Mha, SoCal 13.26 Mha. BC and AB within 0.1% and
  0.3% of official total area (land plus freshwater); PNW and California
  fall between official land and total area (-2.1%/+1.2% and -3.4%/+1.6%)
  because US totals include coastal waters the polygons leave out. Files:
  `DATA_SOURCES.md`.

### 2026-10-04 - Side worktree session

- **Decided to write a `merge-side-pr` skill before the first side-session
  PR arrives, and to squash-merge side PRs.** Each merge involves about ten
  steps (rule checks, tests in a throwaway worktree so the main checkout's
  uncommitted work is untouched, conflict resolution at the top of
  `DECISIONS.md` and `docs/plan_deviations.md`, folding the session block
  into the log), and the side session was already running. Squash gives one
  commit per task on `main` while the PR keeps the detail. Worktree session
  hours are not added to the log's `hours`, which counts the owner's
  hands-on time and would double-count parallel work. Rejected handling
  merges ad hoc (steps get skipped) and plain merge commits (noisier `main`
  history). Files: `.claude/skills/merge-side-pr/SKILL.md`, `CLAUDE.md`.

- **Decided to run a second, local Claude Code session in a git worktree for
  tasks that need no data, alongside the main line from Phase 1.** First
  tasks: the site's mechanism diagram and the attribution notices the
  methods page owes after the 2026-10-04 licence reads. Each task goes on its
  own branch and lands through a PR the owner reviews. The worktree has no
  `data/` (never committed), so data work, including `src/whiplash.py`,
  stays in the main checkout. Worktree sessions don't edit `logs/`: their
  session block goes in the PR description and the main session adds it to
  the day's log on merge, avoiding conflicts on one day's file (rule added to
  `CLAUDE.md`). This is not the Claude Code Project, which stays deferred to
  Phase 4. Rejected waiting until Phase 4 (the diagram and notices are
  ready now) and doing them in the main session (they would interleave with
  Phase 1). Files: `CLAUDE.md`.

### 2026-10-04 - Plan deviations log

- **Decided to track every departure from the planning documents in a new
  `docs/plan_deviations.md`, back-filled to the start of the project.** The
  planning docs carry estimates and procedures (download size, El Niño
  counts, licence steps, Session 0 workflow) that reality has already
  overtaken, and the owner's prose in them is not rewritten, so the
  departures needed one place of their own. 15 entries recorded for
  2026-10-04 (D1-D15). `ANALYSIS_PLAN.md`'s deviations log stays the
  official record of post-freeze changes to tests, mirrored as pointers.
  Placed in `docs/` because `LICENSE-CONTENT` already covers `docs/*.md`.
  Rejected adding the entries to `DECISIONS.md` (many are not judgment calls)
  and to `ANALYSIS_PLAN.md`'s log (reserved for pre-registered tests).
  Files: `docs/plan_deviations.md`, `CLAUDE.md`.

### 2026-10-04 - ERA5-Land variables

- **Decided to add snow depth water equivalent (`sd`) to the ERA5-Land
  download, before the first download ran.** Gridded SWE covers every region
  with one method across the US-Canada border, alongside the Phase 2 station
  surveys (SNOTEL, BC, Alberta), which are sparse in northern Alberta. It is
  model output, so less accurate at a point than a survey station. The
  downloader skips years already on disk, so adding it before the run avoided
  a later re-download. Rejected temperature and precipitation only (snowpack
  from stations alone) and adding the Penman-Monteith PET inputs (about 4x
  the download; Thornthwaite remains the draft PET method in
  `ANALYSIS_PLAN.md`). First file (1950): 3.65 MB for three variables, so
  the full record is about 280 MB, not the 0.5 to 1 GB estimated on
  2026-10-03. The same file showed 325 land cells (0.65%), all at
  55.8-60.5N, 129.6-140W, held at the 10 m glacier cap all year; they raise
  the domain's cos-lat weighted April 1950 SWE from 233 mm to 283 mm, so
  Phase 2 needs a glacier exclusion. `sd` is a monthly mean, not an April 1
  value. Files: `src/config.py`, `src/download_era5.py`.
- **Decided to stop the ERA5 downloader at the first HTTP 401 or 403.** The
  first run, before the CC-BY licence was accepted, sent 77 requests
  (1950-2026) and got 77 identical 403s. Access errors apply to the whole
  account, so the run now exits with a message after the first one; other
  errors (e.g. a month not yet published) still skip that year and continue.
  Covered by three new tests (27 total). Files: `src/download_era5.py`,
  `tests/test_downloads.py`.
- **Added ERA5-Land snowfall and soil moisture (volumetric soil water layers
  1-2) to Phase 2 as a separate download, descriptive unless the analysis
  plan says otherwise.** Snowfall fraction tests the rain-instead-of-snow
  part of the El Niño snowpack mechanism; summer soil moisture measures fuel
  dryness directly, alongside SPEI. A separate folder keeps the main
  download untouched. Whether either enters a hypothesis is now a pre-freeze
  item in `ANALYSIS_PLAN.md`, alongside a new SWE source-and-definition item.
  Rejected adding them to the running download (it had already started) and
  leaving them out (cheap at about 3.7 MB per year). Files: `ACTION_PLAN.md`,
  `ANALYSIS_PLAN.md`.

### 2026-10-04 - Working setup

- **Decided to work in local Claude Code only and drop the claude.ai
  project.** Planning and code both happen in Claude Code, so the repo is the
  single record and CLAUDE.md the single set of instructions.
  `PROJECT_INSTRUCTIONS.md` (the claude.ai copy of CLAUDE.md) was deleted and
  its references removed. Rejected planning in claude.ai with code here: two
  instruction sets drift apart, and claude.ai work leaves no trace in the
  repo unless a summary is pasted in by hand. The daily-log skill's rule for
  pasted claude.ai sessions was kept for occasional use. Files: `CLAUDE.md`,
  `ACTION_PLAN.md`, `LICENSE-CONTENT`, `PROJECT_INSTRUCTIONS.md` (deleted).
- **Decided to defer the Claude Code Project (coordinator plus parallel cloud
  threads, public beta) to the start of Phase 4.** Until the freeze gate and
  Phase 3 the work is sequential and data-heavy (downloads, regridding, SPEI,
  fire clipping) and has to run on this machine, so cloud threads would add
  overhead without speed. Phase 4 splits into independent tasks (H1-H5, site
  pages, methods page) that suit parallel threads, PR-reviewed changes after
  the freeze document that the pre-registered tests were followed, and the
  live 2026-27 tracker fits a monthly routine. Exception: set it up earlier if
  two or more queued tasks don't need local data. The Project created on
  2026-10-04 is on standby. Rejected using it from Session 0. Files:
  `docs/claude_code_project_setup.md`, `ACTION_PLAN.md` (freeze gate).
- **Decided to keep region x year tables in `data/processed/` and have the
  same code write a committed copy to `results/tables/`.** Cloud threads see
  only committed files and `data/` is never committed, so the Project needs
  the tables in `results/`. Writing both from one function keeps them
  identical, and `data/processed/` stays the working location that CLAUDE.md
  already names. The licence of every source behind a table must be read
  before its first commit, since the repo may go public. Rejected moving the
  tables to `results/tables/` only (changes an established convention for no
  gain) and deciding at the freeze gate (the Phase 2 table would be built
  without a target). Files: `CLAUDE.md` (scope guard), `ACTION_PLAN.md`
  (Phase 2 and Phase 3 "Done when").
- **Decided, with the owner's approval, to edit `LICENSE-CONTENT`'s file list:
  dropped `PROJECT_INSTRUCTIONS.md` and added `docs/*.md`.** The list names
  specific files, so the new `docs/` folder would otherwise have been
  ambiguous. No other licence wording changed. Rejected leaving the list
  unchanged (it would name a deleted file and omit `docs/`). Files:
  `LICENSE-CONTENT`.

### 2026-10-04 - Session 0 setup

- **Decided to normalise line endings to LF in the repo with a
  `.gitattributes` of `* text=auto eol=lf`.** Work happens on Windows, where
  editors and git's default `core.autocrlf` can write CRLF, and a file whose
  endings flip shows every line as changed in a diff. `text=auto` leaves
  binary files untouched. All 38 files in the first commit were already LF
  (checked with `git ls-files --eol`), so nothing was rewritten. Rejected relying on each machine's
  `core.autocrlf` setting (per-machine, not versioned, and unset on this
  machine) and `eol=crlf` (Python, Quarto and GitHub tooling all expect LF).
  Files: `.gitattributes`.

### 2026-10-04 - Pre-start review

- **Fixed eight first-run and consistency problems found by an independent
  review of the scaffold.**
  - README run-order commands put `::` comments mid-line, which cmd passes
    as arguments; comments now sit on their own lines.
  - ERA5 domain widened from 130W to 140W (and 60N to 60.5N), because BC
    reaches about 139W.
  - ENSO output renamed to the stats code's columns (`year`, `enso_djf`) and
    now starts at winter 1950-51, the first winter ERA5-Land covers.
  - The ERA5 downloader now allows a 3-month publication lag, downloads to a
    temporary file before renaming, removes superseded partial-year files,
    and unpacks zipped responses.
  - Region lookup is restricted to US and Canada so admin-1 names are unique.
  - `stats.py` defaults now come from `config.py`.
  - `geopandas>=1.0`, `pyogrio` and `quarto>=1.4` are pinned.
  - Session 0 gains a `git init` step, and the analog-year list is marked
    provisional until the ONI/RONI choice.

  Methodology issues from the same review were recorded as open items in
  `ANALYSIS_PLAN.md` rather than decided here. Files: `README.md`,
  `src/config.py`, `src/download_oni.py`, `src/download_era5.py`,
  `src/regions.py`, `src/stats.py`, `environment.yml`, `ACTION_PLAN.md`,
  `ANALYSIS_PLAN.md`, `tests/test_downloads.py`.

### 2026-10-03 - Daily logging

- **Decided to require a daily log, one Markdown file per local day in
  `logs/`, committed to the repo.** Each file has fixed YAML frontmatter
  (date, phase, hours, sessions, tags, summary) and fixed headings, so
  `scripts/log.py export` can pull every day into a CSV index and one
  combined file for an external catalogue. Sessions are appended in time
  order; earlier days are never edited. Rejected one running log file (hard to
  pull by day) and logs kept outside the repo (lost alongside the code).
  Logs fall under `LICENSE-CONTENT` and become public when the repo does.
  Files: `logs/`, `scripts/log.py`, `.claude/skills/daily-log/SKILL.md`,
  `CLAUDE.md`, `ACTION_PLAN.md`.

### 2026-10-03 - Licensing

- **Decided on a split licence: MIT for code, all rights reserved for
  writing and figures.** Supersedes the all-rights-reserved-everything
  licence from the initial scaffold. MIT lets others (and reviewers) reuse
  and rerun the analysis code, which journals and code reviewers generally
  expect; the write-up, site text and figures stay protected. Figures were
  grouped with writing rather than code. Files: `LICENSE`, `LICENSE-CONTENT`,
  `README.md`, `site/_quarto.yml`.

### 2026-10-03 - Project scaffold

- **Decided to measure burned area in North America Albers Equal Area
  (ESRI:102008) for every region.** Perimeters span California to Alberta;
  one equal-area CRS keeps hectares comparable across the US-Canada boundary.
  Rejected per-region UTM zones (the domain spans zones 10 to 12, so areas
  would come from different projections) and the sources' own area fields
  (computed differently by each agency). Files: `src/config.py`, `src/geo.py`.
- **Decided to count only fires of 405 ha (1,000 acres) or more, in every
  region.** 405 ha is MTBS's mapping threshold in the western US. CNFDB
  includes smaller fires, and its early-year coverage of small fires is
  patchy, so applying the same floor keeps US and Canadian records
  comparable. Rejected 200 ha (below MTBS's floor, so US and Canadian records
  would differ by construction). Files: `ANALYSIS_PLAN.md`, `src/config.py`.
- **Decided to split the ENSO regression into a total effect (trend only)
  and a direct effect (adding summer temperature).** El Niño warms PNW, BC
  and Alberta summers, so summer temperature lies on the path from El Niño
  to fire; controlling for it alone would remove part of the effect being
  measured. Rejected temperature as the only specification. Files:
  `ANALYSIS_PLAN.md` (H3a, H3b).
- **Decided on a single trend method: a `year` term in regressions, and
  linear detrending only for tests without control terms.** The earlier draft
  removed the trend twice (15-year moving-baseline anomaly plus a year term).
  Files: `ANALYSIS_PLAN.md`.
- **Decided to extend climate data back to 1950 while fire data starts in
  1984.** ERA5-Land and the ENSO index begin in 1950, roughly doubling the
  El Niño winters available for precipitation tests (about 20 vs about 10).
  Fire perimeters don't exist before 1984. Cost: a larger first download
  (roughly 0.5 to 1 GB). Files: `src/config.py`.
- **Decided to add Alberta as a primary region with an April to October fire
  window.** Spring boreal fires are a large share of Alberta's burned area
  (e.g. Fort McMurray, May 2016, after the 2015-16 El Niño); a June start
  would miss them. Files: `src/config.py`, `src/regions.py`.
- **Decided to keep La Niña and a prediction model out of scope for now.**
  Both are planned later extensions; La Niña years are labelled in the ENSO
  output and analysis tables are kept tidy (region x year) so neither needs
  rework later. Files: `ACTION_PLAN.md`, `CLAUDE.md`.
