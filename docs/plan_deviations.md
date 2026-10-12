# Plan deviations

Every place where what actually happened departed from what the planning
documents said: estimates, assumptions, procedures, scope and workflow. Covers
`ACTION_PLAN.md`, `ANALYSIS_PLAN.md`, `README.md`, `CLAUDE.md`,
`DATA_SOURCES.md`, the 2026-10-03 and 2026-10-04 planning entries in
`DECISIONS.md`, and the scaffold code's built-in assumptions. Newest first;
never edit an old entry, add a new one that supersedes it.

**How this relates to the other records.** `DECISIONS.md` holds the
reasoning for judgment calls; an entry here points to it rather than
repeating it. After the freeze, a change to a pre-registered test is logged in
`ANALYSIS_PLAN.md`'s deviations log (the official pre-registration record) and
mirrored here as a one-line pointer.

**Entry format:** an ID, then *Plan* (the document and section, and what it
said), *Actual* (what happened, with numbers), *Why*, *Recorded* (where the
reasoning lives) and *Plan doc* (updated, or left as written). Wording in the
planning documents that is the owner's own prose is left as written and
flagged here instead.

**Substantial deviations.** When the owner judges a deviation substantial
enough to change the plans themselves (e.g. a scope change), the entry says
*Substantial: yes*, the planning documents are edited directly, and every
changed spot carries the marker `[mid-project: Dnn]`, so mid-project
additions stay distinguishable from the original plan.

## 2026-10-12

### D87 · Rollout calendar: one dated list, new settings in `config.py`
- **Plan:** `ACTION_PLAN.md` "Second goal", tracker item: "its dates live
  in `src/config.py`" (`TRACKER_WINDOW`, `TRACKER_FREEZE_DATE`,
  `TRACKER_DATA_DAY`); no plan lists the arrivals after April 2027, the
  undated releases (CNFDB 2025, CanSWE v9) or what each one changes on
  the site. D76: the forecast is published "in dated stages as the winter
  data arrive, the final one after the April 1 snowpack", with no number
  of stages and no dates.
- **Actual:** owner, 2026-10-12: "session 10 might need to scaffold
  exactly what the site is waiting for and when". `src/rollout.py` builds
  one list (18 items) from the settings already in `config.py` and writes
  `results/tables/rollout_calendar.json`; the tracker page's timetable
  and the scheduled reminders read that file. New settings, added after
  the freeze: `ROLLOUT_WINDOWS` (expected windows for five arrivals with
  no fixed date; expectations from release records, not measurements),
  `ROLLOUT_REMINDER_LEAD_DAYS` (3), `RONI_REVISION_MONTHS` (2). The six
  tracker months are October to March: the months whose data arrives
  inside `TRACKER_WINDOW`. The list marks two forecast stages, the first
  at CPC's first RONI release after February 2027 (the frozen plan's
  input for the H3a forecast), the final at the 1 April snowpack; a
  proposal until the owner confirms the stages.
- **Why:** the timetable, the reminders and the pipeline would otherwise
  each hold their own dates.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Session 10: rollout calendar".
- **Substantial:** no (no test, input or registered number changes; the
  new settings are read only by `src/rollout.py`).
- **Plan doc:** `ACTION_PLAN.md` "Second goal", tracker item, sentence
  marked `[mid-project: D87]`.

### D86 · A shared design system (scope addition)
- **Plan:** `ACTION_PLAN.md` "Second goal" names a Quarto site and its
  pieces; no plan names a theme, a tokens file or a design system
  (`site/_quarto.yml` uses the stock `cosmo` theme).
- **Actual:** owner, 2026-10-12 (sessions 9 and 10): the site's look is
  redesigned with a design system of its own, a Design System artifact
  plus one tokens file in the repository read by the site, the results
  page template, the methods page and the figures.
- **Why:** five pages and the figures had drifted into separate
  palettes; one source keeps them in step.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Session 10: design system,
  hosting and the map page".
- **Substantial:** no (presentation only; no test, input or result
  changes).
- **Plan doc:** left as written.

### D85 · Map page (scope addition)
- **Plan:** `ACTION_PLAN.md` "Second goal" lists six site pieces; no map
  of the regions with a dataset toggle is among them.
- **Actual:** owner, 2026-10-12 (session 10): a map page with all seven
  regions and a toggle per dataset (fire, snowpack, rainfall,
  temperature), built after the stamped download paths and the hard-line
  item. It shows each year's values from the committed region x year
  tables; no trend statistic is computed.
- **Why:** owner's idea at the end of session 9; a reader sees where the
  regions are and how the datasets differ across them.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Session 10: design system,
  hosting and the map page".
- **Substantial:** yes (a new site piece).
- **Plan doc:** `ACTION_PLAN.md` "Second goal", new item marked
  `[mid-project: D85]`. No row in the frozen plan's deviations log (no
  registered or reported test changes).

### D84 · Hosting: own domain through Cloudflare, not GitHub Pages
- **Plan:** `ACTION_PLAN.md` "Second goal": "A Quarto site in `site/`,
  published on GitHub Pages"; `README.md`: "Quarto explainer site
  (published to GitHub Pages)".
- **Actual:** owner, 2026-10-12 (session 10): the static Quarto build is
  hosted on the owner's own domain through Cloudflare. Streamlit was
  considered and rejected. Nothing is deployed yet; the exact Cloudflare
  setup is settled when the first piece is ready.
- **Why:** the owner's own domain; a direct upload of the built site
  does not need a public repository.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Session 10: design system,
  hosting and the map page".
- **Substantial:** yes (where the site is published).
- **Plan doc:** `ACTION_PLAN.md` "Second goal", sentence marked
  `[mid-project: D84]`; the `README.md` line left as written.

### D83 · Prediction model moved up: next after the registered runs
- **Plan:** `ACTION_PLAN.md` "Later extensions": "Prediction model. ...
  Builds on Phases 2-4, so start it once the historical analysis is
  solid", and the roadmap's "after Phase 4, when asked". `CLAUDE.md`
  scope guard: "Don't build either unless asked."
- **Actual:** owner, 2026-10-12 (session 9, after `run1` was seen):
  "note the prediction model in roadmap and methodology. this is what i
  want to get to next, maybe we can try training it on the past years
  and have it try on years not yet seen. maybe this can be done in
  parallel with the design-focused session 10?" and "maybe we should
  scope out the extent of the model, how it should be trained, whether
  machine learning would be an interesting V2 after what's currently
  scoped out for it". The seasonal-outlook model becomes the next
  analysis, scoped first, then built as a side session beside session
  10. Nothing is built yet.
- **Why:** the registered tests are committed, and `run1` showed where
  the signal is (winter moisture and snowpack, not the El Niño index).
- **Constraint (post-results protocol, section 2):** it is a new
  analysis added after results were seen: exploratory, uncorrected,
  reported apart from the registered tests, never replacing one. What
  had been seen: all of `run1`, including the validation table (H3a
  skill against a trend-only model -0.03 to +0.01; H6 snowpack up to
  +0.06). The registered 2027 forecast stays the H3a model. The model's
  inputs, the way it is scored on unseen years and its baseline are
  written down and agreed before any model is fitted.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Prediction model is next;
  owner's answers at the end of session 9".
- **Substantial:** yes (order of work and scope; no registered test,
  input or result changes).
- **Plan doc:** `ACTION_PLAN.md` "Later extensions", marker
  `[mid-project: D83]`. No row in the frozen plan's deviations log (no
  registered or reported test changes).

### D82 · A second pinned reader, for the raw ENSO files
- **Plan:** `docs/post_results_protocol.md` section 5 and D73: "Tables
  are opened only through `src.pin_inputs.load_input`", which opens only
  a pinned table in `results/tables/`.
- **Actual:** owner, 2026-10-12 (session 9, before any test): the runner
  also reads the two pinned raw ENSO files through
  `pin_inputs.enso_raw_path(index)`, which checks the file's sha256
  against its pin. The ONI robustness runs take their index from
  `data/raw/oni.ascii.txt`; the RONI file is read to check that the
  committed tables hold its values.
- **Why:** every committed table holds RONI only; ONI exists only in
  the pinned raw file, outside `results/tables/`.
- **Recorded:** `DECISIONS.md` 2026-10-12 "First hypothesis runs
  planned; runner written"; `docs/methods_register.md` "Pinned ENSO
  reader".
- **Substantial:** no (safeguard code; no test, input or pin changes).
- **Plan doc:** dated note at the bottom of
  `docs/post_results_protocol.md`. No row in the frozen plan's
  deviations log (no registered or reported test changes).

### D81 · NBAC coverage split reported as a limitation; no NBAC re-run
- **Plan:** `ACTION_PLAN.md` Phase 4: "the exploratory NBAC re-run of
  the Canadian tests ... each yes or no" before the first hypothesis
  test. `ANALYSIS_PLAN.md` (frozen) names CNFDB as the Canadian fire
  source and reports no coverage figure against NBAC.
- **Actual:** owner, 2026-10-12, before any test: no re-run. The
  per-fire split is reported beside the BC, AB and YT results: NBAC area
  in fires with no same-YEAR CNFDB polygon under more than half of them,
  on provincial labels, AB 2.7%, BC 2.0%, YT 3.1% of NBAC area
  (1984-2024), with the seasons over 10% named (AB 6, BC 9, YT 3 of 41).
- **Why:** 2-3% of area, log-series correlation 0.990-0.997, parks and
  defence lands already handled (D69, D71); a re-run needs its own date
  rule and another build before 2026-11-06.
- **Recorded:** `DECISIONS.md` 2026-10-12 "No NBAC re-run";
  `docs/methods_register.md` "NBAC per-fire split".
- **Substantial:** no (a reported number; no test, input or rule
  changes).
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, row 19 (added);
  `ACTION_PLAN.md` Phase 4 item ticked.

### D80 · Plain OLS check one-sided beside the one-sided H3a and H3b tests
- **Plan:** D66 and the `ANALYSIS_PLAN.md` deviations log, eighth row: a
  plain OLS p beside the registered p of the ENSO tests, kept where its
  measured size is near 5%; the size table held only a two-sided plain
  OLS row for H3a and H3b, while PNW, BC and AB are registered one-sided.
- **Actual:** owner (2026-10-11 and 2026-10-12, before any test): the
  check takes the sidedness of its registered test. One-sided size
  measured: H3a 4.75%, H3b 5.60% (2,000 datasets, Monte Carlo SE 0.49%);
  kept. `test_size.csv` 63 to 71 rows, the earlier rows identical.
- **Why:** a check should ask the registered test's question; a two-sided
  p beside a one-sided one is double by construction.
- **Recorded:** `DECISIONS.md` 2026-10-12 "Plain OLS check takes the
  registered test's sidedness"; `docs/methods_register.md` "Size label
  lookup".
