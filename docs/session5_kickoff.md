# Session 5 kickoff: freeze, then Phase 3

Written during session 4 (2026-10-05 21:15 to 2026-10-06 17:30, main
checkout); updated at its end, after the second audit round (main at
4928b71 or later). Part 1 is the handoff: the state the next session starts from.
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout. Part 3 is the prompt for a separate, read-only audit session that
runs first, before the freeze (owner's choice, 2026-10-06).

## Part 1 · Handoff

**Where things stand.**

- Every pre-freeze item in `ANALYSIS_PLAN.md` is decided and ticked, each with
  a `DECISIONS.md` entry, its settings in `src/config.py` (tested in
  `tests/test_config.py`), methods register rows and data dictionary entries.
  **The plan is not frozen yet:** the owner wants another read first. Freeze
  target about 18 October; no fire data has been opened anywhere.
- Decided in session 4 (`DECISIONS.md` 2026-10-05):
  - ENSO index **RONI**, ONI as the robustness check; committed tables,
    figures (now `*_roni.png`) and notebooks 01-03 rebuilt (D41).
  - SWE in tests: ERA5-Land April 1 SWE z against 1991-2020 (`era5_swe_z`),
    station z as the check; SoCal left empty (normal under 10 mm).
  - Trend rule for climate variables as for burned area; two secondary
    compounding tests C1 (snowpack) and C2 (burned area) (D38 closed).
  - Hypotheses: new **H6** (low April 1 snowpack and a dry winter predict
    more burned area); whiplash, season length, snowfall fraction and soil
    moisture descriptive; directions and sidedness per test
    (`TEST_DIRECTIONS`); H4 one north-vs-SoCal contrast; H5 `precip_anom`
    Oct-Mar z; AK and YT own family, H2/H3 two-sided; Alaska stays one
    region (D42).
  - Data rules: California fire season June to January of Y+1, BC
    April-October, AK and YT April-September; floor-then-clip fire rules;
    zero-fire years kept with a sensitivity run; strong-flag flip
    sensitivity (D43).
  - Inference: `use_t`, Driscoll-Kraay for H4 with df = years - 1,
    expanding-window validation from 20 seasons, Holm families
    (`CORRECTION_FAMILIES`) (D45).
  - H1 uses DJF precipitation; `CLAUDE.md` fire-window line updated.
- Audits: a first audit (`docs/audit_2026-10-05_phase2.md`, follow-up
  section added), two re-audits and an independent audit in a separate
  session with a neutral prompt (`docs/audit_2026-10-06_climate.md`). Fixed:
  polar-day PET; Thornthwaite heat index made climatological with N/30 (the
  per-year index had inflated 2026 PET; D47); glacier cells out of SPEI;
  SoCal SWE z blanked; 24 duplicate station sites counted once; stats.py
  guards (NaN, contiguous HAC years, repeated index); 0.06 band rounding;
  plan gaps closed in ANALYSIS_PLAN "Execution details" (last fire season
  2025, one-sided convention, H4 model, forecast, gap CI, zero-year scope,
  station minimum frozen at 5). All SPEI refit, tables and notebooks rebuilt
  (4928b71); pytest 209 passed.
- Side PRs merged: #18 (tracker in three states, D44), #19 (tracker from
  October, California verification after January 2028, D46), #20
  (low-severity audit fixes; its 6 review findings fixed in main).
- Known limitation to state with the 2027 forecast input: SoCal's 2025-26
  winter was 3.0 °C above normal and Thornthwaite PET is very temperature
  sensitive (DJF 2026 SPEI ranks 58 of 76, precipitation 20; 9.9% of cells
  at the clip).
- Deviations: up to D48. Main numbers its own from D49.

