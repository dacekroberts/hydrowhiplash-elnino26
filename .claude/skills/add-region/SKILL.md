---
name: add-region
description: Add a study region to the project (as Alaska and Yukon were added on 2026-10-04, D20). Use when the owner decides to add, split or re-role a region. Walks through the decisions, config, polygons, ERA5-Land domain, downstream data, site figures, planning documents with [mid-project] markers, and records, in order, with the checks that caught real problems.
---

# Add a region

Drawn from adding Alaska (AK) and Yukon (YT) on 2026-10-04 (`DECISIONS.md`
"Alaska and Yukon added", D20, D21). A region touches config, polygons,
downloads, every per-region table, the site and four planning documents, so
do it in this order and don't skip the records. Data steps run in the main
checkout (side sessions have no `data/`).

## 1. Decide with the owner first (nothing changes before this)

Get answers, then log them in `DECISIONS.md` before touching code:

- **Why** the region belongs (the mechanism and its source), and why now.
- **Role:** `primary`, `contrast`, or a new role (AK/YT got `north`, their
  own hypothesis family, so the PNW/BC/AB Holm corrections stayed
  unchanged). A new role needs footnote wording in `src/diagrams.py`
  `ROLE_NOTES`, or the mechanism diagram stops with an error.
- **Boundary:** whole admin-1 unit, clipped, or split (Alaska: clipped at
  169W because the Near Islands cross the antimeridian; Interior/coast split
  left open). A split needs a boundary source with its licence read.
- **Fire window:** first and last month; mark it provisional if unsure
  (AK/YT Apr-Sep).
- **Hypotheses:** which ones include the region, expected signs and
  sidedness. Before the freeze this becomes a pre-freeze item in
  `ANALYSIS_PLAN.md`; after the freeze adding a region is a deviation in its
  deviations log, not a quiet edit.
- **Substantial?** Scope changes are substantial: the plans are edited
  directly with `[mid-project: Dnn]` markers (step 8).

## 2. Config (`src/config.py`)

- `REGIONS`: name -> role, in display order.
- `FIRE_SEASON_MONTHS`: the window, with a comment if provisional.
- Any clip constant (`ALASKA_WEST_LON`) as a named value, never a literal.
- `ERA5_DOMAINS`: a new download box if the region lies outside the existing
  ones (name -> ([N, W, S, E], folder)), with half a degree to a degree of
  buffer; a comment with the region's extent.
- Station lists that are per state or province (`NRCS_STATES`).
- Run `python -m pytest` (config changed).

## 3. Polygons (`src/regions.py`)

- Add the geometry in `main()`, from Natural Earth admin-1 (US and Canada
  only, so names are unique), clipped with a box built from the config
  constant.
- Run `python -m src.regions`; check the printed area against the official
  land or total area (AK came out +0.9%, YT +0.4%; polygons include inland
  water).

## 4. Climate data (ERA5-Land)

- `python -m src.download_era5 <domain>` for the core set, and
  `--set snow_soil <domain>` if Phase 2 variables are in use; hourly April 1
  SWE with `python -m src.download_era5_april1 <domain>`. A new box costs
  about 50 minutes and 77 files per set.
- `era5.assign_domains` picks the first box that fully contains each
  region: check the new region maps to the intended domain.
- **Overlap check:** where boxes overlap, the same cells must agree
  (notebook 01 cell 5; AK's box agreed with main to float32 rounding, max
  relative difference 7e-7, so compare with a tolerance, not equality).
- **Completeness:** every year's file present and months contiguous (the
  loader now refuses gaps; check its message).

## 5. Downstream data (Phase 2 onward)

- Re-run the per-region builders: `python -m src.era5`, then
  `python -m src.whiplash` (per-cell SPEI cache is per domain: about
  45-50 minutes for a new box), `python -m src.snow`, `python -m src.phase2`.
- Check the glacier and perennial-snow mask for the region (AK lost 1,642
  cells) and any cells with no SPEI fit (111 north cells), and record both.
- Station snowpack: new sources need a download script, a licence read
  (`read-licence` skill), a `DATA_SOURCES.md` row and notices; watch for
  networks that cross borders (six Yukon sites lie in Alaska or BC).
- Fire data (after the freeze): which source covers it (MTBS/WFIGS in the
  US, CNFDB in Canada) and the same `MIN_FIRE_HA` threshold.
- Commit the `results/tables/` copies.

## 6. Site and figures

- Mechanism diagram: `python -m src.diagrams`, commit `results/figures/`
  (`tests/test_diagrams.py` fails until the SVGs match the new config).
- Phase 1 figures: `python -m src.winter_figures`. The 1997-98 map's extent
  is hard-coded (D28): check the new region is inside it.
- `python scripts/check_site.py` if anything under `site/` or
  `results/figures/` changed.

## 7. Tests

Add the region to any test that lists regions or domains
(`tests/test_era5.py` domain assignment, `tests/test_diagrams.py`
footnotes); run `python -m pytest`.

## 8. Planning documents and records

- Edit every place that lists the regions, marking each changed spot
  `[mid-project: Dnn]`: `CLAUDE.md` (scope line, fire-season window),
  `README.md` (scope line, methods table), `ACTION_PLAN.md` (goal, phase
  regions, downloads, station and fire sources), `ANALYSIS_PLAN.md`
  ("Data and years", "Outcomes", plus the pre-freeze or deviations entry).
- `docs/plan_deviations.md`: one entry, *Substantial: yes*, listing every
  file changed.
- `docs/methods_register.md`: a row for every new control (clip, window,
  mask counts).
- `docs/data_dictionary.md`: the regions section and any new source.
- `DECISIONS.md`: the decisions from step 1, with numbers measured since.
- `docs/enso_regions_out_of_scope.md`: remove the region from the
  out-of-scope list if it was there.
- Write the day's log (`daily-log` skill).

## Checks that caught real problems

- Exact-equality overlap check failed on float32 noise: use a tolerance.
- Admin-1 names repeat worldwide: restrict to US and Canada before lookup.
- A region crossing the antimeridian breaks boxes and masks: clip it.
- A whole-state climate mean can describe a different place from where the
  fire is (Alaska's wet south coast vs fire in the Interior): say so, or
  split.
