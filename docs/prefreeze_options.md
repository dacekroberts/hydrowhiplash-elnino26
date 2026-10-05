# Pre-freeze options: whiplash timing, and Alaska and Yukon

Draft for the owner, 2026-10-05. Options with a recommendation for two open
items in `ANALYSIS_PLAN.md` "Decisions to make before freezing": **Whiplash
timing** and **Alaska and Yukon**. Nothing here is decided; the owner picks,
and the choice then goes into `ANALYSIS_PLAN.md`, `src/config.py` and
`DECISIONS.md` as usual. Freeze target about 18 October.

All numbers are descriptive (ONI; 25 El Niño, 7 strong, 25 neutral winters,
1951-2026), from `logs/2026-10-05.md`, `docs/session3_kickoff.md` Part 1 and
D19. "SD" means standard deviations of all winters. No fire data has been
seen.

## What the numbers say so far

El Niño minus neutral winters, per region:

| Region | Whiplash (SD) | Winter SPEI-3 (SD) | Implied summer SPEI-3 (SD) | April 1 SWE | DJF precipitation |
|---|---|---|---|---|---|
| PNW | +0.41 | -0.28 | +0.13 | -6.9% (-0.17 SD) | -5.6% (-0.21 SD) |
| BC | +0.75 | -0.37 | +0.38 | -6.9% (-0.42 SD) | -4.8% (-0.26 SD) |
| AB | +0.92 | -0.47 | +0.45 | -22.9% (-0.56 SD) | -11.8% (-0.52 SD) |
| AK | +0.29 | -0.29 | 0.00 | -0.8% (-0.06 SD) | -3.6% (-0.20 SD) |
| YT | +0.52 | -0.46 | +0.06 | -7.0% (-0.41 SD) | -10.0% (-0.41 SD) |
| NorCal | -0.09 | not listed | not derivable | +30.7% (+0.43 SD) | +9.5% (+0.24 SD) |
| SoCal | -0.81 | +0.74 | -0.07 | not listed | +37.9% (+0.62 SD) |

Strong El Niño winters against all winters: April 1 SWE PNW -22.0%, BC
-12.4%, AB -23.9%, AK -5.4%, YT -1.2%; DJF precipitation PNW -0.3%, BC
+0.5%, AB -14.9%, AK -12.4%, YT -5.8%.

*Implied summer SPEI-3* is whiplash plus winter SPEI-3, since
`src/whiplash.py` defines whiplash = SPEI-3(JJA) - SPEI-3(DJF) on the
re-standardised regional values; it is derived from the rounded numbers
above, not measured separately.

Three readings matter for both items:

1. **The north's positive whiplash is two signals.** Half or more is the dry
   winter (negative winter SPEI); in BC and AB the rest is a *wetter than
   normal summer* (+0.38, +0.45), which works against fire. A positive
   northern whiplash is therefore not "drier overall", and its expected
   relation to burned area is ambiguous.
2. **Snowpack carries the strong-winter signal that precipitation misses.**
   In PNW and BC, strong El Niño winters bring normal precipitation (-0.3%,
   +0.5%) but 12-22% less April 1 snow: the warm-winter path (rain instead
   of snow, earlier melt), not a dry winter.
3. **AK barely responds by April 1** (SWE -0.8%), consistent with the D20
   rationale that El Niño acts there through warm springs and early melt,
   which happen after 1 April in Interior Alaska.

**A caution on circularity.** Winter precipitation, SPEI and SWE have now
been looked at descriptively, so any hypothesis about them (H1, or a
"El Niño lowers SWE" test) is no longer a blind test: its result is largely
known. The confirmatory tests are the ones about burned area, which nobody
has seen. The options below keep the climate variables as mechanism checks
or predictors, not as new confirmatory hypotheses.

## Item 1 · Whiplash timing

The plan's item: SPEI(JJA) - SPEI(DJF) uses summer, inside the fire season,
so it can't feed a spring forecast; either call it a concurrent mechanism
variable or redefine it winter to spring (DJF to MAM).

**What constrains it.** Fire windows start in **June** for PNW, BC, NorCal
and SoCal but in **April** for AB, AK and YT (`config.FIRE_SEASON_MONTHS`).
Anything measured after March is inside the fire season for half the
regions. Known before every window opens: winter SPEI-3 (end of February)
and April 1 SWE.

### Options

**A. Keep JJA - DJF as a concurrent mechanism variable.** Report it, use it
in H5-style mechanism checks, never as a forecast predictor.
- Good: built and cached; captures SoCal's wet-to-dry swing.
- Weak: no forecasting use; in the north it mixes a dry winter with a wet
  summer, so its sign for fire is unclear.
- Expected signs (burned area on whiplash): SoCal negative (wet winter then
  dry summer, i.e. more negative whiplash, more fire); north none stated.
  Sidedness: two-sided everywhere.

**B. Redefine as MAM - DJF (winter to spring).** SPEI-3 at May minus SPEI-3
at February; the two windows don't overlap. Cheap from the per-cell cache.
- Good: avoids summer; a spring index for June-start regions.
- Weak: still inside the fire season for AB, AK and YT (April start), so not
  a forecast predictor there; a new variable nobody has looked at, so its
  behaviour is unknown.
- Expected signs: north negative MAM - DJF less likely (a dry winter raises
  it); fire on index unclear. Sidedness: two-sided.

**C. Drop the difference; use its parts.** Pre-register **winter SPEI-3**
and **April 1 SWE** as the forecast predictors (both known by 1 April in
every region) and keep JJA SPEI-3 as a concurrent control, alongside
`temp_jja` in H3b.
- Good: forecastable for all seven regions; each part has a clear expected
  sign; separates the dry-winter path (SPEI) from the warm-winter path
  (SWE), which item 2 above shows differ in PNW and BC.
