---
name: read-licence
description: Establish what a data source's terms actually permit before building on it or publishing anything derived from it. Use when adding any dataset to DATA_SOURCES.md or before publishing the site. One source per run.
---

# Read a data source's licence

Adapted from the expanded-heatmap project. Goal: a verdict backed by the
publisher's own words, recorded in `DATA_SOURCES.md`.

## Steps

1. **Get the declared terms from the source itself.** Check the dataset page,
   any machine-readable metadata (ArcGIS `?f=json`, CKAN `package_show`,
   STAC/THREDDS metadata, CDS dataset "Licence" tab), and any README shipped
   with the download. A missing licence field does not mean permissive.
2. **Follow every pointer.** Phrases like "see our X notice", "subject to",
   "governed by" point to documents that are part of the terms. Open each one.
3. **Look for incorporation by reference.** "Use constitutes acceptance of",
   "terms of use" links: those documents now bind the data too.
4. **Separate website terms from data terms.** Language about "design, text,
   images" covers the website; "datasets", "redistribute", "derivative works"
   covers the data. Only the second decides what can be published.
5. **Check the original publisher, not just a mirror or catalogue.** A third-
   party catalogue may add its own terms on top.
6. **Capture three kinds of obligation separately:**
   - *Notices to display:* required credit lines and disclaimers, copied
     verbatim.
   - *Restrictions on claims:* e.g. no implied endorsement, no accuracy
     guarantees.
   - *Acts owed:* registration, notification, sharing results on request.
     Publishing does not discharge these; log them with dates.
7. **If a page won't load,** retry in a normal browser before recording it as
   unreadable.
8. **State one verdict:**
   - PERMITTED (quote the granting sentence)
   - PERMITTED WITH CONDITIONS (quote the conditions; mark notices vs acts)
   - SILENT (name the pages reviewed)
   - NOT PERMITTED or AMBIGUOUS (quote it; raise with the owner, never assume)

## Record

- `DATA_SOURCES.md` ledger row: licence as stated (exact title), attribution
  required, redistribution of derived outputs, retrieval date, residual issues.
- Required notices, verbatim, under "Notices this project must display".
- Acts owed, under "Acts owed to publishers".
- A `DECISIONS.md` entry if the verdict changes what the project can do.
