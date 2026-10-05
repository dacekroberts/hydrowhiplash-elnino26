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

## 2026-10-05 (Phase 2)

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
