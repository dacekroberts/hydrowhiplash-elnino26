# Addendum 3: the finer coast and a whiplash scene

For the film already in this chat. Both changes land in one re-export, dark and light.
Change nothing else: the pace constant, the other scenes' timings and the credits layout stay.

## Finer coast (Scene 2)

`card_map_shapes.json` replaces the outlines in `map_shapes.json`. Same frame: SVG path data,
x to the right, y down, in a 640 by 690.4 box. Per region: `d` (closed rings to fill),
`border` and `coast` (open lines), `label` (the same label point as the map page). The top-level
`coast` is land outside the regions. The file is about 205 KB; report if that breaks a limit or
slows the scene. A boundary is `border` only where another region shares it, or on a long inland
run of a region's largest part; islands and lakes are always `coast`. Compare the two files and
report what changes before swapping. Keep the existing rule for BC: the bright line on its
mainland only, drawn as already approved.

## Whiplash scene (new, between Scenes 7 and 8, about 12 to 15 s)

Card line (DRAFT, the owner may reword it; show as written and list it in the return notes):

> A wet winter changes what burns in only some places: more the next year in Northern California, less the same year in Alberta.

Show the two rows in `addendum3_whiplash_tests.json`, the way Scene 7 shows a result. The percent
is the plain reading; the estimate is in log points per 1 SD. You may draw the index from
`addendum3_whiplash_series.csv` behind or before them; `addendum3_ref_whiplash.png` shows the look.

## Rules for the scene

- The two rows are H5, a test of wet winters (October to March precipitation) against burned area.
  Both pass the Holm correction, and they are already in Scene 7. 'Significant' may be used for
  these two rows and nothing else in the scene.
- The series is the whiplash index: summer SPEI-3 minus winter SPEI-3. It is description only and
  was not tested. Never show a p-value, 'significant', or a link to burned area for it.
- Never say the index predicts a fire season: summer falls inside the season.
- A bar below zero swings from wet to dry. In the north a bar above zero can be a dry winter and a
  wetter summer, so don't call every large bar 'wet to dry'.
- Associations, not causes. No 'drives', 'causes' or 'leads to'. This is apart from El Niño: don't
  imply El Niño produces these two results.
- Every figure comes from these files. Reading time at least 3 s, as elsewhere. If the film passes
  3:00, flag it; don't shorten other scenes.
- Credits: ERA5-Land and burned area, as Scene 7 carries them (credits.md in the first bundle).

## What comes back

- Both MP4s at 1920 x 1080, 30 fps.
- Every scene's new start time and length.
- What the finer coast changed in Scene 2: label or pill moves, and draw speed.
- Every new on-screen line, word for word, for the site's transcript.

## Files and why each may leave the repository

| File | Why |
|---|---|
| `addendum3.md` | this note |
| `card_map_shapes.json` | committed in the public repository; display only; land from Natural Earth (public domain) |
| `addendum3_whiplash_tests.json` | rows of results/tables/run1/registered_tests.csv, public |
| `addendum3_whiplash_series.csv` | columns of results/tables/whiplash_swe_region_year.csv, public; no fire data |
| `addendum3_ref_whiplash.png` | results/figures/, drawn by code; (c) Dace Roberts |