- **Substantial:** no (completes D66's reported addition).
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, row 18 (added); frozen
  text above the log unchanged.

## 2026-10-11

### D79 · Interior Alaska check measured (scope addition, descriptive)
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Alaska and Yukon": Alaska stays
  one region; the limitation "climate means include wet coasts that
  rarely burn" is stated, not measured. `ACTION_PLAN.md` Phase 4: the
  check is "each yes or no" before the first hypothesis test.
- **Actual:** owner, 2026-10-11, before any test: yes to the boundary
  download. NOAA NCEI Alaska climate divisions downloaded (terms read the
  same day), Interior = divisions 3, 4, 5 clipped to the AK polygon
  (41.8% of its area). Climate controls 1951-2026, Interior against whole
  AK: correlation 0.98 for `temp_jja` and `temp_mam`, 0.79 for
  `precip_djf_mm`, 0.82 for `precip_octmar_mm`; El Nino minus other
  winters, in SD of each series, DJF precipitation -0.37 against -0.18,
  Oct-Mar -0.25 against -0.04, `temp_mam` +0.45 against +0.37. No fire
  table read; AK stays one region in every test.
- **Why:** the check had to be settled before results, so that reporting
  it could not look chosen to fit them.
- **Recorded:** `DECISIONS.md` 2026-10-11 "Session 8";
  `docs/methods_register.md` "Interior Alaska (descriptive check)";
  `DATA_SOURCES.md` row "Alaska climate divisions".
- **Substantial:** yes (a new dataset and a descriptive measurement).
- **Plan doc:** frozen text unchanged; no row in the frozen plan's log
  (no registered or reported test changes). Whether the numbers are
  reported beside the AK results is the owner's call, still open.
- **Settled (owner, 2026-10-11, same session, before any test):**
  reported beside the Alaska results as a descriptive limitation;
  `ANALYSIS_PLAN.md` deviations log, row 17 (added, reported, not
  registered).

### D78 · Claude Code Project not used for the registered runs
- **Plan:** `ACTION_PLAN.md` Phase 4 "Before starting": "Then set up the
  Claude Code Project ... so H1-H5 and the site pages can run as parallel
  threads"; D63: decided after the audits.
- **Actual:** owner, 2026-10-11: no-go for the registered runs and the
  runs reported beside them, which one runner in the main checkout makes
  in one commit; the Project is taken up again for site pages after the
  runs.
- **Why:** each run is seconds of compute; the preflight verifies 30
  pinned inputs, 23 of them under `data/`, which cloud threads never see;
  the protocol wants one run folder written once.
- **Recorded:** `DECISIONS.md` 2026-10-11 "Session 8".
- **Substantial:** yes (how Phase 4 is run).
- **Plan doc:** `ACTION_PLAN.md` Phase 4, sentence marked
  `[mid-project: D78]`. No test or rule touched.

### D77 · DeepSeek review and delegation (scope addition)
- **Plan:** `ACTION_PLAN.md` Phase 4: the pre-results audit runs in cold
  read-only rounds until the gate closes; `CLAUDE.md` names no outside
  model. No DeepSeek step anywhere.
- **Actual:** owner, 2026-10-11: a DeepSeek read-only review of the
  safeguard code (and of the runner once written) as an extra read
  outside the closed gate; no delegated build before the registered
  runs are committed; a delegated-build pilot and a methods-page line
  ("DeepSeek helper agents contributed here") after them.
- **Why:** a second model's read of code that one short cold check has
  covered is cheap; a build before 2026-11-06 is new scope the date does
  not need.
- **Recorded:** `DECISIONS.md` 2026-10-11 "DeepSeek delegation: what is
  taken up, and when".
- **Substantial:** yes (a new review step and an outside service).
- **Plan doc:** `ACTION_PLAN.md` Phase 4, new item marked
  `[mid-project: D77]`. No test or rule touched.

### D76 · Rolling publication of the site
- **Plan:** `ACTION_PLAN.md` "Second goal": "Done when: the site is public
  with the first four pieces"; Phase 5: "Spring 2027: update with the
  final winter data and publish".
- **Actual:** owner, 2026-10-11: pieces go public on a rolling basis as
  each becomes ready (licences of its sources read; for anything setting
  burned area beside ENSO, the registered runs committed first); the 2027
  forecast in dated stages as the winter data arrive, the final one after
  the April 1 snowpack.
- **Why:** the pieces finish months apart, and dated stages keep the
  record that each statement was made before the season.
- **Recorded:** `DECISIONS.md` 2026-10-11 "Portfolio review follow-up".
- **Substantial:** yes (when the site goes public).
- **Plan doc:** `ACTION_PLAN.md` "Second goal", paragraph marked
  `[mid-project: D76]`; the Phase 5 line left as written. No test or rule
  touched.

### D75 · The 2026-11-06 commit also holds the reported runs
- **Plan:** `ACTION_PLAN.md` Phase 4 and D73: "Registered runs committed
  by Friday 2026-11-06"; the runs reported beside them carry no date.
- **Actual:** owner, 2026-10-11, before any test: the same commit holds
  the ONI robustness check, the frozen-rules run (D62), the Parks Canada
  sensitivity run (D69) and the strong-only results.
- **Why:** they read the same pinned inputs, so running them after the
  first tracker update would set them on different inputs from the tests
  they sit beside.
- **Recorded:** `DECISIONS.md` 2026-10-11 "Portfolio review follow-up";
  frozen plan's deviations log, row 16.
- **Substantial:** yes (more work before the deadline).
- **Plan doc:** `ACTION_PLAN.md` Phase 4, sentence marked
  `[mid-project: D75]`. No test or rule touched.

## 2026-10-08

### D74 · Site methods flowchart (scope addition)
- **Plan:** `ACTION_PLAN.md` "Second goal" lists the site pieces
  (mechanism diagram, winter rainfall map, historical charts, tracker);
  no methods diagram.
- **Actual:** owner, 2026-10-08: a plain-language methods flowchart for
  `site/methods.qmd` (sources, variables, region x year table, tests,
  charts), built in code like the mechanism diagram.
- **Why:** the private notebooks doc's pipeline diagram showed how much a
  flow picture helps; the audience version shows the analysis, not the
  repository.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Site methods flowchart".
- **Substantial:** yes (a new site piece).
- **Plan doc:** `ACTION_PLAN.md` "Second goal", new item marked
  `[mid-project: D74]`. No test or rule touched.

### D73 · Run sequencing and runner safeguards (audit round 5 S1-S6)
- **Plan:** `ACTION_PLAN.md` Phase 4 sets no date for the registered
  runs; Phase 5's hard-line item (D55, early November 2026) downloads every
  published 2026 month and rebuilds the climate tables; the download
  scripts write onto the pinned paths (`download_oni`, `download_wfigs`,
  `download_cnfdb`, `download_mtbs`; only NBAC's file name carries its
  release); nothing protects the pinned inputs from a rebuild or says how
  a change after results is handled.
- **Actual:** owner, 2026-10-08, before any fire data were tested: the
  registered runs are computed and committed by Friday 2026-11-06, the day
  before October's ERA5-Land data is expected (`TRACKER_DATA_DAY` 7, D55).
  Every later download writes to a release- or retrieval-stamped path,
  never over a pinned input. If the runs miss the date, only the climate
  tables are re-pinned, logged, and only if every value a registered test
  reads is identical; the ENSO and fire pins are not touched. An offline
  copy of the 30 pinned inputs is kept. Before the first run: a protocol
  for changes after results (S6, written first), builders that refuse to
  overwrite a pinned file without `--rebuild` and a re-pin log (S2), one
  pinned loader (S3), a frozen-text check and preflight (S4), a
  provenance record beside every result (S5); a short cold check of that
  code.
- **Why:** audit round 5 S1: RONI is revised monthly and WFIGS is live,
  so a download onto a pinned path either breaks `--verify` or puts a
  revised input under the tests (trap 7).
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 5 settled;
  pre-results gate closed".
- **Substantial:** yes (a deadline and a procedure for the inputs).
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, fifteenth row;
  `ACTION_PLAN.md` Phase 4 (two items) and Phase 5 (hard-line item)
  marked `[mid-project: D73]`; frozen text above the log unchanged.

### D72 · Corrections to D71 (audit round 5 L2, L3)
- **Plan:** D71: NBAC gives every defence-land part cause "Undetermined",
  satellite-only, "58 of 63 undated"; the `ANALYSIS_PLAN.md` deviations
  log, thirteenth row: "1% of AB's area".
- **Actual:** 60 parts for 1984-2024, the range measured (63 with 2025),
  every one "Undetermined" and MAFiMS, 58 undated; the 109,773 ha are
  0.98% of AB's counted burned area 1984-2024 (of 11,149,758 ha), not of
  AB's land area. No value or decision changes.
- **Why:** the part count was read on a 1984-2025 base; "area" dropped
  "counted burned".
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 5 settled;
  pre-results gate closed"; `docs/methods_register.md` "Defence lands
  (DND)".
- **Substantial:** no.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, fourteenth row (added,
  correcting row 13); frozen text above the log unchanged.

### D71 · Corrections to D69 and D70; defence lands a stated limitation
- **Plan:** D69 (and the `ANALYSIS_PLAN.md` deviations log, eleventh
  row): "CNFDB holds no Parks Canada polygon for 2016-2021"; NBAC and CNFDB
  park area "within 1%" over AB 1984-2017 (1,250,741 vs 1,259,913 ha),
  single seasons within 5% in 5 of 14; Wood Buffalo 1.75 of 1.85 million
  ha. D70: the plain OLS check measures 4.3-5.4% under the label scenario.
- **Actual:** audit round 4 (M1, L1, L2, L3), rechecked here: CNFDB holds
  no Parks Canada polygon at or above 405 ha in BC, AB or YT for
  2016-2021: none at all for 2018-2020, Nahanni (NWT) only in 2016 (5)
  and 2017 (8), and 2021 small fires only (28 polygons in the study
  regions, largest 65 ha). The seasons flagged (AB 2016-2019) and every
  table value stand. Union to union, NBAC park area in AB 1984-2017 is
  1.3% above CNFDB's (1,250,741 vs 1,234,910 ha; 1,259,913 was CNFDB's
  sum of pieces); both above 0 in 25 seasons, within 5% in 6, within 15%
  in 11, ratio 0.45 to 2.08; Wood Buffalo 2.08 of 2.17 million ha (95.7%;
  the old figure unioned across years). After round 3 pooled the labels,
  the plain OLS label rows run 4.1-5.0%. Also found (round 4 M2): fires
  on Department of National Defence land in AB (CFB Wainwright,
  Suffield), 109,773 ha over 1984-2024 (0.98% of AB), are in no CNFDB
  polygon in any year; owner chose (2026-10-08, before any test) a stated
  limitation, not added to the sensitivity table: NBAC gives every part
  cause "Undetermined", satellite-only, 58 of 63 undated, so they cannot
  be told from range burning, and the plan counts wildfires.
- **Why:** the D69 wording generalised from the counted pieces; the
  agreement figures compared an NBAC union with a CNFDB sum.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 4 settled";
  `docs/methods_register.md` "Parks Canada gap", "Defence lands (DND)".
- **Substantial:** no.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, thirteenth row (added,
  correcting row 11); frozen text above the log unchanged.

