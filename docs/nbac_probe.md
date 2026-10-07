# NBAC probe (documentation only), 2026-10-07

Facts for the owner's choice on D56 (CNFDB polygons end in 2024, while the
frozen plan's fire tests run to 2025) for BC, AB and YT. The options as
the main session framed them:

- **(2)** end the Canadian fire series at 2024;
- **(3a)** NBAC fills 2025 only, fixed now, with CNFDB 2025 reported beside
  the results when it arrives (about January 2027), never substituted;
- **(3b)** NBAC for the whole Canadian series, 1984-2025.

This file answers questions about the National Burned Area Composite
(NBAC). It does not choose an option.

**How it was read.** Only documentation, metadata, catalogue records,
licence pages and method papers. No perimeter file, raster, service,
attribute table or burned-area summary was opened, for any year.

- **Skipped as data or values:** every `*_shp.zip` and annual
  `NBAC_YYYY_*.zip`, the `NBAC_MRB` rasters, `NBAC_summarystats_*.xlsx`,
  the burn-map PNGs, the WFS/WMS links and the CWFIS fire-history explorer.
- **The metadata PDF:** a print of an HTML page with no text layer. It was
  rendered to page images in a scratch folder (PyMuPDF installed there, not
  in the `whiplash` environment) and read from the images.
- **Who checked what:** a research agent read the pages. The catalogue
  licence and citation, the release listing, the ISO dates, the lineage
  and the date-field definitions were rechecked directly.

**Incidental exposure, disclosed.** None of these is a BC, AB or YT value,
and none was copied:

- a summarising fetch of the Hall et al. (2020) abstract carried one
  national 2004-2016 mean annual area;
- a sentence search of Skakun et al. (2022) surfaced one ecozone trend
  slope and one NWT caribou-habitat figure;
- the metadata PDF shows the record count of the merged file.

## Sources

