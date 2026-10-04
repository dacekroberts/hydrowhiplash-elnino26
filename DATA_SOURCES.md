# Data Sources

Every dataset, boundary file and index used anywhere in the project gets a row
here before it is used. Licence terms are recorded **as stated on the
publisher's own page**, found with the `read-licence` skill; a government
portal suggests permissive terms but doesn't guarantee them. Rows marked
"to verify" have not been read yet and block publishing the site.

## Ledger

| Dataset | Publisher | Used by | Endpoint | Licence as stated | Attribution required | Redistribution of derived outputs | Retrieved | Residual issues |
|---|---|---|---|---|---|---|---|---|
| Oceanic Niño Index (ONI) / Relative ONI (RONI) | NOAA Climate Prediction Center | `src/download_oni.py` | https://www.cpc.ncep.noaa.gov/data/indices/ | To verify. Expected: US federal work, public domain | To verify | To verify | | Index choice pending (ANALYSIS_PLAN.md) |
| ERA5-Land monthly means | Copernicus Climate Change Service (ECMWF) | `src/download_era5.py` | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means | To verify. Accepted on the dataset page before first download | To verify. Copernicus products normally require a specific credit line | To verify | | |
| Natural Earth admin-1, 10m | Natural Earth | `src/regions.py` | https://www.naturalearthdata.com/downloads/10m-cultural-vectors/ | Public domain (to confirm on the terms page) | None required; credit appreciated | Permitted | | |
| SNOTEL April 1 SWE | USDA NRCS | Phase 2 | https://www.nrcs.usda.gov/wps/portal/wcc/home/ | To verify | To verify | To verify | | |
| BC snow surveys | Government of British Columbia | Phase 2 | https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-science-data/water-data-tools/snow-survey-data | To verify | To verify | To verify | | |
| Alberta snow surveys | Government of Alberta | Phase 2 | https://rivers.alberta.ca/ | To verify | To verify | To verify | | |
| MTBS burned-area perimeters | USGS / USDA Forest Service | Phase 3 | https://www.mtbs.gov/direct-download | To verify. Expected: US federal work | To verify | To verify | | Covers 1984 to about 2 years ago; mapping threshold 1,000 acres in the West |
| WFIGS / NIFC perimeters | National Interagency Fire Center | Phase 3 | https://data-nifc.opendata.arcgis.com/ | To verify | To verify | To verify | | Recent years only; check overlap with MTBS |
| Canadian National Fire Database (CNFDB) | Natural Resources Canada | Phase 3 | https://cwfis.cfs.nrcan.gc.ca/ha/nfdb | To verify. Expected: Open Government Licence - Canada | To verify | To verify | | Early-year coverage of small fires is patchy; project uses fires >= 405 ha only |

## Notices this project must display when published

Filled in from the ledger once licences are read. Each notice is copied
verbatim from the publisher and shown on the site's methods page.

1. _(none recorded yet)_

## Acts owed to publishers

Obligations that publishing alone doesn't discharge (registration,
notification, providing statistics on request), with dates and outcomes.

| Publisher | Act owed | Date | Outcome |
|---|---|---|---|
| | | | |