### D70 · Corrections to the D66 and D68 wording
- **Plan:** D66 (and the `ANALYSIS_PLAN.md` deviations log, eighth row)
  says the registered robust tests reject a true null in 6-9% of
  synthetic datasets (joint F about 20%); D68 says the plain OLS check
  kept for H3a, H3b, C1, C2 measures 3.8-5.6%.
- **Actual:** audit round 3 (L3, L5): the C2 interaction shape, added to
  the size table in round 2, measures 10.0-10.4% under Newey-West
  (`results/tables/test_size.csv`; round 3's own generator 11.5%, with the
  real RONI regressor 9.9%), so the robust per-region tests run 6-10%; the
  plain OLS rows for H3a, H3b, C1, C2 run 3.8-6.1% over the three
  scenarios (4.3-5.4% under the label scenario). No rule or number used by
  a test changes; the labels come from `test_size.csv`.
- **Why:** the two entries quote ranges measured before the C2 shape and
  the second run existed.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 3 settled".
- **Substantial:** no.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, twelfth row (added,
  correcting rows 8 and 10); frozen text above the log unchanged.

### D69 · Parks Canada gap: AB 2016-2019 flagged, NBAC sensitivity run added
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Outcomes" and "Fire record
  rules": BC, AB and YT burned area from the CNFDB agency polygons; the
  Parks Canada gap was known only as "no Parks Canada polygons for
  2018-2020" (CNFDB update log; methods register, "not handled").
- **Actual:** measured 2026-10-08 (session 7, read-only, fire only, no
  ENSO): CNFDB holds no Parks Canada polygon for 2016-2021, and the
  provinces do not map inside the parks (non-Parks Canada polygons inside
  the park footprint: AB 0 ha in 2018-2020). NBAC (release v20260513,
  downloaded with the owner's yes) splits fires at park boundaries; its
  park area in AB is 6,855 ha (2016), 38,980 (2017), 10,909 (2018),
  118,328 (2019), 0 (2020, 2021): 1.3%, 39.1%, 20.4% and 14.3% of each
  season missing (log_burn +0.013, +0.50, +0.23, +0.16); BC 2017, 2018,
  2023 and YT 2022, 2023 at most 0.9%. Where both sources have park
  polygons, NBAC and CNFDB Parks Canada area agree within 1% summed over
  AB 1984-2017, single seasons within 5% in 5 of 14 and up to about 2x.
  Owner chose (2026-10-08, before any test) B + C: (B) the AB 2016-2019
  seasons flagged `parks_gap` in both fire tables (`PARKS_GAP_SEASONS`),
  values unchanged; (C) every burned-area test that uses AB (H2, H3a,
  H3b, H4, H5, H6, C2) rerun on `fire_region_year_parks_nbac.csv`, the
  main table with NBAC's park area added for those four seasons
  (`src/parks_gap.py`), reported beside the main results, exploratory,
  uncorrected. BC and YT: a stated limitation. Rejected: a limitation only
  (AB 2017 39% short); filling the main table with NBAC (mixes sources in
  the registered series, single seasons disagree by up to 2x).
- **Why:** AB is a primary region in H2-H6; the gap is large in three
  seasons, and its effect on the results is unknown until tested.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 3 settled";
  `docs/methods_register.md` "Parks Canada gap".
- **Substantial:** yes (owner, 2026-10-08): scope addition, a reported
  analysis and a new dataset in a committed table.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, eleventh row (added,
  reported, not registered); `ACTION_PLAN.md` Phase 4 item marked
  `[mid-project: D69]`; frozen text above the log unchanged.

### D68 · Plain OLS check dropped for the H4 contrast (narrows D66)
- **Plan:** D66 and `ANALYSIS_PLAN.md` deviations log, eighth row: a
  plain OLS p reported beside the registered p of the ENSO tests (H3a,
  H3b, H4 contrast, C1, C2), kept only where its own measured size is
  near 5%.
- **Actual:** audit round 2 (M1) found the H4 contrast's plain OLS p fails
  that condition: size 0.7% with regions correlated 0.5 (0.000 at 0.8,
  0.045 at 0; session 7 measured 0.6%), and power at a true
  north-minus-SoCal slope difference of 0.10 / 0.15 / 0.20 of 0.11 /
  0.30 / 0.58 against the registered Driscoll-Kraay test's 0.38 / 0.64 /
  0.88. The shared year shock cancels in a between-region contrast, so
  plain OLS overstates the contrast's variance. Owner chose (2026-10-08,
  before any result): drop it for the H4 contrast; the measurement and
  reason are kept in the internal records (methods register "Test size
  (simulated)", `results/tables/test_size.csv`), not reported beside the
  results. Kept for H3a, H3b, C1, C2 (3.8-5.6% in the second run).
  Registered p-values and Holm verdicts unchanged.
- **Why:** beside the registered p, a non-significant plain OLS p would
  read as a failed check that the check could not have passed.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 2 settled".
- **Substantial:** no (narrows D66's reported addition).
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, tenth row (added);
  frozen text above the log unchanged.

### D67 · CNFDB fires: parts merged only within 1 km
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Fire record rules" and
  "Outcomes": the 405 ha floor applies to each whole fire's area before
  clipping; silent on CNFDB fires recorded as several polygons. The round 1
  fix (32e8d42, audit M3) merged every polygon sharing agency, YEAR and
  FIRE_ID before the floor, with no plan log row.
- **Actual:** audit round 2 (H1) found agencies reuse FIRE_ID within a
  year: the parts of the 136 groups lie a median 25 km apart, over 300 km
  in 75%, up to 1,109 km. Among counted fires the round 1 merge joined
  three pairs of separate fires: BC 1998-N40187 and N40188 (each two
  sub-floor fires 25-26 km apart, now passing the floor together: BC 1998
  +1,015 ha, 22 to 24 fires) and BC 1994-K50087 (43 km; 11 to 10 fires).
  Owner chose (2026-10-08): merge only parts that touch or lie within
  1 km of another part of the group, chained (`CNFDB_MERGE_KM` = 1.0,
  distance in ESRI:102008); further parts stay separate fires. Rebuild:
  58 merged fires from 121 polygons; 10 among the counted pieces, all with
  parts within 0.5 km, the next counted pair 25 km apart (any distance
  from 0.5 to 25 km gives the same tables). Against per polygon, 6
  Canadian seasons change, no US season: BC 2003 +645 ha (56 to 57 fires),
  BC 2006 +33 ha, AB 2012 +40 ha, and BC 2004, YT 1990, YT 1995, AB 2012
  one fire fewer; BC 1998 (60,120.5 ha, 22 fires) and BC 1994 (11) as per
  polygon. The frozen-rules table rebuilt the same way. Decided after fire
  data was opened, before any test; a defect fix under D62's firm line.
- **Why:** the frozen rule floors each fire's whole area; a merge of two
  fires floors their sum. Rejected: reverting to per polygon (round 1
  option b), which would undo the 10 sound merges; the NFDB points file
  as a check (a new download, not needed with a 25 km gap and, for
  N40188, different months and causes).
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 2 settled";
  `docs/methods_register.md` "CNFDB fires in several polygons".
- **Substantial:** no.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, ninth row (added, also
  covering the round 1 merge); frozen text above the log unchanged.

### D66 · Test size reported; plain OLS p added as a size check
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Small-cluster corrections",
  "Headline methods" 2-3, "Supporting methods": Newey-West and
  Driscoll-Kraay p-values with t critical values, the H4 joint F as
  secondary; no size check beyond the block bootstrap CI of the H3a and
  H3b coefficients.
- **Actual:** audit round 1 (M1) and session 7 simulations
  (`scripts/stats_size_check.py`) found the registered robust tests reject
  a true null more often than 5% on synthetic data like the project's
  (Newey-West H3a shape 7.5-8.9%, H4 contrast Driscoll-Kraay 6.3-8.2%,
  joint F about 20%). Owner chose (2026-10-08, before any result): (a)
  the measured size printed beside every Newey-West, Driscoll-Kraay and
  joint-F p-value; (c) the joint F kept as reported, labelled with its
  size; (b) a size check beside the registered p-values, kept only where
  its own measured size is near 5%: plain OLS p kept for the ENSO tests
  (H3a, H3b, H4 contrast, C1, C2; 3.9-5.7%, the H4 contrast 0.6% with
  correlated regions), not for H5 and H6 (7-9% at their predictors'
  persistence, lag-1 up to 0.27); the year-block bootstrap p measured
  6-9% and dropped everywhere. Registered p-values and Holm verdicts
  unchanged.
- **Why:** the size labels alone describe the test, not each result; a
  check of near-nominal size shows which significant results survive.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Audit round 1 settled".
- **Substantial:** yes (owner, 2026-10-08): scope addition, reported
  analyses.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, eighth row (added,
  reported, not registered); frozen text above the log unchanged.

### D65 · Small-sample correction on in every robust fit
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Small-cluster corrections" and
  "Execution details": `use_t=True`, Newey-West maxlags 2, Driscoll-Kraay
  for H4 with df = years - 1; silent on the small-sample correction of the
  robust covariance. Session 7 kickoff trap 3: "Decide before any result
  (lean: off, the default)".
- **Actual:** a read of statsmodels 0.15.0 found its defaults differ by
  fit: Newey-West uncorrected, Driscoll-Kraay and year-clustered corrected
  (cluster factor). Owner chose (2026-10-08, before any result) the
  correction on everywhere: n/(n - k) for Newey-West, the cluster factor
  G/(G - 1) x (N - 1)/(N - K) for Driscoll-Kraay and year clustering
  (`ROBUST_SMALL_SAMPLE_CORRECTION`). SEs about 3.8% wider for H3a, 5.1%
  for H3b, 4.9% for the H4 Driscoll-Kraay fit.
- **Why:** one rule for every fit, in the conservative direction for
  41-42 seasons; the kickoff's lean was written before the defaults were
  known to differ.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Small-sample correction on in
  every robust fit".
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, seventh row (an
  execution detail the frozen text leaves open; no fire data run through
  the statistics code); frozen text above the log unchanged.

### D64 · Pre-results audit in repeated rounds
- **Plan:** `ACTION_PLAN.md` Phase 4 (D51): "then checked by a read-only
  audit with a neutral prompt, before any of it runs on the fire table".
- **Actual:** owner chose (2026-10-08) rounds of cold read-only audits,
  each after the previous round's fixes, until one finds nothing high and
  the owner agrees.
- **Why:** owner: "I want to be extra certain we have a solid foundation
  before the following steps"; the pre-freeze series needed three rounds.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Pre-results audit in repeated
  rounds".
- **Substantial:** yes (owner, 2026-10-08): procedure for the gate.
- **Plan doc:** `ACTION_PLAN.md` Phase 4 marked `[mid-project: D64]`.

### D63 · Claude Code Project set up after the pre-results audit
- **Plan:** `ACTION_PLAN.md` Phase 4 "Before starting": "Then set up the
  Claude Code Project (on standby since 2026-10-04) using
  `docs/claude_code_project_setup.md`, so H1-H5 and the site pages can run
  as parallel threads"; the reminder (2026-10-07) put the decision at the
  start of the statistics code.
- **Actual:** owner chose (2026-10-08) to build the D51 gate's code in the
  main session and decide on the Project after the audit, for the
  hypothesis runs.
- **Why:** the gate's pieces share one module and depend on each other.
- **Recorded:** `DECISIONS.md` 2026-10-08 "Claude Code Project decided
  after the audits".
- **Plan doc:** left as written (workflow, not a test); flagged here.

## 2026-10-07 (Phase 3, session 6: after the freeze, after fire data was opened)

### D62 · Frozen-rules robustness run; audit gate covers the fire build
- **Plan:** `ANALYSIS_PLAN.md` (frozen): no robustness run for the fire
  record rules; `ACTION_PLAN.md` Phase 4: the pre-results audit (D51)
  covers the statistics code and unbuilt variables only.
- **Actual:** owner added (20:17) a rerun of every burned-area test on a
  fire table built under the frozen rules (summed area, Other dropped,
  undated CNFDB dropped, frozen years), and extended the D51 audit to
  the fire build, with the firm line on rule changes at its close.
- **Why:** four rules changed after fire data was opened (D58-D61).
- **Recorded:** `DECISIONS.md` 2026-10-07 "Frozen-rules robustness run;
  firm line on fire rules".
- **Substantial:** yes (owner, 2026-10-07): scope addition.
- **Plan doc:** `ACTION_PLAN.md` Phase 4 marked `[mid-project: D62]`;
  `ANALYSIS_PLAN.md` deviations log, sixth row (an added reported
  analysis; no registered test changed).

### D61 · MTBS complete only through 2023; union area; D60 re-run on 2023
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Fire record rules": "MTBS for
  every year it holds complete, WFIGS after"; "Outcomes": burned area is
  "total hectares of counted fires per region per fire season"; D60's
  rule on 2024; DECISIONS (this date) cutover 2025-01-01.
- **Actual:** a fire-by-fire match found MTBS missing 22-58% of 2024's
  WFIGS area (114 fires, 537,228 ha), so 2024 is not complete in MTBS;
  the products agree within 1-5% on matched fires 2021-2024. Owner chose
  (20:03, before computing) the cutover 2024-01-01, union area per
  region, season and source (overlapping polygons once; area counted
  twice before: CNFDB 46,012 ha, WFIGS 38,439, MTBS 1,767), and D60's
  rule re-run on 2023 with union areas: pass, frozen years stand; fail,
  US regions end at 2023.
- **Why:** the 2025 cutover rested on fire counts, not area; D60 ran on
  a year that failed its own premise; summing double-counts duplicates
  and complex outlines (NorCal 2023 "BLOCK", Mosquito).
- **Recorded:** `DECISIONS.md` 2026-10-07 "MTBS complete through 2023;
  cutover, union area, D60 re-run".
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, fifth row (2026-10-07),
  stating what had been seen when it was decided; the frozen text above
  the log unchanged (checked against the tag).

### D60 · Last fire season set by a source-agreement rule on 2024
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Fire record rules": "MTBS for
  every year it holds complete, WFIGS after; the cutover year is fixed and
  recorded at download, and the last overlapping year is compared as a
  reported check"; "Execution details" and the deviations log (D57): US
  regions' fire tests 1984-2025.
- **Actual:** owner asked whether every region should end at 2024. Decided
  (16:40 UTC-07:00, before the comparison was computed) that the 2024
  overlap check also decides it: if |log(1 + ha_WFIGS) - log(1 + ha_MTBS)|
  >= 0.10 for 2024 ignitions in any of PNW, AK, NorCal, SoCal, every
  region ends at 2024; otherwise 2025 stands. The check stops being
  report-only. Fire data had been opened (attribute profiles, MTBS counts
  and acres by state and year), nothing joined to ENSO.
- **Why:** D57 rejected a splice of a different product into the last
  season at a gap of 11-17%; the same test applied to the US splice.
- **Recorded:** `DECISIONS.md` 2026-10-07 "Fire record rules settled at
  download (session 6)".
- **Plan doc:** superseded by D61 before it changed any year; its rule and
  re-run are in the plan's deviations log, fifth row.

### D59 · CNFDB fires without a month or day counted by YEAR
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Fire record rules" and "Fire
  windows": fires "assigned by ignition date"; CNFDB date completeness
  reported by decade (for season length). Undated fires are not mentioned.
- **Actual:** large CNFDB fires without month or day (YT 102, 97 of them in
  2022; AB 39; BC 0) cannot be checked against the window; owner chose to
  count them for season YEAR (flagged, out of season length). Dated fires
  outside the windows hold 0.01-0.9% of area.
- **Why:** dropping them would remove most of Yukon's 2022 fires.
- **Recorded:** same entry.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, fourth row (2026-10-07).

### D58 · MTBS has "Other", not "Unknown"
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Fire record rules": MTBS incident
  types "Wildfire, Wildland Fire Use and Unknown kept (Unknown counted and
  reported)"; `src/config.py` `MTBS_KEEP_TYPES`.
- **Actual:** the 2026-10-07 release has no "Unknown"; its fourth type is
  "Other" (4,311 polygons; 128 fires and 1.0% of Wildfire acres in the five
  states), while its metadata still documents "Unknown" (UNK). Owner chose
  to read Other as Unknown.
- **Why:** label changed in the data, not the rule.
- **Recorded:** same entry.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, third row (2026-10-07);
  `MTBS_KEEP_TYPES` lists "Other".

## 2026-10-07 (after freeze)

### D56 · CNFDB polygons end in 2024; fire tests run to 2025
- **Plan:** `ANALYSIS_PLAN.md` (frozen, acf7a80) "Execution details",
  Years: "Fire tests use fire seasons 1984 to 2025 (`FIRE_LAST_YEAR`);
  2026 is described only (CNFDB 2026 not yet published, ...)", which
  assumes CNFDB holds 2025; `src/config.py` `FIRE_LAST_YEAR = 2025`.
- **Actual:** the licence read (2026-10-07) found the current NFDB
  polygon release (files dated 28 Jan 2026) covers BC 1917-2024, AB
  1931-2024 and YT 1946-2024. The 2025 season is only in the NFDB points
  (Aug 2026) and NBAC (1972-2025, May 2026, same licence); the next
  polygon release is expected about a year after the last.
- **Why:** CNFDB polygons are released annually, about 13 months after
  the season they add. No data was opened; coverage is from the
  catalogue record.
- **Recorded:** `DECISIONS.md` 2026-10-07 "Fire perimeter licences read
  (side session)"; `DATA_SOURCES.md` CNFDB row. How to handle 2025 for
  BC, AB and YT (wait for a release, end the Canadian series at 2024, or
  another product) is open for the owner; a change to the pre-registered
  years goes in `ANALYSIS_PLAN.md`'s deviations log.
- **Plan doc:** left as written (frozen).

## 2026-10-07 (gate)

### D57 · Canadian fire series end at 2024 (D56 settled)
- **Plan:** `ANALYSIS_PLAN.md` (frozen) "Execution details", Years: fire
  tests on seasons 1984-2025 in every region; D56 left the Canadian 2025
  season open.
- **Actual:** owner chose (2026-10-07, before any fire data was downloaded
  or opened) to end the BC, AB and YT fire tests at 2024, the last CNFDB
  polygon year, after a documentation-only NBAC probe (PR #22,
  `docs/nbac_probe.md`): NBAC's area runs 11-17% below CNFDB on average,
  so filling 2025 from NBAC would put a step into the last season, and
  NBAC throughout would need new handling rules. US regions keep 2025;
  H4 uses 1984-2024 for all five regions; Canadian expanding-window
  predictions 2004-2024. CNFDB 2025 is reported beside the results when
  released, not substituted. Rejected waiting for the next CNFDB release
  (about January 2027; Phase 4 at the mercy of a release date), NBAC for
  2025 only, NBAC throughout, and the NFDB points (agency-reported areas).
- **Why:** see `DECISIONS.md` 2026-10-07 "Canadian fire series end at
  2024".
- **Recorded:** `DECISIONS.md` 2026-10-07 "Canadian fire series end at
  2024".
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, second row
  (2026-10-07); `src/config.py` `CNFDB_LAST_YEAR`,
  `FIRE_LAST_YEAR_BY_REGION`, `POOLED_LAST_YEAR`. The frozen text above the
  log stays as written; D56 is left as written.

### D55 · ERA5-Land monthly means arrive within a week; supersedes D54
- **Plan:** D54 (this date) said ERA5-Land monthly means run about 3
  months behind, citing a "measured" lag, and held the tracker's arrival
  dates; `src/config.py` `ERA5_LAG_MONTHS` = 3 (pre-start review,
  2026-10-04); the methods register's "data ends 2026-07".
- **Actual:** a CDS probe on 2026-10-07 (one cell, 2 m temperature) found
  July, August and September 2026 monthly means published. The 3 months
  were a download margin set in the pre-start review, not a measurement;
  the July end of the data came from the setting. PR #19's assumption (by
  the 6th of the next month) holds; `TRACKER_DATA_DAY` is set to 7, the day
  observed. D54's premise was wrong.
