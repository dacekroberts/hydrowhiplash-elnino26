# Brief

The decisions, the scene skeleton and the card lines are approved (owner, 2026-10-13). Later changes are made in the Motion session and come back in its return notes.

## Decided by the owner, 2026-10-13

- One film, 16:9, 1920 x 1080 px, 30 fps, 150 s at most.
- A shorter cut or a longer one is decided after this film is seen. Build each scene as its own module so one can be dropped or stretched.
- Dark first. The light film waits until the dark one is refined: keep every colour in one theme module, read from tokens.json, so light is a switch.
- The seven regions are shown on a real map in one scene (map_shapes.json).
- One pace constant for every cut and camera move, set in one place. Start slow: the last film's cuts were judged too fast.
- Typefaces from the files here: National Park for display, Public Sans for text, JetBrains Mono for figures.

## Rules the film keeps

- Every figure on screen comes from numbers.json, tests.csv, seasons.csv or winters.csv. None is typed or rounded differently from the site.
- Every year is drawn. El Niño years are highlighted on the full record, never shown alone.
- Associations, not causes: no 'drives', 'causes' or 'leads to' for a result.
- 'Significant' is used only for the 4 of 52 tests that pass the Holm correction. 0 of the 25 tests that set El Niño against burned area pass it; the film says so plainly.
- Effect size and interval before any p-value. A null result is shown as a result.
- No season after the ones in seasons.csv is drawn. 2027 appears only as an empty slot or a date.
- Burned area counts fires of 405 ha or more, by ignition date, in each region's fire season.
- The map is a picture: nothing is measured from its shapes, and one shade covers a whole region.
- A scene that shows burned area or climate values carries its sources' credit (credits.md). The closing card carries all of them.
- Nothing flashes more than three times a second.

## Scene skeleton (approved 2026-10-13)

| # | Start | Length | On screen | Draws from |
|---|---|---|---|---|
| 1 | 0 s | 15 s | The question, over the season strips of all seven regions. | seasons.csv, ref_banner_social_dark.png |
| 2 | 15 s | 18 s | Where: the seven regions on the map, north to south, named once. | map_shapes.json |
| 3 | 33 s | 21 s | The idea being tested: the two pathways, north and south, built step by step. Only the diagram's two top boxes and three steps a side; no footnotes. | numbers.json (mechanism), ref_mechanism.png for the look |
| 4 | 54 s | 15 s | How it was tested: four sources into one table, the plan frozen before any fire data was read, the tests run once. | numbers.json (flow), ref_project_flow.png |
| 5 | 69 s | 27 s | The record: winters, then the fire seasons that followed, El Niño years highlighted on the full record. | winters.csv, seasons.csv |
| 6 | 96 s | 24 s | The main result: El Niño against burned area, region by region, every interval crossing zero. | numbers.json (ledger, counts), tests.csv |
| 7 | 120 s | 18 s | What did pass: the four results, each with its estimate and interval. | numbers.json (survived) |
| 8 | 138 s | 12 s | What comes next: the dates up to the 2027 season, and the site's address. | timetable.csv, numbers.json (next) |

Total 150 s.

## Card lines (approved 2026-10-13)

One line per scene. The site's address closes scene 8: hydrowhiplash.dacekroberts.dev

1. Does an El Niño winter say how much the next fire season will burn?
2. Seven regions, from Alaska to Southern California.
3. The idea: after an El Niño winter the north runs milder and often drier, the south wetter.
4. I fixed 52 tests in writing before opening any fire data, then ran them once.
5. Every fire season since 1984. A shaded year follows an El Niño winter.
6. 0 of the 25 tests that set El Niño against burned area are significant. Every interval crosses zero.
7. 4 of 52 tests are significant after correcting for the number of tests. These are associations, not causes.
8. A forecast for 2027 goes up before the season and is checked against it afterwards.

Scene 7 also shows each of the results that pass, with its label and its description as written in numbers.json (survived: label, what, note), then its estimate and interval.

## What comes back

- The dark film at the size above, exported from the film's page; light follows later.
- A scene table with each scene's start time and length.
- Every figure and every credit on screen, per scene.
- Any on-screen wording added or changed since this brief.
- The value of the pace constant and where it is set.
