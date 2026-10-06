# Audit: Phase 2 code and the climate dataset, 2026-10-05

Two read-only audits run before the analysis plan is frozen, at the owner's
request (session 4), following the phase-boundary audit rule (D35). Both by
research agents of the main session; the data audit needs `data/`, so it ran
in the main checkout. No fire data was opened. Findings were reported to the
owner, who chose the fixes (`DECISIONS.md` 2026-10-05 "Pre-freeze audit").

- **Commit audited:** `main` at `5386222` (after the pre-freeze decisions).
- **Data audit scope:** the three committed tables, the six region x year
  tables in `data/processed/`, the ENSO table and raw RONI file, the per-cell
  SPEI caches, glacier masks, the cleaned station table, and the ERA5-Land
  monthly and April 1 file sets.
- **Code audit scope:** `whiplash.py`, `snow.py`, `phase2.py`, `stations.py`,
  `snow_soil.py`, `winter_figures.py`, Phase 2 parts of `figures.py`,
  `download_era5_april1.py`, the four station downloaders, `config.py`,
  `stats.py` (readiness for the decided inference only), notebooks 02 and 03
  code cells, and their tests.
- **Method:** values recomputed independently from inputs (scripts in the
  session scratchpad); code read against `CLAUDE.md`, the data dictionary,
  `ANALYSIS_PLAN.md`, `DECISIONS.md` and the methods register; a grep for
  hard-coded tunables; edge-case probes on synthetic data.

## Passed

- **Shape and keys:** every region x year table has 532 rows (7 regions x 76
  winters, 1951-2026), no duplicate region-years, region names as in
  `config.REGIONS`, integer `year`, `winter` = (Y-1)-Y everywhere. The
  committed tables equal their `data/processed/` twins exactly.
- **Gaps as expected:** station index starts AK 1960, AB 1963, YT 1975; AB
  2026 empty; no index for NorCal and SoCal; summer values (`spei3_jja`,
  `whiplash`, `soil_moisture`) NaN only in 2026 (ERA5-Land ends July 2026).
  No NaN turned into 0.
- **ENSO:** `enso_djf` equals the RONI DJF value for all 76 winters; phase
  and strong flags 0 mismatches against the thresholds (26 El Niño, 26
  neutral, 24 La Niña, 7 strong; from 1984: 14, 9, 20, 3); identical ENSO
  columns in every table.
- **Recomputed:** regional SPEI mean 0.000 and SD 1.000 over 1951-2020;
  `whiplash` = `spei3_jja` - `spei3_djf` to 9e-16; `era5_swe_z` mean 0, SD 1
  over 1991-2020; station index (`n_stations`, z, %) rebuilt from the cleaned
  table with difference 0; at least 5 stations wherever the index exists.
- **Physical ranges:** glacier-excluded April 1 SWE means AK 225.8, YT 167.2,
  BC 442.0, AB 67.1, PNW 135.8, NorCal 68.0, SoCal 0.06 mm, all
  non-negative; snowfall fraction 0.007-0.996 and equal to sf/tp; soil
  moisture 0.107-0.393 m³/m³; Nov-Mar precipitation above DJF in all 532
  rows.
- **Inputs:** ERA5-Land monthly folders contiguous, 919 months to 2026-07;
  April 1 files 1950-2026; glacier masks 752 main, 2,250 north; station
  table 71,759 rows, 2,180 stations, no duplicates, nothing negative or above
  5,000 mm (maximum 3,819 mm, BC coast 1999), no date outside ±10 days except
  flagged `date_unknown`, every station inside its region polygon.
- **The 111 unfitted north cells** (an open item since session 2): all are
  glacier icefield cells (AK 26, YT 85), already excluded from SWE; north has
  35,761 region cells = 35,650 fitted + 111.
- **Code:** units, season labels (DJF by February's year, Nov-Mar by March's,
  April 1 by its own year), regional means only via `geo.regional_mean`
  (empty or all-NaN regions give NaN, not 0), SPEI fit and clip, glacier and
  station cleaning rules as decided; `TEST_DIRECTIONS` matches the plan's
  directions table cell for cell; no tunable literals in the data path.

## Findings