- **Why:** D54 took a setting for a measurement without checking.
- **Recorded:** `DECISIONS.md` 2026-10-07 "Tracker data arrival measured".
- **Substantial:** yes (owner, 2026-10-07): a hard-line item for the first
  tracker update.
- **Plan doc:** `ANALYSIS_PLAN.md` deviations log, first row (2026-10-07):
  `ERA5_LAG_MONTHS` 3 to 1 at the first tracker update (early November
  2026), decided before any fire data, no registered test changed;
  `ACTION_PLAN.md` Phase 5, hard-line item marked `[mid-project: D55]`.
  D54 is left as written; `ACTION_PLAN.md`'s "early November" stands.

### D54 · Tracker data arrival: monthly means run about 3 months behind
- **Plan:** `ACTION_PLAN.md` "Second goal" (D44, D46): October's data
  "arrives in early November", with the first countdown to it; PR #19's
  table: monthly data by the 6th of the following month (marked an
  assumption to measure), first data 2026-11-06, last 2027-04-06.
- **Actual:** ERA5-Land monthly means run about 3 months behind
  (`ERA5_LAG_MONTHS`, measured 2026-10-04: data ended in July 2026, still
  so on 2026-10-07); only the hourly product is about 5 days behind
  (`ERA5_HOURLY_LAG_DAYS`). From monthly means, October 2026 would arrive
  about January 2027 and March 2027 about June. The April 1 snowpack
  (hourly) is unaffected.
- **Why:** an assumption in the tracker plan, found when the dates were
  added to `src/config.py` after the freeze.
- **Recorded:** `DECISIONS.md` 2026-10-07 "Freeze and tracker".
- **Plan doc:** left as written pending the owner's decision (arrival
  dates not set in `config.py`).

