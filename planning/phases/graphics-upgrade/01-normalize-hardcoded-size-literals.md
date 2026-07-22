# Phase 1: Normalize hardcoded size literals

- Status: Done (2026-07-22)
- Depends on: [ADR-0002](../../adr/0002-normalize-hardcoded-size-literals-before-bump.md)

## Goal

Replace copy-pasted size/resolution literals in UI state code with
references to the actual `tuxemon/platform/const/sizes.py` constants, so
the Phase 2 constant bump is a single-source-of-truth change.

## Entry criteria

- None — this phase can start immediately, independent of the rest of the
  epic.

## Tasks

- [x] `tuxemon/states/monster_info.py:407` — replace inline `16`, `256`,
      `144` with the corresponding `sizes.py` constants.
- [x] `tuxemon/states/item_menu.py:81`, `tuxemon/states/technique_menu.py:69`,
      `tuxemon/states/shop_base.py:83` — replace `scale_int(32)` magic
      number with a named constant reference.
- [x] `tuxemon/states/item_menu.py:100`, `shop_base.py:92`,
      `technique_menu.py:129` — review the `* 0.16` / `* 0.45` fractional
      layout literals; either consolidate into one shared constant/helper
      or confirm they're intentionally independent per-file.
- [x] `tuxemon/states/transition_mosaic.py:32-54` — rename the local
      `tile_size` parameter (e.g. `mosaic_block_size`) to remove the naming
      collision with game tile size.
- [x] Grep `tuxemon/states/` and `tuxemon/ui/` for other stray `256`, `144`,
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

## Outcome

Completed 2026-07-22 on branch `graphics-upgrade/01-normalize-size-literals`.
Deviations and findings vs. the plan:

- The `/ 256`, `/ 144` pattern was far wider than `monster_info.py:407`:
  the re-grep found ~70 sites across `monster_info.py`, `monster_moves.py`,
  `combat_menus.py`, `journal_info.py`, and `control_state.py`
  (`_native_w, _native_h = 256, 144`). All were converted.
- Added shared helpers `fix_native_x` / `fix_native_y` in
  `tuxemon/tools.py` (wrapping `fix_measure` with `NATIVE_RESOLUTION`),
  matching the nominal-pixel style `journal_info.py` had privately
  invented. Per-file `fxw`/`fxh` closures now delegate to them, so call
  sites read `fxw(37)` (native px) instead of `fxw(37 / 256)`.
- The description box was a whole copy-pasted rect, not just the `32`:
  added `DESC_BOX_TOP/LEFT/WIDTH/HEIGHT` (106/3/250/32) to `sizes.py`,
  used by `item_menu.py`, `technique_menu.py`, `shop_base.py`.
- The fractional anchors were byte-identical copy-paste, not independent:
  consolidated as `MENU_ITEM_CENTER_RATIO` (0.164, 0.13) and
  `MENU_DISPLAY_CENTER_RATIO` (0.16, 0.45) in `sizes.py`.
- `transition_mosaic.py`: renamed param and attribute to
  `mosaic_block_size` (no external callers existed).
- `monster_info.py:380/388` contain `y + (0.2 / 144)` NOT wrapped in
  `fxh` — almost certainly a typo for `fxh(0.2)`, but fixing it would
  shift the +/- taste icons by ~1px, so the value was kept verbatim
  (now written against `NATIVE_RESOLUTION[1]`). Revisit in Phase 2.
- Verification: `pytest tests` = 4220 passed, 9 failed — the 9 failures
  (nineslice/blit-alpha pixel asserts) are pre-existing and byte-identical
  on the unmodified baseline (env/pygame-ce version related). mypy error
  set is byte-identical to baseline (25 pre-existing errors). Ruff
  clean on all touched files.
- Tooling gotchas for later phases: ruff was unpinned (`tox.ini`) and
  version drift reformatted ~26 files repo-wide — unrelated files were
  reverted to keep this diff scoped, and ruff is now pinned to 0.15.22
  (~23 files of pre-existing format drift remain repo-wide). Local
  `.venv` lacks pytest/pytest-mock; use
  `uv run --with pytest --with pytest-mock pytest tests`.