- Weak: no single "whiplash" number; SPEI and SWE are correlated, so in one
  model their coefficients share variance (report each alone and both
  together).
- Expected signs (burned area on predictor): north (PNW, BC, AB) winter
  SPEI-3 negative, April 1 SWE negative, **one-sided**; SoCal winter SPEI-3
  positive if the grass path holds (wet winter, more fine fuel) but it may
  lag a year (H5), **two-sided**; NorCal **two-sided**; AK and YT see item 2.

**D. A and C together.** C for the tests and the forecast; A's JJA - DJF
kept as a descriptive mechanism variable in figures and in H5's discussion.

### Recommendation: D

C is the only option that gives every region a predictor known before its
fire season opens, which the 2027 forecast needs, and it splits the two
northern paths that the numbers show behave differently. Keeping the
existing whiplash as a described, untested variable (A) costs nothing and
keeps SoCal's wet-to-dry story visible. B adds a new index with no
forecasting use for half the regions.

What D would change in the plan: the "Test the core variables" item gets
its answer (SWE and winter SPEI become predictors; whiplash descriptive);
H5 states whiplash as a mechanism variable, not a test; `whiplash_table`
stays as is.

## Item 2 · Alaska and Yukon

The plan's item: say which hypotheses include AK and YT and their expected
directions (winter precipitation may not be lower), and whether Alaska stays
one region or splits Interior from coast. They form their own family (role
`north`), separate from PNW/BC/AB, so the existing Holm families are
unchanged (D20).

### Options for the hypotheses

**A. Descriptive only.** AK and YT appear in every table and figure, with no
confirmatory test.
- Good: honest about a weak, different mechanism and a late addition; no
  extra multiple-comparison burden.
- Weak: the owner added them for a reason (the reported El Niño link to
  Interior Alaska fire); nothing would test it.

**B. Their own family, two-sided, with stated expected signs.** Burned-area
hypotheses only (H2, H3a, H3b), Holm within the north family.
- H2 (burned area after El Niño): expected higher; **two-sided**.
- H3a/H3b (ENSO strength on burned area, trend only / plus `temp_jja`):
  expected positive; H3b smaller than H3a if the warm-season path carries
  the effect; **two-sided**.
- H1 (winter precipitation): **descriptive only** (seen: AK -3.6%, YT
  -10.0%; strong AK -12.4%, YT -5.8%).
- H4 (north vs SoCal interaction) and H5: not extended to AK and YT.
- Mechanism variable: a spring one, since April 1 is too early there
  (AK SWE -0.8%). Candidates: MAM temperature from ERA5-Land, or SWE on
  1 May; descriptive, chosen before the freeze.
- Good: tests the reason they were added, with no claim of direction
  strength the precursors don't support.
- Weak: two-sided tests on about 40 fire seasons have little power; a null
  is the likely outcome and must be reported as such.

**C. Their own family, one-sided** (burned area higher after El Niño).
- Good: more power.
- Weak: the precursors are mixed (AK's April snowpack doesn't move; its
  winter is only slightly drier), so a one-sided claim rests on the
  literature link alone, which the plan hasn't cited yet.

**D. Fold into the primary family.** Rejected in D20 (it would dilute the
PNW/BC/AB corrections and mix mechanisms); listed for completeness.

### Recommendation: B

It tests what they were added for, states expected signs without
overclaiming, keeps H1 descriptive now that winter precipitation has been
seen, and leaves the primary family's power untouched. If the owner finds a
citable source for the El Niño-Interior Alaska fire link before the freeze,
C becomes defensible for H2.

### Alaska as one region or Interior and coast

**A. Keep one region (east of 169W).** Simple and already built. The
state-wide climate mean is dominated by the wet south coast, while fire is
almost all Interior, so climate predictors and fire would describe different
places.

**B. Split Interior from coast.** Needs a boundary with clear terms (e.g.
NOAA's Alaska climate divisions, mentioned in DECISIONS.md 2026-10-04), its
licence read, a change to `src/regions.py` and `config.REGIONS`, and a
re-run of the region tables. Fire would then be counted in Interior only.

**C. One region for climate, Interior fire only.** Keep the polygon, but
count only fires in an Interior boundary. Mismatched the other way: the
predictors would still describe the whole state.

**Recommendation: B if a licensed boundary is found in the next few days,
otherwise A with the mismatch stated as a limitation.** Finding and reading
the licence of a boundary source is a data-free task the side session can
take. The split doesn't need fire data.

## Summary of expected signs and sidedness under the recommendations

| Test | PNW, BC, AB | AK, YT | NorCal | SoCal |
|---|---|---|---|---|
| Burned area on winter SPEI-3 | negative, one-sided | descriptive | two-sided | positive if grass path, two-sided |
| Burned area on April 1 SWE | negative, one-sided | descriptive (spring variable instead) | two-sided | not applicable (little snow) |
| H2, burned area after El Niño | as the plan (higher) | higher, two-sided | two-sided | two-sided (plan's open item) |
| H3a/H3b, ENSO strength | as the plan (positive) | positive, two-sided; H3b smaller | two-sided | two-sided |
| Whiplash JJA - DJF | descriptive | descriptive | descriptive | descriptive (expected negative after El Niño) |
| H1, winter precipitation | descriptive (already seen) | descriptive | descriptive | descriptive |

The SoCal and NorCal cells follow the plan's open "Directions and
sidedness" item (suggested: SoCal two-sided, NorCal expectations added);
they are listed for completeness and decided there.
