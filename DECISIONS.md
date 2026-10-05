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
