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
