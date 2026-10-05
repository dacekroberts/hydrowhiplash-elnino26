# Alberta April 1 SWE for 2026 and 2027: sources

Read-only research, 2026-10-05, for the session 3 handoff
(`docs/session3_kickoff.md` Part 1). The question: CanSWE v8 ends 31 July
2025, so where can Alberta April 1 snow water equivalent (SWE) for 2026 and
2027 come from, with clear published terms? Alberta's own portal
(`rivers.alberta.ca`) has no data licence (`DATA_SOURCES.md` Alberta row,
D30). Nothing was downloaded; candidates were read from their catalogue
metadata and licence texts. This note doesn't edit `DATA_SOURCES.md`; a
chosen source gets its ledger row there in the usual way.

## Short answer

- **2026:** CanSWE's next version (v9) should carry it, around February to
  March 2027 on the release record below.
- **2027, for the forecast (needed in April 2027):** no station source with
  clear terms publishes in time. **ERA5-Land April 1 SWE**, which the
  project already computes for every region (`src/snow.py`, hourly 1 April
  00:00 UTC, CC-BY 4.0, about 5 days behind real time), is the only licensed
  source available by mid-April 2027.
- **2027, for checking afterwards (verification panel, fall 2027):** the OSM
  snow survey (below) may have it by about June 2027 for one part of
  northeast Alberta; CanSWE only around March 2028.

So the recommendation is: **ERA5-Land as Alberta's April 1 SWE for 2026-27,
with station SWE as a historical check on it** (CanSWE to 2025, then 2026
from v9), plus the OSM survey as an optional regional check. Asking Alberta
Environment and Protected Areas for terms on `rivers.alberta.ca` data stays
the last resort.

## Candidates

### 1. CanSWE (ECCC, Zenodo): already in use, about one year behind

Release record (Zenodo concept DOI 10.5281/zenodo.4734371, read 2026-10-05
from the Zenodo API; every version licensed `canada-crown`, i.e. OGL-Canada
2.0):

| Version | Published | Data to |
|---|---|---|
| v1 | 2021-05-10 | 2020 |
| v2 | 2021-08-19 | 2020 |
| v3 | 2022-01-21 | 2021 |
| v4 | 2022-06-13 | 2021 |
| v5 | 2023-03-14 | 2022 |
| v6 | 2024-03-18 | 2023 |
| v7 | 2025-02-20 | 2024 |
| v8 | 2026-03-17 | 2025 (ends 31 July 2025) |

Since v5, one version a year, published February or March, with data
through the previous July. Expected: **v9 about February-March 2027 (April
2026 values), v10 about February-March 2028 (April 2027 values)**. Alberta's
snow pillow archive is part of CanSWE (Vionnet et al., ESSD 2021), so v9
should add Alberta's 2026 courses and pillows. Terms already read (D30;
`DATA_SOURCES.md` CanSWE row, notice 7).

- Good: same source, licence and processing as 1928-2025.
- Limit: too late for the 2027 forecast; v10 also arrives after the fall
  2027 verification panel.

### 2. ERA5-Land April 1 SWE: licensed, timely, gridded

Already in the pipeline for all seven regions (Phase 2): hourly ERA5-Land at
1 April 00:00 UTC, glacier and perennial-snow cells excluded (D27), CC-BY
4.0 (`DATA_SOURCES.md`, notice 2). Hourly ERA5-Land publishes about 5 days
behind real time (`config.ERA5_HOURLY_LAG_DAYS` = 7 as margin), so 1 April
2027 is available about 8 April 2027.

- Good: no new source or licence; same method in every region and year;
  available in time for the forecast.
- Limit: model output, weakest in complex terrain (the Rockies) and where
  stations are sparse (data dictionary s.2); the station comparison planned
  for session 3 measures how far it can be trusted in Alberta.

### 3. OSM Snow Survey Data (Alberta, Oil Sands Monitoring): licensed, regional

`https://osmdatacatalog.alberta.ca/dataset/osm-snow-survey-data`, read
2026-10-05 (CKAN metadata, dataset page, catalogue About page, licence
text). Not downloaded.

- **Publisher:** Alberta Environment and Protected Areas, Oil Sands
  Monitoring program (contributor Hatfield Consultants).
