# planning/

This folder holds durable planning artifacts for multi-session engineering
initiatives ("epics") — work too large for one sitting, where each phase
should be pickable up cold in an isolated session.

## Layout

```text
planning/
  CLAUDE.md            — this file
  roadmap.md            — index of all epics: status + links, nothing else
  adr/                  — architecture decision records, one global sequential log
  phases/<epic-slug>/   — one self-contained file per phase, per epic
  upstream-fixes.md     — log of fixes for bugs inherited from upstream Tuxemon
```

## Working in this folder

- To resume an epic: read `roadmap.md` to find its status and phase folder,
  then read only the specific phase file you're picking up. Each phase file
  is self-contained (goal, entry/exit criteria, tasks) — you should not need
  to re-read the whole epic history to start it.
- Read an ADR only when a phase file links to it, or when making a decision
  that changes/reverses one already recorded.

## Conventions

- **ADRs** are numbered sequentially across the whole project (`0001`, `0002`,
  ...), regardless of which epic prompted them — they record architecture-wide
  decisions, not epic-scoped notes. Status is one of `Proposed`, `Accepted`,
  `Superseded by ADR-00XX`. Never edit an ADR's Decision once it has been
  executed/implemented — if a decision changes after that, write a new ADR
  that supersedes it. An ADR whose work has not run yet may still be edited
  in place at will.
- **Phase files** live under `phases/<epic-slug>/`, named `01-slug.md`,
  `02-slug.md`, etc. (zero-padded, ordered). Each one has: Goal, Depends on
  (prior phases / ADRs), Entry criteria, Tasks, Exit criteria, Notes. When a
  phase finishes, append a short "Outcome" note recording what actually
  happened / deviated from plan — this is what makes the next phase (and the
  next epic) smarter than the last.
- **`roadmap.md`** stays a thin index (epic name, status, links). Anything
  more detailed than that belongs in a phase file, not the roadmap.
- **`upstream-fixes.md`** gets an entry whenever a bug's root cause turns
  out to exist in upstream Tuxemon (verify against `upstream/development`
  before logging): symptom, root cause, fix commit, upstream PR status.
  Fork-introduced bugs don't go here — git history covers those.

## Starting a new epic

1. Add a row to `roadmap.md`.
2. Create `phases/<epic-slug>/` with one file per phase.
3. Write any ADRs the epic's design forces — link them from the relevant
   phase file(s).
