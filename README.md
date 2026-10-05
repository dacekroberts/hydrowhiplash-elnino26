# hydrowhiplash-elnino26

Analog analysis of how strong El Niño winters affect hydroclimate whiplash and
the following fire season in the Pacific Northwest, British Columbia and
Alberta, plus Alaska and Yukon [mid-project: D20], contrasted with Northern and Southern
California. The current target
is the 2026–27 event, with the 2027 fire season as the outcome.

Author: Dace Roberts.

**Licensing:** code is MIT-licensed (`LICENSE`). Writing and figures are
© 2026 Dace Roberts, all rights reserved (`LICENSE-CONTENT`). Third-party data
stays under its publishers' terms (`DATA_SOURCES.md`).

See `ACTION_PLAN.md` for the roadmap and `ANALYSIS_PLAN.md` for the
pre-registered hypotheses and tests.

## Statistical approach

This project is built around inference, not just description. With roughly 10 to 13
El Niño years in the fire record, every method is chosen for small,
autocorrelated samples:

| Question | Method |
|---|---|
| Do El Niño years differ from the rest? | Permutation test and bootstrap confidence interval |
| Does ONI strength matter after controlling for temperature and the long-term trend? | Regression with controls and Newey-West standard errors |
| Does El Niño affect the PNW, BC and Alberta (and Alaska and Yukon [mid-project: D20]) differently from California? | Pooled regression with an ONI × region interaction |
| Does a wet year raise fire risk afterwards (the whiplash mechanism)? | Lagged regression |
| Are consecutive years independent? | Autocorrelation check and block bootstrap |
| Are some results significant by chance? | Holm and Benjamini-Hochberg corrections |
| How reliable is the 2027 forecast? | Leave-one-year-out prediction intervals with empirical coverage |

Hypotheses and tests were committed in `ANALYSIS_PLAN.md` before the fire data
was analysed; any changes are logged there with reasons.

## Setup (Windows)

1. Install **Miniforge** from https://github.com/conda-forge/miniforge
   (the Windows x86_64 installer). Use the **Miniforge Prompt** it adds to the
   Start menu for the commands below.

2. Create the environment from the project folder:

   ```bat
   cd path\to\hydrowhiplash-elnino26
   mamba env create -f environment.yml
   conda activate whiplash
   ```

3. Copernicus CDS API key (for ERA5-Land). Log in at
   https://cds.climate.copernicus.eu, copy your personal access token from
   your profile page, and create a file called `.cdsapirc` in your home folder
   (`C:\Users\<you>\.cdsapirc`, no file extension) containing:

   ```
   url: https://cds.climate.copernicus.eu/api
   key: <your-personal-access-token>
   ```

   Notepad tends to add `.txt`; save with "All files" selected, or run
   `notepad %USERPROFILE%\.cdsapirc` from the prompt. Also open the ERA5-Land
   monthly dataset page once and accept its licence.

4. In VS Code, pick the `whiplash` interpreter (Ctrl+Shift+P →
   "Python: Select Interpreter") so notebooks use this environment.

## Run order

```bat
:: ENSO index -> data\processed\enso_index.csv and el_nino_winters.csv
python -m src.download_oni
:: ERA5-Land monthly precip + temp -> data\raw\era5_land\
python -m src.download_era5
:: region polygons -> data\processed\regions.geojson
python -m src.regions
:: Phase 1 winter precipitation figures -> results\figures\
python -m src.winter_figures
:: tests for the statistics, spatial and log helpers
python -m pytest
:: style check before committing
python scripts\check_no_em_dashes.py
:: start today's log (logs\YYYY-MM-DD.md)
python scripts\log.py new
:: logs -> logs\export\index.csv and all_logs.md
python scripts\log.py export
:: explainer site, live preview in the browser
quarto preview site
```

## Layout

```
data/raw/         untouched downloads (not committed)
data/processed/   cleaned, clipped outputs (not committed)
notebooks/        exploration
src/              reusable code; config.py holds every tunable value
results/          figures and tables for the write-up and site
site/             Quarto explainer site (published to GitHub Pages)
tests/            pytest checks for src/stats.py, src/geo.py and scripts/log.py
logs/             daily progress logs, one file per day (template inside)
scripts/          daily-log helper and repo checks
.claude/skills/   Claude Code skills (daily-log, read-licence)
CLAUDE.md         project conventions for Claude Code
```

Progress is logged daily in `logs/`. Data provenance and licences are tracked in `DATA_SOURCES.md`; judgment
calls and their reasoning in `DECISIONS.md`.
