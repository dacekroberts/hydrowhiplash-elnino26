# Claude Code Project setup (Phase 4)

**DRAFT, revisit at integration.** Written 2026-10-04 from the planning-chat
handoff. The Project feature was in public beta then; re-check its docs
(thread model, Remote Control version, instruction limit) before relying on
anything below. Reasoning: DECISIONS.md, 2026-10-04 "Working setup".

## When

At the start of Phase 4, right after the freeze gate and Phase 3 (about week
4, late Oct or early Nov 2026). Until then the work is sequential and
data-heavy (downloads, regridding, SPEI, fire clipping) and runs on this
machine anyway, so cloud threads add overhead, not speed. Phase 4 splits into
independent tasks (H1-H5, site pages, methods page) that suit parallel
threads, and PR-reviewed changes after the freeze are good evidence the
pre-registered tests were followed. The live 2026-27 tracker (from Nov 2026)
fits a monthly project routine.

Set it up earlier only if two or more queued tasks don't need local data.

A Project was created on 2026-10-04 and is on standby, told not to start
threads until Phase 4. Its instructions are a placeholder; replace them with
the draft below.

## Checklist

- [ ] `ANALYSIS_PLAN.md` is frozen (dated commit) and Phase 3 is done.
- [ ] Licences read with the `read-licence` skill for every source behind the
      tables (ERA5-Land, ENSO index, snowpack, MTBS, WFIGS/NIFC, CNFDB), and
      `DATA_SOURCES.md` confirms derived tables may be committed.
- [ ] Analysis-ready region x year tables written by code to `results/tables/`
      (committed), alongside the working copies in `data/processed/`. Cloud
      threads only see committed files, and `data/` is never committed.
- [ ] Claude Code on this computer is v2.1.280 or later, for Remote Control.
- [ ] Project instructions replaced with the draft below, checked against the
      current CLAUDE.md, and kept well under the 16,000-character limit.
- [ ] Branch protection on `main` (PRs required) considered, so thread work
      can only land through review.
- [ ] First thread is a small, low-risk task (e.g. one site page) to test the
      branch, PR and report flow before the hypothesis tests.
- [ ] Standby message withdrawn; DECISIONS.md entry for the integration.

## Draft project instructions

```
Project: hydrowhiplash-elnino26 (github.com/dacekroberts/hydrowhiplash-elnino26)

Conventions, measurement rules and analysis rules are in CLAUDE.md at the repo
root. Read it first; it overrides anything here that conflicts. State lives in
ACTION_PLAN.md (open work), ANALYSIS_PLAN.md (pre-registered tests, frozen)
and DECISIONS.md (the official decision record).

Project-specific rules:

1. Threads branch from main and open a PR. The owner reviews and merges.
   Never merge, force-push, rewrite history, or edit ANALYSIS_PLAN.md above
   its deviations log. A change to a pre-registered test is a deviation row,
   not an edit.
2. No fire data (MTBS, WFIGS/NIFC, CNFDB) is downloaded, opened or
   summarised until ANALYSIS_PLAN.md is frozen.
3. Anything that downloads data or reads data/ runs on the owner's computer
   via Remote Control, never in the cloud. The Copernicus key (.cdsapirc)
   stays on that computer. Cloud threads work from committed files only,
   including the region x year tables in results/tables/.
4. Threads do not edit logs/. Each thread ends its report with a session
   block in the daily-log format (### HH:MM-HH:MM · Claude Code, timestamped
   bullets, plus any decisions and next step). One end-of-day log thread
   writes logs/YYYY-MM-DD.md from those reports with the daily-log skill.
5. Judgment calls go in DECISIONS.md in the PR that makes them. Project
   memory is for working preferences only, never for decisions or results.
6. Run python -m pytest and python scripts/check_no_em_dashes.py before
   opening a PR, and report the results in the PR description.
7. Flag scope additions in the PR description rather than implementing them.
```
