# V1 retrospective: hydrowhiplash-elnino26

**Live site:** <https://hydrowhiplash.dacekroberts.dev>

Written 12 October 2026, the day the site first went public. A draft by
Claude Code for Dace Roberts to edit; it is in Dace's first person, and
where the assistant made an error it is named as Claude Code. Every number
is from the repository's own records (the decisions log, the deviations
log, the daily logs, the audits, the run tables, git history) at commit
b0b1724. Private: nothing here is published on the site.

## 1. In short

I set out to answer one question: does a strong El Niño winter tell us
anything about the fire season that follows it in western North America,
and if so, what should we expect in 2027? In nine days I built the data
pipeline, wrote 52 tests down before opening any fire data, ran them once,
and put the result on a public site.

The answer is mostly no. Of the 52 tests, 4 are significant after
correcting for the number of tests, and none of the 4 links El Niño itself
to burned area. What shows up is the step after it: winter moisture goes
with burned area in Alberta and Northern California. These are
associations over about 42 seasons, not causes.

V1 is the analysis, the registered result and a four-page site. The
forecast for 2027, the winter tracker and the check against what burns are
not in V1: they arrive on dates already on the calendar.

## 2. What was planned

Three documents held the plan from the first day (4 October):

- `ACTION_PLAN.md`: five phases, from regions and climate data to the
  fire-season analysis, with a second goal alongside them, a public
  explainer page.
- `ANALYSIS_PLAN.md`: the hypotheses and tests, to be frozen before any
  fire data was opened.
- `DECISIONS.md`: the reasoning behind each judgment call.

The original scope was five regions (the Pacific Northwest, British
Columbia and Alberta, with Northern and Southern California as the
contrast), climate from 1950 and fire from 1984, one ENSO index, and a
site on GitHub Pages. La Niña and a prediction model were named as later
extensions, not to be built unless asked.

The first session was planned at one to two hours and took about 2.1.
That is deviation D1, and the smallest of them.

## 3. What was built

- **Data.** ERA5-Land precipitation, temperature and snowpack for two
  domains; NOAA's ENSO indices; snow stations from US and Canadian
  networks; fire
  polygons from MTBS, WFIGS, CNFDB and NBAC. 19 rows in the source ledger,
  each with its licence read and a verdict.
- **Regions.** Seven, not five: Alaska and Yukon were added on the first
  day (D20).
- **Code.** 48 modules in `src/` (about 10,500 lines) and 41 test files
  holding 415 test functions; the last full run of the suite passed 432
  cases. 195 commits, 24 merged pull requests, four tags
  (`analysis-plan-frozen`, `pre-results-gate-closed`, `registered-run1`,
  `prediction-handoff`).
- **The registered run.** 52 tests in eleven groups, run once on 12
  October from pinned inputs (commit 4951e41), with the runs reported
  beside them and a validation table.
- **An exploratory prediction model.** Three versions in a day (D90 to
  D92). Spring inputs beat a trend-only model by about 0.01 in skill. It
  then moved to a private sibling repository and was split from this one
  (D94).
- **The site.** Four pages: the overview, a map of the seven regions by
  year, a tracker timetable, and methods and limitations.
- **Records.** 96 deviation entries numbered to D99, a methods register of
  every threshold and filter, a data dictionary, 12 audit reports, and a
  log for each of the 8 working days.

The logs record 58.5 hours of sessions. That undercounts: the 12 October
figure (11.8 hours) was written before that evening's work on the map's
ocean panels, the deploy step and the publication.

## 4. Where reality departed from the plan

There are 96 logged departures. Most are small (a wording left stale, an
estimate that was off). Of the entries that state it, 26 are marked
substantial and 16 not. By kind:

- **Scope additions I chose.** Alaska and Yukon (D20); snowfall and soil
  moisture (D13); a sixth hypothesis on snowpack and drought (D42); the
  map page (D85, D98); a shared design system (D86); three methods-page
  items (D96); sea-surface temperature for the map, display only (D99).
- **Changes the data forced.** NOAA made RONI its official index, so the
  project followed (D15, D41). Canadian fire polygons end in 2024 (D56,
  D57). MTBS is complete only through 2023 (D61). Parks Canada sent no
  large fires for 2016 to 2021, so four Alberta seasons are flagged and a
  sensitivity run was added (D69). Fires on defence land are in no polygon
  and are a stated limitation (D71).
- **Method changes before the freeze.** California's fire season runs
  through January (D43). H4's errors are Driscoll-Kraay (D45). SPEI
  follows the reference implementation (D49).
- **Process added because the stakes rose.** Read-only audits at phase
  boundaries (D35), a pre-results audit gate (D51) run in repeated rounds
  (D64), pinned inputs (D82, D88), rolling publication (D76).
