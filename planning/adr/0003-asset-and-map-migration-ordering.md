# ADR-0003: Asset production and map migration ordering

- Status: Proposed
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

Total scope: `mods/tuxemon/sprites/` (208 PNGs), `mods/tuxemon/sprites_obj/`
(24), `mods/tuxemon/gfx/` (1,322: `sprites/battle/` 413, `sprites/player/`
357, `ui/` 258, `items/` 177, `tilesets/` 77, `bubbles/` 12, `borders/` 6),
and `mods/tuxemon/maps/*.tmx` (263 files). Tile pixel stride is baked into
each TMX (`tilewidth`/`tileheight` plus tileset image references), so
regenerating tilesets at 2x also requires rewriting all 263 maps'
tile-size metadata, not just the tileset PNGs.

`scripts/make_map_migration.py` is an existing precedent for scripted TMX
migrations in this codebase.

## Decision

Produce and migrate assets in dependency order, not all at once:

1. Tilesets (77 files) + a scripted rewrite of all 263 maps'
   `tilewidth`/`tileheight` and tileset image references (mirroring the
   approach in `scripts/make_map_migration.py`) — everything else renders
   on top of this layer, so it has to be right first.
2. NPC overworld sprites (`sprites/` 208 + `sprites_obj/` 24).
3. Battle/monster sprites (`gfx/sprites/battle/` 413 + `gfx/sprites/player/`
   357).
4. UI/icons/items/borders/bubbles (`gfx/ui/` 258, `gfx/items/` 177,
   `gfx/bubbles/` 12, `gfx/borders/` 6).

## Consequences

- Each step is independently checkable against the schema validator
  (`database/validator.py`) before moving to the next, which limits how far
  a mistake propagates before it's caught.
- Map migration is the highest-risk single step (263 files, scripted,
  touches collision/event math indirectly) and should get its own dedicated
  validation pass (see phase 04-validation) rather than being bundled into
  general asset review.
