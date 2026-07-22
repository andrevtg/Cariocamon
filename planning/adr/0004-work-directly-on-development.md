# ADR-0004: Work directly on development, prove the pipeline first

- Status: Accepted
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

ADR-0001 established that the resolution/constant bump is all-or-nothing —
there is no supported mixed-resolution state. ADR-0003's scope is ~1,554
image assets and 263 maps, which cannot reasonably land in one sitting.

An earlier draft of this ADR planned the epic on a long-lived feature
branch, following upstream Tuxemon's contribution model
(`CONTRIBUTING.md`). In practice this repo is a personal fork
(`andrevtg/Cariocamon`) with a single developer: Phase 1's PR (#1)
could not even be approved (GitHub forbids self-approval) and added
ceremony without review value.

## Decision

Commit epic work directly to `development` — no feature branches or
PRs within this fork. Two mechanisms replace the safety the branch
model would have provided:

1. **A git tag before the breaking window opens.** Immediately before
   the Phase 2 constant bump lands, tag `development` as
   `pre-hd-baseline` — the last commit where the old-resolution game is
   fully playable and schema-valid. Anything needing a working game
   (bisects, side quests, demos) checks out that tag until Phase 3
   completes.
2. **Prove the pipeline before scaling up.** Before committing to full
   asset production, prove the pipeline end-to-end on a small
   representative slice — one tileset, one NPC sprite sheet, one icon
   category — validated against the schema validator and a manual
   playtest (Phase 2's throwaway test assets). Only then does asset
   production (ADR-0003) begin, and Phase 4's validation gate is
   unchanged: working on `development` changes where commits land, not
   the bar for declaring the epic done.

## Consequences

- Between the Phase 2 bump and the end of Phase 3, `development` will
  not validate or play correctly — ADR-0001's "no mixed-resolution
  state" now applies to the default branch instead of a feature
  branch. Accepted for a solo fork; `pre-hd-baseline` is the fallback.
- Phase 5 shrinks from a rebase-and-PR rollout to a close-out
  checklist (roadmap status, attributions, push).
- Work intended for upstream `Tuxemon/Tuxemon` still needs feature
  branches + PRs per `CONTRIBUTING.md` — this ADR covers the fork only.
