# Phase 5: Close-out

- Status: Not started
- Depends on: Phase 4 (complete), [ADR-0004](../../adr/0004-work-directly-on-development.md)

## Goal

Wrap up the HD upgrade on `development` (no PR/rollout step — per
ADR-0004 all work lands on `development` directly).

## Entry criteria

- Phase 4 fully green: validation, tests, lint/type, playtest all pass.

## Tasks

- [ ] Update `ATTRIBUTIONS.md` for any new/re-authored art per
      `CONTRIBUTING.md`'s asset contribution rules, if applicable.
- [ ] Push `development` to origin.
- [ ] Delete the `pre-hd-baseline` tag or keep it as a historical
      marker — decide and record here.
- [ ] Update this epic's status to Done in `planning/roadmap.md`.

## Exit criteria

- `development` pushed, epic marked Done in `planning/roadmap.md`.

## Notes

Originally a rebase-and-PR rollout phase; reduced to a close-out
checklist when ADR-0004 moved all work onto `development` directly. Record any real-world surprises here as an "Outcome" note —
useful input for the next epic that uses this same planning method.
