# Session 4 kickoff: pre-freeze decisions

Written at the end of session 3 (2026-10-05, 01:45-11:50 with a pause);
updated at 11:50 with the merges of PRs #16 and #17.
Part 1 is the handoff: the state the next session starts from. Part 2 is the
prompt to paste into a new Claude Code session in the main checkout.

## Part 1 · Handoff

**Where things stand (main at 91aa1ea or later).**

- Phase 2 done. Gridded: SPEI-3, whiplash, April 1 SWE (ERA5-Land hourly,
  glacier cells excluded). Stations: `src/stations.py` cleans NRCS, BC,
  Yukon and CanSWE into `data/processed/station_swe_apr1.csv` (71,759
  station-years, 2,180 stations, 1950-2026) and a regional index beside
  ERA5-Land in `results/tables/station_swe_region_year.csv`. New ERA5-Land
  columns: snowfall fraction (Nov-Mar, ratio of regional totals) and JJA soil
  moisture (0-28 cm) in `results/tables/snow_soil_region_year.csv`
  (`src/snow_soil.py`). Notebook 03 and three figures. pytest 171 passed
  (after PR #17).
- Committed tables now: `whiplash_swe_region_year.csv`,
  `station_swe_region_year.csv`, `snow_soil_region_year.csv` (532 rows each,
  7 regions, 1951-2026). Notices for outputs carrying station values are
  listed in `DATA_SOURCES.md` ("Outputs carrying station values").
- Station rules and index (owner, 2026-10-05; `DECISIONS.md` "Station
  snowpack cleaning rules", "Regional station index"): NRCS B and S dropped;
  1 July dates kept as `date_unknown`; ±10-day window; pillows on 1 April;
  BC codes as flags; Yukon estimates kept, sites outside Yukon dropped;
  provincial files over CanSWE; median % of the 1991-2020 normal plus mean
  z; 20 of 30 years; at least 5 stations per region-year (owner may widen
  this for AB and YT). Index starts PNW and BC 1951, AK 1960, AB 1963, YT
  1975; AB ends 2025 (D37).
- Side PRs #10-#17 merged (option drafts, log rule, Alberta source
  research, notebook 01 on `src.winter_figures`, expansion table, add-region
  skill, site-check trigger, numbering at merge). Side blocks go in the
  merge day's log. The side worktree
  (`.claude/worktrees/compassionate-tesla-8a3554`) is detached and idle;
  nothing of its is open.
- Climate change: a new pre-freeze item "Trend and climate change" in
  `ANALYSIS_PLAN.md` and a "Compounding with climate change" bullet under
  Later extensions in `ACTION_PLAN.md` (D38; owner's request).
- Every main-checkout session now ends by refreshing the private data
  guide artifact, https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P
  (`CLAUDE.md`; D39). Roadmap artifact at v8 (same URL as before), next
  step set to session 4.
- Deviations: up to D40 used (main D36-D39 in session 3; D40 is PR #17's).
  No more ranges: main numbers its own entries directly from the next free
  number (D41 now); side sessions write placeholders that the merge numbers
  (PR #17, merged 91aa1ea; `CLAUDE.md` and `merge-side-pr` steps 5, 8, 10,
  including `merge_append_only.py --check-log` after folding a block).

**Descriptive results that bear on the freeze** (ONI; no tests).

- Stations agree with ERA5-Land on the direction of the El Niño April 1
  SWE difference in all five northern regions (yearly correlation
  0.78-0.95). Strong El Niño minus all winters, points of normal, stations /
  grid: PNW -8.5 / -25.6, BC -14.3 / -13.0, AB -38.9 / -32.3, AK -4.1 /
  -5.0, YT -5.5 / -2.1.
- The PNW gap is elevation: low-third stations -42, high third +3. The
  network sits high (median station normal 3.1 times the grid mean), so it
  under-samples where El Niño warmth turns snow to rain. Snowfall fraction
  agrees (strong winters PNW -0.84 SD, BC -0.67 SD).
- Median station index collapses in snow droughts (PNW 2015 3.3%, 2026
  4.7%), so keep the z column beside it.
- From Phase 2: whiplash after El Niño is positive in the north (BC +0.75,
  AB +0.92 SD vs neutral), negative in SoCal (-0.81); the side session's
  `docs/prefreeze_options.md` finds about half the north's positive whiplash
  is wetter summers.

**Pre-freeze items in `ANALYSIS_PLAN.md`** (all boxes still unticked):

- Already settled in practice, boxes to tick with the owner's yes: SPEI
  settings (`DECISIONS.md` 2026-10-04); SWE definition (glacier rule,
  hourly April 1) and station rules; snowfall and soil seasons and layers.
- Open: ENSO index (ONI or RONI; repo recommends RONI with ONI as a
  check); test the core variables (whiplash, SWE, season length); whiplash
  timing (drafts in `docs/prefreeze_options.md`); directions and sidedness;
  H4's test; H5 definitions; Alaska and Yukon (drafts in
  `docs/prefreeze_options.md`); trend and climate change (D38, new); SWE
  source for the tests (stations, ERA5-Land or both); snowfall and soil
  moisture in a hypothesis or descriptive; fire windows; fire record rules;
  zero-fire years; small-cluster corrections; forward validation;
  correction families. Plus the operational call on near-threshold winters
  (2009-10 ONI 1.47, 1991-92 1.54, 1972-73 1.55) and the Alberta 2026-27
  SWE source (`docs/alberta_swe_sources.md` recommends ERA5-Land).

**Flagged, not done.**

- Elevation-matched ERA5-Land comparison (grid cells near station
  elevations): a scope addition, not built.
- 111 north region cells with no SPEI fit: not investigated.
- Done in PR #16 (3362e18): `src/winter_figures.py` now triggers the
  site check in `prescreen_prs.py` and `merge-side-pr` step 3.
- Done in PR #17 (91aa1ea): side-session deviation numbers given at
  merge, with the post-fold log check.
- D28: the 1997-98 map's hard-coded extent and title wording (owner's call).
- Freeze target about 18 October. At the freeze, the reminder to set up the
  Claude Code Project is due (memory note).

## Part 2 · Prompt for session 4

Paste everything below into a new Claude Code session in the main checkout.

```text
Session 4 for hydrowhiplash-elnino26: pre-freeze decisions (gate before Phase 3).

1. Orient: read CLAUDE.md, ACTION_PLAN.md (gate and Phase 3),
   ANALYSIS_PLAN.md (all of it), docs/session4_kickoff.md (Part 1),
   logs/2026-10-05.md ("Next" and the session 3 block),
   docs/prefreeze_options.md, docs/alberta_swe_sources.md,
   docs/plan_deviations.md D36-D38 and the top of DECISIONS.md. Then read
   the roadmap artifact with the Artifact tool (action "read"):
   https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers, then continue. Main
   numbers its own deviations from the next free number (D41 as of
   91aa1ea); side PRs use placeholders that the merge numbers.

2. Explain each data type and concept as it comes up (memory note
   "explain-data-types"), and keep docs/data_dictionary.md current.

3. Walk me through the open pre-freeze items in ANALYSIS_PLAN.md one group
   at a time (hypotheses, data rules, inference), each with options, the
   relevant numbers from results/tables/ and your recommendation; ask before
   recording any choice. Start with the ENSO index (ONI or RONI), because
   every test depends on it, then the SWE source for the tests and the new
   "Trend and climate change" item (D38). Ask before ticking the boxes that
   are already settled in practice (SPEI settings, SWE definition, snowfall
   and soil seasons).

4. Record each answer: fill in ANALYSIS_PLAN.md, a DECISIONS.md entry,
   settings in src/config.py (run pytest after config changes), the
   methods register, and docs/plan_deviations.md for departures. My own
   prose in the plans is off-limits for rewriting: flag stale wording.

5. If a choice changes ENSO_INDEX or another setting behind a committed
   table, rerun the affected modules (src.era5, src.snow, src.whiplash
   (reuses its per-cell cache), src.phase2, src.stations, src.snow_soil, notebooks
   01-03) and report changed numbers before committing.

6. Freeze only with my explicit yes: commit ANALYSIS_PLAN.md with the date
   and hash filled in, tag the commit analysis-plan-frozen, push. Then raise
   the Claude Code Project reminder (memory note). No fire data anywhere
   before the freeze commit exists.

7. Parallel work: merge side PRs only with the merge-side-pr skill and my
   yes. Multi-line Python goes in a script file. Emailing a data publisher
   is a last resort.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push. Refresh the data
   guide artifact at the same URL
   (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P): read it, update
   every data type, setting and number that changed from the repo (data
   dictionary, config, methods register, results/tables), and the snapshot
   commit in its footer. Offer to update the roadmap artifact at the same
   URL, and write the next session's kickoff the same way.

Optional, if time allows: the 111 north region cells with no SPEI fit; the
elevation-matched ERA5-Land comparison only if I approve it as scope.
```
