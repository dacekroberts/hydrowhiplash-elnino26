# Session 3 kickoff: station snowpack cleaning

Written at the end of the Phase 2 session (2026-10-04 22:50 to 2026-10-05
01:20). Part 1 is the handoff: the state the next session starts from. Part 2
is the prompt to paste into a new Claude Code session in the main checkout.

## Part 1 · Handoff

**Where things stand (main, after the commit that adds this file).**

- Phase 2 core done: `src/whiplash.py` (Thornthwaite PET, per-cell SPEI-3,
  regional whiplash), `src/snow.py` (glacier mask, April 1 SWE from hourly
  ERA5-Land), `src/phase2.py` (join, writes `data/processed/` and
  `results/tables/`), notebook 02, two figures. First committed table:
  `results/tables/whiplash_swe_region_year.csv` (532 rows, 7 regions,
  1951-2026).
- Settled pre-freeze items: SPEI settings (1951-2020, log-logistic ML,
  clip ±3.09, per-cell then re-standardised); gridded SWE definition (cap or
  perennial-snow glacier rule, D27; hourly 1 April 00:00 UTC). Table
  licensing settled (LICENSE-CONTENT third-party note).
- Station snowpack downloaded raw, not cleaned, not used in any number:
  `data/raw/stations/{nrcs,bc,yukon,canswe}/`. Download scripts
  `src/download_{nrcs_snow,bc_snow,yukon_snow,canswe}.py`. Licences in
  `DATA_SOURCES.md` (NRCS public domain; BC, Yukon, CanSWE Open Government
  Licences with fixed attribution lines, notices 4-7). Alberta comes from
  CanSWE (its portal has no data licence; D30).
- Also downloaded, not yet used: ERA5-Land snowfall and soil moisture
  layers 1-2, both domains (`data/raw/era5_land*_snow_soil/`, 77 files each).
- Caches: per-cell SPEI in `data/processed/spei3_cells_{main,north}.nc`
  (about 95 minutes to rebuild; `python -m src.whiplash --refresh`).
- Deviations: main uses up to D31; the side session's PR #8 added D35.
  Session 3 takes D36-D39; the side session uses D40 onward (agreed in the
  handoff below).
- Handed to the side session at the end of the Phase 2 session (owner's
  choice), one PR each: (1) `docs/prefreeze_options.md`, option drafts for
  "Whiplash timing" and the Alaska/Yukon hypotheses; (2) one rule for which
  day's log a side block goes in (merge-side-pr vs daily-log); (3)
  `docs/alberta_swe_sources.md`, research on an Alberta April 1 SWE source
  for 2026-27 (CanSWE ends July 2025); (4) the expansion readiness table,
  an add-a-region skill, and notebook 01 pointing at `src.winter_figures`.
  Its file boundary keeps it out of `src/config.py`, the Phase 2 modules,
  notebooks 02-03, the methods register, the data dictionary,
  `DATA_SOURCES.md` and `ANALYSIS_PLAN.md`.
