# Analysis Plan (pre-registered)

Write this **before looking at any fire data**, then commit it. With roughly
10 to 13 El Niño years in the fire record, deciding the tests in advance is what keeps
the p-values honest. Any later change goes in the deviations log at the bottom,
with a date and reason; don't edit the plan above it after freezing.

- **Author:** Dace Roberts
- **Frozen on:** ____-__-__ (commit hash: ________)

## Decisions to make before freezing

- [x] **ENSO index: ONI or RONI.** NOAA now classifies events with the
      Relative Oceanic Niño Index (RONI), which subtracts the warming of the
      whole tropical ocean so events from 1950 and 2026 are judged on the same
      scale. Recommended: **RONI**, with ONI as a robustness check. Confirm
      which index CPC's file provides and set `ENSO_INDEX` (and its URL) in
      `src/config.py`. Chosen: **RONI** (`RONI.ascii.txt`), with every
      headline test re-run on ONI (`ENSO_ROBUSTNESS_INDEX`) and reported in
      one robustness table; conclusions rest on RONI. Reason: NOAA's
      official index (PIS 26-05), so the 2026-27 forecast input and the
      training index match, and 1950s and 2020s winters sit on one scale.
      Chosen on these grounds, not on the descriptive climate numbers, which
      point both ways (`DECISIONS.md` 2026-10-05 "ENSO index: RONI").

Raised by the pre-start review (2026-10-04). Each one changes what a test
means, so settle it here, put any numbers in `src/config.py`, and log the
reasoning in `DECISIONS.md`. Suggested answers are starting points, not
decisions.

**Hypotheses**

