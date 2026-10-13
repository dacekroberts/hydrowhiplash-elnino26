# Session 13 kickoff: the hard-line item, the Motion bundle, what the phone showed

Written at the end of session 12 (2026-10-13). Part 1 is the handoff;
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout. `docs/session12_kickoff.md` keeps the longer history (going
public, the pilot, the wording rounds); where the two disagree, this
note wins.

## Part 1 · Handoff

**Status at the end of 13 October 2026.** V1 is complete and the
repository is public (github.com/dacekroberts/hydrowhiplash-elnino26,
code MIT, writing and figures all rights reserved). The site has had
nine uploads; the ninth is from commit 940de8f (deployment b0e09d94,
61 files, 10,476,791 bytes). Session 12 built the sample visuals and
closed the small things list.

**Where things stand.**

- **Nothing in `results/tables/run1/` is edited, renamed or deleted.**
  Any change that can move a registered number follows
  `docs/post_results_protocol.md`.
- **Sample visuals (D100), built on 2026-10-13.**
  - A private dashboard, five scenes, with the project flowchart cut to
    its spine in the opening scene and ending at the live site:
    https://claude.ai/artifact/HmzF6jWNnpLdSa38k9vVR2 (version 2).
    Rebuilt by `python scripts/build_dashboard.py --out <file>` and
    republished to that address. Looked at in the light theme at desktop
    width only.
  - Three banners, `python -m src.banner`:
    `results/figures/banner_social_dark.png` (1280 x 640) and
    `banner_readme_light.png` / `banner_readme_dark.png` (1280 x 320,
    the README header). The design typefaces are drawn from
    fixed-weight copies made in a temporary folder (no licence in
    `site/fonts/` declares a reserved font name). The site's charts
    still use the system sans; the same way round would work for them.
  - A Motion reference folder, `motion_handoff/` (ignored by git),
    rebuilt by `python scripts/build_motion_handoff.py --capture`: a
    numbers file, the seasons and the timetable as CSV, the tokens, the
    typefaces with their licences, 17 figures, the dashboard as a
    storyboard draft, four pictures of the live site (they come out in
    the machine's theme, dark here) and `00_MANIFEST.md`, which says why
    each file may leave and what is missing.
- **Small things, all closed or answered (2026-10-13):** the winter
  rainfall map is ticked, the map page standing in for it (D101); the
  coverage chart has a phone drawing; the notes' title band follows the
  theme; the owner tried a phone (the map works, the Overview bars were
  too small to tap), and a year slider was built for phones (D102). The
  owner tried it with a finger ("looks good") and it was reworked the
  same day: a larger thumb, one coloured box per winter with a key, a
  fold button, live since the tenth upload (commit 4d89fee, deployment
  f95a2d88). A finger has not tried the reworked one.
- **Private pages:** roadmap
  https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT, data guide
  https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P, methods reading copy
  https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf, design system
  https://claude.ai/artifact/JEsfHNH6vN7VknKmkVLP3M, results page
  https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk, dashboard as above.

**Yours to word or decide.**

- The dashboard's and banners' line, a draft: "Does an El Niño winter
  say how much the next fire season will burn?". The three Scene 4 lines
  on the dashboard, drafts reworded on 2026-10-13
  (`scripts/build_dashboard.py`, `SURVIVED`). The slider's hint is
  approved (2026-10-13).
- The two Overview captions gained a phone clause on the owner's word,
  "; on a phone, slide to a year" (`site/index.qmd`); the clause is a
  suggestion until the owner words it.
- The social preview: upload `results/figures/banner_social_dark.png`
  in the repository's Settings, Social preview (GitHub takes it by hand
  only). Owner, 2026-10-13: "i will do soon".
- The two agency links in "Who this forecast is for" are still to be
  confirmed by the owner.
- **The pattern inside a region** (owner, 2026-10-13: "an item we can
  add to the site with existing data? to go on map or overview page?").
  A scope addition, not started. The ERA5-Land grid under `data/` holds
  it; a gridded picture needs the region outlines, so a run that reads
  polygons. Session 12's suggestion: the map page, as a gridded layer
  for winter rain only, since that page already says one shade covers a
  whole region.
- **For a Motion film, before any scene is built:** an approved
  storyboard and the brief (the owner's wording), map shapes as vector
  data (a polygon read), and the decisions the `claude-motion-handoff`
  skill lists: every aspect ratio, one pace constant, light or dark,
  export sizes in pixels, what the Motion session returns.

**Next work, in order.**

1. **The hard-line item, when the 4 November reminder fires**
   (`ACTION_PLAN.md` Phase 5; D55, D88): "set `ERA5_LAG_MONTHS` from 3
   to 1 in `src/config.py`, download every published 2026 month, refit
   SPEI and rebuild the tables, and report the changed numbers." The
   downloads use `--stamp`, the refit takes about 55 minutes, the
   rebuild uses `--stamp`, the report is `changed_cells.csv`, and
   `TRACKER_DATA_DAY` is rechecked against the day October appeared.
   Then the tracker's month table and tiles. Checked on 2026-10-13,
   nothing run: the setting is still 3, the stamped paths exist, the
   Copernicus key file is present.
2. The map page: this winter's months after item 1; the owner's wording
   of its labels; the ocean panels' wording (`SEA_TEXT`).
3. The Motion bundle, when the owner starts it (see above).
4. The pattern inside a region, if the owner says so.

**Open, low:** pins walk one folder level (review F3); two tests need
the tag `analysis-plan-frozen` in the clone; `scripts/methods_numbers.py`
and the matching need `data/`; a test run in a copy without `results/`
writes a made-up `data/processed/whiplash_swe_region_year.csv` into that
copy; the headline charts' type is small on a desktop (about 7 px).

**Carried over, unchanged:** `data/` stays out of reach of every
DeepSeek plan; ask before any run that reads polygons, before every
DeepSeek call and before every upload; nothing private goes into a
commit (no keys, nothing under `data/`, not the retrospective, not the
other project's name).

**Next free deviation number: D103.** The frozen plan's deviations log
is at row 19.

## Part 2 · Prompt for session 13

```text
Session 13 for hydrowhiplash-elnino26: the hard-line item if its date
has come, otherwise the Motion bundle and the open wording.

1. Orient: read CLAUDE.md, docs/session13_kickoff.md (the status block
   at the top of Part 1 first), logs/2026-10-13.md, the top of
   DECISIONS.md (the 2026-10-13 entries), docs/post_results_protocol.md,
   results/tables/rollout_calendar.json and ACTION_PLAN.md Phase 5 and
   "Second goal". ANALYSIS_PLAN.md is frozen: never edit above its
   deviations log.
   Read with the Artifact tool (action "read"):
   the roadmap, https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D103.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is 4 November 2026 or later, read the hard-line item in Part 1
   (item 1 of "Next work") before anything else, and tell me what the
   reminder found.

5. The repository is public. Nothing private goes into a commit: no
   keys, nothing under data/, not the retrospective, not the other
   project's name.

6. Before the hard-line date: put "Yours to word or decide" in Part 1 to
   me briefly, each with a recommendation. My prose is mine to write:
   suggest, don't rewrite.

7. The Motion bundle only if I say so: the claude-motion-handoff skill,
   motion_handoff/00_MANIFEST.md for what is missing, and the storyboard
   approved by me before any brief is written.

8. Ask me before any run that reads polygons, before every DeepSeek
   call, and before every upload of the site. Flag scope additions
   rather than building them.

9. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   python scripts/check_site.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild
   the results page, the methods reading copy and the dashboard if they
   changed, update the roadmap artifact, and write the next kickoff the
   same way.
```
