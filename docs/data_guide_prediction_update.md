# Data guide update: prediction model (versions 1 and 1b)

For the main-checkout session that merges the `side/prediction-model` PR.
The private data guide (https://claude.ai/artifact/3AYyz3EQbj3tyjTbPYdH8P)
is refreshed only from the main checkout, so this side session wrote the
additions here instead of publishing them. Each block below is ready to
paste into the guide's HTML at the place named. It uses the guide's own
classes and was written against the guide as published at snapshot commit
9d2bd9c (session 9).

Sources: `docs/data_dictionary.md` sections 8c and 8d, the `PRED_*` and
`PRED_1B_*` settings in `src/config.py`, `docs/methods_register.md`
("Prediction model"), `results/tables/prediction_v1/*/skill.csv` and
`results/tables/prediction_v1b/variants.csv`. If a block and the repo
disagree, the repo wins.

Block 3 names the two placeholder deviations of this PR. The merge numbers
them there with every other reference (`merge_append_only.py` rewrites the
files the PR changes). Once the guide is republished, this file can be
deleted.

## 1. Header legend: one chip

Append inside `<div class="legend">`, after the S9 chip (and after any
chip a later session added):

```html
<span class="chip"><span class="s fire">PM</span> prediction model, exploratory, 12 Oct</span>
```

## 2. "Derived variables" table: two rows

Append at the end of the table's `<tbody>`, after "Result tables of run1":

```html
<tr><td class="name">Prediction model tables, version 1<small>exploratory, after run1; never replaces a registered test</small></td><td>Three runs, each in its own sub-folder with the same three tables and a <code>.provenance.json</code> beside each: <code>forecast/</code> (inputs known in spring), <code>hindsight/</code> (June to August temperature added, so it cannot forecast) and <code>no_zero_fire/</code> (the forecast run without SoCal 2014). <code>predictions.csv</code>: one row per region and unseen season, 2004 to the region's last year (151 rows): actual and predicted <code>log_burn</code>, the 80% interval, whether it held, the ridge penalty chosen, and a yes or no outcome (<code>actual_yes</code>: above the two-thirds quantile of the region's training seasons) with the model's probability <code>p_yes</code>; columns ending <code>_trend</code> give the same for the trend-only baseline. <code>skill.csv</code>: one row per scope (all seven, AK and YT, other five, each region): RMSE and MAE, <code>skill</code> = 1 − RMSE ÷ RMSE of the trend-only model (above 0: the inputs beat the trend), interval coverage, Brier scores (mean squared gap between a probability and the 0 or 1 outcome; lower is better) with skill against a constant one in three and against the trend-only model, hits and false alarms, and 95% intervals from resampling whole unseen years. <code>coefficients.csv</code>: per predicted year, each input's coefficient per 1 SD of the input. Trap: burned area trends up, so 83 of 151 unseen seasons are "yes" under a cut taken from earlier seasons.</td><td class="units">log points; probabilities 0 to 1; skill unitless</td><td><code>results/tables/prediction_v1/</code></td><td><span class="s fire">PM</span></td></tr>
<tr><td class="name">Prediction model tables, version 1b<small>exploratory; changed after version 1 was seen</small></td><td>One sub-folder per variant, six fixed before any was run: <code>regions</code>, <code>scaled</code>, <code>regions_scaled</code>, <code>spring_inputs</code>, <code>june_update</code>, <code>hindsight</code> (the last cannot forecast), each with the three tables of version 1, and <code>variants.csv</code> comparing them all with version 1 rescored the same way. New inputs: <code>precip_anom_lag1</code>, <code>snowfall_frac</code>, and <code>temp_mam</code> in <code>june_update</code> only. New columns: <code>penalty_shared</code> and <code>penalty_region</code> (two ridge penalties: one on the coefficient all regions share, one on each region's departure from it; <code>inf</code> in the second means no departures); <code>scale</code> (the region's training spread around its trend) and <code>skill_scaled</code> (skill with each error divided by its region's <code>scale</code>, so regions count about equally in a pooled row); <code>cut_above_trend</code> (the yes or no bar is now a distance above the trend line, so 57 of 151 seasons are "yes"; not comparable with version 1's bar); <code>spread_from</code> (whether the 80% interval came from the region's earlier unseen-year errors, once 8 exist, or from the training spread). <code>coefficients.csv</code> is long: one row per predicted year, region and input. Trap: the variants share the same 22 unseen years, so the best of them flatters itself; read the whole table.</td><td class="units">log points; probabilities 0 to 1; skill unitless</td><td><code>results/tables/prediction_v1b/</code></td><td><span class="s fire">PM</span></td></tr>
```

## 3. "Settings in use" table: one row

Append at the end of the table's `<tbody>`, after "Predictor
autocorrelation":

```html
<tr><td class="name">Prediction model (exploratory)</td><td>Planned after <code>run1</code> was seen (D83), uncorrected, reported apart from the registered tests; the registered 2027 forecast stays the H3a model. Reads only committed tables. Outcome <code>log_burn</code>; inputs standardised within region on the training seasons. Version 1 inputs (<code>PRED_PREDICTORS</code>): <code>enso_djf</code>, <code>precip_octmar_mm</code>, <code>swe_z</code>, <code>spei3_djf</code>; hindsight adds <code>temp_jja</code>. SoCal's <code>swe_z</code> is set to 0, "no information" (<code>PRED_NO_SNOW_REGIONS</code>; D?a). Model: ridge regression (least squares with a penalty that shrinks the input coefficients toward 0) pooled over the seven regions, with each region's level and year trend left unshrunk, so an infinite penalty is exactly the trend-only model. Penalty picked from 13 values, 0.01 to 1000 per training row (<code>PRED_RIDGE_GRID</code>), by leaving one year out inside the training seasons. Scored on unseen years only: at least 20 training seasons (<code>FORWARD_MIN_TRAIN_YEARS</code>), so 2004 onward, all regions predicted for a year at once. Yes or no outcome: top third (<code>PRED_TOP_SHARE</code>), a "yes" call at probability 0.5 or more. Skill intervals 95%, whole unseen years resampled, 10,000 draws, seed 2026. Groups: all seven, AK and YT, other five. Version 1b (D?b): 7 values for each of two penalties (<code>PRED_1B_GRID</code>); spring inputs add <code>precip_anom_lag1</code> and <code>snowfall_frac</code> (<code>PRED_1B_SPRING</code>), the June update adds <code>temp_mam</code>; intervals from a region's earlier unseen-year errors once 8 exist (<code>PRED_1B_MIN_PAST_ERRORS</code>). Rule agreed before the fit for trying machine learning: the skill interval wholly above zero, otherwise a follow-up conversation. Not met.</td></tr>
```

## 4. "What the data says so far": two cards

Append inside `<div class="facts">`, after the last card. Plain cards
(no `key` class): these are exploratory, and the two `run1` cards stay
the headline.

```html
<div class="fact"><span class="eyebrow">Prediction model, exploratory · skill over the trend</span><span class="big num">+0.012</span><p>Best forecasting variant of version 1b (<code>spring_inputs</code>): error 1.2% below a trend-only model on 151 unseen region-seasons, 2004 to 2025; 95% interval −0.001 to 0.032. Version 1: 0.002 (−0.007 to 0.015). By region: NorCal 0.067, AB 0.052, PNW 0.025, each with an interval reaching zero; BC 0.005, YT 0.003, AK −0.003, SoCal −0.005. AK and YT together 0.000 (−0.019 to 0.020). Best of five variants on the same 22 years, uncorrected.</p></div>
<div class="fact"><span class="eyebrow">Prediction model · with summer temperature known</span><span class="big num">+0.09</span><p>The hindsight run, which cannot forecast: 0.096 (0.041 to 0.183) in version 1, 0.090 (0.030 to 0.184) in version 1b. Most of what the spring inputs miss is the summer itself. Yes or no outcome, <code>spring_inputs</code>: Brier skill against the trend-only model 0.023 (−0.002 to 0.048). 80% intervals held 77.5% of seasons (BC 62%).</p></div>
```

## 5. Header eyebrow, lede and footer

- Eyebrow: add "and the exploratory prediction model" after the session
  it names.
- Lede, one sentence at the end: "A side session on 12 October built an
  exploratory prediction model from the committed tables
  (`results/tables/prediction_v1/` and `prediction_v1b/`): spring inputs
  cut the error of a trend-only model by about 1%, with an interval
  that reaches zero; it is reported apart from the registered tests."
- Footer snapshot line: set the commit to the squash commit of this PR
  and add "prediction model versions 1 and 1b (exploratory; settings
  `PRED_*` and `PRED_1B_*` added to `src/config.py`; no registered
  result, input or fire number changed)".
