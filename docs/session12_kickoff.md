# Session 12 kickoff: the owner's wording, the DeepSeek pilot, before the hard-line item

Written at the end of session 11 (2026-10-12). Part 1 is the handoff;
Part 2 is the prompt to paste into a new Claude Code session in the main
checkout.

## Part 1 · Handoff

**Where things stand.**

- **Nothing in `results/tables/run1/` is edited, renamed or deleted.**
  Any change that can move a registered number follows
  `docs/post_results_protocol.md`.
- **Figures and charts (work item 1 of session 11, done).** Every data
  figure in `src/figures.py` takes its colours from `theme/tokens.json`
  (no hex value is typed in the file). `src/results_figures.py` draws one
  chart per headline from `run1` into `results/figures/headline*.png`;
  `src/fire_figures.py` also writes a Plotly version of the season
  history (`burned_area_season_history_roni.html`) with an empty slot
  for 2027. `site/methods.qmd` embeds the four charts and
  `site/index.qmd` the Plotly one. Not yet looked at in a browser. The
  1997-98 map was not redrawn (it reads polygons: ask first).
- **Typefaces.** The three design typefaces are bundled in `site/fonts/`
  and the site loads them itself. The figures stay on the system sans:
  matplotlib draws a variable font at its default weight only. Owner,
  2026-10-12: "leave font for now, address how we can work around this
  when the time comes". Ways round, when it matters: static Regular and
  Bold files made from the variable ones (read each licence's
  reserved-name clause first), or figures as SVG with text left as text
  so the browser sets the type.
- **Verification sources (D93).** "in fall 2027 the panel covers PNW and
  AK (WFIGS, provisional); BC, AB and YT are verified from NBAC, marked
  provisional, when it holds 2027 (about May 2028), and CNFDB 2027 is
  set beside it when it arrives (about January 2029)." The rollout
  calendar holds 20 items, 14 shown on the tracker page; 12 reminders are
  scheduled (the two new ones: 2028-04-28 and 2028-12-29).
- **The 2026 season (D95)** is redrawn after 31 January 2027, at the
  4 February 2027 reminder: WFIGS to a stamped path, US regions,
  described only. Reads polygons: ask first.
- **Stamped rebuilds** can name the index retrieval they read
  (`--index-stamp YYYY-MM-DD`); without it the latest closed one is
  taken.
