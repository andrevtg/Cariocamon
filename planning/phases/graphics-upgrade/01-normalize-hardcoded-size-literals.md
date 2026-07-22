# Phase 1: Normalize hardcoded size literals

- Status: Not started
- Depends on: [ADR-0002](../../adr/0002-normalize-hardcoded-size-literals-before-bump.md)

## Goal

Replace copy-pasted size/resolution literals in UI state code with
references to the actual `tuxemon/platform/const/sizes.py` constants, so
the Phase 2 constant bump is a single-source-of-truth change.

## Entry criteria

- None — this phase can start immediately, independent of the rest of the
  epic.

## Tasks

- [ ] `tuxemon/states/monster_info.py:407` — replace inline `16`, `256`,
      `144` with the corresponding `sizes.py` constants.
- [ ] `tuxemon/states/item_menu.py:81`, `tuxemon/states/technique_menu.py:69`,
      `tuxemon/states/shop_base.py:83` — replace `scale_int(32)` magic
      number with a named constant reference.
- [ ] `tuxemon/states/item_menu.py:100`, `shop_base.py:92`,
      `technique_menu.py:129` — review the `* 0.16` / `* 0.45` fractional
      layout literals; either consolidate into one shared constant/helper
      or confirm they're intentionally independent per-file.
- [ ] `tuxemon/states/transition_mosaic.py:32-54` — rename the local
      `tile_size` parameter (e.g. `mosaic_block_size`) to remove the naming
      collision with game tile size.
- [ ] Grep `tuxemon/states/` and `tuxemon/ui/` for other stray `256`, `144`,
      `16`, `32`, `24` literals near layout/rect code; fix any real matches.

## Exit criteria

- No behavior change: the game renders pixel-identical to before this
  phase (this is a refactor, not a visual change).
- `pytest tests` and `tox -e lint`/`type` pass.
- Every size value that used to be a literal now traces back to a single
  `sizes.py` constant.

## Notes

Found via an Explore-agent audit on 2026-07-22; line numbers may drift as
the codebase changes — re-grep rather than trusting them blindly if this
phase starts much later.
