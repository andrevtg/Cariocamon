# Phase 5: Rollout

- Status: Not started
- Depends on: Phase 4 (complete), [ADR-0004](../../adr/0004-rollout-on-a-long-lived-feature-branch.md)

## Goal

Land the completed HD upgrade on `development` through the project's
normal contribution process.

## Entry criteria

- Phase 4 fully green: validation, tests, lint/type, playtest all pass.

## Tasks

- [ ] Rebase the feature branch on current `development`; resolve any
      conflicts from unrelated work merged during asset production.
- [ ] Open a PR against `development` per `CONTRIBUTING.md` (fork & pull
      model; target branch `development`).
- [ ] Call out in the PR description that this is a single all-or-nothing
      merge (per ADR-0001/ADR-0004) — reviewers should not expect or
      request incremental/partial merges of this branch.
- [ ] Update `ATTRIBUTIONS.md` for any new/re-authored art per
      `CONTRIBUTING.md`'s asset contribution rules, if applicable.
- [ ] After merge, update this epic's status to Done in
      `planning/roadmap.md`.

## Exit criteria

- Merged to `development`.
- `planning/roadmap.md` updated to reflect completion.

## Notes

Record any real-world surprises from the merge/review process here as an
"Outcome" note — useful input for the next epic that uses this same
planning method.
