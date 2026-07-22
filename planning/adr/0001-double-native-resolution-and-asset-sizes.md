# ADR-0001: Double native resolution and all fixed asset-size constants together

- Status: Accepted (implemented in graphics-upgrade Phase 2)
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

The renderer scales every loaded image by one global integer factor
(`tuxemon/scaling.py`, computed in `tuxemon/prepare.py` from
`config.resolution / NATIVE_RESOLUTION`). `scale_surface`
(`tuxemon/graphics.py:307-311`) reads the loaded image's *actual* pixel size
and multiplies it by that factor — it does not know or check what the
"correct" native size for that asset was supposed to be. Separately,
`tuxemon/db.py`'s pydantic validators (`database/validator.py:68-73`) reject
any icon/item/status/element/border/battle-background image whose pixel
dimensions don't exactly equal the constants in
`tuxemon/platform/const/sizes.py` (`ICON_SIZE`, `STATUS_ICON_SIZE`,
`ITEM_SIZE`, `ELEMENT_SIZE`, `BORDERS_SIZE`, `BATTLE_BG_SIZE`).
(Correction during implementation: `TECH_ICON_SIZE`, originally listed
here, was wired to nothing — no validator or consumer.)

Both mechanisms are global, process-wide singletons, not per-mod or
per-asset. This means a higher-resolution asset pack cannot be introduced
piecemeal or as an optional override: an oversized sprite renders too big
next to everything else, and an oversized icon/item/status/border/
battle-background image fails schema validation outright.

## Decision

Adopt a single 2x multiplier across every native-resolution constant at
once: `NATIVE_RESOLUTION` 256x144 -> 512x288, `TILE_SIZE` 16x16 -> 32x32,
and `ICON_SIZE`, `TECH_ICON_SIZE`, `STATUS_ICON_SIZE`, `ITEM_SIZE`,
`ELEMENT_SIZE`, `BORDERS_SIZE`, `BATTLE_BG_SIZE` all doubled. Same aspect
ratio, same relative proportions — this is the smallest change that keeps
the existing scaling/validation architecture intact rather than requiring
new source-size-aware logic in `scale_surface` or the schema validators.

`MONSTER_SIZE`, `MONSTER_SIZE_MENU`, `SPRITE_SIZE`, and `TEMPLATE_SIZE`
(`sizes.py:38-45`) are currently unused anywhere in the engine — confirm
this is still true before relying on them, and either wire them up or drop
them rather than doubling dead constants for appearances' sake.
(Resolution: all four plus `TECH_ICON_SIZE` were confirmed dead and
dropped in Phase 2; the real sheet formats are recorded as the asset
spec in the Phase 3 file.)

Implementation additions (Phase 2): the doubling also covers every
native-px value multiplied by the window scale at draw time — the
`fix_native_x`/`fix_native_y` and `scale_int` literal args in the UI
states, `DESC_BOX_*`, `FONT_SIZE_*`, and the `db.py` pydantic defaults
for HUD/battle offsets and sheet-slicing rects. The default window
resolution moved from 1280x720 (5x of 256x144) to 1536x864 (3x of
512x288), preserving the 16-tile field of view; `scaling.py` computes
`scale = int(window_w / native_w)`, so the default window must remain an
integer multiple of the native width.

## Consequences

- This is an all-or-nothing engine change: there is no supported way to run
  mixed old/new-resolution assets simultaneously. Asset production (see
  ADR-0003) must complete before this can ship, not alongside it.
- `tuxemon/map/loader.py:403-410`'s tile-size-overwrite logic (native TMX
  `tilewidth`/`tileheight` gets read once for collision/event math, then
  clobbered with the scaled `context.tile_size` for the pyscroll rendering
  path) needs re-verification against the new `TILE_SIZE`, since it encodes
  the "native size x global scale" assumption directly.
- Default window `resolution`/`scaling` behavior in `tuxemon/config.py` may
  need re-tuning so a fresh install still gets a sane default window size
  relative to the new native resolution.
