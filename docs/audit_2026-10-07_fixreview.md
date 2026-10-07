# Read-only review of the pre-freeze fixes: 97663e5..ee9503d (2026-10-07)

Commit reviewed: `main` at `ee9503d` (2 commits, 17 files since `97663e5`).
Read-only session: `git status` clean before and after; scripts in the session
scratchpad outside the repo; no `src` module that writes files was run (only
its functions were imported); pytest run with no cache and no bytecode; no
fire data opened. Order: CLAUDE.md, data dictionary and ANALYSIS_PLAN first;
then code, data and recomputation; only then DECISIONS (2026-10-07),
plan_deviations D49-D51, the methods register and the saved audit.

Saved outside the repo at the owner's request so it survives the review
session; the main session may copy it to `docs/` as the earlier audit was.

## 1. What passed

| Check | Result |
|---|---|
| Tests | 210 passed |
| Per-cell SPEI from raw ERA5-Land | Own Thornthwaite with an independent day-length formula agrees with `pet_thornthwaite` within 1.5-3.3 mm/month on 7 cells (1-2%, the day-length formula only). Own 3-month sums of monthly amounts plus an own log-logistic fit reproduce the cache to 0.001 in February on 5 of 7 cells; where the own fit diverged, xclim's fit had the higher log-likelihood in every case (multi-start check on 4 cells x 2 months found no better optimum), so the cache is the ML optimum |
| Regional SPEI | Rebuilt from the cache with the region masks: max difference 4e-16; `results/tables` equals `data/processed`; re-standardisation reproduces from the cell-mean columns; 0 glacier cells carry SPEI; fitted cells 33,867 main and 33,850 north match `whiplash_run.log`; region cells with SPEI PNW 7,331, BC 12,980, AB 9,457, NorCal 2,802, SoCal 1,297, AK 25,379, YT 8,471 |
| Station table | Rebuilt in memory from the raw files with the `src.stations` functions: identical 71,250 rows and 2,168 stations; dedupe 18 pairs, 509 rows dropped (PNW 352, YT 123, AK 34); the old all-years rule gives 24 pairs; the 6 pairs no longer merged are exactly the six the register names. Index rebuilt: identical; 933 stations with a normal; z runs contiguous (PNW, BC 1951-2026; AK 1960-2026; AB 1963-2025; YT 1975-2026); minimum 5 stations everywhere |
| Table changes old to new | DJF max 0.146 (AB 1979), JJA 0.049, whiplash 0.160; El Niño minus neutral BC DJF -0.54, JJA +0.34, whiplash +0.88, all as recorded |
| Recorded refit numbers | DJF 2026 SoCal -0.70, NorCal +0.15, AK +0.69, YT +2.10; SoCal cells at the clip 9.0% (0% in 1998); calibration mean -0.0069 and -0.0076, SD 0.985; whiplash range -4.33 (YT 2004) to +4.13 (AB 1993); DJF-JJA correlation -0.17 (AK) to 0.22 (BC); all match DECISIONS and the register |
| R SPEI source (fetched, sbegueria/SPEI) | Monthly means are clipped at 0 after averaging per calendar month, as the code does; constant 0.01792; K = N/12 x days/30; PET = K x 16 x (10 T / J)^q at every temperature; the scale window is a rolling (weighted) sum. The three D49 claims hold |
| Config vs plan | Directions, families, fire windows, years, thresholds, near-threshold winters (1.53, 1.46, 1.44), 7 strong and 26 El Niño winters all match |
| Figure | Only `whiplash_series_roni.png` changed in the range; its extremes match the table |

## 2. Findings, most severe first (nothing high or medium)

### F1 (low, code, latent): dedupe priority reads the wrong source for mixed-id stations
`src/stations.py:352` ranks each station id by the source of its *first* row.
After `combine`, 57 station ids hold rows from two sources; for 5 of them the
earliest row is CanSWE while the bulk is the provincial file (BCE-1A01,
BCE-1C09A, BCE-1E01B, BCE-3B02A, YT-09FB-SC01), so they rank as CanSWE (2)
instead of provincial (1). None of the five is in any of the 18 merged pairs,
so no table changes today; a future near-duplicate of one of them could keep
the wrong copy. Fix: rank by the best source present, not the first.

### F2 (low, test): the new dedupe test does not exercise the motivating case
`tests/test_stations.py:322`. Its first case fails the 3-snowy-year minimum,
not the agreement share. No test has 3 or more snowy shared years with
all-year agreement above 80% and snowy-year agreement below it (the
23G10/23G12 pattern: 21 shared years, 3 snowy, 0% agreement in them).

### F3 (low, records vs data)
- `docs/methods_register.md` "Station normal" row still says 935 stations,
  YT 56; the current table has 933, YT 54 (PNW 405, BC 205, AK 159, AB 110).
- The register "Duplicate sites" row and DECISIONS 2026-10-07 say all six
  un-merged pairs "disagree" in their snowy years; 710:OR:SNTL / 22F05:OR:SNOW
  (0.7 km, 10 shared years) agree in their one snowy year and were dropped
  only for having fewer than 3 such years.

### F4 (low, plan wording): "follow the SPEI reference implementation" is wider than what was adopted
The R package's default fit is unbiased probability-weighted moments on a
3-parameter log-logistic, and its heat index uses the whole input series; the
project keeps maximum likelihood (decided 2026-10-04) and 1951-2020. The
2026-10-07 note in `ANALYSIS_PLAN.md` lists three specific points, so it is
not a contradiction, but a stranger can read it as a method switch. One clause
saying the fit stays ML closes it. Related, already in the register: the ML
fit degenerates in some cell-months (PNW August: shape 1.6e5, location
-1.3e6), values stable.

### F5 (low, stranger-executability of ANALYSIS_PLAN)
1. The permutation p-value is written as "the share of permuted differences
   at least as large"; the code and register use (count + 1) / (n + 1).
2. "Every headline test re-run on ONI" can mean the four headline methods or
   every registered test.
3. The zero-fire indicator sentence promises equal coefficients and df, which
   holds; HAC and Driscoll-Kraay standard errors will not equal a fit without
   those years (zero residuals enter the lag sums). Worth one clause.
4. The near-threshold flip does not say whether the three winters flip
   together or one at a time.

### Info
The known-gap count of 11 near-identical pairs 3-12 km apart used all-year
agreement; under the snowy-years rule the deduped table holds 5 such pairs
(e.g. 21A01:WA:SNOW / BCE-WA12, 5.3 km, 51 years).

## 3. Gaps nobody has checked, still cheap before the freeze

- **G1.** The Thornthwaite hand-computation test (`tests/test_whiplash.py:50`)
  copies the constants from the code, so it cannot catch a wrong constant. A
  test against one published worked example (tabulated Thornthwaite PET for a
  temperature series and latitude) would be independent.
- **G2.** The per-cell change statistics in DECISIONS (0.03 and 0.01 SD,
  largest 0.77) are unverifiable now that the old cache is overwritten; only
  the regional changes were reproduced. Either state they rest on the refit
  session's own measurement, or keep only the regional numbers.
- **G3.** Notebooks 02-03 were compared cell by cell against the tables
  (outputs match), not re-executed. A re-run before the freeze confirms they
  still execute end to end after the two code changes.

## 4. Could not check

Fire data; `temp_jja`, `temp_mam`, `precip_anom` (unbuilt); Thornthwaite's
1948 text (only the R source read); a full-grid independent refit (7 cells,
2 months in depth); the previous per-cell cache (gone).
