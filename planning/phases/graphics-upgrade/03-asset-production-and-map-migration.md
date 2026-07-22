# Phase 3: Asset production and map migration

- Status: Not started
- Depends on: Phase 2 (complete), [ADR-0003](../../adr/0003-asset-and-map-migration-ordering.md)

## Goal

Produce/regenerate all game art at the new native resolution and migrate
every map's tile metadata to match, in dependency order.

## Entry criteria

- Phase 2 complete: constants bumped, pipeline proven on throwaway test
  assets.

## Tasks

- [ ] **Tilesets** (`mods/tuxemon/gfx/tilesets/`, 77 files) — regenerate at
      2x native tile size.
- [ ] **Map migration** (`mods/tuxemon/maps/*.tmx`, 263 files) — script a
      rewrite of `tilewidth`/`tileheight` and tileset image references,
      following the precedent in `scripts/make_map_migration.py`. Do not
      hand-edit 263 files.
- [ ] **NPC overworld sprites** (`mods/tuxemon/sprites/` 208 +
      `sprites_obj/` 24).
- [ ] **Battle/monster sprites** (`mods/tuxemon/gfx/sprites/battle/` 413 +
      `gfx/sprites/player/` 357).
- [ ] **UI/icons/items/borders/bubbles** (`gfx/ui/` 258, `gfx/items/` 177,
      `gfx/bubbles/` 12, `gfx/borders/` 6).
- [ ] After each category above, run the schema validator
      (`database/validator.py` / `scripts/validate_mod_data.py` if
      applicable) against just that category before moving to the next.

## Exit criteria

- All categories pass schema validation (exact-size checks) at the new
  constants.
- All 263 maps load without collision/event-grid errors.
- Spot-check a sample map + a battle + a menu visually for
  stretched/misaligned art.

## Notes

This is the largest and most error-prone phase by volume (~1,554 image
files + 263 maps) — track progress per-category rather than as one
monolithic checklist item, and don't skip the per-category validator run.
