# Phase 3a: Mechanical 2x migration (assets + maps)

- Status: Complete
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

## Outcome (2026-07-23)

Completed in one sitting, one commit per category. Findings vs. plan:

- `scripts/make_map_migration.py` turned out to be an interactive
  tile-*mapping* tool, not a TMX rewriter — wrote
  `scripts/migrate_maps_2x.py` instead: purely textual regex rewrite of
  px-valued attributes only (map/tileset `tilewidth`/`tileheight`,
  image `width`/`height`, object `x`/`y`/`width`/`height`,
  polyline/polygon `points`), preserving formatting. Not idempotent —
  never re-run it over already-migrated files.
- Corpus facts the plan didn't know: 79 maps have *embedded* tilesets
  (contra the external-only convention), 28 maps have polylines, 17
  external `.tsx` files exist, all object coords are integers, no
  imagelayers/offsets/margins anywhere.
- Category counts as migrated: tilesets 77 PNG (76 changed; one was
  identical after round-trip) + 17 TSX, maps 263/263, NPC overworld
  232, battle/player/flairs 771 (flairs/ subdir wasn't in the plan),
  UI+items+bubbles+borders 453, straggler sweep 211 (animations/
  technique+tileset+item+intro 207, plus menu cursor `gfx/arrow.png`
  and the touch overlay d-pad/a/b buttons). Deliberately NOT doubled:
  window icons (`gfx/icon*.png`), unreferenced legacy `gfx/menu-*.png`,
  `tuxemon_wip_colorpalette.png`, `gfx/test/` (already HD).
- Phase 2's guard test `test_old_resolution_icon_fails_doubled_icon_
  size_check` relied on a real icon still being stale — rewritten to
  use the HD test tile as the wrong-size input.
- Verification: `db.load(validate=True)` clean; 263/263 maps load
  through `TMXMapLoader` (headless; needs `SDL_VIDEODRIVER=dummy` plus
  `pygame.display.set_mode` for pytmx surface conversion); 25s headless
  boot with zero errors; pytest back to the exact 9-failure
  pre-existing baseline (element-icon errors from Phase 2 cleared).
  Pre-existing, unrelated: a few maps log "Skipping event 'None'"
  (unnamed event objects) — content issue, untouched by migration.
- **Post-completion straggler (found by user playtest, fixed):** four
  native-px `db.py` defaults are validated only when a battle starts,
  so neither boot nor the test suite caught them:
  `island_width`/`island_height` (`IslandSheet` crashed on the first
  wild encounter), `combat_frame_width`/`combat_frame_height`
  (`CombatSheet`), and `trainer_exit_offset`. Doubled, plus regression
  tests in `test_hd_asset_size_validation.py` covering every
  environment island sheet and NPC combat sheet. Lesson for Phase 4:
  lazily-loaded asset paths need explicit exercise — boot success
  proves little about battle assets.
