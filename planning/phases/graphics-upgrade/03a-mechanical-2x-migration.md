# Phase 3a: Mechanical 2x migration (assets + maps)

- Status: Not started
- Depends on: Phase 2 (complete),
  [ADR-0003](../../adr/0003-asset-and-map-migration-ordering.md),
  [ADR-0005](../../adr/0005-hd-pixel-art-via-algorithmic-enhancement.md)

## Goal

Make every game asset the correct 2x pixel size (nearest-neighbor — no
aesthetic change) and migrate every map's tile metadata, restoring a
bootable, schema-valid `development`. Purely mechanical and scripted;
visual enhancement is Phase 3b.

## Entry criteria

- Phase 2 complete: constants bumped, pipeline proven on throwaway test
  assets, `scripts/upscale_png_2x.py` available.

## Tasks

- [ ] **Tilesets** (`mods/tuxemon/gfx/tilesets/`, 77 files) — NN 2x
      in place. Check for external `.tsx` tileset files referenced by
      maps: their `tilewidth`/`tileheight` and image dimensions must be
      rewritten in the same commit as the images.
- [ ] **Map migration** (`mods/tuxemon/maps/*.tmx`, 263 files) — script a
      rewrite of `tilewidth`/`tileheight` (16 -> 32) and any pixel-unit
      object/tile coordinates that Tiled stores in px, following the
      precedent in `scripts/make_map_migration.py`. Do not hand-edit 263
      files. Update `tests/tuxemon/test_folder_maps_tmx.py`'s
      `MULTIPLIER = 16` to 32 in the same commit.
- [ ] **NPC overworld sprites** (`mods/tuxemon/sprites/` 208 +
      `sprites_obj/` 24) — NN 2x.
- [ ] **Battle/monster sprites** (`gfx/sprites/battle/` 413 +
      `gfx/sprites/player/` 357) — NN 2x.
- [ ] **UI/icons/items/borders/bubbles** (`gfx/ui/` 258, `gfx/items/`
      177, `gfx/bubbles/` 12, `gfx/borders/` 6) — NN 2x.
- [ ] **Straggler sweep** — audit remaining image dirs not in the ADR-0003
      list (`mods/tuxemon/animations/`, `effects/`, any loose `gfx/`
      files) for art that renders in native-px space; double whatever
      does. (Flagged during plan refinement; scope confirmed at
      execution.)
- [ ] After each category above, run the schema validator
      (`database/validator.py` / `scripts/validate_mod_data.py` where
      applicable) against just that category before moving to the next.
- [ ] Full boot (`run_tuxemon.py`) and test suite back to the
      pre-existing failure baseline (including the 30
      `test_element_types_handler.py` errors from Phase 2 clearing).

## Exit criteria

- All categories pass schema validation (exact-size checks) at the new
  constants; `db.load(validate=True)` no longer raises.
- All 263 maps load without collision/event-grid errors.
- Game boots and is playable; visuals are pixel-identical to
  pre-upgrade (NN doubling changes nothing on screen).

## Notes

Largest-volume phase (~1,554 images + 263 maps) — track progress
per-category and don't skip the per-category validator run. Map
migration is the highest-risk step (ADR-0003) and gets its own
dedicated validation attention in Phase 4.

### Asset spec (measured from current assets, then doubled — Phase 2)

Target sizes after the 2x bump; the engine constants/defaults already
expect these (`tuxemon/platform/const/sizes.py`, `db.py`):

| Category | Old (uniform) | New target |
| --- | --- | --- |
| Tiles | 16x16 | 32x32 |
| NPC overworld sheet (3x4 frames of 16x32) | 48x128 | 96x256 |
| Battle/monster sheet (front+back 64x64, two 24x24 menu icons) | 128x88 | 256x176 |
| Party/template icons | 7x7 | 14x14 |
| Status icons | 9x9 | 18x18 |
| Item sprites | 24x24 | 48x48 |
| Element icons | 24x24 | 48x48 |
| Dialog borders (3x3 nine-slice) | 18x18 | 36x36 |
| Battle backgrounds | 256x108 | 512x216 |
| Economy/menu backgrounds (max bound) | ≤256x144 | ≤512x288 |

Sheet slicing rects live in `db.py` (`MonsterSpritesModel`,
`NpcTemplateModel`) and were doubled in Phase 2. Two boot-relevant facts
from Phase 2: `db.load()` validates with `validate=True` and raises on
the first wrong-size asset (game won't boot until all validated
categories are consistent), and `tests/tuxemon/test_folder_maps_tmx.py`'s
`MULTIPLIER = 16` must be updated when maps migrate to 32px tiles.