- Side session: worktree `.claude/worktrees/compassionate-tesla-8a3554`, last
  on `side/winter-figures` (merged as PR #9). Merge side PRs only with the
  `merge-side-pr` skill, pre-screening with `scripts/prescreen_prs.py`, and
  only with the owner's yes.

**Descriptive results so far** (ONI; 25 El Niño, 7 strong, 25 neutral
winters; from `results/tables/whiplash_swe_region_year.csv` via
`src.describe.phase_summary`; full list in `logs/2026-10-05.md`).

- April 1 SWE, El Niño minus neutral: PNW -6.9% (-0.17 SD), BC -6.9%
  (-0.42), AB -22.9% (-0.56), AK -0.8% (-0.06), YT -7.0% (-0.41), NorCal
  +30.7%. Strong winters vs all: PNW -22.0%, BC -12.4%, AB -23.9%, while
  strong-winter DJF precipitation is -0.3% (PNW) and +0.5% (BC).
- Whiplash, El Niño minus neutral (SD): north positive (PNW +0.41, BC
  +0.75, AB +0.92, AK +0.29, YT +0.52), SoCal -0.81.

**Raw station traps already found** (data dictionary s.3; methods
register "Station snowpack"):

- NRCS SNOTEL before 1980 is almost all QC flag B (regression back-estimates
  homogenising pillow and snow course records): 932 of 976 April 1 values.
- 2,163 NRCS snow-course April 1 values carry a placeholder collection date
  of 1 July (1950-2009); 89 negative SNOTEL values (lowest -108 in); 25
  listed NRCS stations returned no data. NRCS SWE is in inches.
- BC: archive and current-season files overlap (96 April 1 course-years);
  headers have leading spaces; CRLF; "Survey Period" spelled two ways for
  June; survey codes (PROBLEM, EARLY/LATE, EST PILLOW, ...) undefined.
- Yukon: quoted `#` comment lines (skip to the `location_code` header); use
  `target_date`; 6.5% of April 1 values estimated from depth; six network
  sites lie in Alaska or BC.
- CanSWE: prefixes `ALE-`, `BCE-`, `YT-`; exclude `HQ-`; pillows have
  daily values; flag B (outside the nominal period), Y (precise date not
  available); data end 31 July 2025, so no April 2026 or 2027 values.
- Overlaps to resolve: BC courses in both the BC file and CanSWE; Yukon in
  both; border sites; Yukon network sites in Alaska and BC.

**Flagged, not done.**

- D28: the 1997-98 map's extent is hard-coded and its title says "1950-2026
  mean" while the colourbar says "1950-51 to 2025-26" (owner's call).
- 111 north region cells (0.3%) got no SPEI fit; not yet investigated.
- PR #7 added a bullet to an existing DECISIONS.md entry rather than a new
  one; merged with the owner's yes.
- `merge-side-pr` files a side block by the day the side session started,
  while `daily-log` says never edit a previous day's log; PR #8's block went
  into the 2026-10-04 log after midnight.
- Freeze target about 18 October. At the freeze gate, the reminder to set up
  the Claude Code Project is due (memory note).

## Part 2 · Prompt for session 3

Paste everything below into a new Claude Code session in the main checkout.

```text
Session 3 for hydrowhiplash-elnino26: station snowpack cleaning (Phase 2, continued).

1. Orient: read CLAUDE.md, ACTION_PLAN.md (Phase 2 and the freeze gate),
   docs/session3_kickoff.md (Part 1, the handoff), logs/2026-10-05.md ("Next"
   and "Problems and fixes"), docs/data_dictionary.md section 3,
   docs/methods_register.md ("Station snowpack" rows), the station rows in
   DATA_SOURCES.md, docs/plan_deviations.md D27-D35 and the top of
   DECISIONS.md. Then read the roadmap artifact with the Artifact tool
   (action "read"): https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers, then continue.

2. Context: ERA5-Land April 1 SWE (glacier cells excluded) is lower after
   El Nino winters in PNW, BC and AB, barely in AK; strong winters PNW -22%
   and BC -12% while winter precipitation barely moves. Station data is
   downloaded raw (NRCS WA/OR/ID/AK, BC, Yukon, CanSWE for Alberta) and not
   yet cleaned. Treat the ERA5-Land pattern as something the stations check,
   not an assumption.

3. Parallel work: the side worktree session
   (.claude/worktrees/compassionate-tesla-8a3554) may open PRs. Merge only
   with the merge-side-pr skill (pre-screen with scripts/prescreen_prs.py,
   never --delete-branch), asking me before each merge unless I say
   otherwise. Main takes D36-D39; the side session uses D40 onward. Its
   queued tasks are listed in the handoff (Part 1).

4. Station cleaning, src/stations.py (plain functions, tests on synthetic
   data): one tidy station x year table of April 1 SWE in mm (station_id,
   source, network, lat, lon, elevation, year, swe_apr1_mm, sample_date,
   flags), every year kept. Before building, ask me each filtering rule,
   with options and your recommendation:
   - NRCS: QC flag B back-estimates, S (suspect), E (estimate); the
     1 July placeholder collection dates; negative values; stations with no
     data.
   - The sample-date window around 1 April for manual surveys (all sources),
     and how pillows (SNOTEL, CanSWE automatic) are read.
   - BC: archive vs current-season duplicates; survey codes.
   - Yukon: estimated SWE; the network's sites in Alaska and BC.
   - CanSWE: pillow vs manual; flags B and Y; overlap with the BC and Yukon
     files (which source wins).
   - Minimum record length for a station to count.

5. Regions: assign stations to the seven regions with the existing polygons
   (point in polygon; no areas measured). Then a regional station index per
   year: ask me the method (e.g. median percent of each station's normal, or
   mean standardised anomaly), the normal period, and the minimum number of
   stations per region-year.

6. Compare station and ERA5-Land April 1 SWE per region: correlation,
   level ratio, and the El Nino differences side by side (descriptive, no
   tests). If they disagree, check units (NRCS inches), dates and the
   glacier mask before anything else.

7. Snowfall fraction and soil moisture (descriptive unless ANALYSIS_PLAN.md
   adds them): ask me the snowfall-fraction season (DJF or Nov-Mar), the
   soil-moisture months (JJA or the fire window) and the layer weighting
   (depth-weighted 0-28 cm or layer 1 only), then add columns via
   src.geo.regional_mean.

8. Notebook 03 importing from src/: station series per region, every winter,
   El Nino winters highlighted, beside ERA5-Land; figures written to
   results/ by code. Region x year table to data/processed/ and
   results/tables/; before committing a table with station values, check
   that the BC, Yukon and CanSWE attribution notices (DATA_SOURCES.md
   notices 4-7) are recorded for it.

9. Sanity check, then stop and show me: do the stations agree with
   ERA5-Land on the direction and size of the El Nino difference in each
   region? Effect sizes descriptively, no tests.

10. Throughout: climate data only, no fire data anywhere (freeze target
    about 18 Oct). Explain concepts as they come up; flag scope additions;
    ask before judgment calls and log each in DECISIONS.md; record every
    control, cap and filter in docs/methods_register.md; log departures in
    docs/plan_deviations.md; run pytest after changes to src/geo.py,
    src/stats.py or src/config.py. Multi-line Python goes in a script file,
    not `conda run python -c`. Emailing a data publisher is a last resort.

11. End of session: write the day's log with the daily-log skill, check it
    with python scripts/log.py list, run python scripts/check_no_em_dashes.py,
    commit and push. Offer to update the roadmap artifact at the same URL,
    and write the next session's kickoff the same way.

Optional, if time allows or for the side session: draft the pre-freeze
"Whiplash timing" and Alaska/Yukon hypothesis options in light of the
positive northern whiplash; investigate the 111 unfitted north SPEI cells;
the expansion readiness table and the add-a-region skill (offered on
2026-10-04, not yet built).
```
