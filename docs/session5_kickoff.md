# Session 5 kickoff: freeze, then Phase 3

Written at the end of session 4 (2026-10-05 21:15 to 2026-10-06, main
checkout). Part 1 is the handoff: the state the next session starts from.
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout.

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
- Pre-freeze audit (`docs/audit_2026-10-05_phase2.md`): data and code
  largely clean. Fixed in session 4: polar PET (north SPEI refit; AK and YT
  SPEI and whiplash changed, see `DECISIONS.md` "Pre-freeze audit"), SoCal
  SWE z blanked, stale register wording. The 111 unfitted north cells are
  glacier icefields. Low-severity code items queued as a side-session task
  ("Fix low-severity Phase 2 audit findings"); its PR needs a main-session
  re-run of the tables after merging.
- PR #18 merged (live tracker as a three-state season timeline page, D44).
  The tracker's config dates come after the freeze, and its window must
  start in October (H5 uses Oct-Mar precipitation).
- Deviations: up to D45. Main numbers its own from D46.

**Stale wording left as written (owner's prose; logged):** `ANALYSIS_PLAN.md`
hypotheses table H2 "higher in SoCal" and H5 "positive lag coefficient,
strongest in SoCal" (D42), Outcomes "Fire-season length" and "Fire season"
lines (D42, D43), Headline methods 3 "errors clustered by year" (D45);
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
   docs/audit_2026-10-05_phase2.md, docs/plan_deviations.md D41-D45 and the
   top of DECISIONS.md. Then read the roadmap artifact with the Artifact tool
   (action "read"): https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from the next free number (D46 as of the end of session 4).

2. Explain each data type and concept as it comes up, and give a short
   summary beside every hypothesis ID (memory notes).

3. If the side PR "Fix low-severity Phase 2 audit findings" is open: pre-screen
   and merge it only with the merge-side-pr skill and my yes, then re-run the
   modules it names and report any changed number before committing.

4. Walk me through ANALYSIS_PLAN.md once more and answer my questions. Freeze
   only with my explicit yes: fill in "Frozen on" with the date and a note that
   the freeze commit is the one tagged analysis-plan-frozen (plus the hash of
   the commit it builds on), commit, tag analysis-plan-frozen, push the tag.
   Then raise the Claude Code Project reminder (memory note). No fire data
   anywhere before the tag exists.

5. After the freeze: add the live tracker's dates to src/config.py (PR #18's
   table, window starting October), and queue the three fire licence reads
   (read-licence skill, one source per run) as side tasks or run them here.
   Phase 3 downloads only after their licences are read.

6. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P) and offer to
   update the roadmap artifact; write the next kickoff the same way.
```
