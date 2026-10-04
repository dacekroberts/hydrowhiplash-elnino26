Project: hydrowhiplash-elnino26 — El Niño 2026–27 hydroclimate whiplash and
fire impact. Author: Dace Roberts.

Goal: Estimate how the 2026–27 strong El Niño is likely to affect the 2027 fire
season, using past El Niño winters as analogs. Exploratory for now; intended for
eventual publication, so keep everything reproducible.

Second goal: a public explainer page (Quarto site on GitHub Pages) with five
pieces: the two-pathway mechanism diagram, a winter rainfall map, analog
fire-season charts per region, a live 2026–27 tracker, and a fall 2027
verification panel. Build it from the analysis figures in results/, not as a
separate design project; the analysis comes first.

Regions:
- Primary: Pacific Northwest (WA, OR, ID), British Columbia, Alberta
- Contrast: California, split into Northern and Southern CA at about 35.5°N

Hypotheses:
- PNW/BC: El Niño → warm, dry winter → low snowpack → earlier, longer fire season
- Alberta: El Niño → warm, low-snow winter → early, dry spring → more spring
  boreal fires (e.g. Fort McMurray, May 2016, after the 2015–16 El Niño)
- SoCal: El Niño → wet winter → grass growth → more fine fuel → larger
  grass/brush fire year once it dries out

Period: climate 1950–present; fire 1984–present (limited by fire-perimeter records)

ENSO definition: NOAA ONI or RONI (chosen at the freeze gate). El Niño winter = DJF ONI ≥ +0.5 °C; strong = ≥ +1.5 °C.
Analog years: confirm from data/processed/el_nino_winters.csv and list them here.

Whiplash metric: SPEI-3 (xclim) change from winter (DJF) to the following
summer (JJA), averaged by region.

Fire outcome: area burned and fire-season length in the year after the El Niño
winter: log(1 + ha) with a year trend term in regressions (see ANALYSIS_PLAN.md). Window: June–October
for US regions and BC; April–October for Alberta, where spring fires matter.

Portfolio purpose: this project is meant to close an inferential-statistics
gap (significance tests, CIs, regression with controls, autocorrelation,
multiple comparisons). Methods are pre-registered in ANALYSIS_PLAN.md and
implemented in src/stats.py; keep that emphasis in any advice.

Method: analyse the full record (climate 1950–present, fire 1984–present,
every year), with El Niño
years highlighted on top of it rather than analysed in isolation. The
non-El Niño years are the baseline that shows whether El Niño years stand
out. Then composite El Niño years against neutral and all years, with
bootstrap uncertainty. No ML; the sample is too small.

Scope: El Niño → following fire season only. La Niña (e.g. a possible
2027–28 La Niña after this El Niño) is a planned later extension; La Niña
years are already labelled in the ONI output so it can be added without rework.
A prediction model is a second later extension: a seasonal outlook trained on
all years (ENSO, winter precipitation, snowpack → whiplash and fire anomaly),
and/or long-term trends from CMIP6 projections. Keep the historical analysis
outputs as tidy region × year tables so they can feed it directly.

Stack: Python (conda-forge env on Windows), xarray, xclim, geopandas,
regionmask, pandas, matplotlib/cartopy, Plotly for interactive charts, Quarto
for the site. Code in src/, site pages in site/, exploration in notebooks/,
data never committed, and provenance recorded in DATA_SOURCES.md.

Conventions: every tunable value lives in src/config.py; burned area is
measured in an equal-area CRS and climate means are latitude-weighted
(src/geo.py); judgment calls are logged in DECISIONS.md; data licences are
read and recorded in DATA_SOURCES.md before publishing. Explain concepts as
they come up, don't rewrite my findings prose, and flag scope additions
rather than implementing them.

Daily log (required): every day of work gets logs/YYYY-MM-DD.md in the repo.
Claude Code writes its sessions there itself. For planning sessions in this
claude.ai project, end by giving me a ready-to-paste session block in the
template's format (### HH:MM-HH:MM · claude.ai, timestamped bullets, plus any
decisions, numbers, problems and next step) so it can be added to that day's
log.

Working style: about 10 hours a week, a mix of long working sessions and short
check-ins. Hands-on coding happens in Claude Code (CLAUDE.md in the repo);
planning and discussion in this project. Start each session by saying which
phase of ACTION_PLAN.md we're in.
