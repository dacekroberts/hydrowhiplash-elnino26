# Data Sources

Every dataset, boundary file and index used anywhere in the project gets a row
here before it is used. Licence terms are recorded **as stated on the
publisher's own page**, found with the `read-licence` skill; a government
portal suggests permissive terms but doesn't guarantee them. Rows marked
"to verify" have not been read yet and block publishing the site.

## Ledger

| Dataset | Publisher | Used by | Endpoint | Licence as stated | Attribution required | Redistribution of derived outputs | Retrieved | Residual issues |
|---|---|---|---|---|---|---|---|---|
| Oceanic Niño Index (ONI) / Relative ONI (RONI) | NOAA Climate Prediction Center | `src/download_oni.py` | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt and .../RONI.ascii.txt | Public domain. NWS Disclaimer (https://www.weather.gov/disclaimer, linked from the CPC ONI page footer): "The information on National Weather Service (NWS) Web pages are in the public domain, unless specifically noted otherwise, and may be used without charge for any lawful purpose so long as you do not: 1) claim it is your own [...], 2) use it in a manner that implies an endorsement or affiliation with NOAA/NWS, or 3) modify its content and then present it as official government material." Verdict: PERMITTED WITH CONDITIONS (restrictions on claims only) | Not required; credit "NOAA Climate Prediction Center" as good practice. Notice under 17 U.S.C. 403 if a published work consists predominantly of NWS material | Permitted ("any lawful purpose"), subject to the three restrictions | ONI 2026-10-04; terms read 2026-10-04 | Index choice pending (ANALYSIS_PLAN.md). Per NWS Public Information Statement 26-05, RONI is now the index for official ENSO monitoring (CPC ONI page, 2026-10-04). Recent RONI values may be revised for up to two months. A committed `results/tables/` file made mostly of index values cannot be "all rights reserved" for that part (see notice 1). No NWS/NOAA logos; no wording implying endorsement. |
| ERA5-Land monthly means | Copernicus Climate Change Service (ECMWF) | `src/download_era5.py` | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means (DOI 10.24381/cds.68d2bb30) | "CC-BY licence" (Creative Commons Attribution 4.0; CDS catalogue `license: CC-BY-4.0`, licence id `cc-by` rev 1). CDS licence document: "This dataset is released for use under the CC-BY licence." Replaced the "Licence to use Copernicus Products" on 2 July 2025 (ECMWF forum announcement). Dataset References add: users "**must**: cite the CDS catalogue entry; provide clear and visible attribution to the Copernicus programme and attribute each data product used". Verdict: PERMITTED WITH CONDITIONS | Yes: catalogue citation, data citation and the Copernicus attribution line with its disclaimer (notice 2), plus CC-BY's licence link and indication of changes | Permitted, including adapted outputs, with attribution. CC-BY 4.0 bars added terms that restrict recipients' use of the licensed material itself | Data 2026-10-04 (77 files, 1950-01 to 2026-07); terms read 2026-10-04 | Licence accepted on the account 2026-10-04 (act 1). Changes to state on the site: regional means, unit conversions, glacier exclusion. A committed `results/tables/` file of ERA5-Land values cannot be "all rights reserved" for those values (LICENSE-CONTENT covers the project's own work). No wording implying EC or ECMWF endorsement. Methods page fills the attribution year `<YYYY_2>` as 2026 (year of access; owner's choice, PR #2); ECMWF's citation guidance ("Copernicus Climate Change Service information [year]") does not define the year, so recheck before publishing: if it means the publication year, a 2027 launch needs 2027. |
| ERA5-Land hourly, April 1 00:00 UTC SWE only | Copernicus Climate Change Service (ECMWF) | `src/download_era5_april1.py` | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land (DOI 10.24381/cds.e2161bac) | "CC-BY licence" (dataset page Licence field; CDS catalogue API `license: CC-BY-4.0`), the same licence as the monthly product. Citation and attribution panel: "In addition to the requirements of the applicable license(s), users must: cite the CDS catalogue entry; provide clear and visible attribution to the Copernicus programme and attribute each data product used". Verdict: PERMITTED WITH CONDITIONS | Yes: catalogue citation, data citation and the Copernicus attribution line (notice 2), plus CC-BY's licence link and changes made | Permitted, including adapted outputs, with attribution | Terms read 2026-10-04 | The attribution line on this page reads "information <2019>" (year filled in), where the monthly page shows the placeholder `<YYYY_2>`; settle the year with the monthly row's open recheck before publishing. Catalogue citation names "Copernicus Climate Change Service (C3S)(2019)", the monthly one "(2022)". Changes to state: April 1 snapshot only, glacier and perennial-snow cells excluded, regional means. |
| Natural Earth admin-1 states and provinces, 10m (`ne_10m_admin_1_states_provinces`, v5.1.1) | Natural Earth (supported by NACIS; files served from naciscdn.org) | `src/regions.py` | https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip (dataset page https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/) | Public domain. Terms of Use page (https://www.naturalearthdata.com/about/terms-of-use/): "All versions of Natural Earth raster + vector map data found on this website are in the public domain." Use permitted "in any manner, including modifying the content and design, electronic dissemination, and offset printing". Disclaimer: "The authors provide Natural Earth as a public service and are not responsible for any problems relating to accuracy, content, design, and how it is used." Contributor licences on the same page (Washington Post, JRC IES rivers, XNR roads, IMA time zones) are grants to Natural Earth with no downstream conditions; name data from Wikidata is CC0. No terms file in the zip (README is a copy of the dataset page). Verdict: PERMITTED | Not required: "No permission is needed to use Natural Earth. Crediting the authors is unnecessary." Suggested credit, optional: "Made with Natural Earth." | Permitted, any purpose | Data and terms 2026-10-04 (v5.1.1, VERSION.txt) | Boundaries generalised at 1:10m; de facto boundaries by default (irrelevant for US states and Canadian provinces). Polygons include inland water, so region areas sit near official total (land + water) areas. |
| Natural Earth 1:50m map layers: ocean, country boundary lines, admin-1 lines with lakes | Natural Earth | `src/figures.py` (cartopy `cfeature.OCEAN`, `BORDERS`, `STATES` at 50m; display only, nothing measured) | https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_ocean.zip and the matching `50m_cultural` files (cartopy's download source) | Same terms as the admin-1 row: "All versions of Natural Earth raster + vector map data found on this website are in the public domain." Verdict: PERMITTED | Not required | Permitted, any purpose | 2026-10-04 (downloaded by cartopy to its cache on first map) | Downloaded from cartopy's S3 mirror, not naturalearthdata.com; same data and terms. |
| SNOTEL April 1 SWE | USDA NRCS | Phase 2 | https://www.nrcs.usda.gov/wps/portal/wcc/home/ | To verify | To verify | To verify | | |
| BC snow surveys | Government of British Columbia | Phase 2 | https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-science-data/water-data-tools/snow-survey-data | To verify | To verify | To verify | | |
| Alberta snow surveys | Government of Alberta | Phase 2 | https://rivers.alberta.ca/ | To verify | To verify | To verify | | |
| MTBS burned-area perimeters | USGS / USDA Forest Service | Phase 3 | https://www.mtbs.gov/direct-download | To verify. Expected: US federal work | To verify | To verify | | Covers 1984 to about 2 years ago; mapping threshold 1,000 acres in the West |
| WFIGS / NIFC perimeters | National Interagency Fire Center | Phase 3 | https://data-nifc.opendata.arcgis.com/ | To verify | To verify | To verify | | Recent years only; check overlap with MTBS |
| Canadian National Fire Database (CNFDB) | Natural Resources Canada | Phase 3 | https://cwfis.cfs.nrcan.gc.ca/ha/nfdb | To verify. Expected: Open Government Licence - Canada | To verify | To verify | | Early-year coverage of small fires is patchy; project uses fires >= 405 ha only |

## Notices this project must display when published

Filled in from the ledger once licences are read. Each notice is copied
verbatim from the publisher and shown on the site's methods page.

1. **ONI / RONI (NOAA CPC):** no credit line required. If a published table
   or figure consists predominantly of CPC index values, state that the NOAA
   material it incorporates is not subject to copyright protection
   (17 U.S.C. 403, as required by the NWS Disclaimer).
2. **ERA5-Land (C3S / ECMWF)**, from the dataset's References section,
   verbatim (`<YYYY_2>` is the publisher's year placeholder):
   - Attribution: "Generated using or contains modified Copernicus Climate
     Change Service information <YYYY_2>. Neither the European Commission
     nor ECMWF is responsible for any use that may be made of the
     Copernicus information or data it contains."
   - Catalogue entry: "Copernicus Climate Change Service (2022): ERA5-Land
     monthly averaged data from 1950 to present. Copernicus Climate Change
     Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.68d2bb30
     (Accessed on DD-MMM-YYYY)"
   - Data: "Muñoz Sabater, J. (2019): ERA5-Land monthly averaged data from
     1950 to present. Copernicus Climate Change Service (C3S) Climate Data
     Store (CDS). DOI: 10.24381/cds.68d2bb30 (Accessed on DD-MMM-YYYY)"
   - CC-BY 4.0: link https://creativecommons.org/licenses/by/4.0/ and state
     the changes made.
   Accessed date for this project: 04-OCT-2026 (first download).
   ERA5-Land hourly (April 1 SWE), from its Citation and attribution
   panel, verbatim:
   - Catalogue entry: "Copernicus Climate Change Service (C3S)(2019):
     ERA5-Land hourly data from 1950 to present. Copernicus Climate Change
     Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.e2161bac
     (Accessed on DD-MMM-YYYY)"
   - Attribution: "Generated using or contains modified Copernicus Climate
     Change Service information <2019>. Neither the European Commission
     nor ECMWF is responsible for any use that may be made of the
     Copernicus information or data it contains."
   - Data: "Muñoz Sabater, J. (2019): ERA5-Land hourly data from 1950 to
     present. Copernicus Climate Change Service (C3S) Climate Data Store
     (CDS). DOI: 10.24381/cds.e2161bac (Accessed on DD-MMM-YYYY)"
3. **Natural Earth admin-1:** none required ("Crediting the authors is
   unnecessary"). Optional credit suggested by the publisher: "Made with
   Natural Earth."

## Acts owed to publishers

Obligations that publishing alone doesn't discharge (registration,
notification, providing statistics on request), with dates and outcomes.

| Publisher | Act owed | Date | Outcome |
|---|---|---|---|
| Copernicus Climate Change Service (ECMWF) | Accept the dataset's CC-BY licence on the CDS account before download | 2026-10-04 | Done; CDS API lists `cc-by` rev 1 as accepted |
