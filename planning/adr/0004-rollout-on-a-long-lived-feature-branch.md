# ADR-0004: Rollout on a long-lived feature branch, prove the pipeline first

- Status: Proposed
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

ADR-0001 established that the resolution/constant bump is all-or-nothing —
there is no supported mixed-resolution state. ADR-0003's scope is ~1,554
image assets and 263 maps. A partial-resolution game state (some assets
upgraded, some not) is not shippable, and this volume of asset production
cannot reasonably land in one PR or one session.

## Decision

Do the engine/constant change (ADR-0001, ADR-0002) on a dedicated feature
branch off `development`, per this project's standard contribution model
(`CONTRIBUTING.md`: work from a feature branch, never commit directly to
`development`). Before committing to full asset production, prove the
pipeline end-to-end on a small representative slice — one tileset, one NPC
sprite sheet, one icon category — validated against the schema validator
and a manual playtest. Only after that slice round-trips correctly does
asset production (ADR-0003) scale up, on the same long-lived branch, merged
to `development` once every category is complete and validated (see phase
04-validation).

## Consequences

- The branch will be long-lived relative to typical Tuxemon PRs; keep it
  rebased/synced with `development` periodically to limit merge conflict
  risk against unrelated ongoing work.
- Nothing here ships incrementally to players — the upgrade is a single
  merge event once all phases pass validation, which is a deliberate
  tradeoff for correctness over incremental delivery.
