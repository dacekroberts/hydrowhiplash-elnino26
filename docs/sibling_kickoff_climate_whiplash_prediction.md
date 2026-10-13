# Kickoff: a separate work-in-progress project

Drafted 2026-10-12 (session 11 of hydrowhiplash-elnino26) with the owner.
The repository was created the same day on the owner's word (checked out
beside the parent); it holds this file as `docs/kickoff.md`, a README and the
licence files, and nothing else. Stage 0 is its first session. Source material:
`docs/prediction_sibling_kickoff.md` (the side session's proposals) and
`docs/prediction_model_spec.md`.

## Part 1 · What is settled (owner, 2026-10-12)

- **Name and home:** a separate work-in-progress repository, a sibling of
  hydrowhiplash-elnino26 (the parent).
- **Inputs from the parent:** the seven tables in `PINNED_RESULT_TABLES`
  and `results/tables/input_pins.csv`, copied at the parent's tag
  `prediction-handoff` (commit a669813, the squash commit of PR #24).
  Each copy is checked against its sha256 in `input_pins.csv`, and the
  sibling records the tag and commit beside them.
- **Licence:** the parent's split. Code MIT; writing and figures (c) Dace
  Roberts, all rights reserved. Third-party values in tables keep their
  sources' terms.
- **Rules kept from the parent:** a decisions log, a daily log, one
  settings file, a data-sources ledger with every licence read before
  anything derived is published, a provenance record beside every table.
  No frozen analysis plan: instead, each step's variants and its reading
  guide are written and committed before any fit, and every variant is
  reported.
- **Held-back seasons, registered in advance:** the 2025 season of BC, AB
  and YT, the 2026 season and the 2027 season are never used to choose or
  tune a model. How they will be scored is written down before the first
  fit, and each is scored once, as it arrives.
- **Scope of the first work:** all seven regions; later issue dates
  (1 April, 1 June, 1 July, 1 August) from the monthly ERA5-Land already
  on disk.
- **Roadmap:** an artifact in the parent's design system for now. Owner's
  note: the model may get its own design system later, "more science-y
  to match the data science lean"; not important until the model is more
  final.
- **The parent's registered 2027 forecast stays the H3a model** (El Niño
  strength on burned area, trend only), whatever the sibling finds.

## Part 2 · What the parent established

Skill = 1 minus the model's RMSE over the RMSE of a trend-only model
(`log_burn ~ year` per region), on 151 unseen region-seasons, 2004 to
2025, each predicted from earlier seasons only; 95% intervals from
resampling whole years. Exploratory, uncorrected. From
`results/tables/prediction_v1c/variants.csv`.

| Run | All seven regions |
|---|---|
| Version 1, four spring inputs | 0.002 (-0.007 to 0.015) |
| Version 1b, best of five (`spring_inputs`) | 0.012 (-0.001 to 0.032) |
| Version 1c, last season's burned area added | 0.008 (-0.008 to 0.025) |
| Ceiling: the summer's temperature, SPEI-3 and soil moisture known (cannot forecast) | 0.126 (0.061 to 0.231) |

The ceiling by region: BC 0.483, AK 0.345, NorCal 0.257, YT 0.221; PNW
0.020, AB 0.003, SoCal -0.038. Winter and spring inputs at region scale
buy about 1%. In four regions the summer's moisture explains a fifth to a
half of the trend-only error; in three, seasonal means over a whole
province or state explain nothing.

The number to reproduce first: `spring_inputs`, 0.012.

## Part 3 · Roadmap

| Stage | Work | Needs | Done when |
|---|---|---|---|
| 0 | Set up the repository: licence files, settings file, decisions log, daily log, ledger; copy and verify the parent's tables; copy `src/prediction*.py` and their 36 tests | The owner's yes | The copied code reproduces 0.012 from the pinned tables |
| 1 | Write the held-back-seasons rule and how each season is scored | Nothing new | Committed before any new fit |
| 2 | Later issue dates: 1 April, 1 June, 1 July, 1 August, with spring and early-summer soil moisture, SPEI and temperature | The parent's `data/` (ERA5-Land monthly), read in place | Skill by issue date and region, every variant reported |
| 3 | A seasonal forecast of the summer as an input (ECMWF SEAS5 hindcasts) | New source: ledger row, licence read | The same table with forecast inputs |
| 4 | Spring fuel dryness (snow-off date, 1 May snowpack, May vapour pressure deficit, the Fire Weather Index drought code) | New sources | As above |
| 5 | Fuel amount (satellite greenness of the previous growing season) | New source | As above |
| 6 | Smaller units (ecoregions or fire zones), and a spring window for Alberta | Rebuilds the fire and climate tables; reads fire polygons | A unit table and its baseline |
| 7 | A longer fire record (before 1984) and other targets (large-fire counts, top-decile seasons) | New sources, record checks | Decided per item |
| 8 | Machine learning as a grid-cell model. Owner: "to be tried later after other items" | Stages 2 to 6 | Decided then |
| Later | The other El Niño regions as targets and as a cross-check (below) | A model that is fixed first | Decided then |

Scored as they arrive: BC, AB and YT 2025 (CNFDB, about January 2027);
the 2026 season (US regions after January 2027; Canada about January
2028); the 2027 season (fall 2027 onward).

### Competing models (owner's idea; format agreed 2026-10-12)

Owner, 2026-10-12: "let's also consider housing multiple models competing
against each other in that project, tuned for different 'strengths' and
'known weaknesses' each attempting to best predict the climate data".

How it is held (owner, 2026-10-12: "yes fixed roster sounds good, held back
only ranking makes sense"); the details are written in stage 1:

- A fixed roster. Each model has a card written before it is fitted: its
  inputs, what it is expected to be good at, where it is expected to
  fail, and the regions or issue dates it is meant for.
- One scoreboard. Every model is scored on the same unseen seasons with
  the same measures, beside the trend-only baseline and an equal-weight
  average of the roster.
- The limit to state up front: with about 22 unseen years, the best of
  several models flatters itself. The scoreboard therefore reports every
  model, and the held-back seasons are the only ranking that counts.
- Open: whether "predict the climate data" means burned area only, or
  also the summer's climate (temperature, moisture) as a target of its
  own. The second would be a new target and a new baseline.

### The other El Niño regions (owner's idea, not a commitment)

Owner, 2026-10-12: "flag the other 20ish regions we found to be affected
by el nino and postulate as longer-term prediction targets once model is
fleshed out, because we can use the actual numbers from those regions
(not yet exposed to the codebase) as a cross check of model accuracy."

The 20 regions are listed in the parent's
`docs/enso_regions_out_of_scope.md`, with an "Expansion readiness" table.
Their value as a check rests on staying unseen: no fire or climate data
for them is downloaded or looked at until the model's form is fixed
(owner, 2026-10-12: "yes no data opened"). The owner calls it "not
entirely fleshed out just a spitball idea we can have to make that
project more interesting": it is on the roadmap as a possibility, with
no stage or date.
What to weigh before choosing any:

- The table marks several as having no fire link found or a weak one
  (for example East Africa, the Sahel, Siberia), and several where El
  Niño goes with less fire, not more (US Southwest, southern Africa).
- Several respond during the developing El Niño ("year 0"), not after
  the December to February winter this project pairs with a fire season.
- Each needs its own fire record, its own ERA5-Land download box and a
  licence read; many sources there were read only as abstracts.
- A model tuned on western North America that fails in Sumatra has
  learned something regional. That is a finding, not a failure of the
  check.

## Part 4 · Decisions still open

- Settled 2026-10-12 (owner: "have it download copies for full
  independence"): the sibling downloads its own data and does not read
  the parent's `data/`.
- What the held-back scores are compared with: the trend-only model
  (proposed) and the parent's H3a forecast.
- Whether the sibling's results are ever shown beside the parent's site.

## Part 5 · Prompt for the sibling's first session

```text
Session 1 for a separate work-in-progress project, a sibling of
hydrowhiplash-elnino26.

1. Read docs/kickoff.md (this file, copied in), the parent's
   docs/prediction_model_spec.md and
   results/tables/prediction_v1c/variants.csv at the tag prediction-handoff.
2. Stage 0 only: licence files (MIT for code; all rights reserved for
   writing and figures), a settings file, DECISIONS.md, logs/ with the
   parent's template, DATA_SOURCES.md. Copy the seven pinned tables and
   input_pins.csv from the parent at prediction-handoff, verify each
   sha256, and record the tag and commit.
3. Copy src/prediction.py, prediction_1b.py, prediction_1c.py and their
   tests. Reproduce spring_inputs (0.012, 95% interval -0.001 to 0.032).
   Stop and report if it differs.
4. Draft the held-back-seasons rule and the scoreboard format with me.
   No new fit before both are committed.
5. Explain each concept as it comes up. Flag scope additions rather than
   building them. No data for any region outside the seven is downloaded.
6. End of session: daily log, checks, commit and push.
```