- **Corrections to my own records.** D70, D71 and D72 each correct an
  earlier entry; D97 corrects D95; D55 supersedes D54 on the day it was written.

The departure that mattered most was an early one, D19: El Niño winter
drying in the Pacific Northwest and British Columbia is weaker than I had
assumed (about 5% less December to February precipitation than in neutral
winters, against 38% more in Southern California). The mechanism the
northern half of the project was built on turned out to be faint in the
first table I made.

## 5. What the findings are, and are not

This section restates what the methods page already says; it adds no new
reading.

| Test | Region | Estimate (95% interval) | Holm p | n |
|---|---|---|---|---|
| H1, El Niño winters and winter precipitation | Southern California | +64 mm (31 to 100) | 0.0005 | 76 |
| H5, winter precipitation and burned area, same year | Alberta | −0.687 (−1.099 to −0.276) | 0.008 | 41 |
| H5, winter precipitation and burned area, year after | Northern California | +0.388 (0.188 to 0.589) | 0.004 | 42 |
| H6, snowpack and burned area | Northern California | −0.377 (−0.616 to −0.138) | 0.025 | 42 |

Burned-area estimates are in log points.

- El Niño winters are wetter in Southern California. That is the one link
  from El Niño to anything.
- No test of El Niño against burned area passes: not the year groups (H2),
  not the strength slopes with or without summer temperature (H3a, H3b),
  not the north against Southern California (H4).
- 48 of 52 tests are null, and the site shows them at the same size as the
  rest.
- The limits are the ones on the methods page: about 42 seasons, whole
  states and provinces as regions, fires of 405 ha or more only, and
  source gaps in Alberta.

## 6. What the checks caught

- **The frozen plan.** `scripts/check_plan_frozen.py` fails any commit
  that alters the plan above its deviations log. It made every later
  change a logged deviation, not a quiet edit.
- **Five rounds of pre-results audit.** Cold, read-only sessions that
  rebuilt numbers by independent code. Rounds 1 to 4 found things to fix;
  round 5 found "nothing high, nothing medium" and six low findings. The
  gate closed only on that cold round.
- **Pinned inputs.** Every table a test reads is hashed; a rebuilt table
  goes beside the pinned one, not over it (D88).
- **The post-results protocol.** Written before the run, so a change to a
  registered number has a procedure before anyone wants one.
- **The site check and the deploy step.** The first catches pages that
  render to nothing and links that break; the second refuses an unpushed
  checkout and any page that still says "draft".
- **Publication day.** A browser check on the live address found
  Cloudflare injecting an analytics script that was in no file of mine; I
  switched it off for the whole domain. The readiness check found the
  sea-temperature source had no credit on the methods page. A screenshot
  of the token screen showed a permission that could create other tokens,
  ticked by mistake, before the token was made.

## 7. How the work was done

- **Sessions.** Twelve main sessions (0 to 11) with Claude Code, each
  started from a kickoff note written at the end of the one before, plus
  side sessions in git worktrees for tasks that needed no data.
- **Logs.** One file per day, appended and never rewritten, exported to
  my catalogue.
- **Private pages.** A roadmap, a data guide, a results page, a methods
  reading copy and a design system, each refreshed from the repository.
- **A second model.** One read-only review of the run code by DeepSeek on
  copies holding no data (D77). A harder pilot, a delegated build, was
  prepared and never run: the assistant's permission check blocked the
  worker, and I have not started it myself.
- **The split.** Prediction work left for a sibling repository on 12
  October, with a one-time handover of code and tables. Three burned-area
  tables for seasons still open are held back and owed later.

## 8. What went wrong, or cost more than it should