| # | Source | Severity | Finding | Where | Status |
|---|---|---|---|---|---|
| 1 | data | high | Thornthwaite day length is NaN in polar day and night, so PET was NaN in June and December north of about 68N and every DJF and JJA SPEI-3 there was missing; regional means skipped those cells silently (AK 15.1% and 17.4% of its weight, YT 5.1% and 6.3%). No pre-registered test affected (AK and YT SPEI and whiplash are descriptive). | `src/whiplash.py` `pet_thornthwaite` | fixed in the main session: polar day lengths 24 h and 0 h; north SPEI refit |
| 2 | data | medium | SoCal ERA5-Land SWE z and % meaningless (normal 0.06 mm; z up to 4.69, % up to 1,787). | `src/stations.py` `compare_era5` | fixed in the main session: empty below a 10 mm normal (`ERA5_SWE_MIN_NORMAL_MM`) |
| 3 | code | low (Phase 4) | statsmodels counts Driscoll-Kraay t degrees of freedom from row order (df 0, 4 or 100 for one dataset; SE identical). | `src/stats.py` (not built) | pre-registered: df = years - 1 (`POOLED_DF_YEARS_MINUS`) |
| 4 | code | low (stale docs) | Methods register whiplash row "timing pending", fire-window row "provisional"; data dictionary "Definition (draft)". | `docs/` | fixed in the main session |
| 5 | code | medium (latent) | `glacier_mask` uses partial years if given one. No effect today (mask years end 2025). | `src/snow.py:36-45` | side-session task |
| 6 | code | low | `restandardise` on unsorted years and `anomalies` with fewer than 2 normal years return NaN silently. | `src/whiplash.py:130`; `src/stations.py:347` | side-session task |
| 7 | code | low | The test predictor `era5_swe_z` uses `STATION_NORMAL_YEARS`. | `src/stations.py:355` | side-session task |
| 8 | code | low | `effects_by_group` crashes on a NaN station elevation. | `src/stations.py:413` | side-session task |
| 9 | code | low | Five Phase 2 figures rebuild only through notebooks 02 and 03. | notebooks | side-session task (optional) |
| 10 | code | low | Notebook literals (SoCal exclusion, NORTH list, axis labels). | notebooks 02, 03 | side-session task |
| 11 | code | low | ENSO join: left in `whiplash_table`, inner in `april1_table` and `snow_soil_table`. | `whiplash.py:155`; `snow.py:84`; `snow_soil.py:62` | side-session task |
| 12 | code | low | A survey with a missing date counted as outside the window. | `src/stations.py:75-77` | side-session task |
| 13 | code | low | Em-dash check skips notebook code cells. | `scripts/check_no_em_dashes.py` | side-session task |
| 14 | data | low | CRLF line endings in five uncommitted `data/processed/` files. | writers in `era5`, `snow`, `whiplash`, `download_oni`, `stations` | side-session task |
| 15 | data | low | `el_nino_winters.csv` has no `enso_index` column. | `src/download_oni.py` | side-session task |
| 16 | data | low | Four Yukon station IDs carry CanSWE and Yukon coordinates (up to 0.13° apart); regions unaffected. | `src/stations.py` `combine` | side-session task |
| 17 | data | low | 17 BC glacier cells have scattered NaN SPEI months (at most 0.10% of BC's weight); SPEI is not glacier-masked, SWE is. | main domain | stated here and in the methods register |
| 18 | data | low | `date_unknown` rows: 2,162 in the table, 2,163 in `config.py` and the docs. | `config.py` comment | open (needs data) |

## Methods notes for the freeze

- NaN cells in regional means are skipped. After the polar fix (north refit
  2026-10-06, 1,947 s), region land cells with no SPEI value: the 111
  icefield cells; finding 17's BC glacier cells; and 46 north cells with no
  February (DJF) value at all though fitted in other months, at 59-63N,
  151-137W (Alaska Range, Wrangell-St Elias), about 0.17% of AK's cells.
  These lie south of the polar circle, where PET is unchanged, so the gap
  predates the fix; cause not yet found (left for the re-audit).
- Effect of the polar fix on the committed tables: only the AK and YT
  `spei3_*` and `whiplash` columns change (largest change 0.62 in
  whiplash; correlation with the old series AK 0.989 DJF, 0.979 JJA; YT
  0.999, 0.998). El Niño minus neutral (RONI), before / after: AK winter
  SPEI-3 -0.06 / -0.03, summer -0.07 / -0.11, whiplash -0.01 / -0.08;
  YT -0.32 / -0.30, -0.08 / -0.07, +0.24 / +0.23. Every other value in the
  committed tables is unchanged except SoCal's emptied SWE z and %.
- ERA5-Land precipitation is not gauge-corrected: SoCal 1997-98 ranks fourth
  wettest (252 mm), behind 1992-93 (361 mm).
- `era5_swe_z` and `station_swe_z` average above 0 over the full record
  because the normal is 1991-2020 (station z PNW +0.28); the trend rule
  handles this.
- `stats.py` is not yet ready for the decided inference: `use_t`,
  Driscoll-Kraay with set df, one-sided p-values, the H4 contrast,
  expanding-window validation, a runner for `CORRECTION_FAMILIES`,
  detrending helpers, builders for `precip_anom`, `temp_jja`, `temp_mam`, and
  a fire-window helper that labels a wrapping season (6, 1) by its first
  month's year (`era5.winter_total` labels by the last month, which would put
  June-January in Y+1). Phase 4 work.

## Could not check

ERA5-Land values against independent observations; SPEI distribution fit
quality beyond NaN and clip counts; station values against the raw downloads
(the index was re-derived from the cleaned table only); variables not yet
built (`temp_jja`, `temp_mam`, `precip_anom`); later revisions of the 2026
ERA5-Land months; anything involving fire data.
