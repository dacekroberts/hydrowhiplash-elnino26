# Analysis Plan (pre-registered)

Write this **before looking at any fire data**, then commit it. With roughly
10 to 13 El Niño years in the fire record, deciding the tests in advance is what keeps
the p-values honest. Any later change goes in the deviations log at the bottom,
with a date and reason; don't edit the plan above it after freezing.

- **Author:** Dace Roberts
- **Frozen on:** ____-__-__ (commit hash: ________)

## Decisions to make before freezing

- [ ] **ENSO index: ONI or RONI.** NOAA now classifies events with the
      Relative Oceanic Niño Index (RONI), which subtracts the warming of the
      whole tropical ocean so events from 1950 and 2026 are judged on the same
      scale. Recommended: **RONI**, with ONI as a robustness check. Confirm
      which index CPC's file provides and set `ENSO_INDEX` (and its URL) in
      `src/config.py`. Chosen: ______ Reason: ______

Raised by the pre-start review (2026-10-04). Each one changes what a test
means, so settle it here, put any numbers in `src/config.py`, and log the
reasoning in `DECISIONS.md`. Suggested answers are starting points, not
decisions.

**Hypotheses**

- [ ] **Test the core variables.** No hypothesis uses the whiplash index,
      snowpack (SWE) or season length, though Phases 2-3 build all three. Add
      a hypothesis for whiplash or SWE (e.g. "low April 1 SWE predicts more
      burned area in PNW/BC/AB"), or label them descriptive only. Test season
      length or drop it.
- [ ] **Whiplash timing.** SPEI(JJA) − SPEI(DJF) uses summer, inside the fire
      season, so it can't feed a spring forecast. Either call it a concurrent
      mechanism variable or redefine it winter to spring (DJF to MAM).
- [ ] **Directions and sidedness.** SoCal "higher" in H2 is weakly justified
      (the grass effect tends to lag, and a wet winter can delay the season).
      Suggested: SoCal two-sided, add NorCal expectations, and state one- or
      two-sided for every test.
- [ ] **H4's actual test.** With SoCal as baseline there are four interaction
      terms. Name the test: a joint Wald test, or one north-vs-south contrast.
- [ ] **H5 definitions.** Fix `precip_anom`'s months (DJF or Oct-Mar),
      baseline period, and units (mm, % of normal or standardised), and give
      the expected sign of lag0 and lag1 per region.

**Data rules**

- [ ] **SPEI settings.** Calibration period (e.g. 1951-2020), distribution,
      PET method (Thornthwaite) and scale 3, in `config.py`.
- [ ] **Fire windows.** Jun-Oct drops California's Nov-Jan wind-driven fires
      (e.g. Thomas, Dec 2017; Camp and Woolsey, Nov 2018), and northeast BC
      has spring boreal fires like Alberta. Suggested: California through
      December, BC Apr-Oct. Decide now, while fire data is unseen.
- [ ] **Fire record rules.** Wildfires only (MTBS includes prescribed burns);
      how fires crossing a region boundary are split (clipped area) and dated
      (ignition date); the MTBS-to-WFIGS cutover year; apply the 405 ha floor
      to computed `area_ha`, not the source's own acres; check CNFDB date
      completeness for season length.
- [ ] **Zero-fire years.** With a 405 ha floor, a region-year with no fires
      jumps from log(1 + 0) = 0 to about 6, and percent-change reporting
      breaks. Pre-specify handling (e.g. a sensitivity analysis excluding or
      flagging zero years) and report how many there are.

**Inference**

- [ ] **Small-cluster corrections.** About 40 years means about 40 clusters:
      use `use_t=True` (t rather than normal critical values) in the HAC and
      clustered fits, and consider Driscoll-Kraay errors for the pooled
      model, since clustering by year ignores serial correlation within a
      region.
- [ ] **Forward validation.** Leave-one-year-out tests interpolation, but
      2027 is a forecast beyond the trend and possibly beyond the observed
      ENSO range. Add expanding-window (forward-chaining) validation.
- [ ] **Correction families.** Define each family explicitly (e.g. one per
      hypothesis across regions) and whether H3a and H3b share one.

## Data and years

- Climate tests (precipitation, temperature, whiplash, SWE): winters 1950–51
  to present (ERA5-Land and the ENSO index both start in 1950).
- Fire tests: fire seasons 1984–present (limited by perimeter records).
- Year convention: the DJF index value labelled year Y is winter (Y-1)–Y and
  is paired with fire season Y.
- ENSO phase: El Niño if DJF index ≥ +0.5 °C, La Niña if ≤ −0.5 °C, otherwise
  neutral. Strong El Niño: ≥ +1.5 °C.
- Regions: PNW (WA/OR/ID), BC, AB, NorCal, SoCal.

## Outcomes

- **Fires counted:** only fires **≥ 405 ha (1,000 acres)** in every region.
  That is MTBS's mapping threshold in the western US; applying it to the
  Canadian records too keeps US and Canadian data comparable and avoids the
  patchy early coverage of small Canadian fires.
- **Burned area:** total hectares of counted fires per region per fire season,
  as `log_burn = log(1 + ha)`.
- **Fire-season length:** days from the first to the last counted fire.
- **Fire season:** June–October (US regions, BC), April–October (AB).
- **Trend handling (one method only):**
  - In regressions, the trend is handled by a `year` term on the raw
    `log_burn`. No moving-baseline anomaly is applied first.
  - In permutation and bootstrap tests, which have no control terms, the
    outcome is `burn_detr`: residuals from `log_burn ~ year` per region.

## Hypotheses

| ID | Hypothesis | Expected direction |
|---|---|---|
| H1 | Winter precipitation differs in El Niño winters vs the rest | lower in PNW/BC/AB, higher in SoCal |
| H2 | Fire-season burned area differs after El Niño winters vs the rest | higher in PNW/BC/AB; higher in SoCal |
| H3a | **Total effect:** ENSO strength predicts burned area, controlling for the long-term trend only | positive in PNW/BC/AB |
| H3b | **Direct effect:** ENSO strength still predicts burned area after also controlling for summer temperature | smaller than H3a |
| H4 | El Niño's effect on burned area differs between northern regions and SoCal | index × region interaction ≠ 0 |
| H5 | Wet years raise burned area afterwards (whiplash mechanism) | positive lag coefficient, strongest in SoCal |

**Why H3 is split.** El Niño makes PNW, BC and Alberta summers warmer, so summer
temperature sits *on the path* from El Niño to fire. Controlling for it removes
part of the very effect being measured. H3a estimates El Niño's whole effect;
H3b estimates what's left beyond the warming. The gap between them is a rough
measure of how much of the effect runs through summer heat.

## Headline methods

1. **Permutation test + bootstrap CI** (H1, H2). Difference in means, El Niño
   years vs all other years, per region, on `burn_detr` (H2) or winter
   precipitation anomaly (H1). 10,000 permutations; 95% percentile bootstrap
   CI. `src/stats.py: permutation_test, bootstrap_ci_diff`.
2. **Regression with controls**, per region, Newey-West (HAC) errors with
   maxlags = 2 (`fit_ols_hac`):
   - H3a: `log_burn ~ enso_djf + year`
   - H3b: `log_burn ~ enso_djf + temp_jja + year`
3. **Interaction term** (H4), regions pooled, errors clustered by year
   (`fit_pooled`):
   `log_burn ~ enso_djf * C(region, Treatment('SoCal')) + C(region):year`
   (a separate trend per region; reported with and without `temp_jja`).
4. **Leave-one-year-out prediction intervals** for the 2027 forecast: 80%
   intervals from the H3a model; report empirical coverage. `loyo_prediction`.

## Supporting methods

- **Lag test** (H5): `log_burn ~ precip_anom_lag0 + precip_anom_lag1 + year`,
  where lag0 = the preceding winter and lag1 = the winter before that.
  HAC errors.
- **Autocorrelation:** report lag-1 autocorrelation of each outcome series;
  moving-block bootstrap (block length 3) as a check on the HAC results.
  `block_bootstrap_ci`.
- **Multiple comparisons:** Holm correction across all region × outcome tests
  within each hypothesis; Benjamini-Hochberg reported alongside.
  `adjust_pvalues`.

## Reporting rules

- Effect sizes and confidence intervals first, p-values second.
  Coefficients on `log_burn` are reported as percent changes:
  `100 * (exp(b) − 1)`.
- Report every pre-registered test, including the null results.
- Strong-El-Niño-only results are exploratory and labelled as such.
- Significance threshold: α = 0.05 after correction.

## Deviations log

| Date | Change | Reason |
|---|---|---|
| | | |