- [x] **Test the core variables.** No hypothesis uses the whiplash index,
      snowpack (SWE) or season length, though Phases 2-3 build all three. Add
      a hypothesis for whiplash or SWE (e.g. "low April 1 SWE predicts more
      burned area in PNW/BC/AB"), or label them descriptive only. Test season
      length or drop it.
      *Decided 2026-10-05:* new hypothesis **H6** (snowpack and winter
      dryness predict burned area; table and methods below). Whiplash is a
      descriptive mechanism variable, never tested. Season length is
      computed and reported, descriptive only (undefined with 0-1 fires;
      CNFDB date completeness unchecked).
- [x] **Whiplash timing.** SPEI(JJA) − SPEI(DJF) uses summer, inside the fire
      season, so it can't feed a spring forecast. Either call it a concurrent
      mechanism variable or redefine it winter to spring (DJF to MAM).
      *Decided 2026-10-05:* kept as SPEI-3(JJA) - SPEI-3(DJF), a concurrent,
      descriptive mechanism variable (option D of
      `docs/prefreeze_options.md`); the forecastable parts, winter SPEI-3
      and April 1 SWE, are tested in H6.
- [x] **Directions and sidedness.** SoCal "higher" in H2 is weakly justified
      (the grass effect tends to lag, and a wet winter can delay the season).
      Suggested: SoCal two-sided, add NorCal expectations, and state one- or
      two-sided for every test.
      *Decided 2026-10-05:* see "Directions and sidedness" under
      Hypotheses below.
- [x] **H4's actual test.** With SoCal as baseline there are four interaction
      terms. Name the test: a joint Wald test, or one north-vs-south contrast.
      *Decided 2026-10-05:* one contrast, the mean `enso_djf` slope of PNW,
      BC and AB minus SoCal's, two-sided; the joint Wald test of the four
      interaction terms reported as secondary. NorCal stays in the model,
      outside the contrast; AK and YT are not in the pooled model.
- [x] **H5 definitions.** Fix `precip_anom`'s months (DJF or Oct-Mar),
      baseline period, and units (mm, % of normal or standardised), and give
      the expected sign of lag0 and lag1 per region.
      *Decided 2026-10-05:* `precip_anom` = October-March total
      precipitation (labelled by the March year; ends before every fire
      window opens), as a z-score against the region's 1991-2020 normal.
      Signs under "Directions and sidedness" below.
- [x] **Alaska and Yukon (added 2026-10-04).** Two new regions, AK (Alaska
      east of 169W) and YT, with the role `north`: their own hypothesis
      family, separate from PNW/BC/AB, because El Niño acts there mainly
      through warm springs and early melt rather than a dry winter. State
      which hypotheses include them and their expected directions (winter
      precipitation may not be lower there), and whether Alaska stays one
      region or splits Interior from coast (different biomes; fire is almost
      all Interior). Fire window Apr-Sep is provisional in `config.py`.
      *Decided 2026-10-05 (hypotheses):* own family; H2, H3a and H3b
      two-sided (expected higher, positive; H3b smaller than H3a); H1 and
      H6 descriptive; H4 and H5 not extended to them; March-May mean 2 m
      temperature from ERA5-Land shown as a descriptive spring mechanism
      variable. *Region (decided 2026-10-05):* Alaska stays one region
      (east of 169W), like every other region a whole state or province. A
      probe found a public-domain Interior boundary (NOAA NCEI climate
      divisions 3-5), but splitting only Alaska would break with BC and
      PNW, which share the coast-interior mismatch. The limitation is
      stated for AK, BC and PNW together: climate means include wet coasts
      that rarely burn, which may dilute El Niño signals toward zero, most
      in AK, where fire is almost all Interior.
- [x] **Trend and climate change** [mid-project: D38]. Trend handling below
      covers burned area only. Decide (a) whether the climate variables
      (SWE, snowfall fraction, whiplash, winter precipitation) are compared
      across ENSO phases raw or detrended, by the same one-method rule; and
      (b) whether to test a compounding effect: does the El Niño snowpack or
      burned-area effect grow over time (an El Niño × year interaction, or
      early vs late halves), as a warmer baseline pushes more terrain past
      the rain-snow line? Session 3 found the PNW strong-winter snowpack loss
      concentrated at low and mid-elevation stations (−42 points of normal in
      the lowest third, +3 in the highest). Also decide whether the ONI/RONI
      choice above is reported as the trend-adjusted index for this purpose.
      Pre-register it here or label it exploratory.
      *Decided 2026-10-05:* (a) the climate variables follow the same
      one-method rule as burned area (see "Trend handling" below); (b) two
      secondary compounding tests are pre-registered (see "Secondary tests:
      compounding" below); (c) RONI is reported as the trend-adjusted index
      for them, ONI as the check. The snowpack test is only partly blind:
      session 3's elevation finding hints at it; the interaction itself had
      not been computed when it was registered.

**Data rules**

- [x] **SPEI settings.** Calibration period (e.g. 1951-2020), distribution,
      PET method (Thornthwaite) and scale 3, in `config.py`.
      *Decided 2026-10-04:* calibration 1951-2020, log-logistic by maximum
      likelihood, Thornthwaite (1948) PET, scale 3, per-cell SPEI clipped at
      ±3.09, regional means of per-cell SPEI re-standardised over the
      calibration period (`DECISIONS.md` 2026-10-04 "SPEI settings").
- [x] **SWE source and definition.** Station surveys, ERA5-Land `sd`, or
      both (one as a check on the other); how April 1 is approximated from
      monthly means; glacier cells excluded (ERA5-Land caps them at 10 m).
      *Source decided 2026-10-05:* ERA5-Land April 1 SWE (glacier cells
      excluded) for every test and the forecast, as the z-score against its
      own 1991-2020 regional normal (`era5_swe_z`); every SWE test repeated
      on the station index z (`station_swe_z`) where it exists, both
      reported. Percent of normal for display only. *Definition (decided
      2026-10-04/05):* April 1 is the 00:00 UTC 1 April field of hourly
      ERA5-Land, so no approximation from monthly means; glacier cells
      excluded by the cap-or-perennial-snow rule (D27); station cleaning
      rules and index in `DECISIONS.md` 2026-10-05.
- [x] **Snowfall and soil moisture.** Say whether snowfall fraction and
      summer soil moisture enter any hypothesis (e.g. as mechanism checks
      for a snowpack or burned-area hypothesis) or are descriptive only.
      *Decided 2026-10-05:* descriptive mechanism checks shown beside H6,
      not tested. Seasons and layers as built: snowfall fraction Nov-Mar as
      a ratio of regional totals; soil moisture JJA, 0-28 cm depth-weighted
      (`DECISIONS.md` 2026-10-05 "Snowfall fraction and soil moisture
      columns").
- [x] **Fire windows.** Jun-Oct drops California's Nov-Jan wind-driven fires
      (e.g. Thomas, Dec 2017; Camp and Woolsey, Nov 2018), and northeast BC
      has spring boreal fires like Alberta. Suggested: California through
      December, BC Apr-Oct. Decide now, while fire data is unseen.
      *Decided 2026-10-05:* NorCal and SoCal **June to January of the next
      year** (a January Y+1 fire counts for season Y; the Oct-Jan
      wind-driven season, including January fires); BC **April-October**;
      PNW June-October; AB April-October; AK and YT April-September,
      no longer provisional. Fires are assigned by ignition date.
      California season Y closes only in February Y+1.
- [x] **Fire record rules.** Wildfires only (MTBS includes prescribed burns);
      how fires crossing a region boundary are split (clipped area) and dated
      (ignition date); the MTBS-to-WFIGS cutover year; apply the 405 ha floor
      to computed `area_ha`, not the source's own acres; check CNFDB date
      completeness for season length.
      *Decided 2026-10-05:* MTBS incident types Wildfire, Wildland Fire Use
      and Unknown kept (Unknown counted and reported), Prescribed Fire
      dropped; prescribed burns dropped from the Canadian records wherever
      flagged. The 405 ha floor applies to each fire's whole `area_ha`
      (ESRI:102008, never the source's acres), then the fire is clipped to
      every region it touches and each region gets its clipped hectares;
      dated by ignition (discovery) date. MTBS for every year it holds
      complete, WFIGS after; the cutover year is fixed and recorded at
      download, and the last overlapping year is compared as a reported
      check. CNFDB: share of fires with an ignition date reported by
      decade (season length is descriptive).
- [x] **Zero-fire years.** With a 405 ha floor, a region-year with no fires
      jumps from log(1 + 0) = 0 to about 6, and percent-change reporting
      breaks. Pre-specify handling (e.g. a sensitivity analysis excluding or
      flagging zero years) and report how many there are.
      *Decided 2026-10-05:* zero years kept in the main analysis
      (`log_burn` = 0) and counted per region; a sensitivity analysis
      excludes them; where they exceed 10% of a region's seasons, results
      are given as `log_burn` coefficients with CIs, not percent changes.
      *Near-threshold winters (operational call, decided 2026-10-05):*
      no exclusion; strong-only results (exploratory) get one sensitivity
      run with the strong flag flipped for winters within 0.06 of 1.5
      (RONI: 1965-66 1.53, 1986-87 1.46, 2009-10 1.44).

**Inference**

- [x] **Small-cluster corrections.** About 40 years means about 40 clusters:
      use `use_t=True` (t rather than normal critical values) in the HAC and
      clustered fits, and consider Driscoll-Kraay errors for the pooled
      model, since clustering by year ignores serial correlation within a
      region.
      *Decided 2026-10-05:* `use_t=True` in every HAC and pooled fit; the
      pooled H4 model uses Driscoll-Kraay errors (maxlags 2), with
      year-clustered errors reported alongside. The t degrees of freedom for
      the Driscoll-Kraay fit are set to the number of years minus 1 (about
      41), not left to the software, which counts them from row order
      (pre-freeze code audit, 2026-10-05).
- [x] **Forward validation.** Leave-one-year-out tests interpolation, but
      2027 is a forecast beyond the trend and possibly beyond the observed
      ENSO range. Add expanding-window (forward-chaining) validation.
      *Decided 2026-10-05:* expanding window: fit on fire seasons 1984 to
      Y-1, predict Y, from the first year with 20 training seasons (2004),
      for H3a and the H6 models; 80% interval coverage and prediction
      error reported beside leave-one-year-out.
- [x] **Correction families.** Define each family explicitly (e.g. one per
      hypothesis across regions) and whether H3a and H3b share one.
      *Decided 2026-10-05:* Holm within each family, Benjamini-Hochberg
      alongside. Main regions (PNW, BC, AB, NorCal, SoCal): H1 (5 tests, a
      check), H2 (5), H3a (5), H3b (5, separate from H3a: the same
      coefficient estimated two ways), H5 (10: lag0 and lag1), H6 (9: SWE
      in four regions, winter SPEI in five); H4 is one test. North (AK,
      YT): H2, H3a, H3b, a family of 2 each. C1 and C2: 3 each. ONI and
      station-z robustness runs are not corrected.

## Data and years

- Climate tests (precipitation, temperature, whiplash, SWE): winters 1950–51
  to present (ERA5-Land and the ENSO index both start in 1950).
- Fire tests: fire seasons 1984–present (limited by perimeter records).
- Year convention: the DJF index value labelled year Y is winter (Y-1)–Y and
  is paired with fire season Y.
- ENSO phase: El Niño if DJF index ≥ +0.5 °C, La Niña if ≤ −0.5 °C, otherwise
  neutral. Strong El Niño: ≥ +1.5 °C.
- Regions: PNW (WA/OR/ID), BC, AB, NorCal, SoCal; AK (Alaska east of 169W)
  and YT (Yukon), role `north` [mid-project: D20].

## Outcomes

- **Fires counted:** only fires **≥ 405 ha (1,000 acres)** in every region.
  That is MTBS's mapping threshold in the western US; applying it to the
  Canadian records too keeps US and Canadian data comparable and avoids the
  patchy early coverage of small Canadian fires.
- **Burned area:** total hectares of counted fires per region per fire season,
  as `log_burn = log(1 + ha)`.
- **Fire-season length:** days from the first to the last counted fire.
- **Fire season:** June–October (US regions, BC), April–October (AB),
  April–September (AK, YT; provisional) [mid-project: D20].
- **Trend handling (one method only):**
  - In regressions, the trend is handled by a `year` term on the raw
    `log_burn`. No moving-baseline anomaly is applied first.
  - In permutation and bootstrap tests, which have no control terms, the
    outcome is `burn_detr`: residuals from `log_burn ~ year` per region.
  - The climate variables (SWE, snowfall fraction, whiplash, SPEI, winter
    precipitation, soil moisture) follow the same rule: detrended values
    (residuals from `value ~ year` per region, over the years the variable
    covers) in permutation and bootstrap tests, a `year` term in
    regressions; figures show raw values. Decided 2026-10-05 [mid-project: D38].

## Hypotheses

| ID | Hypothesis | Expected direction |
|---|---|---|
| H1 | Winter precipitation differs in El Niño winters vs the rest | lower in PNW/BC/AB, higher in SoCal |
| H2 | Fire-season burned area differs after El Niño winters vs the rest | higher in PNW/BC/AB; higher in SoCal |
| H3a | **Total effect:** ENSO strength predicts burned area, controlling for the long-term trend only | positive in PNW/BC/AB |
| H3b | **Direct effect:** ENSO strength still predicts burned area after also controlling for summer temperature | smaller than H3a |
| H4 | El Niño's effect on burned area differs between northern regions and SoCal | index × region interaction ≠ 0 |
| H5 | Wet years raise burned area afterwards (whiplash mechanism) | positive lag coefficient, strongest in SoCal |
| H6 | Low April 1 snowpack and a dry winter predict more burned area (added 2026-10-05) | negative in PNW/BC/AB |

### Directions and sidedness (decided 2026-10-05)

| Test | PNW, BC, AB | NorCal | SoCal | AK, YT (own family) |
|---|---|---|---|---|
| H1 winter precipitation | lower, two-sided; a check, not a finding (values seen before the freeze) | two-sided | higher, two-sided | descriptive |
| H2 burned area after El Niño | higher, one-sided | two-sided | two-sided | higher, two-sided |
| H3a ENSO strength | positive, one-sided | two-sided | two-sided | positive, two-sided |
| H3b ENSO strength with `temp_jja` | positive, one-sided; the H3a minus H3b gap reported with a CI, not tested | two-sided | two-sided | positive, two-sided |
| H4 contrast | mean PNW/BC/AB slope minus SoCal slope, two-sided | in model | baseline | not in model |
| H5 lag0 / lag1 | negative one-sided / two-sided | two-sided / two-sided | two-sided / positive one-sided | not extended |
| H6 SWE z / winter SPEI-3 | negative one-sided / negative one-sided | two-sided / two-sided | not applicable / two-sided | descriptive |

Descriptive only, reported but not tested: whiplash (JJA - DJF), season
length, snowfall fraction, summer soil moisture, AK and YT spring (MAM)
temperature.

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
   *H1's months (decided 2026-10-05):* DJF total precipitation
   (`precip_djf_mm`), detrended per region as under "Trend handling".
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
- **Snowpack and winter dryness** (H6): per region, HAC errors,
  `log_burn ~ swe_z + year` and `log_burn ~ spei3_djf + year`, each
  predictor alone (the tests), plus both together reported, not tested
  (they correlate about 0.6). `swe_z` = ERA5-Land April 1 SWE z (station z
  as the check); `spei3_djf` = winter SPEI-3, known by 1 March.
- **Autocorrelation:** report lag-1 autocorrelation of each outcome series;
  moving-block bootstrap (block length 3) as a check on the HAC results.
  `block_bootstrap_ci`.
- **Multiple comparisons:** Holm correction across all region × outcome tests
  within each hypothesis; Benjamini-Hochberg reported alongside.
  `adjust_pvalues`.

## Secondary tests: compounding (decided 2026-10-05 [mid-project: D38])

Outside the headline results; C1 and C2 are each a Holm family of 3 tests.
`year_c` is the year centred on the mean year of the model's data, so the
`enso_djf` coefficient is the effect at mid-record. Per primary region
(PNW, BC, AB), HAC errors as in H3:

- **C1, snowpack:** `swe_z ~ enso_djf + year_c + enso_djf:year_c`,
  winters 1951-2026, `swe_z` = ERA5-Land April 1 SWE z. Expected
  interaction **negative** (El Niño's snowpack loss deepens over time);
  one-sided. Repeated on the station index z where it exists.
- **C2, burned area:** `log_burn ~ enso_djf + year_c + enso_djf:year_c`,
  fire seasons 1984-present. Expected interaction **positive**;
  **two-sided** (about 14 El Niño seasons give little power).
- Early versus late halves of the record are shown as a figure only, not
  tested.

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