**Stale wording left as written (owner's prose; logged):** `ANALYSIS_PLAN.md`
hypotheses table H2 "higher in SoCal" and H5 "positive lag coefficient,
strongest in SoCal" (D42), H4 "interaction ≠ 0" (D48), Outcomes
"Fire-season length" and "Fire season" lines (D42, D43), Headline methods 3
"errors clustered by year" (D45), Supporting methods "lag0 = the preceding
winter" and Data and years "Climate tests (... temperature, whiplash ...)"
(D48);
`ACTION_PLAN.md` "ONI strength" / "ONI × region" (D41) and Phase 3 windows
(D43).

**Flagged, not done.**

- Fire licence reads (MTBS, WFIGS/NIFC, CNFDB): owner chose to wait for the
  freeze; the first side task after it.
- Possible descriptive check with the NOAA NCEI Interior Alaska boundary in
  Phase 4 (scope; not decided).
- Elevation-matched ERA5-Land comparison: scope addition, not approved.
- Roadmap artifact: offered for update at the end of session 4.
- At the freeze: the Claude Code Project reminder (memory note).

## Part 2 · Prompt for session 5

Paste everything below into a new Claude Code session in the main checkout.

```text
Session 5 for hydrowhiplash-elnino26: freeze the analysis plan, then start Phase 3.

1. Orient: read CLAUDE.md, ANALYSIS_PLAN.md (all of it), docs/session5_kickoff.md
   (Part 1), the latest log in logs/ ("Next" and the session 4 block),
   docs/audit_2026-10-06_climate.md, docs/plan_deviations.md D41-D48 and the
   top of DECISIONS.md. Then read the roadmap artifact with the Artifact tool
   (action "read"): https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from the next free number (D49 as of the end of session 4).

2. Explain each data type and concept as it comes up, and give a short
   summary beside every hypothesis ID (memory notes).

3. Targeted audit before the freeze: before changing anything, ask me to
   start a separate read-only audit session with the Part 3 prompt of
   docs/session5_kickoff.md (a cold session with a neutral prompt; it reviews
   every change since bfbc802, which only main-session agents have checked,
   and whether the plan can be run as written). Keep main unchanged while it
   runs. When its report arrives, save it unchanged as
   docs/audit_<date>_prefreeze.md, compare it with the earlier audits, and
   walk me through its findings; fix only what I choose, recording each as
   usual. Freeze only once its findings are settled.

4. Side PRs, if any are open: pre-screen and merge only with the
   merge-side-pr skill and my yes; re-run any module a merge names and report
   changed numbers before committing.

5. Walk me through ANALYSIS_PLAN.md once more and answer my questions. Freeze
   only with my explicit yes: fill in "Frozen on" with the date and a note that
   the freeze commit is the one tagged analysis-plan-frozen (plus the hash of
   the commit it builds on), commit, tag analysis-plan-frozen, push the tag.
   Then raise the Claude Code Project reminder (memory note). No fire data
   anywhere before the tag exists.

6. After the freeze: add the live tracker's dates to src/config.py (PR #19's
   table: window from 1 October 2026), and queue the three fire licence reads
   (read-licence skill, one source per run) as side tasks or run them here.
   Phase 3 downloads only after their licences are read.

7. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and offer to
   update the roadmap artifact; write the next kickoff the same way.
```

## Part 3 · Prompt for the targeted audit session

Start this in a separate Claude Code session in the same folder, before the
main session changes anything. Neutral on purpose: it names the scope, not
what anyone expects to find.

```text
Read-only audit of hydrowhiplash-elnino26 (this folder). Change no files; put
any scripts in a temp folder outside the repo. Do not run any module in src/
that writes files (e.g. python -m src.whiplash, src.phase2, src.stations,
src.era5, src.snow, src.snow_soil, src.download_*): import their functions
instead. Do not run git commands that change state (checkout, stash, pull,
commit, reset). Another session works in this folder at the same time. No
fire data: do not open, download or search for fire perimeters or
burned-area data.

Scope: every change since commit bfbc802 (git diff bfbc802..HEAD and git log
bfbc802..HEAD), in code, config, tests, committed tables and documents; and
whether ANALYSIS_PLAN.md can be executed by a stranger without making choices
of their own.

Goal: find anything wrong before the analysis plan is frozen: wrong numbers,
silent errors, formulas that differ from their published definitions, code
that doesn't do what its docstring or the docs say, tests that don't test
what they claim, settings that differ between ANALYSIS_PLAN.md and
src/config.py, and records that disagree with the code.

Work in this order:
1. Read CLAUDE.md, docs/data_dictionary.md and ANALYSIS_PLAN.md only.
2. Read the diff and form your own view from the code and the data in data/
   (raw and processed): recompute values independently where you can, from
   raw inputs where possible, and test edge cases.
3. Only then read DECISIONS.md, docs/methods_register.md,
   docs/plan_deviations.md and docs/audit_*.md, and check whether the code
   matches them. Report where the records and the code disagree.

Run Python through C:\Users\dacek\miniforge3\Scripts\conda.exe run -n whiplash
--no-capture-output python <script file>, from the repo root with
PYTHONPATH set to it (multi-line Python only in script files). Report: the
commit audited, what passed (with numbers), findings ranked by severity with
file:line, and what you could not check. Send the report to the main session
when the owner asks.
```
