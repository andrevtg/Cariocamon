# Phase 2: Bump native resolution and size constants

- Status: Complete
- Depends on: Phase 1 (complete), [ADR-0001](../../adr/0001-double-native-resolution-and-asset-sizes.md)

## Goal

Double the native-resolution/tile/icon size constants and confirm the
engine's scaling and map-loading code still behaves correctly at the new
values, before any real asset production starts.

## Entry criteria

- Phase 1 complete and merged (no stray literals left to desync).

## Tasks

- [x] Before anything lands: tag current `development` as
      `pre-hd-baseline` (per [ADR-0004](../../adr/0004-work-directly-on-development.md)
      — last fully-playable old-resolution commit, since `development`
      will not validate again until Phase 3 completes).
- [x] In `tuxemon/platform/const/sizes.py`, double: `NATIVE_RESOLUTION`,
      `TILE_SIZE`, `ICON_SIZE`, `STATUS_ICON_SIZE`,
      `ITEM_SIZE`, `ELEMENT_SIZE`, `BORDERS_SIZE`, `BATTLE_BG_SIZE`.
- [x] Confirm `MONSTER_SIZE`, `MONSTER_SIZE_MENU`, `SPRITE_SIZE`,
      `TEMPLATE_SIZE` are still unused; either wire them into an actual
      validator/consumer or leave a note explaining why they stay dead.
      (Resolved: dropped, together with `TECH_ICON_SIZE` — also dead.)
- [x] Double every native-px UI value that scales with the window:
      `DESC_BOX_*`, `fix_native_x`/`fix_native_y` literal args,
      `scale_int`-style literal args, `FONT_SIZE_*`, and the native-px
      defaults in `db.py` (`BattleHudModel`, `BattleGraphicsModel`
      offsets, `MonsterSpritesModel` rects, `NpcTemplateModel` frame
      size). (Added during execution — see Outcome.)
- [x] Re-verify `tuxemon/map/loader.py:403-410`'s tile-size-overwrite logic
      (`data.tilewidth, data.tileheight = context.tile_size`) against the
      new `TILE_SIZE` — trace through with a single test map.
- [x] Re-tune default `resolution`/`scaling` behavior in `tuxemon/config.py`
      if the new native resolution changes what a sane default window size
      looks like. (Resolved: default window 1536x864 = exact 3x.)
- [x] Build one throwaway test asset per category (one tile, one NPC
      sprite frame, one icon) at the new native size to sanity-check the
      full render pipeline before real art production begins.

## Exit criteria

- Engine boots and renders the throwaway test assets at the correct scale
  (no oversized/misaligned sprites).
- Existing test suite passes (expect failures on real asset size checks
  until Phase 3 catches up — track those separately, don't treat as this
  phase's exit blocker).
- `database/validator.py`'s exact-size checks pass for the throwaway test
  assets.

## Notes

This phase is expected to make the *existing* (old-resolution) asset set
fail schema validation — that's expected and resolved by Phase 3, not a
regression to chase here.

## Outcome (2026-07-22)

Completed with a scope expansion the original task list missed: doubling
`NATIVE_RESOLUTION` silently halves the on-screen fraction of every
native-px value that goes through `fix_native_x`/`fix_native_y` or
`scale_int`, so all of those had to double in the same change:

- ~139 `fxw`/`fxh`/`fix_native_*` literal args in `monster_info.py`,
  `journal_info.py`, `monster_moves.py`, `combat_menus.py` (plus the
  variable-fed `step`/`_height`/`x_positions`/`y_position` definitions
  and the `0.2 / NATIVE_RESOLUTION[1]` offsets).
- ~50 `scale_int`/`scale_tuple`/`scale_sequence` literal args across
  `sprite.py`, `menu/layout_engine.py`, and the states.
  `menu/theme.py:83`'s `scale_int(1)` was deliberately left alone — it is
  the global scale factor itself, not a px length.
- `FONT_SIZE_*` in `platform/const/graphics.py` (their old comment
  claiming "relative size indices" was wrong — consumers use
  `scale_int(FONT_SIZE)` as the pixel font size).
- Native-px pydantic defaults in `db.py`: `BattleHudModel` (tray/bar
  offsets), `BattleGraphicsModel` (island/base offsets, jump distance),
  `MonsterSpritesModel` sheet rects, `NpcTemplateModel` frame size.
  None are overridden by content, so the engine defaults are live.

Decisions taken (with user sign-off):

- Default window: **1536x864** (exact 3x of 512x288, same 16-tile FOV as
  the old 1280x720@5x). Existing user configs keeping 1280x720 truncate
  to scale 2 (zoomed-out but playable); not migrated.
- Dead constants **dropped** rather than doubled: `MONSTER_SIZE`,
  `MONSTER_SIZE_MENU`, `SPRITE_SIZE`, `TEMPLATE_SIZE`, and
  `TECH_ICON_SIZE` (newly confirmed dead; ADR-0001 wrongly listed it as
  validator-wired).
- `large_gui` (forces scale 2) left untouched; its on-screen result is
  now twice as large as before relative to the assets.

Verification results:

- Map-loader trace (taba_town, headless): collision/event math reads the
  TMX-authored tile size before the overwrite, so coordinates are in tile
  units and unaffected; the pyscroll path gets `context.tile_size` (96 at
  scale 3). The logic is scale-agnostic as designed.
- Render smoke test: scratch 8x6 TMX of the 32px throwaway tile renders
  a pixel-exact 96px grid at scale 3; a 32x64 NPC frame lands on-screen
  at 96x192, tile-aligned.
- Full boot (`run_tuxemon.py`, dummy video) succeeds with zero errors
  once the size-validated asset categories are 2x-upscaled — done
  locally and reverted, since Phase 3 owns asset production. Note:
  `db.load()` runs with `validate=True` and **raises** on the first
  wrong-size asset, so committed `development` will not boot at all
  until Phase 3 lands (worse than "entries dropped"; the
  `pre-hd-baseline` tag is the playable fallback).
- Test suite: back to the pre-existing 9-failure baseline plus 30
  errors in `test_element_types_handler.py` (real element icons are
  24px vs the new 48px constant — Phase 3 resolves). Updated
  intended-behavior expectations in `test_config.py`,
  `test_menu_layout_*`, `test_draw_text.py` (±1px centering tolerance;
  offsets are floored and the doubled font size flipped text-width
  parity). New `test_hd_asset_size_validation.py` covers the throwaway
  assets. `tests/tuxemon/test_folder_maps_tmx.py` still asserts
  `MULTIPLIER = 16` against map-authored data — correct until Phase 3
  migrates the maps.
- `scripts/upscale_png_2x.py` added (nearest-neighbor 2x) — reusable
  for Phase 3 placeholder upscales.
