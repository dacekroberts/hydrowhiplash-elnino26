# Prediction model spec (D83): seasonal outlook, exploratory

Written 2026-10-12 on branch `side/prediction-model`, before any model is
fitted. Sections 1 to 6 are the scope the owner agreed on 2026-10-12
("i agree with proposed scope"; `DECISIONS.md` 2026-10-12 "Prediction model
scope agreed"). Section 7 lists what is not agreed yet; no fit happens
until each line there has the owner's yes and is moved up.

**Status of this analysis.** Planned after all of `run1` was seen,
including `validation.csv` (H3a skill against a trend-only model -0.03 to
+0.01; H6 snowpack up to +0.06). Exploratory, uncorrected, reported apart
from the registered tests, never in place of one
(`docs/post_results_protocol.md` section 2). The registered 2027 forecast
stays the H3a model. Nothing in `results/tables/run1/` is edited.

**Expectation, stated up front.** In `run1` single predictors beat the
trend by at most 0.06 on unseen years. A small gain or none is the likely
outcome, and either is reported plainly.

## 1. Data

Committed tables in `results/tables/` only, opened through
`src.pin_inputs.load_input`. One row per region and fire season, 1984 to
each region's last test year: 291 region-seasons (PNW, AK, NorCal, SoCal
42 each, to 2025; BC, AB, YT 41 each, to 2024).

| Role | Column | Table |
|---|---|---|
| Outcome | `log_burn` = log(1 + ha) | `fire_region_year.csv` |
| Winter index | `enso_djf` (RONI) | `fire_region_year.csv` |
| October to March precipitation | `precip_octmar_mm` | `climate_controls_region_year.csv` |
| 1 April snowpack | `era5_swe_z` | `station_swe_region_year.csv` |
| Winter SPEI-3 | `spei3_djf` | `whiplash_swe_region_year.csv` |
| Year trend | `year` | |
| Hindsight run only | `temp_jja` | `climate_controls_region_year.csv` |

## 2. Version 1: a pooled linear model

One model across the seven regions with region terms and shrinkage
(ridge), so that correlated predictors do not blow up. Predictors are the
five above, all known before the fire season.

## 3. Scoring

Only on seasons the model has not seen: an expanding window from 20
training seasons (first predicted season 2004), every region predicted for
the same year at once. Baseline: the year trend alone. Reported: skill
against the baseline with an interval, and how often the 80% interval held
the real value. Skill is reported per region, and for Alaska and Yukon
apart from the other five. The 2027 season is the first real test.

## 4. Two outcomes

- Total log burned area.
- Yes or no: whether the season falls in the top third of that region's
  seasons. The cut is taken from the training seasons only at each step,
  so the unseen year never sets its own bar. Scored against the base rate
  (one in three).

## 5. Hindsight run

The same model with June to August temperature added, in a separate run
with its own label. It cannot be used to forecast; it shows how much of
the missing skill is summer weather.

## 6. Version 2 and what stays out

- Version 2, only if version 1 beats the trend: a small tree ensemble on
  the same inputs and the same scoring, judged only on the unseen years,
  against version 1.
- Out of both versions: summer weather as a forecasting predictor,
  anything trained on El Niño years only, any claim that replaces a
  registered test.

## 7. Not agreed yet (proposals; nothing here is in force)

Left open by the agreed scope:

- **A. Shrinkage setting**, and how it is chosen inside the training
  seasons only.
- **B. Skill measure for the yes or no outcome.**
- **C. The rule that decides whether version 2 is tried.**

Gaps found while reading the tables (no fit was run to find them):

- **D. SoCal has no snowpack value.** `era5_swe_z` is empty for all 42
  SoCal seasons (its 1 April snowpack averages 0.06 mm).
- **E. SoCal's zero-fire season, 2014.** `log_burn` is 0, about 10 log
  points under any other SoCal season.
- **F. How the 80% interval and the interval on skill are made.** A
  shrunken model has no textbook formula for either.
- **G. Trend and region terms.** The scope says "a year trend" and "region
  terms" without saying whether the trend is shared or one per region.
  `run1`'s baseline is one trend per region.

## Outputs

`results/tables/prediction_v1/` (and `prediction_v1_hindsight/`), written
through `src.run_guard.write_result` with a provenance record beside each
table. Settings in `src/config.py`.