- **I trusted the mechanism before I had measured it.** D19 came in
  Phase 1. The honest framing ("what do past El Niños suggest", not "what El
  Niño does") followed, but the regions and hypotheses had been chosen
  around a dipole that is weaker than the textbooks suggest.
- **Records needed correcting more than once.** D69 was corrected by D71,
  and D71 by D72. Each correction was caught by an audit, which is the
  system working, and each was a claim written faster than it was
  checked.
- **Claude Code misread a register line.** D95 quoted 26,609 ha as the
  2026 season's area; it is the overlap between two sources. D97 corrects
  it, and the sibling project was sent the correction.
- **Claude Code wrote log times ahead of the clock, twice in one day.**
  Entries ran to 22:45 when it was 20:17. Both were corrected against
  commit times. The fix is to read the clock before writing a time.
- **A request was misheard and built three times.** I asked for bigger
  "section headers" on the methods page and meant the subsection
  headings. The section headings went to 24 pt, back to 19.5 pt, and only
  then did the subsections go up.
- **Messages went to the wrong sessions.** A request meant for one
  project reached another's session, which correctly did nothing.
- **Cloudflare had moved.** Its dashboard and tooling now steer new sites
  to Workers. Creating the Pages project failed until a flag was added,
  the dashboard listed no projects until refreshed, and the analytics
  setting was in a third place after two wrong ones.
- **First guesses on sources.** The sea-temperature data was first
  proposed as version 5; NOAA builds its index from version 6. The first
  ERA5-Land download estimate was off (D10, D21).
- **Wording is still open.** Three of four pages went public marked as
  work in progress, by my choice, so that the site could go up.

## 9. The final product

**Live at <https://hydrowhiplash.dacekroberts.dev>** since 12 October
2026, from commit bf8a9e7: 42 files, 8.7 MB, hosted on Cloudflare Pages by
direct upload.

- **Overview.** The question, the data areas, the regions and the
  hypotheses in one panel; the two-pathway diagram; two hover charts of
  every winter and every fire season with El Niño years marked; dated
  notes where the tracker and the verification will go. Wording approved.
- **Map.** Seven regions coloured against their own normal, four
  datasets, every year from 1951, a strip of every winter's El Niño
  class, and the Pacific's sea-surface temperature for that winter as a
  picture only. Work in progress.
- **Tracker.** The timetable of every date the site is waiting for. Work
  in progress; the month tiles come with the first winter data.
- **Methods and limitations.** The method, every test including the
  nulls, what was filtered out, limits grouped by the claim each one
  constrains, and source credits. Sections fold. Work in progress; the AI
  use section is one placeholder line.

**How it is protected.** A copyright line in every footer;
machine-readable rights tags in every page's head; a credit inside each
figure file; `LICENSE-CONTENT` separating my writing and figures from the
MIT-licensed code and from third-party data. The built site asks no other
host for anything: fonts and the chart library are bundled, and
Cloudflare's default analytics is off.

**Crawlers.** `robots.txt` allows search engines and asks thirteen
AI-training crawlers to stay out. That is a request they may ignore.
So on 13 October I also had Cloudflare refuse them at its edge, which
does not depend on their good behaviour: 15 crawlers it classes as AI
crawlers are blocked for the whole domain. Search crawlers are not
blocked, and neither is Claude-User, which fetches a page when a person
asks for it.

**What a visitor cannot yet see.** The 2027 forecast, this winter's
months, the verification, three drafted methods items held in comments,
and the code: the repository is private.

## 10. Where to go from here

**On the calendar already:**

| When | What |
|---|---|
| 4 November 2026 | The tracker's hard-line item, then its month tiles |
| by 7 November, then monthly to April 2027 | Each month's ERA5-Land data |
| January to February 2027 | CNFDB 2025 polygons; then the 2025 table owed to the sibling |
| after 31 January 2027 | California's 2026 season closes; the 2026 season is redrawn (D95) |
| 1 to 14 March 2027 | The winter's index value; the forecast is published at it |
| about 8 April 2027 | Snowpack on 1 April; the forecast's final stage |
| after 31 October 2027 | The northern fire seasons end; first verification |
| after 31 January 2028 | California's 2027 season ends; verification complete |

**Before the repository goes public:** resolve the work-in-progress
wording on three pages, write the AI use section, decide the three held
methods items, and audit code comments and site prose against my tone
guide.

**Open decisions:**

- Whether the DeepSeek build pilot runs; if it does, its results go to
  the sibling project.
- Cloudflare's list of AI crawlers grows; new ones start unblocked, so
  the list needs a look now and then, as `robots.txt` does.
- Whether to move from Cloudflare Pages to its Workers-based hosting
  before Pages is retired, not after. Only the upload step and the token
  would change.
- The year in the ERA5-Land attribution line, to recheck at each
  publication.
- Small type on the two-panel headline charts; figures keep a light
  ground in the dark theme; the map's class cut-offs were chosen by eye.

**Later extensions, still unbuilt by design:** La Niña, and anything
predictive in this repository.

## 11. What to do differently next time

**Keep:**

- Freezing the tests before the data, with a script that enforces it.
- Cold, read-only audits that rebuild numbers independently, and closing
  a gate only on a clean cold round.
- One log per day, one decisions log, one deviations log, written as the
  work happens.
- Numbers on the site read from result tables, never typed.
- A deploy step that refuses unfinished pages, and a real-browser check
  of the live address after every publication.

**Change:**

- Measure the mechanism before choosing regions around it. A one-day
  pilot table would have shown D19 before the plan was written.
- When a request names something that could be two things, ask which
  before building. The heading sizes cost three rounds.
- Read the clock before writing a time, and quote a register line whole
  before citing a number from it.
- Treat a hosting provider's defaults as unknown until checked in a
  browser. The analytics script was on by default and invisible to every
  check that did not load a page.
- Confirm which project a session belongs to before sending it a request.
- Settle wording page by page before publication day, not on it.