- **Content:** manual snow surveys (snow depth, density, SWE; standard
  federal sampler), four watersheds and four land-cover types in the
  **Lower Athabasca Region** (northeast Alberta, boreal plains), from
  2009-02-01, including Regional Aquatics Monitoring Program data
  2009-2017; "3 times per year"; one ZIP of CSVs (41 kB), resource "Last
  updated: 20260625".
- **Licence as stated:** "Open Data Commons Attribution License"
  (`license_id: odc-by`, link http://www.opendefinition.org/licenses/odc-by;
  text at https://opendatacommons.org/licenses/by/1-0/).
- **Grant (ODC-By 1.0, 3.1):** "the Licensor grants to You a worldwide,
  royalty-free, non-exclusive, terminable (but only under Section 9) license
  to Use the Database ... These rights explicitly include commercial use".
- **Notices to display:**
  - For published results (ODC-By 4.3, "Produced Work"): a notice that the
    content was obtained from the database and is available under ODC-By.
    The licence's own example: "Contains information from OSM Snow Survey
    Data which is made available under the ODC Attribution License", with
    hyperlinks to the dataset and to the licence.
  - For a redistributed copy of the data or a derived table of its values
    (4.2, e.g. a `results/tables/` file): the licence or its URI, and the
    existing notices kept intact.
  - Citation given by the publisher: "Rokaya, P. (2025). OSM Snow Survey
    data, Alberta Environment and Protected Areas".
- **Restrictions on claims (disclaimers):** dataset "Usage considerations":
  "Alberta Environment and Protected Areas, the Oil Sands Monitoring Program
  and the Government of Alberta make no guarantees as to the accuracy of
  these data." Catalogue About page: "The OSM program makes no warranty,
  representation, or guaranty as to the content, accuracy, timeliness, or
  completeness of any of the data ... OSM shall assume no liability".
- **Acts owed:** none found (no registration or notification).
- **Pages reviewed:** dataset page and CKAN `package_show`; catalogue home
  and About pages (no site terms of use; the only legal link is the
  licence); ODC-By 1.0 text. A Box folder linked from the catalogue home
  page didn't render without a browser; it isn't presented as terms.
- **Verdict: PERMITTED WITH CONDITIONS** (attribution notices above; the
  disclaimers).
- Good: an explicit open licence from an Alberta government body; boreal
  northeast Alberta is fire country (e.g. Fort McMurray 2016).
- Limits: one corner of the AB region, plains not mountains, so not an
  Alberta-wide April 1 value; survey dates within the year not checked
  (needs the data); updated in June, so 2027 surveys likely appear around
  June 2027, after the forecast. Useful as a regional check on ERA5-Land,
  not as Alberta's April 1 SWE.

### 4. Ruled out or not found

- **`open.alberta.ca` (OGL-Alberta):** searched by API for snow pillow,
  snow survey, snow course, snow water equivalent and water supply
  forecast. Only protocols and other publications (OGL-Alberta), no SWE
  data. "Mountain snow conditions and water supply forecasts for Alberta"
  holds 12 monthly PDFs from 2001-2002 only; current reports are on
  `rivers.alberta.ca`.
- **`rivers.alberta.ca` (snow courses, snow pillows, water supply
  outlooks):** the data Alberta would need, but no data licence (D30).
- **ECCC near-real-time SWE:** none found for Alberta stations; ECCC's
  station SWE is published through CanSWE. Open Canada's "Current Season
  Manual Snow Survey Data" and "Archive Automated Snow Weather Station
  Data" are British Columbia's, already used.
- **Gridded satellite SWE products** were not pursued: passive-microwave
  SWE products typically mask mountains, where Alberta's snowpack matters
  most, and ERA5-Land already covers the need.

## Last resort

Email Alberta Environment and Protected Areas (the `DATA_SOURCES.md`
Alberta row lists EPA.WaterSupply@gov.ab.ca for historical records) to ask
for the terms on `rivers.alberta.ca` snow data, so Alberta's own 2027 April
1 courses and pillows could be used. Only if ERA5-Land's agreement with
Alberta stations turns out too poor, and the owner decides to ask.
