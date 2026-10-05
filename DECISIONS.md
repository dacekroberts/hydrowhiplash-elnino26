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
