# Phase 5: Close-out

- Status: Complete (2026-07-23)
- Depends on: Phase 4 (complete), [ADR-0004](../../adr/0004-work-directly-on-development.md)

## Goal

Wrap up the HD upgrade on `development` (no PR/rollout step — per
ADR-0004 all work lands on `development` directly).

## Entry criteria

- Phase 4 fully green: validation, tests, lint/type, playtest all pass.

## Tasks

- [x] Update `ATTRIBUTIONS.md` for any new/re-authored art per
      `CONTRIBUTING.md`'s asset contribution rules, if applicable.
      Not applicable — every shipped asset is an algorithmic
      derivative of the same CC-licensed art already attributed
      (recorded in 3b and re-confirmed in 3c); the Real-ESRGAN model
      is BSD-3-Clause tooling, not shipped content.
- [x] Push `development` to origin (andrevtg/Cariocamon).
- [x] Delete the `pre-hd-baseline` tag or keep it as a historical
      marker — decide and record here. **Kept AND pushed to
      origin**: it is not just historical — every enhancement script
      reads originals from it (`--ref pre-hd-baseline`), so it is
      required input for any future re-enhancement or another 2x
      bump. `hq2x-build` stays local-only (A/B rollback point,
      per the 3c exit criteria).
- [x] Update this epic's status to Done in `planning/roadmap.md`.

## Exit criteria

- `development` pushed, epic marked Done in `planning/roadmap.md`.

## Notes

Originally a rebase-and-PR rollout phase; reduced to a close-out
checklist when ADR-0004 moved all work onto `development` directly. Record any real-world surprises here as an "Outcome" note —
useful input for the next epic that uses this same planning method.

### Outcome (2026-07-23)

The epic (phases 3c, 4, 5) closed in a single session with no
rollout surprises. What the planning method should learn:

- The phase-3c spec's "gotchas" list (zsh word-splitting, git show
  repo-relative paths, compute-unit crash) paid for itself — every
  one recurred and was dodged. Write those sections.
- Two model input limits were NOT in the spec and cost a mid-batch
  crash: Core ML input must be 8–512 px per side after the NN-2x
  pre-upscale. Now recorded in GRAPHICS.md; pre-check file sizes
  against model limits before any future batch.
- Playtests kept surfacing pre-existing content drift unrelated to
  the epic (stale event syntax, dead music/environment slugs,
  missing set_environment on encounter maps). Sweeping the whole
  content tree for each *class* of error on first sight — instead of
  fixing single instances — turned four bug reports into four
  complete fixes. Consider a standing `scripts/`-style content-lint
  for slug references as a future epic.
- Counts in plans drift (spec said 77 tilesets; the tree has 76).
  Derive batch lists from the tree at execution time, use the plan's
  numbers only as sanity checks.