| Short name | Source | How read |
|---|---|---|
| Catalogue | CWFIS catalogue record https://cwfis.cfs.nrcan.gc.ca/en/catalogue/results/537a1fd0-698e-4a7b-85a1-e02581ae78b2 | Browser |
| Listing | https://cwfis.cfs.nrcan.gc.ca/downloads/nbac/ (directory listing: names and dates only) | curl |
| ISO | GeoNetwork ISO 19115 record 537a1fd0-698e-4a7b-85a1-e02581ae78b2 (`catalogue.cwfif.nrcan.gc.ca/geonetwork/srv/api/records/.../formatters/xml`) | curl |
| Metadata PDF | `NBAC_1972to2025_20260513_shp_metadata.pdf` (ArcGIS metadata "NBAC_metadata_20260513", printed 15 May 2026) | Rendered pages |
| README | `downloads/nbac/archive/README_updates.txt` (release notes to v20240530) | curl |
| Hall 2020 | Hall, R.J., Skakun, R.S., Metsaranta, J.M., et al. (2020). Generating annual estimates of forest fire disturbance in Canada: the National Burned Area Composite. *Int. J. Wildland Fire* 29, 878-891. doi:10.1071/WF19201 | Summarising fetch (the publisher's page sits behind a bot check) |
| Skakun 2022 | Skakun, R., Whitman, E., Little, J.M., Parisien, M.-A. (2022). *Remote Sensing* 14(13), 3050 | Browser |
| Skakun 2024 | Skakun, R., Castilla, G., Jain, P. (2024). Mapping wildfires in Canada with Landsat MSS, 1972-1983. *Int. J. Wildland Fire*, WF24138 | Summarising fetch |
| OGL-C | https://open.canada.ca/en/open-government-licence-canada (v2.0) | curl and browser |

Quotes from Hall 2020 and Skakun 2024 passed through a summarising fetch.
Check them against the PDFs before quoting them anywhere public.

## 1. Coverage

- **The current release includes 2025:**
  - stamp **20260513**, years **1972-2025** (Listing):
    `NBAC_1972to2025_20260513_shp.zip` and annual `NBAC_2025_20260513.zip`,
    all dated 22-May-2026;
  - ISO: creation and publication 2026-05-13; temporal extent begins 1972;
    maintenance "annually"; status "onGoing";
  - Metadata PDF: lineage heading "NBAC v20260513".
- **Update rhythm:** Catalogue: "Maps are available for each year back to
  1972 and are updated to current year at the end of each wildfire
  season."
- **BC, AB and YT in 2025:** no document lists 2025 coverage by province.
  - The `ADMIN_NAME` codes include AB, BC and YT (Metadata PDF).
  - The v20260513 lineage says "includes improved agency data from Alberta
    for years 2021 to 2024". It is silent on 2025.
  - The CNFDB polygon release ends at 2024 for all three (DATA_SOURCES.md
    CNFDB row).
  - So whether the 2025 BC, AB and YT polygons rest on agency perimeters
    or on satellite mapping alone is **undocumented**.
- **Version mismatch:** the Metadata PDF gives update frequency "as
  needed"; the ISO record says "annually".

## 2. Unit

- **Vector polygons grouped into fire events, not pixels:**
  - Metadata PDF: "Geometry type Polygon"; "Object type composite".
  - Hall 2020: "each fire event is assigned a unique National Fire
    Identification (NFIREID) value, where a fire event comprises one or
    more polygons over a localised spatial region for a specific year."
- **One record is not always one fire.**
  - README (2019): "NBAC burn polygons subdvided by provincial,
    territorial, and national parks boundaries".
  - `NFIREID` is the common ID that links a fire event crossing such a
    boundary.
  - `GID` concatenates fire year and `NFIREID`, "useful for selecting
    unique fire records merged by year" (Metadata PDF).
  - A per-fire 405 ha floor therefore needs the records dissolved by `GID`
    (or year plus `NFIREID`) first. That fits the plan's rule: floor on
    the whole fire's `area_ha`, then clip.
- **Overlapping polygons are merged into one event:** Hall 2020: "agency,
  MAFiMS and HANDS polygons intersecting with the same fire event polygon
  in a given year are assigned the same NFIREID value".
- **Separate raster products exist:** `NBAC_MRB_1972to2025_30m` and
  `_250m`. They were not opened, and the polygons are the relevant product.

## 3. Dates

Field definitions, verbatim from the Metadata PDF (rechecked):

- **`HS_SDATE`:** "the date of the first detected hotspot within the
  spatial extent of the fire event. Null if no hotspots were detected.
  AVHRR hotspots are used from 1989 to 2000. MODIS hotspots are from 2001
  to current." (`HS_EDATE` is the same, for the last hotspot.)
- **`AG_SDATE`:** "the fire start date reported by the agency. The date
  could also represent the recorded date or detection date of the fire by
  the agency. Where different dates are recorded by agencies for
  cross-border fires, NBAC uses the earliest date. Null if agency date was
  not provided." (`AG_EDATE` is the agency end date.)
- **`CAPDATE`:** "the acquisition date of the source data. Examples
  include date of GPS acquisition, air photo acquisition, and satellite
  image."

What this means for the fire windows:

- **No field is a true ignition date.** `AG_SDATE` is the closest, and it
  may be a detection or recorded date. `HS_SDATE` is satellite first
  detection.
- **Before 1989, hotspot dates are null by construction.** Fire seasons
  1984-1988 depend on agency dates alone.
- **Completeness, as documented:**
  - Skakun 2022, 1986-2020: "Fire start and end dates from satellite
    hotspots or agency metadata were present in 82% of all fire polygons,
    corresponding to 98% of the total burned area."
  - Skakun 2022: "Some fire dates were missing because hotspot data
    collections did not begin until 1989 and not all agencies recorded a
    start or end date for every fire."
  - Agency dates are "transferred from the agency polygon to its
    counterpart in MAFiMS or C2C" (Skakun 2022), so a satellite-mapped
    polygon can carry the agency date.
- **Not documented:** completeness of each field separately, by year
  range or by province. Measuring it would mean opening the attribute
  table, which this probe did not do.

## 4. Fire type

- **A flag exists:** `PRESCRIBED` "identifies a prescribed fire as
  reported by the agency"; the only listed value is "true" (Metadata PDF).
  It was added in v20240228 (README: "added a field for prescribed fires
  (true/false)").
- **Cause field:** `FIRECAUS` "Human" lists "prescribed burn" among its
  examples (Metadata PDF).
- **Not excluded by construction.** Burns the agency did not report as
  prescribed, and satellite-only polygons without an agency counterpart,
  are presumably not flagged. That is undocumented.

## 5. Method and relation to CNFDB

**How it is built:**

- Catalogue: NBAC "provides annual maps of burned area polygons using the
  best-available fire perimeter data collected from the Canadian fire
  agencies combined with satellite-derived fire data from Natural
  Resources Canada."
- A rule picks one source per fire event (Metadata PDF: "A rule-based
  decision process is used to select the best data source for each fire
  event").
- **2004 onward** (Hall 2020): "the NBAC selects MAFiMS polygons when
  available, then agency polygons, followed by HANDS polygons (if no other
  data source is available)". Agency polygons from aerial photography or
  high-resolution imagery are preferred over MAFiMS. Hall reports shares
  of 2004-2016 area of about 66% MAFiMS (Landsat), 33% agency and 1.5%
  HANDS (method shares, not burned-area values).
- **1986-2003** (Skakun 2022): priority "higher quality agency data (e.g.,
  from aerial photography), MAFiMS, C2C, lower quality agency data (e.g.,
  aerial survey), and HANDS".
- **1972-1983** (Skakun 2024): Landsat MSS mapping; "CNFDB data were used
  when a particular fire could not be mapped by MSS".
- **1984-1985:** how these two years were built is not stated in the
  documents read. They sit between the MSS era and the 1986 start of
  Skakun 2022, so this matters for option (3b).
- **Per-record source:** `BASRC` takes MAFiMS, C2C, TFMS or Agency;
  `FIREMAPS` gives the platform; `FIREMAPM` the delineation method
  (Metadata PDF).
- **By province:** no source mix is documented, only examples, such as
  aerial-photo agency polygons being "all in Alberta" (Skakun 2022).

**Are the pre-2025 polygons the CNFDB polygons? Partly.**

- Agency polygons in NBAC come from CNFDB or the agencies: "CNFDB fire
  polygons for the period 1986 to 2003 were obtained from the Canadian
  Wildland Fire Information System" (Skakun 2022).
- Many agency polygons are replaced by Landsat mapping (MAFiMS, C2C, MSS).
- v20260513 "includes remapped agency polygons using MAFIMS for years 1984
  to 2024" and "includes new mapped fires that were previously missed for
  years 1984 to 2024" (Metadata PDF lineage).
- NBAC is therefore a different mapping from CNFDB, not a copy.

**Documented differences in area** (method level only; no values were read):

- Hall 2020: NBAC estimates are "mostly lower than those of the CNFDB,
  largely because the MAFiMS was used to replace large, broadly delineated
  agency polygons that included unburned forest islands and water". In a
  few years NBAC is higher, where it "captured fire events that were not
  mapped by the agencies".
- Skakun 2022: CNFDB-style agency mapping "overestimated annual burned
  area by 11% on average since comprehensive reporting began in the
  1950s".
- Skakun 2024: "Compared with MSS, the CNFDB perimeters reported a 16.6%
  greater area on average" (1972-1983).
- **What this means for the options:**
  - for **(3a)**, the 2025 value (NBAC) and 1984-2024 (CNFDB) come from
    methods documented to differ in area, typically by about 10-17%, with
    NBAC lower;
  - for **(3b)** there is no splice, but the series mixes sources by era
    (MSS and CNFDB fallback before 1986, a different priority order in
    1986-2003 and from 2004).

## 6. Known limits

- **Minimum mapped size:** none for the product as a whole; it varies by
  source.
  - Agency polygons: README (2016): "removed the 10 ha minimum size filter
    for agency burns".
  - HANDS: 50 ha after 2013 (Hall 2020).
  - MSS era: 200 ha (Skakun 2024).
  - C2C: polygons with no other source were checked by hand only above
    1,000 ha (Skakun 2022).
  - All of these sit below the project's 405 ha floor.
- **Resolution:** Landsat 30 m and MSS 60 m, plus Sentinel-2 (Metadata PDF
  `FIREMAPS` values).
- **Unburned islands:**
  - removed in polygons covering most of the area (Hall 2020, about 90%);
  - lower-quality agency and HANDS polygons carry a modelled adjusted area
    (`ADJ_HA`, where `ADJ_FLAG` = 2; README 2021) instead;
  - the project measures area from geometry (`src.geo.area_ha`), not
    `ADJ_HA`, so those polygons count at their full outline;
  - MTBS boundaries also keep unburned islands inside ("do not delineate
    unburned islands", MTBS FAQ).
- **Gaps:** no hotspot dates before 1989; how 1984-1985 were built is not
  documented (section 5).
- **Revisions:** past years change between releases. v20260513 changed
  1984-2024 (lineage above), and `VERSION` "identifies the annual dataset
  version". The release used must be fixed by its stamp at download.
- **Preliminary status:** none is documented for 2025. Hall 2020 describes
  mapping as "an annual exercise performed the year after the fires
  occur". 2026 is not in the release.

## 7. Licence

The full read is in `DATA_SOURCES.md` (NBAC row, notice 11). In brief:

- **Licence:** Open Government Licence - Canada 2.0 (Catalogue and ISO).
- **Verdict:** PERMITTED WITH CONDITIONS.
- **Conditions:**
  - the provider's citation and a licence link;
  - no endorsement, crests or logos;
  - the third-party-rights exemption, the same open question as CNFDB.
- **No act owed.**

## Open, not answerable from documentation

- Which source stands behind the BC, AB and YT polygons in 2025 (agency or
  satellite only).
- How 1984 and 1985 were built.
- Completeness of `AG_SDATE` and `HS_SDATE` by year and province.
- Whether `PRESCRIBED` and `FIRECAUS` are carried onto satellite-only
  polygons.

Each needs the attribute table, so it can only be measured after the
option is fixed.
