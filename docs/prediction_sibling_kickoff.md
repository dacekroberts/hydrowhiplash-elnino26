# Kickoff: a sibling project for the fire-season prediction model

Written 2026-10-12 by the `side/prediction-model` session, at the owner's
request, for the main-checkout session to pick up after PR #24 merges.
A draft: every proposal below is the session's recommendation, and
nothing in it is adopted until the owner says yes. The owner's view so
far: further work can leave this project's pipeline, and a project that
derives from this one is a sibling of it.

## 1. Why a separate project

Three versions of an exploratory model were built here from committed
tables only (`docs/prediction_model_spec.md`; `results/tables/`
`prediction_v1/`, `prediction_v1b/`, `prediction_v1c/`). The next step
meets all three conditions the session proposed for splitting off:

1. **It needs data this project does not hold** (new downloads, new
   licence reads).
2. **Its unit or target differs** from this project's region × season
   tables.
3. **It needs its own clean test.** Six forecasting variants have been
   scored on the same 22 unseen years, so more variants here would only
   flatter the best one.

It also keeps the registered work clean: the 2027 forecast stays the H3a
model, and nothing in `results/tables/run1/` is touched by either
project.

## 2. What this project established

Skill = 1 minus the model's RMSE over the RMSE of a trend-only model
(`log_burn ~ year` per region), on 151 unseen region-seasons, 2004 to
2025, each predicted from earlier seasons only; 95% intervals from
resampling whole years. Exploratory, uncorrected.

| Run | All seven regions | Reading |
|---|---|---|
| Version 1, spring inputs | 0.002 (-0.007 to 0.015) | no gain over the trend |
| Version 1b, best of five (`spring_inputs`) | 0.012 (-0.001 to 0.032) | about 1%; NorCal 0.067, AB 0.052, PNW 0.025, each interval reaching zero |
| Version 1c, last season's burned area added | 0.008 (-0.008 to 0.025) | no help |
| Hindsight, summer temperature known | 0.090 (0.030 to 0.184) | cannot forecast |
| Ceiling, summer temperature, SPEI-3 and soil moisture known | 0.126 (0.061 to 0.231) | cannot forecast |

The ceiling splits by region: BC 0.483 (0.351 to 0.594), AK 0.345
(0.162 to 0.513), NorCal 0.257 (0.130 to 0.383), YT 0.221 (0.027 to
0.444); PNW 0.020, AB 0.003, SoCal -0.038. Summer soil moisture carried
the largest summer coefficient in every region.

What that leaves:

- **Winter and spring inputs at region scale are used up.** ENSO,
  October to March precipitation, 1 April snowpack, winter SPEI-3, last
  winter's precipitation, the snowfall share, March to May temperature
  and last season's burned area together buy about 1%.
- **In BC, AK, NorCal and YT the summer's moisture explains a fifth to a
  half of the error.** Inputs that carry information about the summer
  are worth trying there.
- **In AB, PNW and SoCal seasonal means over a whole province or state
  explain nothing.** Those need a different target, unit or season
  window, not more inputs. Possible reasons, none tested: Alberta's
  largest fires start in May; PNW and SoCal burned area is driven by
  short wind events.
- **Two known weak points of the baseline:** a straight trend runs ahead
  of AB and behind BC (14% and 62% of unseen seasons above the yes or no
  bar), and SoCal 2014, the one zero-fire season, is 28% of the pooled
  squared error unless each region is put on its own scale.
- **Limits of the ceiling:** linear, three seasonal means, whole
  regions, so a low estimate; June to August soil moisture is measured
  while the season is under way; the regional split was read after the
  run, and the 0.15 and 0.20 guide values were the session's, not
  confirmed by the owner.

## 3. What carries over

- **Inputs, read at a tagged commit of this repo** (proposal: tag the
  squash commit of PR #24, e.g. `prediction-handoff`): the seven tables
  in `PINNED_RESULT_TABLES` and `input_pins.csv`. 291 region-seasons:
  1984-2025 for PNW, AK, NorCal and SoCal; 1984-2024 for BC, AB and YT.
- **Code to copy or import** (MIT): `src/prediction.py` (pooled ridge
  with unshrunk region levels and trends, expanding-window scoring,
  Brier skill, year-block bootstrap), `src/prediction_1b.py` (regional
  coefficients shrunk toward a shared one, per-region scale, intervals
  from earlier errors), `src/prediction_1c.py`, and their 36 tests on
  synthetic data.
- **Baselines to beat, already written:** `prediction_v1c/variants.csv`
  (every variant on one page) and each variant's `predictions.csv`.
- **Habits worth keeping:** variants and a reading guide written and
  committed before any fit; every variant reported; one settings file;
  a provenance record beside every table; a decisions log; licences read
  before anything derived is published.
- **Data the sibling cannot get from this repo:** everything under
  `data/` (ERA5-Land, fire perimeters) lives only in the owner's main
  checkout. The sibling either reads that folder in place or downloads
  again with this project's scripts.

## 4. Candidate work, in the session's suggested order

1. **Hold back the test seasons first.** No model in the sibling is
   tuned on the 2025 Canadian season, the 2026 season or the 2027
   season. They are scored once, as they arrive.
2. **Later issue dates** (1 April, 1 June, 1 July, 1 August) from
   monthly ERA5-Land already in `data/`: spring and early-summer soil
   moisture, SPEI and temperature. Cheapest route to summer information,
   and it tests the soil-moisture finding directly.
3. **A seasonal forecast of the summer as an input:** ECMWF SEAS5
   hindcasts of June to August temperature and precipitation issued 1
   May (Copernicus Climate Data Store; the session's understanding is
   that hindcasts start in 1981 or 1993 depending on the product, to be
   checked). A new source: ledger row and licence read first.
4. **Spring fuel dryness:** snow-off date, 1 May snowpack, May vapour
   pressure deficit, and Canada's Fire Weather Index drought code, which
   carries over the winter (a Copernicus fire-danger reanalysis exists;
   coverage and licence to be checked).
5. **Smaller units for AB, PNW and SoCal:** ecoregions or fire zones,
   and for Alberta a spring window apart from the summer one. This
   rebuilds the fire and climate tables, so it is the largest step.
6. **Other targets:** counts of large fires, or the chance of a
   top-decile season, which one fire dominates less than total area.
7. **Only then machine learning,** and on a grid-cell and month table
   (tens of thousands of rows), not on 291 region-seasons.

Out of scope unless the owner says otherwise: predicting individual
weather events (owner, 2026-10-12: "predicting actual weather events
which is out of scope here").

## 5. Decisions for the owner before the first session

- **Go or no-go** on a sibling project at all, and its name.
- **Where it lives:** its own repository (the session's recommendation,
  with its own roadmap, decisions log and licence files) or a folder in
  this one.
- **Regions:** all seven, or the four where the ceiling is high first.
- **Which of steps 2 to 6 is first.** The session recommends step 2.
- **Registered or exploratory:** whether the 2026 and 2027 held-back
  scores are written down in advance as a registered test of the
  sibling. The session recommends yes, since they are the only clean
  seasons.
- **Published or private,** and whether it is shown beside this
  project's site.

## 6. First session of the sibling, proposed

1. Read this file, `docs/prediction_model_spec.md` and
   `results/tables/prediction_v1c/variants.csv`.
2. Create the repository, with a roadmap, a decisions log, a settings
   file, a data-sources ledger and the split licence the owner chooses.
3. Pin the parent tables at the handoff tag and reproduce the 1b
   `spring_inputs` figure (0.012) from them, to prove the copied code.
4. Write the held-back-seasons rule and the first step's variants, and
   commit them before any fit.
