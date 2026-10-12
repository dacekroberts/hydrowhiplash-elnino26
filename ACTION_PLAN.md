# Action Plan: hydrowhiplash-elnino26

Goal: estimate how the 2026–27 strong El Niño is likely to shape the **2027 fire
season** in the Pacific Northwest, BC and Alberta, plus Alaska and Yukon
[mid-project: D20], contrasted with Northern and
Southern California.

**Analysis principle:** every step runs on the **full record** (climate 1950–present, fire 1984–present),
with **El Niño years highlighted** on top of it. The other years aren't thrown
away; they're the baseline that shows whether El Niño years actually stand out.

**Required every session:** a daily log in `logs/YYYY-MM-DD.md` (template in
`logs/_TEMPLATE.md`; Claude Code writes it with the `daily-log` skill). One file
per day, sessions appended in order. Pull them into your catalogue with
`python scripts/log.py export`.

Timeline assumes about 10 hours a week. Each phase ends with a concrete
deliverable so you always know when you're done.

---

## Session 0 — Setup (tomorrow, ~1–2 hours)

- [x] Install **Miniforge** for Windows (https://github.com/conda-forge/miniforge)
      and open the **Miniforge Prompt**
- [x] `mamba env create -f environment.yml`, then `conda activate whiplash`
- [x] Create a **private** GitHub repo named `hydrowhiplash-elnino26` and push
      these starter files
- [x] Register for a **Copernicus Climate Data Store** account
      (https://cds.climate.copernicus.eu), accept the ERA5-Land licence on the
      dataset page, and create `C:\Users\<you>\.cdsapirc` (see README)
- [x] `git init`, commit the starter files, and push to the private GitHub
      repo. The freeze gate relies on dated commits, so commit from day one.
- [x] Run `python -m src.download_oni` and review the winters it lists. This
      list is **provisional**: final analog years are locked at the freeze
      gate, after the ONI vs RONI choice.
- [x] Start `python -m src.download_era5` (1950–present, roughly 0.5–1 GB of
      monthly data; one file per year, so it can run in the background and
      be resumed)
- [x] `python scripts/log.py new` to start the day's log, then end the session
      by filling it in (the 2026-10-03 log shows the format)

**Done when:** the environment works, the ONI table is saved, and ERA5 is downloading.

## Phase 1 — Regions & climate data (week 1)

- [x] `python -m src.regions` to build the region polygons
      (PNW, BC, AB, NorCal, SoCal; AK and YT added [mid-project: D20])
- [x] Download the north ERA5-Land domain (Alaska and Yukon, 51-71.5N x
      169-123.5W) with `python -m src.download_era5 north` [mid-project: D20]
- [x] Notebook `01_explore_era5.ipynb`: open the ERA5 files, convert units
      (see `download_era5.py`), and plot regional winter (DJF) precipitation
      as a **full time series, 1950–present, with El Niño winters marked**
      (strong ones emphasised)
- [x] Map winter precipitation for one strong El Niño winter (1997–98)
      against the all-years average
- [x] Sanity check: do SoCal winters stand out wet and the PNW/BC dry in the
      highlighted years? If not, check units and dates before going further.

**Done when:** you have the highlighted time series per region and a map of
the El Niño precipitation dipole.

## Phase 2 — Whiplash index (week 2)

- [x] `src/whiplash.py`: compute PET (Thornthwaite to start) and **SPEI-3**
      with `xclim`, then whiplash = SPEI-3(JJA) − SPEI-3(preceding DJF)
      for **every year**
- [x] Average by region to get one time series per region per year
- [x] Add April 1 snowpack: SNOTEL (WA/OR/ID), BC and Alberta snow surveys;
      Alaska SNOTEL and Yukon snow surveys [mid-project: D20]
- [x] Gridded snowpack from ERA5-Land SWE (`sd`, already downloaded), with
      two fixes before any regional mean:
      - **Exclude glacier cells.** ERA5-Land holds glacier ice at a 10 m
        water-equivalent cap. In 1950, 325 cells (0.65% of land, Coast
        Mountains and Alaska panhandle) raised the domain's April SWE from
        233 to 283 mm. Use the CDS glacier mask (Invariant variables) or
        flag cells at the cap in every month.
      - **April 1, not April mean.** `sd` is a monthly mean centred
        mid-month, after melt has begun at low elevations. Approximate
        April 1 from the March and April means, or download the April 1
        00:00 field from hourly ERA5-Land (77 time steps).
- [x] Download ERA5-Land **snowfall** and **volumetric soil water layers 1-2**
      (0-28 cm) to their own folder (the three-variable download is
      about 3.7 MB per year, so this is cheap). Snowfall over total precipitation shows how much
      of a warm El Niño winter fell as rain, explaining low snowpack beyond
      the precipitation deficit; summer soil moisture is a direct
      fuel-dryness measure alongside SPEI. Descriptive unless
      `ANALYSIS_PLAN.md` adds them before the freeze.
- [x] Plot whiplash and SWE as full time series with El Niño years highlighted

**Done when:** you have a table of regions × all years with whiplash, SWE and
the ENSO phase label for each year, saved in `data/processed/` with a
committed copy in `results/tables/`.

## Gate — freeze the analysis plan (end of week 2)

- [x] Fill in and commit `ANALYSIS_PLAN.md` (including the ONI/RONI choice)
      **before any fire data is downloaded or opened.** Climate data can be
      looked at freely; the fire outcomes can't, or the tests could end up
      chosen after seeing results. The dated commit is the proof.
- [x] Consider setting up the Claude Code Project here. First commit
      analysis-ready tables to `results/tables/`; checklist in
      `docs/claude_code_project_setup.md`.

## Phase 3 — Fire data (week 3)

- [x] Download US fire perimeters (MTBS for 1984 to about 2 years ago,
      NIFC/WFIGS for recent years) and Canadian perimeters (CNFDB) for BC and AB;
      MTBS/WFIGS for Alaska and CNFDB for Yukon [mid-project: D20]
- [x] Clip to regions and compute **area burned** and **season length**
      (first to last fire date) for every year, counting only fires ≥ 405 ha
      in all regions so US and Canadian records match: June–October for US
      regions and BC, **April–October for Alberta**, April–September for
      Alaska and Yukon (provisional) [mid-project: D20]
- [x] Record dataset versions in `DATA_SOURCES.md`

Done 2026-10-07 (session 6): `src/download_mtbs.py`, `src/download_wfigs.py`,
`src/download_cnfdb.py`, `src/fire.py`; MTBS through 2023, WFIGS from 2024
[mid-project: D61]; `results/tables/fire_region_year.csv` (291 rows).

**Done when:** you have a table of regions × all years with area burned,
season length and ENSO phase, saved in `data/processed/` with a committed
copy in `results/tables/`.

## Phase 4 — Historical analysis with inferential statistics (weeks 4–6)

**Before starting:** confirm `ANALYSIS_PLAN.md` was committed at the gate,
before Phase 3. Any change since then goes in its deviations log. Then set up
the Claude Code Project (on standby since 2026-10-04) using
`docs/claude_code_project_setup.md`, so H1-H5 and the site pages can run as
parallel threads. [mid-project: D78] Decided 2026-10-11: the registered
runs and the runs reported beside them are made by one runner in the main
checkout, not in Project threads; the Project is taken up again for site
pages after the runs.

**Pre-results audit gate** [mid-project: D51]: every piece of statistics
code the plan needs but `src/stats.py` lacks at the freeze (one-sided
p-values, `use_t`, Driscoll-Kraay errors with df = years - 1, the H4
contrast and its F test, expanding-window validation, zero-fire indicators,
the Holm/BH family runner) and every variable not yet built (`temp_jja`,
`temp_mam`, `precip_anom`) is built and tested on synthetic data with known
answers first, then checked by a read-only audit with a neutral prompt,
before any of it runs on the fire table. No hypothesis result is computed
until that audit's findings are settled. The audit runs in rounds: each
round's findings are settled and fixed, then a fresh cold read-only review
covers the fixes and the whole gate, until a round finds nothing high and
the owner agrees [mid-project: D64]. The same audit also reviews the
fire build (`src/fire.py`, the download scripts and
`results/tables/fire_region_year.csv`); until it closes, a fire record rule
changes only for a defect a check finds, logged with before-and-after
numbers, and after it, before the first test, only bug fixes. No view
that sets burned area beside ENSO until Phase 4 [mid-project: D62].

Gate code built 2026-10-08 (session 7): `src/stats.py`, `src/climate_vars.py`,
the frozen-rules fire table (`python -m src.fire --frozen-rules`) and input
pins (`src/pin_inputs.py`); small-sample correction on everywhere (D65).
Audit round 1 settled 2026-10-08 (D66); round 2 settled 2026-10-08 (D67,
D68); round 3 settled 2026-10-08 (D69, D70; Parks Canada check done);
round 4 settled 2026-10-08 (D71); round 5 settled 2026-10-08 (D72; no
high, no medium, 6 low). **Gate closed on round 5** (owner's standard: a
cold round with no high and no medium findings), tag
`pre-results-gate-closed`.

- [x] **Decide before the first hypothesis test (owner, 2026-10-08):** the
      exploratory NBAC re-run of the Canadian tests and the NOAA NCEI
      Interior Alaska check, each yes or no, logged in `DECISIONS.md`. No
      hypothesis test runs while either is open. Settled: Interior Alaska
      measured and reported (2026-10-11, D79); no NBAC re-run, the
      per-fire coverage split reported as a limitation (2026-10-12, D81).
- [x] **Registered runs committed by Friday 2026-11-06** [mid-project: D73]:
      the day before October's ERA5-Land data is expected
      (`TRACKER_DATA_DAY` 7), so the first tracker update cannot change a
      pinned input under the tests. If the date is missed, see the
      hard-line item in Phase 5. [mid-project: D75] The same commit
      holds the runs reported beside the registered tests: the ONI
      robustness check, the frozen-rules run, the Parks Canada
      sensitivity run and the strong-only results. Done 2026-10-12
      (session 9): `results/tables/run1/`, commit 4951e41, tag
      `registered-run1`.
- [x] **Runner safeguards before the first run** [mid-project: D73]
      (audit round 5): first, a written protocol for changes after results
      exist (the first results are never edited, reruns go beside them,
      any change gets a log row and an old-vs-new table; S6); then
      builders that refuse to overwrite a pinned file without `--rebuild`
      and a re-pin log (S2), `pin_inputs.load_input` as the runner's only
      way to open a table (S3), `scripts/check_plan_frozen.py` and a
      preflight the runner calls first (S4), a provenance record beside
      every result (S5), the size labels read from `test_size.csv`; tests,
      then a short cold check of that code. An offline copy of the 30
      pinned inputs (S1). Done 2026-10-11 to 12 (session 8):
      `docs/post_results_protocol.md`, `src/run_guard.py`,
      `src/pin_inputs.py`, `pinned_inputs_copy/`; cold check 4 medium,
      8 low, all fixed.
- [ ] **DeepSeek review of the safeguard code** [mid-project: D77]: a
      read-only review of `src/run_guard.py`, `src/pin_inputs.py`,
      `scripts/preflight.py` and `scripts/check_plan_frozen.py` with the
      `deepseek-delegate` skill, an extra read outside the closed gate;
      each finding checked before it counts, bug fixes only; the same for
      the runner once written. No delegated build before the registered
      runs are committed. *After the runs:* a delegated-build pilot (the
      pin report after `--rebuild`), and the methods-page line on where
      DeepSeek was used. Review run 2026-10-12 on the four files and
      `src/run_hypotheses.py`: 8 findings, 2 fixed, 6 not taken
      (`DECISIONS.md` 2026-10-12); the after-the-runs parts stay open.
- [x] **Parks Canada sensitivity run** [mid-project: D69]: every
      burned-area test that uses AB (H2, H3a, H3b, H4, H5, H6, C2) rerun on
      `fire_region_year_parks_nbac.csv` (NBAC park area added for AB
      2016-2019), beside the main results, uncorrected, exploratory.
      Done 2026-10-12: `run1/reported_beside.csv`, `run_kind` =
      `parks_nbac`.

- [x] **Frozen-rules robustness run** [mid-project: D62]: every burned-area
      test (H2, H3a, H3b, H4, H5, H6, C2) rerun on a fire table built under
      the rules as frozen where they can still be built (summed area, MTBS
      "Other" dropped, undated CNFDB fires dropped, the frozen years), one
      table beside the main results, uncorrected; a difference from the
      main results is reported as a limitation of the main analysis.
      Done 2026-10-12: `run1/reported_beside.csv`, `run_kind` =
      `frozen_rules`.

Headlines 1 to 4 and the supporting tests below were computed in
`run1` (2026-10-12); their boxes stay open until the charts and the
write-up that report them exist.

- [ ] **Full-record view:** fire-season anomaly for every year 1984–present
      (climate variables 1950–present), El Niño years highlighted
- [ ] **Headline 1 — permutation test + bootstrap CI:** El Niño years vs
      the rest, per region, for winter precipitation and burned area
- [ ] **Headline 2 — regression with controls:** burned area on ONI strength
      with summer temperature and a year trend, Newey-West errors
- [ ] **Headline 3 — interaction term:** regions pooled with ONI × region,
      answering "does El Niño affect the north differently from SoCal?"
- [ ] **Headline 4 — leave-one-year-out prediction intervals:** how often
      past 80% intervals contained the real outcome
- [ ] Supporting: lag test for the whiplash mechanism, autocorrelation check
      with block bootstrap, Holm/BH correction within each hypothesis's
      family (as defined in `ANALYSIS_PLAN.md`)
- [ ] Write the **Methods and limitations** section as you go, including
      every null result

All functions are in `src/stats.py`, tested on synthetic data with known
effects.

**Done when:** each pre-registered hypothesis has an effect size, a confidence
interval and a corrected p-value, and the methods section explains why each
technique was chosen.

## Phase 5 — Forecast & write-up (Nov 2026 → spring 2027)

- [ ] Plug in the observed 2026–27 winter as it arrives (ERA5 updates monthly)
      and place it on the full-record charts
- [ ] **Hard-line, first tracker update (early November 2026)**
      [mid-project: D55]: set `ERA5_LAG_MONTHS` from 3 to 1 in
      `src/config.py`, download every published 2026 month, refit SPEI and
      rebuild the tables, and report the changed numbers. Decided
      2026-10-07, before any fire data, and logged in the frozen plan's
      deviations table that day; no registered test changes. Recheck the
      arrival day (`TRACKER_DATA_DAY`, 7) against when October appears.
      [mid-project: D73] Every download writes to a release- or
      retrieval-stamped path, never over a pinned input. If the registered
      runs are not committed by then, only the climate tables are
      re-pinned, logged, and only if every value a registered test reads
      is identical; the ENSO and fire pins are not touched.
- [ ] Spring 2027: update with the final winter data and publish
- [ ] Fall 2027: verify against the actual season, which could become a preprint

## Second goal — public explainer page (runs alongside Phases 1–5)

A Quarto site in `site/`, published on GitHub Pages: "What past El Niños
suggest for the 2027 fire season." Each piece reuses a figure the analysis
already makes, so add it when its phase is done; don't design ahead of results.

- [ ] **Mechanism diagram** — the pathways (PNW/BC/AB dry → low snowpack →
      long or early season; SoCal wet → grass → big grass fires). No data
      needed, so it can go up first. *Any time.*
- [ ] **Methods flowchart** [mid-project: D74]: sources, the variables made
      from them, the region x year table, the pre-registered tests and the
      site's charts, in plain language for `site/methods.qmd`; drawn in
      code like the mechanism diagram (`src/diagrams.py` to
      `results/figures/`). Structure only, no numbers. No data needed, so a
      worktree session can take it. *Any time.*
- [ ] **Winter rainfall map** — the El Niño precipitation dipole, from
      Phase 1. Static cartopy is fine. *After Phase 1.*
- [ ] **Historical charts** — per region: every fire season since 1984, El Niño
      years highlighted, with an empty slot for 2027. Plotly for hover. This
      is the key result. *After Phase 4.*
- [ ] **Live 2026–27 tracker** — this winter's precipitation and snowpack so
      far against all past winters, El Niño winters highlighted, updated
      monthly through spring. *Oct 2026 → spring 2027* [mid-project: D46].
      One page in three states, at one URL [mid-project: D44]:
      - *Before winter* (if the build is done before the first month of
        data, October's, arrives in early November): an October-April
        season timeline [mid-project: D46] with a countdown to the first
        month of data, and the date the analysis plan was frozen.
      - *Tracking:* region × month tiles fill in as each month's ERA5-Land
        data arrives, with a countdown to the April 1 snowpack, the last
        input.
      - *Final:* the countdown goes and the page becomes the results page,
        keeping the completed timeline as the record that the forecast was
        issued before the season; the verification panel builds on it.
      Countdowns target expected data arrival, not calendar dates, and run
      in the visitor's browser; the page picks its state from what is in
      `results/`; its dates live in `src/config.py`.
- [ ] **Verification panel** — what actually happened in 2027 against the
      prediction. *Fall 2027* for PNW, BC, AB, AK and YT; *after January
      2028* for NorCal and SoCal, whose 2027 season runs to January 2028
      [mid-project: D46].

**Done when:** the site is public with the first four pieces, and the
verification panel is added after the 2027 season.

**Rolling publication** [mid-project: D76]: each piece goes public as it
becomes ready, not all at once. A piece is ready when the licence of
every source behind it has been read and, for anything that sets burned
area beside ENSO, the registered runs are committed. The 2027 forecast
is published in dated stages as the winter data arrive, the final one
after the April 1 snowpack.

## Later tooling (add when the need appears)

Ideas carried over from expanded-heatmap and link-station-commercial that
aren't worth building yet:

- **Published-numbers check.** link-station's "compute once, cite many"
  checker. The site doesn't need it: Quarto inline Python pulls numbers
  straight from `results/`, so pages can't go stale. Add a small checker only
  if figures start being quoted in Markdown that Quarto doesn't render (the
  README, a preprint draft). *When: Phase 5, if numbers appear in the README.*
- **Pre-push hook running `scripts/check_all.py`.** Worth it once there are
  three or more checks (pytest, em dashes, plus a provenance or drift check).
  Same pattern as expanded-heatmap: `.githooks/pre-push` calls the script,
  any failure blocks the push, enabled once per clone with
  `git config core.hooksPath .githooks`. *When: after Phase 4, before the
  site goes public.*
- **Drift check.** Regenerate `results/` tables and compare them with the
  committed versions, so a code change can't silently alter published
  numbers. A CSV-only version is enough (no HTML normalisation needed).
  Distinguish code drift (scripts changed) from source drift (ERA5 or fire
  data refreshed). *When: once `results/` feeds the live site.*

## Later extensions

- **La Niña.** A strong El Niño is often followed by La Niña, so 2027–28 could
  swing the other way. The ONI output already labels La Niña years; adding it
  means a second highlight colour on the same charts, not new infrastructure.
- **Prediction model.** Turn the historical results into a model that
  forecasts what comes next. Two possible directions, which can be done in
  either order:
  - *Seasonal outlook:* a statistical model that predicts next season's
    whiplash and fire-season anomaly per region from ENSO strength, winter
    precipitation and April 1 snowpack. Train on **all years** (about 40),
    not just El Niño years, so it has enough data; keep it simple (regression
    or quantile regression) and validate with leave-one-year-out testing.
    The 2027 season is its first real out-of-sample test.
  - *Long-term trends:* apply the same relationships to CMIP6 climate
    projections to ask whether whiplash and its fire effects grow or shrink
    over the coming decades, which was the original question behind this
    project.
  - *Compounding with climate change* [mid-project: D38]: whether warming
    amplifies El Niño's effects on snowpack and fire (the same El Niño
    warmth on a warmer baseline pushes more terrain past the rain-snow
    line). The historical part, an El Niño × time test, is a pre-freeze
    item in `ANALYSIS_PLAN.md`; the projection part belongs with the CMIP6
    direction above.
  Builds on Phases 2–4, so start it once the historical analysis is solid.

---

## Pitfalls to watch

- **Small sample.** Roughly 10 to 13 El Niño winters in the fire record
  (1985+) and about 5 strong ones; about 20 or more in the climate record
  (1951+). Recount from `el_nino_winters.csv` once it's downloaded. Report
  uncertainty and don't over-claim.
- **Units.** ERA5-Land monthly precipitation is in metres per day, not
  millimetres per month.
- **Year labels.** An El Niño winter of 1997–98 affects the **1998** fire season.
- **Data seams.** US and Canadian fire records come from different agencies,
  so check for jumps in coverage over time.
- **Fire suppression and land-use changes** affect area burned too, beyond climate.
