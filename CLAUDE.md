# CLAUDE.md - hydrowhiplash-elnino26

Analog study: how strong El Niño winters shape the following fire season in the
PNW (WA/OR/ID), BC and Alberta, contrasted with NorCal and SoCal. Target: the
2026-27 El Niño and the 2027 fire season. Three documents hold the state:

- `ACTION_PLAN.md`: roadmap, open work, current phase
- `ANALYSIS_PLAN.md`: pre-registered hypotheses and tests (frozen once committed)
- `DECISIONS.md`: reasoning trail for judgment calls

`docs/plan_deviations.md` tracks where reality departed from these plans.

## Required every session: daily log

At the end of every work session, before the final commit, write today's log
with the `daily-log` skill: `logs/YYYY-MM-DD.md`, one file per local day, a
new timestamped session block appended (never rewrite earlier sessions or
earlier days). Same frontmatter and headings as `logs/_TEMPLATE.md` every
time, because the user exports these into an external catalogue. A session
isn't finished until its log is written and `python scripts/log.py list`
parses it.

## Working with this user

- Explain statistical and geospatial concepts conversationally as they come
  up, not in bulk.
- The user's own findings and interpretation prose is off-limits for
  rewriting. Discuss the numbers and flag stale or inconsistent wording only.
- Flag scope additions rather than implementing them.
- Log every judgment call in `DECISIONS.md` as it's made (format at the top
  of that file).
- Log every departure from the planning docs (estimates, assumptions,
  procedures, scope) in `docs/plan_deviations.md` as it's found, including
  stale wording left as written.

## Environment

- Windows, conda env `whiplash` from `environment.yml` (conda-forge only;
  don't pip-install geospatial packages).
- Run modules from the repo root: `python -m src.<module>`.
- Use `pathlib` paths, never hard-coded `/` or `\` separators.

## Single source of truth

- Every tunable value (thresholds, years, regions, CRS, fire windows, domain,
  statistics settings) lives in `src/config.py`. Never hard-code one of these
  in a script or notebook; import it. If a value in `config.py` changes after
  `ANALYSIS_PLAN.md` is frozen, that's a deviation and needs a row in its log.

## Measurement rules (silent-bug territory)

Units, measurement methods and traps for every dataset and derived variable:
`docs/data_dictionary.md`.

- **Area:** measure burned area only via `src.geo.area_ha`, which projects to
  the equal-area CRS (`CRS_EQUAL_AREA`, ESRI:102008). Never measure area or
  distance in EPSG:4326, and don't use sources' own area fields. EPSG:4326 is
  for storage and display only.
- **Regional climate means:** only via `src.geo.regional_mean`, which weights
  cells by cos(latitude). An unweighted mean over-counts northern cells.
- **ERA5-Land units:** precipitation is m/day (monthly mean), so mm/month =
  tp * 1000 * days_in_month; temperature is kelvin. Time dimension is
  `valid_time`.
- **Fires counted:** only fires >= `MIN_FIRE_HA` (405 ha) in every region.
- **Fire-season window:** `FIRE_SEASON_MONTHS` (Jun-Oct, Alberta Apr-Oct).
- **Year labels:** the DJF index value labelled year Y is winter (Y-1)-Y and
  is paired with fire season Y.

## Analysis conventions

- Statistics: use `src/stats.py` and follow `ANALYSIS_PLAN.md`. Report effect
  sizes and CIs before p-values, and report null results too.
- Years: climate 1950-present, fire 1984-present.
- Analyse every year; never filter down to El Niño years only. El Niño years
  (strong ones emphasised) are highlighted on full-record charts and compared
  against neutral and all years.
- Column names used by the stats code: `year`, `region`, `enso_djf`,
  `log_burn` (= log(1 + ha)), `burn_detr`, `temp_jja`, `precip_anom_*`.
- Reusable code in `src/` as plain functions; notebooks import from `src/`.

## Data and outputs

- Never commit anything in `data/`. Every new dataset gets a download script
  in `src/` and a ledger row in `DATA_SOURCES.md`, with its licence read via
  the `read-licence` skill before anything derived from it is published.
- Pipeline and site boundary: code writes figures and tables to `results/`;
  the Quarto site only reads from `results/`. Nothing in `results/` is made by
  hand, so the site can be rebuilt from scratch.
- Numbers on the site come from `results/` through Quarto inline Python
  expressions, never typed in by hand.

## Checks

- `python -m pytest` after any change to `src/stats.py`, `src/geo.py` or
  `src/config.py`.
- `python scripts/check_no_em_dashes.py` before committing.

## Code style

- Comments and docstrings in neutral voice: no "I", "we" or "you". State what
  and why; keep every measured value and every "re-measure if X changes"
  note. The full story of a decision goes in `DECISIONS.md`, with a one-line
  pointer in the code at most.
- No em dashes in Python comments, docstrings or strings (enforced by
  `scripts/check_no_em_dashes.py`). Markdown and Quarto prose is exempt.

## Scope guard

La Niña and a prediction model are planned later extensions. Don't build
either unless asked. Keep `phase` labels intact, and save analysis outputs as
tidy region x year tables in `data/processed/`, so both can be added later
without rework. The same code also writes a committed copy to
`results/tables/` (cloud threads only see committed files); before the first
such commit, read the licence of every source behind the table.

## Licensing

Split licence. Code (Python in `src/`, `tests/`, `scripts/`, notebook code
cells, config files) is MIT (`LICENSE`). Writing and figures (Markdown,
Quarto prose, notebook narrative, `results/` figures and tables, site text)
are (c) Dace Roberts, all rights reserved (`LICENSE-CONTENT`). Don't change
either licence or add licence headers without asking.
