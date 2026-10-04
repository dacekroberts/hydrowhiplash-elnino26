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