### D53 · ONI band, strong-only scope, H6 coverage; zero-fire pointer
- **Plan:** `ANALYSIS_PLAN.md` at b9153a4: the ONI robustness runs repeat
  "the strong-only results" without saying which winters flip under ONI;
  strong-only results name no regions or sidedness; leave-one-year-out
  coverage (Headline methods 4) for H3a only; the 2026-10-05 "Zero-fire
  years" note says "a sensitivity analysis excludes them", while
  "Execution details" (2026-10-07) keeps the rows in regressions.
- **Actual:** the second fix review (2026-10-07, findings 1, 2, 8, 9) found
  each open or in conflict. Owner chose: ONI's own strong set and band;
  the parent test's regions, two-sided, uncorrected; leave-one-year-out
  coverage also for the two H6 models; a dated pointer from the zero-fire
  note to "Execution details".
- **Why:** see `DECISIONS.md` 2026-10-07 "Second fix review settled".
- **Recorded:** `DECISIONS.md` 2026-10-07 "Second fix review settled".
- **Plan doc:** updated before the freeze, each spot marked D53: the
  "Zero-fire years" note, Headline methods 4, and "Execution details"
  (strong-only results, ONI robustness runs, opening line).

### D52 · Plan clarifications from the fix review
- **Plan:** `ANALYSIS_PLAN.md` (after D49-D51): "PET and SPEI follow the
  SPEI reference implementation"; one-sided permutation p as "the share of
  permuted differences"; zero-fire indicators "equal those of a fit without
  those years"; one near-threshold "sensitivity run"; "every headline test
  re-run on ONI" (ENSO index note).
- **Actual:** the fix review (2026-10-07, F4, F5) found each open to a
  stranger's reading: the R package's default fit and heat index differ
  from the project's; the code counts (count + 1) / (n + 1); HAC and
  Driscoll-Kraay standard errors are not those of a dropped fit; joint or
  separate flips; headline methods or every test. Owner chose: the fit
  stays ML with 1951-2020; (count + 1) / (n + 1); the standard-error
  difference stated and accepted; one joint flip; ONI for every test that
  uses the ENSO index.
- **Why:** see `DECISIONS.md` 2026-10-07 "Fix review findings settled".
- **Recorded:** `DECISIONS.md` 2026-10-07 "Fix review findings settled".
- **Plan doc:** updated before the freeze: the "SPEI settings" 2026-10-07
  note and "Execution details" (one-sided tests, zero-fire sensitivity,
  strong-only results, a new ONI robustness bullet) and a dated scope note
  under the ENSO-index item, each marked D52.

### D51 · Phase 4 gains a pre-results audit gate
- **Plan:** `ACTION_PLAN.md` Phase 4: "Before starting", confirm the freeze
  commit and set up the Claude Code Project; "All functions are in
  `src/stats.py`, tested on synthetic data with known effects". No review
  step between building the statistics code and running it on fire data.
- **Actual:** the pre-freeze audit (2026-10-07, Info) found that none of
  the inference the plan specifies beyond the basics exists in code yet
  (one-sided p, `use_t`, Driscoll-Kraay, expanding window, the contrast),
  and `temp_jja`, `temp_mam`, `precip_anom` are unbuilt; all of it will be
  written after fire data exists. Owner chose a gate: each piece built and
  tested on synthetic data, then a read-only audit with a neutral prompt,
  before anything runs on the fire table.
- **Why:** code written after the outcomes exist is where an error could
  meet the results unseen; an audit before the first run keeps the
  pre-registration's protection.
- **Recorded:** `DECISIONS.md` 2026-10-07 "Pre-freeze audit findings
  settled".
- **Substantial:** yes (owner, 2026-10-07).
- **Plan doc:** updated, the changed spot marked `[mid-project: D51]`:
  `ACTION_PLAN.md` Phase 4, after "Before starting". Phase 4's stale
  "ONI strength" and "ONI × region" stay as written (D41).

### D50 · Zero-fire sensitivity by indicators; execution details completed; trend-only baseline; precedence sentence
- **Plan:** `ANALYSIS_PLAN.md` "Execution details" (2026-10-06): the
  zero-fire sensitivity covers every burned-area test "without the zero
  years", while HAC series "must be contiguous runs of years"; one-sided
  regression p "for the coefficient's sign"; the forecast's 80% intervals,
  the expanding-window error and "the H6 models", the H4 Wald test's
  distribution, glacier cells in `temp_jja`, `temp_mam`, `precip_anom`, and
  the scope of strong-only results unstated; "α = 0.05 after correction"
  did not name the deciding correction. No rule said which text wins
  where stale passages contradict decided notes.
- **Actual:** the pre-freeze audit (2026-10-07, P1-P3) found the plan could
  not be run as written (dropping zero years leaves gaps that
  `fit_ols_hac` refuses) and six choices still open. Owner chose
  per-year indicators in the regressions (permutation tests drop the
  years), the six answers in `DECISIONS.md`, and a precedence sentence in
  the owner's wording under "Frozen on". Scope addition (owner, same
  day): a trend-only baseline and skill score in the expanding-window
  validation, descriptive.
- **Why:** see `DECISIONS.md` 2026-10-07 "Pre-freeze audit findings
  settled".
- **Recorded:** `DECISIONS.md` 2026-10-07 "Pre-freeze audit findings
  settled".
- **Plan doc:** updated before the freeze: "Execution details" (dated
  2026-10-07 in its opening line, the zero-fire bullet and the
  trend-only baseline), a dated
  clarification under "Correction families" (Holm decides) and the
  precedence sentence. The stale passages stay as written (owner's prose).

### D49 · SPEI as in the reference implementation: summed amounts, 0.01792, no hot-range table
- **Plan:** `ANALYSIS_PLAN.md` "SPEI settings" (revised 2026-10-06, D47):
  "Thornthwaite (1948) as published"; `docs/data_dictionary.md`: monthly
  P - PET "summed over 3 months".
- **Actual:** the code averaged daily rates over 3 months (February counted
  as a full month), used xclim's exponent constant 0.01791 instead of
  0.01792, and extended the power law above 26.5 °C, where Thornthwaite
  (1948) used a separate table (pre-freeze audit 2026-10-07, P5, P6). The
  R package SPEI, the index's reference implementation, sums monthly
  amounts, uses 0.01792 and has no hot-range table. Owner chose to follow
  it; both domains refit.
- **Why:** see `DECISIONS.md` 2026-10-07 "Pre-freeze audit findings
  settled".
- **Recorded:** `DECISIONS.md` 2026-10-07 "Pre-freeze audit findings
  settled".
- **Plan doc:** `ANALYSIS_PLAN.md` "SPEI settings" carries a dated
  2026-10-07 revision note (before the freeze); data dictionary updated.

## 2026-10-06 (gate)

### D48 · More stale plan wording; D43's CLAUDE.md claim no longer true
- **Plan:** `ANALYSIS_PLAN.md` Hypotheses table, H4 "index × region
  interaction ≠ 0"; Supporting methods, H5 "lag0 = the preceding winter and
  lag1 = the winter before that"; Data and years, "Climate tests
  (precipitation, temperature, whiplash, SWE)". D43's *Plan doc* line says
  `CLAUDE.md` was "left as written".
- **Actual:** H4's test is one north-vs-SoCal contrast (D45, "H4's actual
  test"); H5's lags are Oct-Mar totals, not winters (DJF); whiplash and
  temperature are not tested (descriptive and a control). `CLAUDE.md`'s
  fire-window line was updated with the owner's yes in 5386222, after D43
  was written. Found by the plan-versus-config re-audit (2026-10-06).
- **Why:** pre-freeze decisions superseded the owner's original wording.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Hypotheses", "Inference", "H1
  months and the CLAUDE.md fire window".
- **Plan doc:** left as written (owner's prose); the decided notes and
  "Execution details" resolve each spot.

### D47 · Thornthwaite PET with a climatological heat index; glacier cells out of SPEI
- **Plan:** `ANALYSIS_PLAN.md` "SPEI settings" (decided 2026-10-04):
  "Thornthwaite (1948) PET", implemented as xclim's TW48; SPEI over every
  region land cell.
- **Actual:** the pre-freeze re-audit and the independent audit (2026-10-06)
  found xclim's TW48 recomputes the heat index per calendar year (inflating
  PET in the incomplete current year and in the 2027 forecast input, giving
  NaN in years with no month above 0 °C, damping the warming response) and
  omits the N/30 factor. The owner chose Thornthwaite's own form: a
  climatological heat index from 1951-2020, N/30 included, PET 0 at or below
  0 °C; and glacier cells left out of SPEI as of SWE. Every SPEI and
  whiplash value was refit (both domains); changes in `DECISIONS.md`.
- **Why:** see `DECISIONS.md` 2026-10-06 "PET heat index".
- **Recorded:** `DECISIONS.md` 2026-10-06 "PET heat index".
- **Plan doc:** `ANALYSIS_PLAN.md` "SPEI settings" carries a dated revision
  note (before the freeze); `src/config.py` `PET_HEAT_INDEX_YEARS`,
  `GLACIER_SPEI_EXCLUDED`.

### D46 · Tracker from October; California verification after January 2028
- **Plan:** `ACTION_PLAN.md` "Second goal": Live 2026-27 tracker *Nov 2026 →
  spring 2027*, and (D44) a November-April season timeline; Verification
  panel *Fall 2027*.
- **Actual:** the timeline runs October-April. H5's `precip_anom` as the
  October-March total was decided before the freeze (DECISIONS.md
  2026-10-05 "Hypotheses"), so October 2026 is an input and its data,
  expected in early November, is the first the page waits for. The California fire windows now run June
  to January of Y+1 (D43), so the 2027 season can be verified in fall 2027
  for PNW, BC, AB, AK and YT, but for NorCal and SoCal only after January
  2028. The private mockup was updated to match (version 2).
- **Why:** follows from two pre-freeze decisions (H5's months, D43);
  D44's November start predates them.
- **Recorded:** `DECISIONS.md` 2026-10-06 "Tracker window and verification
  dates follow the pre-freeze decisions".
- **Substantial:** yes, as a correction to D44's plan edit (owner,
  2026-10-06).
- **Plan doc:** updated, each changed spot marked `[mid-project: D46]`:
  `ACTION_PLAN.md` "Second goal", the tracker's time span and timeline
  months, and the Verification panel's timing. D44 is left as written.

## 2026-10-05 (gate)

### D45 · H4 errors Driscoll-Kraay, not clustered by year
- **Plan:** `ANALYSIS_PLAN.md` "Headline methods" 3: the H4 pooled model
  with "errors clustered by year (`fit_pooled`)".
- **Actual:** owner chose Driscoll-Kraay errors (maxlags 2) as H4's primary
  errors, year-clustered reported alongside, and `use_t=True` in every fit
  (2026-10-05, pre-freeze item "Small-cluster corrections").
- **Why:** see `DECISIONS.md` 2026-10-05 "Inference".
- **Recorded:** `DECISIONS.md` 2026-10-05 "Inference".
- **Plan doc:** pre-freeze item filled in; "Headline methods" 3 left as
  written (owner's prose), stale: H4's primary errors are Driscoll-Kraay.

### D44 · Scope: live tracker becomes a three-state season timeline page
- **Plan:** `ACTION_PLAN.md` "Second goal", Live 2026-27 tracker: this
  winter's precipitation and snowpack against all past winters, updated
  monthly, *Nov 2026 → spring 2027*. Nothing before November, and the
  tracker and the results were separate pieces.
- **Actual:** one page in three states at one URL. Before winter, a
  November-April timeline with a countdown to the first month of data and
  the freeze date; while tracking, region × month tiles that fill in as data
  arrives, with a countdown to the April 1 snowpack; at the end, the
  countdown goes and the page becomes the results page, keeping the
  timeline as the record that the forecast came before the season.
  Countdowns target expected data arrival and run in the browser; the state
  comes from `results/`; the dates go in `src/config.py` (added by the main
  session after the freeze). A private mockup of the three states was
  published for review.
- **Why:** owner's idea, 2026-10-05: if the build finishes before November,
  the site can go public with a reason to come back, and the timeline then
  carries over into the results.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Season timeline page for the live
  tracker".
- **Substantial:** yes. The owner decided the scope change warrants editing
  the plan directly (2026-10-05).
- **Plan doc:** updated, the changed spot marked `[mid-project: D44]`:
  `ACTION_PLAN.md` "Second goal", Live 2026-27 tracker bullet. The "Done
  when" line is left as written (the tracker is still the fourth piece).

### D43 · Fire windows: California through January, BC from April
- **Plan:** `ANALYSIS_PLAN.md` "Outcomes" and `ACTION_PLAN.md` Phase 3:
  June-October for US regions and BC, April-October for Alberta,
  April-September for Alaska and Yukon (provisional); `CLAUDE.md`
  measurement rules say the same; the pre-freeze item suggested California
  through December.
- **Actual:** owner chose NorCal and SoCal June to January of the next year,
  BC April-October, AK and YT April-September confirmed (2026-10-05, before
  any fire data).
- **Why:** see `DECISIONS.md` 2026-10-05 "Data rules".
- **Recorded:** `DECISIONS.md` 2026-10-05 "Data rules".
- **Plan doc:** `ANALYSIS_PLAN.md` item filled in; its "Fire season" line
  under Outcomes, `ACTION_PLAN.md` Phase 3 and `CLAUDE.md` "Fire-season
  window" left as written, stale (owner's prose; `CLAUDE.md` wording
  proposed to the owner).

### D42 · H6 added; whiplash and season length descriptive; H2 and H5 wording stale
- **Plan:** `ANALYSIS_PLAN.md` Hypotheses has H1-H5, with H2 "higher in
  SoCal" and H5 "positive lag coefficient, strongest in SoCal";
  "Outcomes" lists fire-season length as an outcome; `ACTION_PLAN.md`
  Phase 2 builds whiplash as the project's core index and Phase 4 runs a
  "lag test for the whiplash mechanism".
- **Actual (owner, 2026-10-05, pre-freeze items):** H6 added (burned area
  on April 1 SWE z and on winter SPEI-3); whiplash, season length,
  snowfall fraction and soil moisture are descriptive only; SoCal H2 is
  two-sided; H5's expected signs differ by region (north lag0 negative,
  SoCal lag1 positive); AK and YT tested on H2 and H3 only, two-sided.
