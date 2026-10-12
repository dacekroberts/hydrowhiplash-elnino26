# Prediction model spec (D83): seasonal outlook, exploratory

Written 2026-10-12 on branch `side/prediction-model`, before any model is
fitted. Sections 1 to 6 are the scope the owner agreed on 2026-10-12
("i agree with proposed scope"; `DECISIONS.md` 2026-10-12 "Prediction model
scope agreed"). Section 7 holds the settings the owner agreed the same day, also
before any fit.

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

## 7. Settings agreed on 2026-10-12, before any fit

Each was chosen after `run1` was seen and before any model was fitted
(`DECISIONS.md` 2026-10-12 "Prediction model: settings agreed before the
fit"; D\?a). Values live in `src/config.py` (`PRED_*`).

- **A. Shrinkage.** Only the four climate predictors are shrunk. Each
  region's own level and its own year trend are left unshrunk, so at a
  very large penalty the model is the trend-only baseline exactly. At each
  step the penalty is picked from a fixed grid of 13 values (0.01 to 1000,
  per training row) by leaving out one training year at a time and taking
  the value with the lowest error; the unseen year plays no part.
  Predictors are standardised per region from the training seasons only.
- **B. Yes or no skill.** The Brier score: the average squared gap between
  the forecast probability and what happened (1 or 0). The probability is
  read off the same model's forecast, as the chance the season lands above
  the training cut. Brier skill is reported against two references: the
  one-in-three base rate, and the trend-only model's probability. Beside
  it: hits and false alarms when the probability is 0.5 or more.
- **C. Rule for version 2.** Tried only if the forecast run's skill on log
  burned area, all seven regions together, has a 95% interval wholly above
  zero. The hindsight run does not count. Owner: "interval above zero, if
  lands below have follow-up dialogue": if the rule is not met, the next
  step is a conversation with the owner, not a second model.
- **D. SoCal snowpack.** `era5_swe_z` is empty for all 42 SoCal seasons
  (its 1 April snowpack averages 0.06 mm). It is set to 0 for SoCal, "no
  information", so SoCal stays in the pool.
- **E. SoCal's zero-fire season, 2014** (`log_burn` 0, about 10 log points
  under any other SoCal season) is kept in, as in `run1`. A third run
  without it, in training and in scoring, is shown beside the forecast run.
- **F. Intervals.** The 80% interval is the forecast plus or minus 1.28
  times that region's training residual spread. The interval on skill
  comes from resampling the unseen years 10,000 times, whole years at a
  time so regions in one year stay together, seed 2026.
- **G. Trend and region terms.** One level and one trend per region,
  matching `run1`'s baseline.

## Outputs

`results/tables/prediction_v1/` (the forecast run),
`prediction_v1_hindsight/` and `prediction_v1_no_zero_fire/`, each with
`predictions.csv`, `skill.csv` and `coefficients.csv`, written by
`python -m src.prediction` through `src.run_guard.write_result` with a
provenance record beside each table.
