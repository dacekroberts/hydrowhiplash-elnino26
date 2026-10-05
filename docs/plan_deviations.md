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

## 2026-10-04 (Session 0)

### D20 · Append-only merge script added
- **Plan:** `merge-side-pr` step 5 resolved `DECISIONS.md` and
  `docs/plan_deviations.md` conflicts by hand; `ACTION_PLAN.md` "Later
  tooling" has no merge tooling.
- **Actual:** `scripts/merge_append_only.py` resolves both files and step 5
  runs it. Numbered D20 because open PRs #1 and #3 add D17-D19.
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