- **Why:** see `DECISIONS.md` 2026-10-05 "Hypotheses".
- **Recorded:** `DECISIONS.md` 2026-10-05 "Hypotheses".
- **Plan doc:** `ANALYSIS_PLAN.md` items filled in, an H6 row and a
  "Directions and sidedness" table added; the H2 and H5 rows of the
  hypotheses table and "Fire-season length" under Outcomes left as written
  (owner's prose), stale: SoCal H2 is two-sided, H5's signs are per region,
  season length is descriptive. `ACTION_PLAN.md` left as written.
  `docs/prefreeze_options.md` numbers are ONI-based (stale under RONI).

### D41 · ENSO index RONI; plan wording still names ONI
- **Plan:** `ANALYSIS_PLAN.md` left ONI or RONI to the freeze (recommended
  RONI); `ACTION_PLAN.md` Phase 4 says "burned area on ONI strength" and
  "ONI × region"; Session 0 calls the ONI list provisional until the choice;
  the project ran on ONI through Phase 2.
- **Actual:** RONI chosen (owner, 2026-10-05), ONI as the robustness check.
  Committed tables and figures rebuilt with RONI; figure files renamed from
  `*_oni.png` to `*_roni.png`. Fire record: 14 El Niño winters either way,
  strong 4 (ONI) to 3 (RONI), neutral 13 to 9.
- **Why:** see `DECISIONS.md` 2026-10-05 "ENSO index: RONI".
- **Recorded:** `DECISIONS.md` 2026-10-05 "ENSO index: RONI".
- **Plan doc:** `ANALYSIS_PLAN.md` item filled in; `ACTION_PLAN.md`'s
  "ONI strength" and "ONI × region" wording left as written (owner's prose),
  stale: the index is RONI.

## 2026-10-05 (Phase 2)

### D40 · Side-session deviation numbers given at merge
- **Plan:** `docs/session3_kickoff.md` and `docs/session4_kickoff.md` split
  the D numbers into agreed ranges per session (session 3: main D36-D39,
  side session D40 onward), with a new split agreed at each session start.
- **Actual:** side sessions no longer pick a number. A new entry is titled
  with a placeholder (D\?a, D\?b...), and `scripts/merge_append_only.py`
  gives it the next free number when main is merged into the PR (merge-side-pr
  step 5), rewriting every reference in the PR's files;
  `scripts/prescreen_prs.py` reports the numbers before approval. The main
  session numbers its own entries directly. This entry is the first to use
  the rule. Owner's decision, 2026-10-05, relayed by the main session.
- **Why:** ranges needed agreeing every session and a message whenever one
  ran out; numbering at merge can't clash and leaves no gaps.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Deviation numbers given at merge".
- **Plan doc:** `.claude/skills/merge-side-pr/SKILL.md` updated; the
  kickoff documents left as written; `CLAUDE.md` wording proposed in the PR
  for the main session to add.

### D39 · Data guide page refreshed at the end of every session
- **Plan:** `CLAUDE.md` "Required every session" names the daily log only;
  the data dictionary is the record of data types.
- **Actual:** the end of every main-checkout session also refreshes a
  private data guide artifact (data types, settings, headline numbers),
  owner's request 2026-10-05. `CLAUDE.md` gained the rule.
- **Why:** owner's request, to keep a readable overview of the whole data
  set current.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Data guide page, refreshed every
  session".
- **Plan doc:** `CLAUDE.md` updated; `ACTION_PLAN.md` left as written.

### D38 · Climate change and compounding added as a pre-freeze item
- **Plan:** `ANALYSIS_PLAN.md` "Data and years" handles the trend for
  burned area only (a `year` term; `burn_detr`); `ACTION_PLAN.md` "Later
  extensions" has CMIP6 long-term trends but no historical test of whether
  El Niño's effects change as the climate warms.
- **Actual:** owner asked (2026-10-05, session 3) to mark the compounding
  effect of climate change for analysis. Added a pre-freeze item "Trend and
  climate change" (trend handling for the climate variables; an El Niño ×
  time test, pre-registered or exploratory) and a "Compounding with climate
  change" bullet under Later extensions.
- **Why:** the station check found the PNW strong-winter snowpack loss
  concentrated at low and mid elevations (low third -42, high third +3
  points of normal), where warming acts first; the choice has to be made
  before the freeze to count as pre-registered.
- **Substantial:** yes (owner's choice); both plans edited with the marker
  `[mid-project: D38]`.
- **Recorded:** this entry; the decision itself is open.
- **Plan doc:** `ANALYSIS_PLAN.md` and `ACTION_PLAN.md` updated.

### D37 · Station SWE index starts 1960-1975 in the north and ends 2025 in Alberta
- **Plan:** `ANALYSIS_PLAN.md` "Data and years": climate tests including
  SWE use "winters 1950–51 to present".
- **Actual (measured with the cleaning rules, 2026-10-05):** with normals
  from 1991-2020 (20 or more values) and at least 5 stations per
  region-year, the station index starts PNW and BC 1951, AK 1960, AB 1963,
  YT 1975, and Alberta ends 2025 (CanSWE ends July 2025). Makes D31's
  network histories concrete for the index; ERA5-Land April 1 SWE still
  covers 1951-2026 everywhere. Of the 7 strong El Niño winters, AB lacks
  1957-58 and YT lacks 1957-58 and 1972-73.
- **Why:** network histories (D31) and the owner's minimum of 5 stations,
  which the owner may widen for AB and YT.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Regional station index".
- **Plan doc:** left as written (owner's prose; the SWE source is still a
  pre-freeze item).

### D36 · Station networks beyond the plan's list
- **Plan:** `ACTION_PLAN.md` Phase 2: "SNOTEL (WA/OR/ID), BC and Alberta
  snow surveys; Alaska SNOTEL and Yukon snow surveys".
- **Actual:** the station table also holds NRCS manual snow courses (WA,
  OR, ID, AK; the pre-1980 record), BC, Alberta and Yukon snow pillows from
  CanSWE, and stations assigned by location whatever their network (15
  BC-run courses in WA and ID count for PNW; Yukon network sites outside
  Yukon dropped). 71,759 station-years, 2,180 stations.
- **Why:** SNOTEL starts about 1980, so snow courses carry 1950-79; pillows
  give exact-date readings; owner's cleaning choices.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Station snowpack cleaning rules".
- **Plan doc:** left as written.

### D35 · Read-only rules audits at phase boundaries
- **Plan:** `ACTION_PLAN.md` has no code audits; review happens per PR in
  `merge-side-pr` (`/code-review low` for changes under `src/`).
- **Actual:** a side session audits the code against `CLAUDE.md`, the data
  dictionary and `ANALYSIS_PLAN.md` at each phase boundary, read-only, with
  a dated report in `docs/`. First run 2026-10-05 on Phase 1 (`9e5f73a`):
  7 findings, 3 fixed in `stats.py`, 4 sent to the main session.
- **Why:** per-PR review sees one change at a time; rule breaks that build
  up across a phase, and silent wrong answers on unusual input, need a
  whole-codebase pass.
- **Recorded:** `DECISIONS.md` 2026-10-05 "Phase 1 audit";
  `docs/audit_2026-10-05_phase1.md`.
- **Plan doc:** left as written. Numbered D35 because main uses D27-D31.

## 2026-10-04 (Phase 2)

### D31 · Station snowpack records start well after 1950
- **Plan:** `ANALYSIS_PLAN.md` "Data and years": climate tests including
  SWE use "winters 1950–51 to present"; `ACTION_PLAN.md` Phase 2 lists the
  station networks without start years.
- **Actual (licence reads, 2026-10-04):** Yukon April SWE starts 1960 but
  has 1-7 courses a year until about 1975; Alaska snow courses start 1951
  with 9 by 1960; SNOTEL pillows start 1978 (WA, OR, ID: 165 sites by
  1985). WA, OR and ID snow courses do reach back (282 begun by 1950, 75
  spanning 1950-2020); BC manual courses run from 1935 (127 with 50 or more
  April 1 values since 1950). Gridded ERA5-Land April 1 SWE covers 1950-2026
  everywhere.
- **Why:** network histories.
- **Plan doc:** left as written (owner's prose; the SWE source and
  definition is still a pre-freeze item).

### D30 · Alberta station snowpack from CanSWE, not Alberta's portal
- **Plan:** `ACTION_PLAN.md` Phase 2 ("BC and Alberta snow surveys");
  `DATA_SOURCES.md` placeholder row with endpoint https://rivers.alberta.ca/.
- **Actual:** Alberta's portal publishes no data licence (website terms
  allow only unmodified, non-commercial copies; historical records by email
  request), verdict AMBIGUOUS. Alberta station data is to come from CanSWE v8
  (Zenodo, Open Government Licence - Canada), which includes about 107
  Alberta manual snow courses and pillows but ends July 2025. Download
  approved by the owner the same session.
- **Why:** owner's choice; emailing the publisher is a last resort.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Station snowpack sources and
  table licensing"; `DATA_SOURCES.md` CanSWE and Alberta rows.
- **Plan doc:** `DATA_SOURCES.md` updated; `ACTION_PLAN.md` left as
  written.

### D29 · Methods register added
- **Plan:** `CLAUDE.md` and `ACTION_PLAN.md` Phase 4 ("Write the Methods
  and limitations section as you go") name no record of controls; units and
  traps sit in `docs/data_dictionary.md`, reasoning in `DECISIONS.md`.
- **Actual:** `docs/methods_register.md` lists every control, cap, filter,
  threshold and data-handling rule with value, code location, reason,
  measured effect and status; back-filled from Session 0 and Phase 1 work
  the same day (about 70 rows). `CLAUDE.md` gained a line requiring it to be
  kept current.
- **Why:** owner's request, so the methods section can be written from it.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Methods register".
- **Plan doc:** `CLAUDE.md` updated; `ACTION_PLAN.md` left as written.

### D28 · Map extent hard-coded; map period worded two ways
- **Plan:** `CLAUDE.md` "Single source of truth": every tunable value
  (including domain) lives in `src/config.py`.
- **Actual:** found by the methods-register sweep. `src/figures.py:116`
  hard-codes the 1997-98 map extent as (-169, -109, 32, 71.5) instead of
  deriving it from `ERA5_DOMAINS`; the values match the two domains today.
  The same map's title (notebook 01, cell 10) says "% of the 1950-2026
  mean" while its colourbar (`src/figures.py:151`) says "1950-51 to
  2025-26"; the colourbar is the precise one (76 winters).
- **Why:** written in Phase 1 before the north domain settled.
- **Plan doc:** left as written; flagged to the owner, not fixed (outside
  Phase 2 scope).

### D27 · Glacier exclusion adds a perennial-snow rule
- **Plan:** `ACTION_PLAN.md` Phase 2 and `ANALYSIS_PLAN.md` "SWE source and
  definition": exclude glacier cells with the CDS glacier mask or by
  flagging cells at the 10 m cap in every month.
- **Actual:** cells at the cap in any month, plus cells keeping more than
  10 mm of snow at the yearly minimum in at least 90% of 1950-2025, one
  fixed mask. The perennial rule catches 394 main-domain and 1,146 north
  cells that hold a steady ~5 m and never reach the cap; with the cap rule
  alone Alaska's mean April SWE stays at 417 mm instead of 229 mm.
- **Why:** measured 2026-10-04 before building; owner's choice.
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land SWE: glacier exclusion
  and April 1"; `docs/methods_register.md`.
- **Plan doc:** left as written (owner's prose); the chosen rule is in
  `src/config.py`.

## 2026-10-04 (Phase 1)

### D26 · Side PRs pre-screened as a merged queue
- **Plan:** `merge-side-pr` tested each PR head alone and asked for the
  owner's yes before main was merged in; `merge_append_only.py` ran only on
  conflicted files. `ACTION_PLAN.md` "Later tooling" has no merge tooling.
- **Actual:** `scripts/prescreen_prs.py` merges every queued PR in order onto
  current main and checks each before any approval; the skill now screens
  first, then reports or (with a yes for the run) merges, with a written
  stop rule. The merge script now runs after every merge, conflicts or not,
  after a replay showed a duplicate D19 passing a clean git merge.
- **Why:** what the owner approved was not what landed, and clashes between
  PRs went unseen.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Pre-screening side PRs".
- **Plan doc:** updated (`merge-side-pr`); `ACTION_PLAN.md` left as written.

### D20 · Scope: Alaska and Yukon added as regions
- **Plan:** five regions everywhere: `CLAUDE.md` ("PNW (WA/OR/ID), BC and
  Alberta, contrasted with NorCal and SoCal"), `ACTION_PLAN.md` Phase 1
  ("PNW, BC, AB, NorCal, SoCal"), `ANALYSIS_PLAN.md` "Data and years" and
  "Outcomes" (fire seasons for US regions, BC and AB only), `README.md`.
  One ERA5-Land domain, 32-60.5N x 140-109W.
- **Actual:** seven regions; AK and YT with role `north`, fire window
  Apr-Sep (provisional); second download domain 51-71.5N x 169-123.5W
  (77 more files, about 50 minutes). Hypotheses for them are a new
  pre-freeze item; H1-H5 as written don't mention them.
- **Why:** owner's decision after discussing the El Niño signal in Alaska.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Alaska and Yukon added".
- **Substantial:** yes. The owner decided the scope change warrants editing
  the plans directly (2026-10-04).
- **Plan doc:** updated, each changed spot marked `[mid-project: D20]`:
  `CLAUDE.md` (scope line, fire-season window), `README.md` (scope line,
  methods table), `ACTION_PLAN.md` (goal, Phase 1 regions and north
  download, Phase 2 snowpack stations, Phase 3 fire sources and windows),
  `ANALYSIS_PLAN.md` ("Data and years" regions, "Outcomes" fire season, plus
  the pre-freeze item). Hypotheses H1-H5 left as written: their AK/YT
  versions are a pre-freeze decision. Code: `config.py`, `regions.py`,
  `download_era5.py`, `era5.py`.

### D21 · First ERA5-Land download duration (corrects D10)
- **Plan:** D10 recorded the main-domain download as "about 50 minutes
  through the CDS queue".
- **Actual:** the CDS client log (`data/raw/era5_download.err.log`) runs
  from 17:05:27 to 18:06:56 on 2026-10-04: 61.5 minutes for 77 requests,
  about 48 s per year. The north-domain download (20:36:11 to 21:36:32) took
  60.3 minutes, about 47 s per year, for 288 MB.
- **Plan doc:** D10 left as written (entries are never edited); this entry
  supersedes its duration.

### D19 · El Niño winter drying in PNW and BC is weaker than assumed
- **Plan:** `ACTION_PLAN.md` Phase 1 sanity check ("SoCal winters stand out
  wet and the PNW/BC dry"); `docs/data_dictionary.md` section 1 ("the
  classic El Niño winter is dry and mild in the PNW, BC and Alberta").
- **Actual (descriptive, ONI, 76 winters):** directions as expected in all
  five regions, but the northern precipitation signal is small. El Niño
  minus neutral DJF precipitation: PNW -5.6% (-0.21 SD), BC -4.8%
  (-0.26 SD), AB -11.8% (-0.52 SD), NorCal +9.5% (+0.24 SD), SoCal +37.9%
  (+0.62 SD). The 7 strong El Niño winters are not drier than average in
  PNW (-0.3%) or BC (+0.5%); AB -14.9%. Alaska and Yukon (added the same
  day, D20): El Niño minus neutral AK -3.6% (-0.20 SD), YT -10.0%
  (-0.41 SD); strong winters AK -12.4% (-0.69 SD), YT -5.8%. Under RONI the
  El Niño minus
  neutral contrast roughly doubles in PNW (-10.7%) and SoCal (+62.9%),
  mostly because the neutral group changes, not the El Niño group.
- **Why:** not yet known; the data dictionary's mechanism also runs through
  temperature (warm winters, rain instead of snow), which DJF precipitation
  alone doesn't capture. Phase 2 SWE and snowfall fraction test that path.
- **Plan doc:** left as written (owner's prose); flagged.

### D18 · Cartopy map layers from Natural Earth 50m
- **Plan:** `DATA_SOURCES.md`: every dataset gets a ledger row before use.
- **Actual:** the 1997-98 map's ocean, country borders and state lines are
  Natural Earth 1:50m layers that cartopy downloaded on first use
  (`ne_50m_ocean`, `ne_50m_admin_0_boundary_lines_land`,
  `ne_50m_admin_1_states_provinces_lakes`). Same publisher and terms as the
  admin-1 file read the same day (public domain); ledger row added after the
  first run.
- **Plan doc:** `DATA_SOURCES.md` updated.

### D17 · ERA5 loading and unit conversion in `src/era5.py`
- **Plan:** `ACTION_PLAN.md` Phase 1: "Notebook `01_explore_era5.ipynb`:
  open the ERA5 files, convert units".
- **Actual:** loading, unit conversion, masks, DJF totals and the region x
  year table are plain functions in `src/era5.py` with 10 tests; the
  notebook imports them. `python -m src.era5` writes
  `data/processed/djf_precip_region_year.csv` (380 rows) without the
  notebook.
- **Why:** owner's Phase 1 brief; Phase 2 reuses the same loader.
- **Plan doc:** left as written.

## 2026-10-04 (Session 0)

### D25 · Site figures embedded through a Python cell, not an image link
- **Plan:** `site/index.qmd` skeleton comment: "figures come from
  ../results/", implying plain image links to `../results/`. The side
  session's brief: check rendering with `conda run ... quarto render site`.
- **Actual:** a plain link renders with exit 0 but Quarto does not copy files
  from outside `site/` into `_site/`, so the image breaks. Figures are now
  embedded with a hidden Python cell that reads `../results/figures/` at
  render time. In the worktree, `quarto render site` found 0 input files
  because the worktree path contains a dot folder (`.claude\`), which Quarto
  skips, and `conda run` printed nothing; the render was checked on a copy in
  a short temp path instead. The main checkout is not affected.
- **Why:** keeps `results/` as the only source and nothing copied by hand.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Mechanism diagram".
- **Plan doc:** left as written (the comment is still true: figures do come
  from `../results/`).

### D24 · Mechanism diagram content
- **Plan:** `ACTION_PLAN.md` "Second goal": "PNW/BC/AB dry → low snowpack →
  long or early season; SoCal wet → grass → big grass fires". No NorCal, no
  shared cause.
- **Actual:** adds the shared cause (warm central-eastern tropical Pacific,
  jet stream shift); the north chain starts "Milder winter, often drier",
  not "dry"; SoCal chain ends "larger grass fires" with no timing; NorCal
  (contrast) and AK and YT (north, added in D20) are named in a footnote
  with no pathway; an "Expected pathways, tested in this study" footer sits
  in the figure. Region labels are the `config.REGIONS` keys.
- **Why:** the SoCal lag and the NorCal, AK and YT expectations are open
  before the freeze, and Phase 1 found the El Niño winter drying small in
  PNW and BC (D19). Numbered D24-D25 because main uses D17-D21 and PRs #5
  and #3 D22-D23.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Mechanism diagram".
- **Plan doc:** left as written.

### D23 · Site render check added ahead of the "Later tooling" plan
- **Plan:** `ACTION_PLAN.md` "Later tooling" lists a published-numbers
  check, a pre-push hook running `scripts/check_all.py` ("worth it once
  there are three or more checks", after Phase 4) and a drift check. No
  site render check. `CLAUDE.md` "Checks" lists pytest and the em-dash
  check only.
- **Actual:** `scripts/check_site.py` added in Phase 1 and run from
  `merge-side-pr` for PRs touching the site. It is a third check, which meets
  the plan's stated threshold for the pre-push hook; the hook is not built
  (its plan date is after Phase 4). Numbered D23 because main uses D17-D21
  and PR #5 D22; PR #1 uses D24-D25.
- **Why:** two silent render failures (exit 0) found while building the
  mechanism diagram.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Site render check".
- **Plan doc:** left as written (`ACTION_PLAN.md`, `CLAUDE.md` "Checks").

### D22 · Append-only merge script added
- **Plan:** `merge-side-pr` step 5 resolved `DECISIONS.md` and
  `docs/plan_deviations.md` conflicts by hand; `ACTION_PLAN.md` "Later
  tooling" has no merge tooling.
- **Actual:** `scripts/merge_append_only.py` resolves both files and step 5
  runs it. Numbered D22 because main's Phase 1 work uses D17-D21; open PRs
  #3 and #1 use D23-D25.
- **Why:** every side-session PR conflicts with the others at the top of both
  files.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Append-only merge script".
- **Plan doc:** updated (`merge-side-pr` step 5); `ACTION_PLAN.md` left as
  written.

### D16 · Parallel worktree session before Phase 4
- **Plan:** `ACTION_PLAN.md` and `docs/claude_code_project_setup.md`
  assume one sequential local session until Phase 4.
- **Actual:** a second local session runs in a git worktree from Phase 1 for
  data-free tasks (mechanism diagram, methods-page notices), one branch and
  PR per task; worktree sessions don't edit `logs/`.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Side worktree session".
- **Plan doc:** updated (`CLAUDE.md` daily-log exception).

### D15 · ENSO index: RONI is now the official index
- **Plan:** `src/config.py` defaults to ONI with the RONI URL as a TODO;
  `ANALYSIS_PLAN.md` leaves the ONI/RONI choice to the freeze; the project
  was planned around ONI.
- **Actual:** the CPC ONI page states that per NWS Public Information
  Statement 26-05, RONI is used for official ENSO monitoring and prediction.
  RONI is published at `RONI.ascii.txt` in the same layout. Compared in
  memory on 2026-10-04: 17 of 76 winters (1950-51 to 2025-26) change class
  between the indices. 2023-24 drops from strong (ONI 1.84) to moderate
  (RONI 1.13), 2019-20 and 1987-88 drop out of El Niño, and 1990-91,
  1992-93 and 1953-54 join it. Fire record (1984+): 14 El Niño winters
  under either index, 4 strong under ONI, 3 under RONI. Mean RONI minus ONI:
  +0.23 for 1951-1980, +0.11 for 1981-2005, -0.29 for 2006-2026.
- **Why:** RONI subtracts the tropical-mean SST anomaly, removing the warming
  trend that makes recent ONI values run warm.
- **Recorded:** `DATA_SOURCES.md` (ONI/RONI row); choice still open in
  `ANALYSIS_PLAN.md`.
- **Plan doc:** `config.py` RONI URL filled; index choice not made.

### D14 · Licence regimes differ from the ledger's expectations
- **Plan:** `DATA_SOURCES.md` expected ONI to be public domain and ERA5-Land
  to need "a specific credit line" under Copernicus terms.
- **Actual:** ONI/RONI confirmed public domain, with three restrictions on
  claims and a 17 U.S.C. 403 notice for works made predominantly of NWS
  material. ERA5-Land is under CC-BY 4.0 (replaced the "Licence to use
  Copernicus Products" on 2 July 2025): catalogue citation, data citation,
  Copernicus attribution line with disclaimer, licence link and statement of
  changes. Both verdicts: PERMITTED WITH CONDITIONS. Neither allows "all
  rights reserved" over the source values themselves in committed tables.
- **Why:** `read-licence` skill run on both sources.
- **Recorded:** `DATA_SOURCES.md` ledger, notices 1-2, acts owed.
- **Plan doc:** updated.

### D13 · Snowfall and soil moisture added to Phase 2
- **Plan:** not in `ACTION_PLAN.md` or `ANALYSIS_PLAN.md`.
- **Actual:** separate ERA5-Land download (snowfall, volumetric soil water
  layers 1-2) added to Phase 2, descriptive unless the analysis plan adds
  them; new pre-freeze item.
- **Why:** rain-instead-of-snow mechanism; direct fuel-dryness measure.
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land variables".
- **Plan doc:** updated.

### D12 · Snowpack: gridded SWE added, with glacier and timing fixes
- **Plan:** `ACTION_PLAN.md` Phase 2: April 1 snowpack from station surveys
  only (SNOTEL, BC, Alberta).
- **Actual:** ERA5-Land SWE (`sd`) downloaded too. In 1950, 325 land cells
  (0.65%) sit at the 10 m glacier cap all year and raise the domain's April
  SWE from 233 to 283 mm, so Phase 2 needs a glacier exclusion; `sd` is a
  monthly mean, so April 1 must be approximated or fetched separately.
- **Why:** owner chose SWE before the first download (see D11).
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land variables".
- **Plan doc:** updated (`ACTION_PLAN.md` Phase 2; `ANALYSIS_PLAN.md`
  pre-freeze item "SWE source and definition").

### D11 · ERA5-Land variables: SWE added
- **Plan:** `src/config.py` and `ACTION_PLAN.md`: total precipitation and
  2 m temperature only.
- **Actual:** `snow_depth_water_equivalent` added before the first download.
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land variables".
- **Plan doc:** updated (`config.py`).

### D10 · ERA5-Land download size
- **Plan:** "roughly 0.5-1 GB" (`ACTION_PLAN.md` Session 0; `DECISIONS.md`
  2026-10-03 "Project scaffold").
- **Actual:** 275 MB for 77 files (1950-01 to 2026-07) with three
  variables, about 3.7 MB per year; about 50 minutes through the CDS queue.
- **Plan doc:** left as written (old `DECISIONS.md` entries are immutable;
  `ACTION_PLAN.md` wording is the owner's).

### D9 · El Niño winter counts
- **Plan:** "roughly 10 to 13" El Niño winters in the fire record "(1985+)"
  and "about 5 strong"; "about 20 or more" in the climate record
  (`ACTION_PLAN.md` Pitfalls; the 10 to 13 figure also in `README.md` and
  the opening of `ANALYSIS_PLAN.md`).
- **Actual (ONI, provisional):** 14 in the fire record, 4 strong; 25 in the
  climate record (1950-51 to 2025-26), 7 strong. Under RONI: 14, 3 strong;
  26 in the climate record.
- **Plan doc:** left as written (owner's prose); flagged.

### D8 · Fire-record start year wording
- **Plan:** `ACTION_PLAN.md` Pitfalls says the fire record is "1985+";
  `src/config.py` sets `FIRE_FIRST_YEAR = 1984`.
- **Actual:** an inconsistency between planning docs, not with reality. The
  counts in D9 are the same either way (winter 1983-84 was La Niña, ONI
  -0.63).
- **Plan doc:** left as written; flagged.

### D7 · ERA5-Land licence step
- **Plan:** `README.md` step 3: "open the ERA5-Land monthly dataset page
  once and accept its licence"; `ACTION_PLAN.md` Session 0: "accept the
  ERA5-Land licence on the dataset page".
- **Actual:** the site terms accepted at registration were taken for the
  dataset licence. The first run sent 77 requests and got 77 HTTP 403s
  ("required licences not accepted"). The fix is the CC-BY licence in the
  "Terms of use" box at the bottom of the dataset's Download tab.
- **Why:** the instruction doesn't say where on the page the licence is or
  that it differs from the account terms.
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land variables" (downloader
  now stops at the first 401/403).
- **Plan doc:** left as written; flagged (README could name the Download
  tab's "Terms of use" box).

### D6 · Downloader error handling
- **Plan:** scaffold `src/download_era5.py` treated every error as
  "month not yet published" and moved on to the next year.
- **Actual:** stops at the first HTTP 401/403; three new tests.
- **Recorded:** `DECISIONS.md` 2026-10-04 "ERA5-Land variables".
- **Plan doc:** code updated.

### D5 · Region x year tables: committed copy
- **Plan:** `CLAUDE.md` scope guard: tables in `data/processed/` (never
  committed).
- **Actual:** the same code also writes a committed copy to
  `results/tables/`, after a licence read for every source behind it.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Working setup".
- **Plan doc:** updated (`CLAUDE.md`, `ACTION_PLAN.md` Phase 2 and 3).

### D4 · Claude Code Project (new; deferred to Phase 4)
- **Plan:** no mention.
- **Actual:** a Claude Code Project was created and put on standby until the
  start of Phase 4; checklist and draft instructions in
  `docs/claude_code_project_setup.md`.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Working setup".
- **Plan doc:** updated (`ACTION_PLAN.md` freeze gate and Phase 4).

### D3 · claude.ai project dropped
- **Plan:** `ACTION_PLAN.md` Session 0: paste `PROJECT_INSTRUCTIONS.md`
  into a claude.ai project; `CLAUDE.md`: that file "mirrors this context for
  the claude.ai project".
- **Actual:** all work in local Claude Code; `PROJECT_INSTRUCTIONS.md`
  deleted and its references removed, including from `LICENSE-CONTENT`.
- **Recorded:** `DECISIONS.md` 2026-10-04 "Working setup".
- **Plan doc:** updated.

### D2 · Commands run from Claude Code, not the Miniforge Prompt
- **Plan:** `README.md` step 2 and `ACTION_PLAN.md` Session 0: open the
  Miniforge Prompt and `conda activate whiplash`.
- **Actual:** Claude Code runs every project command through
  `C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash`; the
  Miniforge Prompt is optional. Miniforge is not on PATH outside it.
- **Why:** owner's preference (2026-10-04).
- **Recorded:** Claude Code memory; `logs/2026-10-04.md`.
- **Plan doc:** left as written (still valid for manual use).

### D1 · Session 0 duration
- **Plan:** `ACTION_PLAN.md`: "Session 0 - Setup (tomorrow, ~1-2 hours)".
- **Actual:** Claude Code 16:04-18:10 (about 2.1 hours), of which about 1
  hour was the ERA5 download and the licence fix; Copernicus registration
  ran in parallel.
- **Plan doc:** left as written ("tomorrow" is now stale).
