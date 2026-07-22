# Phase 2: Bump native resolution and size constants

- Status: Not started
- Depends on: Phase 1 (complete), [ADR-0001](../../adr/0001-double-native-resolution-and-asset-sizes.md)

## Goal

Double the native-resolution/tile/icon size constants and confirm the
engine's scaling and map-loading code still behaves correctly at the new
values, before any real asset production starts.

## Entry criteria

- Phase 1 complete and merged (no stray literals left to desync).

## Tasks

- [ ] Before anything lands: tag current `development` as
      `pre-hd-baseline` (per [ADR-0004](../../adr/0004-work-directly-on-development.md)
      — last fully-playable old-resolution commit, since `development`
      will not validate again until Phase 3 completes).
- [ ] In `tuxemon/platform/const/sizes.py`, double: `NATIVE_RESOLUTION`,
      `TILE_SIZE`, `ICON_SIZE`, `TECH_ICON_SIZE`, `STATUS_ICON_SIZE`,
      `ITEM_SIZE`, `ELEMENT_SIZE`, `BORDERS_SIZE`, `BATTLE_BG_SIZE`.
- [ ] Confirm `MONSTER_SIZE`, `MONSTER_SIZE_MENU`, `SPRITE_SIZE`,
      `TEMPLATE_SIZE` are still unused; either wire them into an actual
      validator/consumer or leave a note explaining why they stay dead.
- [ ] Re-verify `tuxemon/map/loader.py:403-410`'s tile-size-overwrite logic
      (`data.tilewidth, data.tileheight = context.tile_size`) against the
      new `TILE_SIZE` — trace through with a single test map.
- [ ] Re-tune default `resolution`/`scaling` behavior in `tuxemon/config.py`
      if the new native resolution changes what a sane default window size
      looks like.
- [ ] Build one throwaway test asset per category (one tile, one NPC
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
