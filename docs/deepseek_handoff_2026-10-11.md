# DeepSeek handoff: hydrowhiplash-elnino26

Handoff from the DeepSeek integration session, 2026-10-11, for a Claude Code
session in this repo. It sits beside `hydrowhiplash-elnino26_PORTFOLIO_REVIEW_NOTES.md`
(the project plan) and only answers one question: **which of this repo's work
should go to the DeepSeek worker, and how.**

**This is a starting brief, not a ruling.** CLAUDE.md, ANALYSIS_PLAN.md and
the decision log outrank it. If something here clashes with them, say so to
Dace and log the correction.

**First pass: read and propose. Change nothing yet.**
1. Read this file, then CLAUDE.md, `ACTION_PLAN.md` Phase 4 and the
   portfolio review notes.
2. Run no DeepSeek call, edit, commit or install on the strength of this file.
3. Reply to Dace with: which candidates below you agree with, which are wrong
   for this repo (with evidence), the order you'd run them in, and your
   questions.
4. Wait for Dace's go-ahead before the first delegation.

---

## 1. How the DeepSeek setup works (short version)

- Use the `deepseek-delegate` skill for every run. Claude plans and verifies;
  DeepSeek builds one bounded task in its own git worktree; Dace approves each
  run and each merge.
- The skill asks before every DeepSeek call, runs a free compatibility check
  first, and logs each run (with token counts) in `~/tools/deepseek/runs.log`.
- **To stop a run:** say "stop the DeepSeek worker". On Windows, stopping the
  background task alone does not stop the worker; the skill also runs the
  stop helper.
- Off-peak (half price) on weekdays is outside 6 to 9 pm and 11 pm to 3 am
  Pacific until Nov 1, and 5 to 8 pm and 10 pm to 2 am after it. Weekends are
  off-peak all day.
- Everything the worker reads goes to DeepSeek, an outside service.

**Lessons from the pilot (Oct 11) that apply here:**
- The build path worked when the plan carried a written acceptance file and
  every check was mechanical. Claude's verification stayed cheap.
- The plan is Claude's main cost. When the plan would be as long as the code,
  Claude should just write the code.
- The pilot was easy: every data trap was in the plan. **This repo is the
  natural place for the harder test** (section 4).

## 2. Good candidates

| Work (from the review notes) | Why it fits | Settings | Acceptance |
|---|---|---|---|
| Runner safeguards S2 to S6 (ACTION_PLAN Phase 4), one safeguard per run | Code with a clear contract, an existing test suite (210 tests) to extend, and no analysis judgment | `deepseek-v4-pro`, high | New tests for the safeguard pass, the full suite still passes, scope check, and a fault the safeguard must catch (a planted bad input) |
| New unit tests around existing helpers (for example `src.geo.area_ha`, config loading) | Mechanical; adds to the audit trail | `deepseek-v4-pro`, high | Tests pass on the current code and fail on a planted mutation Claude writes |
| A bug-hunting review of runner code before Nov 6 | A second model's eyes on code that five audit rounds already covered; cheap | `deepseek-flash`, max | Findings printed, each checked by Claude before it counts |
| Plotting code for the "What happened after past El Niño winters" chart, once results exist | Bounded, reads `results/` only | `deepseek-v4-pro`, high | The chart's numbers match `results/`; reruns from scratch |

## 3. Keep with Claude or Dace

- **Anything that touches ANALYSIS_PLAN.md, `src/config.py` tunables, test
  choices or a deviation.** The plan is frozen; a deviation needs a log row and
  a `[mid-project: Dnn]` marker, and that judgment stays with Claude and Dace.
- **The NBAC and Interior Alaska decide-before-any-test items.** They are
  logged yes-or-no decisions, not code.
- **The registered runs themselves (Nov 6).** Claude runs and checks them.
- **Results wording, the methods paragraphs, the responsibility statement,**
  the "why not ML" paragraph: Dace's prose; Claude drafts only when asked.
- **The daily log and the data guide artifact refresh.** Required every
  session by CLAUDE.md, and written by the main session, not the worker.
- **Licence reads** (`read-licence` skill).

## 4. The harder pilot: one safeguard, less spoon-feeding

The Oct 11 pilot proved the build path on an easy, fully specified task. This
repo's safeguards are the right size for the next test, where the worker has
to read the existing runner and work out where the change goes.

- **Pick one safeguard** (Claude proposes which, from S2 to S6, the one least
  tangled with the others).
- **Write the plan as a goal plus acceptance tests**, not a step-by-step
  recipe: what the safeguard must refuse, the tests that prove it, the files
  it may touch. Don't list every trap. Note in the plan which things Claude
  deliberately left out, so the efficiency review can judge what the worker
  found by itself.
- **Time-box it to before Oct 25**, so a failed attempt can't threaten the
  Nov 6 date. If it fails twice (the skill's retry limit), Claude builds it.
- **Afterwards, run the `deepseek-efficiency-review` skill** (it exists on
  Dace's machine) and add a row to `~/tools/deepseek/efficiency-reviews.tsv`.

## 4b. Rules for every plan in this repo

- The worker works inside its worktree only. Name the allowed files; forbid
  ANALYSIS_PLAN.md, `src/config.py`, the decision log, the daily logs and
  anything under `results/` unless the task is the chart.
- **No data files go to DeepSeek.** Raw ERA5 and fire tables aren't in the
  worktree if they're gitignored; keep it that way. Tests use small synthetic
  fixtures that the plan describes.
- The worker loads this repo's CLAUDE.md and skills. Tell it in the plan not
  to run the `daily-log` or `read-licence` skills and not to start subagents;
  those belong to the main session.
- The worktree has no virtual environment. The plan says how to get one (or
  the skill's preflight confirms the environment Claude will use for checks).
- **Shared machine memory (32 GB):** don't run a DeepSeek build while a large
  ERA5 job or expanded-heatmap's batch is running.
- Each DeepSeek run gets a line in that day's daily log: what was delegated,
  the outcome, and the runs.log line.

## 5. Open decisions for Dace

1. Use the safeguards as the harder pilot, or keep them all with Claude
   because of the Nov 6 date?
2. Is a DeepSeek review of the runner worth adding as a sixth audit round
   before the registered runs?
3. Should DeepSeek's involvement be mentioned in the methods page, and how?
   (If it writes any code that produces results, I'd say yes, one line.)

## How to start the session

Open Claude Code in `~\Documents\Portfolio\hydrowhiplash-elnino26` and paste:

```
Read the attached hydrowhiplash-elnino26_DEEPSEEK_HANDOFF.md and follow its "First pass: read and propose" steps. Do not run DeepSeek yet.
```

Attach or point to this file's path wherever you saved it.
