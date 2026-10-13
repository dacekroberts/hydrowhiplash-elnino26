# Addendum 1: the results that came close

For the film already in this chat. One supporting beat is added to Scene 7; nothing else changes. The beat's line and any row marked draft are suggestions for the owner to word.

## What the beat shows

8 of the 52 registered tests have a two-sided 95% interval that excludes zero. 4 of them pass the Holm correction and are in Scene 7 already. The other 4 are this beat. The rule picks them: no cut-off was chosen by eye.

| Rank of 52 | Region | Test | Estimate | 95% interval | Holm p | Wording |
|---|---|---|---|---|---|---|
| 5 | Alberta | H6 (winter water balance and burned area) | -0.394132 | -0.712703 to -0.0755604 | 0.0666769 | draft |
| 6 | Northern California | H5 (wet winters and burned area, same year) | -0.470479 | -0.820098 to -0.120861 | 0.0774874 | approved 2026-10-13 |
| 7 | Alberta | H1 (winter precipitation, El Niño winters against the rest) | -8.72334 | -15.7212 to -1.83089 | 0.0863914 | approved 2026-10-13 |
| 8 | Alberta | H6 (1 April snowpack and burned area) | -0.59544 | -1.12235 to -0.0685249 | 0.0973437 | approved 2026-10-13 |

Units and the percent changes are in addendum1_close_tests.json. A burned-area row is in log points per one standard deviation of the winter measure; pct_change is the same figure as a percent.

## Suggested line

4 more have an interval clear of zero but did not pass the correction. 3 of them are in Alberta.

## Rules for the beat

- The beat sits inside Scene 7, after the results that pass. The film stays at 150 s at most and the pace constant is not raised to fit it. If it does not fit, say so in the return notes and build Scene 7 as approved.
- 'Significant' still means only the 4 of 52 tests that pass the Holm correction. The 4 in this beat are never called significant, nearly significant, borderline, marginal or a trend. Their name on screen is the rule: 'interval clear of zero; did not pass the correction'.
- They are drawn below the results that pass and lighter: the same interval bar, a hollow mark where a passing result has a filled one, text in the muted ink. The reference picture shows the two forms as the site draws them.
- Each shows its region, its label and description as written in addendum1_close_tests.json, then its estimate and interval. No p-value is needed; if one is shown it is p_holm.
- A row marked draft carries wording the owner has not approved; show it as written and list it in the return notes.
- Associations, not causes, as for the rest of the film. None of the 4 sets El Niño against burned area, so card line 6 stands unchanged.
- The beat carries Scene 7's credits (credits.md in the first bundle).

## What comes back

- Scene 7's new start time and length, and the start time of the beat.
- Every figure on screen in the beat, and the wording shown with it.
- Whether the beat fitted without changing the pace constant or another scene's length.

## Prompt to paste

Addendum 1 to the bundle you already hold: three files, addendum1.md, addendum1_close_tests.json and addendum1_ref_passed_and_close_dark.png.

Add one supporting beat at the end of Scene 7, as addendum1.md describes. Take every figure from addendum1_close_tests.json and keep the rules in addendum1.md, above all the one on the word 'significant'.

Change nothing else in the film. Send back what addendum1.md lists under 'What comes back'.

## Files and why each may leave the repository

| File | Why |
|---|---|
| `addendum1.md` | this note; results/tables/run1/registered_tests.csv as committed: all 52 registered tests; public in the repository |
| `addendum1_close_tests.json` | rows of the same table, cut by rule; results/tables/run1/registered_tests.csv as committed: all 52 registered tests; public in the repository |
| `addendum1_ref_passed_and_close_dark.png` | drawn by code from the same table; (c) Dace Roberts |