- **Sibling repository (D94): split on 2026-10-12.**
  `climate-whiplash-prediction` (private, `..\climate-whiplash-prediction`
  and on GitHub) finished its stage 0 and, from its commit 371ed60, reads
  no file of this project without the owner's yes in its own session. It
  downloads its own data (owner: "have it download copies for full
  independence"). The tag `prediction-handoff` (a669813) is never moved
  or deleted. Its roadmap is
  https://claude.ai/artifact/1HcVPoH7YdwFBFUxwLGtcg; its sessions keep it
  current from here on. Owed to it from here, each when it exists and
  handed over from this side with a manifest: the 2025 burned area of BC,
  AB and YT, the redrawn 2026 season and the 2027 season (`DECISIONS.md`
  2026-10-12 "This project supplies the sibling's held-back burned-area
  numbers"). A large handover was made on 2026-10-12; three documents
  went redacted.
- **Three methods-page items (D96).** Drafts sit in `site/methods.qmd`
  as HTML comments, shown to no reader: "Why regression, not a trained
  model" (after "How the tests work"), "Who this forecast is for" (top
  of "The 2027 forecast") and "Where coverage is thin" (before "What the
  whole analysis cannot say"). The wording is the owner's.
- **DeepSeek build pilot (D77): prepared, not run.** The owner chose a
  staged copy (code only). The implement call was refused by Claude
  Code's permission check, because the worker starts with
  `--allow-bypass`; no call was made. The staged copy lived in session
  11's scratch folder and may be gone: staging again takes one command
  (the tracked files of `src/`, `tests/`,
  `scripts/check_no_em_dashes.py` and `environment.yml` into a new git
  repository outside the project). The plan's text is in `DECISIONS.md`
  2026-10-12 "the delegated-build pilot is prepared on a staged copy" in
  outline: eight modules, a goal with acceptance tests, five traps left
  out on purpose. The owner either runs the worker command in a terminal
  or allows it for the session.
- Private pages, all current at the end of session 11: roadmap
  https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT, data guide
  https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P, methods reading copy
  https://claude.ai/artifact/1eLGjcTZLfa6seLUq4xJqf, design system
  https://claude.ai/artifact/JEsfHNH6vN7VknKmkVLP3M. The results page
  (https://claude.ai/artifact/Af97Us4ZZoXsnEqnWue9Tk) did not change.

**Yours to word or decide (flagged in session 11, nothing changed):**

- Captions and alt text of the four headline charts and the Plotly
  history; the three new timetable rows on the tracker page.
- The three D96 drafts, and the two agency names in the second.
- The methods page's "AI use" section, with your line "DeepSeek helper
  agents contributed here" (D77); suggested place: that section, naming
  the review.
- "What a fuller version would add" still calls a prediction model "the
  next step" and "planned"; versions 1 to 1c are merged and the work
  moved (D94).
- The DeepSeek pilot ran and was merged on 2026-10-13 (`DECISIONS.md`
  "The delegated-build pilot ran and was merged"); the owner starts the
  worker in a terminal, since the session's start is refused. The
  efficiency review is written (`docs/deepseek-efficiency-review.html`,
  2026-10-13).
- `ACTION_PLAN.md` "Historical charts" is ticked (owner, 2026-10-13).
- Wording, 2026-10-13: the five captions, the three D96 items and the
  prediction bullet, "Notebooks and code", "AI use" and the page notes
  are approved and shown; no "[WIP]" mark is left on the site (the
  tracker keeps its note until November). Open: the owner to confirm the
  two agency links in "Who this forecast is for"; the retrospective. When the repository goes public (owner: "soon"), link
  "logged" in the AI use section to `DECISIONS.md`; the tone-guide pass
  was done on 2026-10-13 (code comments clean; five prose edits applied).
- Closed 2026-10-13: the Design System's empty `type.fonts` is right for
  faces hosted by Google Fonts.
- Dark-mode drawings exist for the four PNG charts and the two diagrams
  (2026-10-13; live since the third upload, commit 4615afc), and the two Plotly charts on the
  Overview page redraw in the page's theme. A longer flowchart of the whole project has its own page,
  `site/flowchart.qmd` (wording marked work in progress; one layout,
  coloured by stream, scrolls sideways on a narrow screen). The navbar reads "Methods and
  Limitations" (owner).
- Built 2026-10-13: a tap or click on a chart's bar keeps its details in a
  readout at the bottom left; on the map, regions, the key and a readout
  under the map are linked (map redrawn on the owner's yes). The three
  ledger charts have a stacked drawing for a phone (`_narrow`); the
  coverage chart does not. Not tried on a real phone. Found in the
  dark-theme check, not fixed: the navy title band of the "Work in
  progress" notes; the headline charts' small type (about 7 px on a
  desktop, 3 px on a phone). `ACTION_PLAN.md`: four site items ticked;
  the winter rainfall map is not built and not ticked. Cloudflare's edge refusal of AI-training crawlers is set
  (owner, 2026-10-13: 15 blocked, search and Claude-User allowed,
  domain-wide).

**Next work, in order:**

1. Done on 2026-10-12 (the site was looked at in a browser, dark,
   light and phone width; `.claude/launch.json` serves `site/_site/`).
   Open from it: the two-panel charts (H1 and H2; H3a and H3b) have
   small type at the page's column width; the Plotly chart's hover box
   was not checked; figures keep a light ground in dark mode.
2. The owner's wording on the list above; make approved drafts visible.
   Going live (owner, 2026-10-12): the first public piece is all four
   pages once the wording is approved, the tracker with its timetable
   only. `scripts/deploy_site.py` stages a checked build; its upload
   is empty until the Cloudflare Pages project and subdomain exist
   (reference: `handoff_cloudflare-setup_reference.md`, untracked, in
   the repository root). The address is hydrowhiplash.dacekroberts.dev (owner).
   The upload uses wrangler and a scoped token the owner sets
   as environment variables (`CLOUDFLARE_API_TOKEN`,
   `CLOUDFLARE_ACCOUNT_ID`); ask before every upload. The Pages project `hydrowhiplash` exists, empty (classic
   Pages, created with `--force`). First published 2026-10-12 from commit bf8a9e7 at
   hydrowhiplash.pages.dev. The custom domain is active (20:22). Cloudflare's
   analytics script (RUM, on by default) was found injected there and
   switched off by the owner for the whole domain; confirmed gone in a
   browser. The V1 retrospective is written
   (`docs/retrospective_v1.md`, a draft for the owner). Open: the
   work-in-progress wording. plotly.js
   is bundled with the site.
   After the site is live: a full V1 retrospective (owner, 2026-10-12:
   "after site is live: do a full V1 Retrospective"). Its scope and
   format are the owner's to set when it starts. To include, in its
   sections on the final product and where to go from here: AI-training
   crawlers are limited by `site/robots.txt` only, which they may
   ignore; Cloudflare can refuse them at its edge if the owner decides
   to (owner, 2026-10-12).
   The repository goes public once the work-in-progress wording is
   resolved and code comments and site prose have been audited against
   the tone guide (owner, 2026-10-12).
3. The DeepSeek pilot, if the owner says so; then the efficiency review
   the handoff asks for (`docs/deepseek_handoff_2026-10-11.md` section
   4).
   When the pilot is complete, its results go to the sibling session
   (owner, 2026-10-12: "we should pass results to the prediction
   modelling session (sister)").
4. The hard-line item, when the 4 November reminder fires (ACTION_PLAN
   Phase 5; D55, D88): `ERA5_LAG_MONTHS` 3 to 1, download every
   published 2026 month with `--stamp`, refit SPEI (about 55 minutes),
   rebuild with `--stamp`, report `changed_cells.csv`, recheck
   `TRACKER_DATA_DAY`. Then the tracker's month table and tiles.
5. The map page (D85, D98): a first version exists (`src/map_page.py`,
   `site/map.qmd`; built 2026-10-12 on the owner's word). Open: the
   owner's wording of its labels and sentences; this winter's months
   after item 4; whether the class edges suit the owner. Ocean panels
   (D99): built 2026-10-12 from NOAA ERSST v6, display only: the
   ocean under the regions and a tropical Pacific strip on the same
   slider, smoothed by default with a switch to the 2° cells, a hide
   switch, and a note that the data entered no calculation. The ocean
   has its own ramp (purple to amber, the owner's choice), land
   outside the regions comes from Natural Earth 1:50m land, La Niña
   winters on the strip are steel blue and neutral ones white. Open
   for the owner: the wording (`SEA_TEXT`). Steel blue is confirmed and
   the private Design System page has the new tokens. The methods
   page's sections fold; its section headings were set to 32 px and
   then put back to the site's 26 px on the owner's word.

**Open, low:** pins walk one folder level (review F3); two tests need
the tag `analysis-plan-frozen` in the clone; `scripts/methods_numbers.py`
and the matching need `data/`; a test run in a copy without
`results/` writes a made-up `data/processed/whiplash_swe_region_year.csv`
into that copy (seen in the staged copy only; worth a look).

**Carried over, unchanged:** `data/` stays out of reach of every
DeepSeek plan; ask before any run that reads polygons; ask before every
DeepSeek call; the going-public question is a leaning, not a decision.

**Next free deviation number: D100.** The frozen plan's deviations log
is at row 19.

## Part 2 · Prompt for session 12

```text
Session 12 for hydrowhiplash-elnino26: the owner's wording on session
11's drafts, the DeepSeek pilot, and readiness for the hard-line item.

1. Orient: read CLAUDE.md, docs/session12_kickoff.md, logs/2026-10-12.md
   (the session 11 block), the top of DECISIONS.md (2026-10-12 session
   11 entries), docs/plan_deviations.md D93-D96,
   docs/post_results_protocol.md, site/methods.qmd, site/index.qmd,
   site/tracker.qmd, results/tables/rollout_calendar.json,
   ANALYSIS_PLAN.md (frozen: never edit above the deviations log) and
   ACTION_PLAN.md Phases 4 and 5 and "Second goal".
   Read with the Artifact tool (action "read"):
   the roadmap, https://claude.ai/artifact/4jc6Gyofq9cVRYtRQiHQeT
   Tell me in 3-4 lines what this session covers. Main numbers its own
   deviations from D100.

2. Explain each concept as it comes up, give a short summary beside every
   hypothesis ID, and quote the actual wording beside every item ID
   (memory notes).

3. Nothing in results/tables/run1/ is edited, renamed or deleted. If
   anything would change a registered number, stop and walk me through
   docs/post_results_protocol.md first.

4. If it is 4 November 2026 or later, read the hard-line item in Part 1
   (item 4) before anything else, and tell me what the reminder found.

5. Build the site and look at it in the browser: the four headline
   charts, the Plotly season history, light and dark. Tell me what you
   see before changing anything.

6. Then the list "Yours to word or decide": put each to me briefly, with
   a recommendation where you have one. My prose is mine to write:
   suggest, don't rewrite.

7. Then the work list in Part 1, in order. Ask me before any run that
   reads polygons, and before every DeepSeek call. Flag scope additions
   rather than building them.

8. End of session: daily-log skill, python scripts/log.py list,
   python scripts/check_no_em_dashes.py, python scripts/check_plan_frozen.py,
   python scripts/check_site.py, commit and push; refresh the data guide
   artifact (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P), rebuild
   the results page and the methods reading copy if they changed, update
   the roadmap artifact, and write the next kickoff the same way.
```
