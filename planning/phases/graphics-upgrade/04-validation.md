# Phase 4: Validation

- Status: In progress (automated gates green 2026-07-23; awaiting
  user playtest)
- Depends on: Phases 3a and 3b (complete; 3c also complete)

## Goal

Confirm the fully-migrated game is correct and stable before rollout —
schema-valid, test-suite-green, and playable.

## Entry criteria

- Phase 3a complete (sizes/maps migrated) and Phase 3b complete (every
  category enhanced or recorded as kept-NN), each individually
  validated.

## Tasks

- [x] Full schema validation pass across all mod data
      (`database/validator.py` / relevant `scripts/verify_*.py` /
      `scripts/validate_mod_data.py`). Green 2026-07-23.
- [x] Run the full test suite (`pytest tests`), with particular attention
      to: `test_camera*`, `test_collision_manager.py`, `test_map*`,
      `test_sprite*`, `test_ui_tile_layout.py`, `test_ui_graphic_box.py`,
      `test_event_middleware_camera.py`, `test_event_loader_map.py`,
      `test_folder_maps_tmx.py`, `test_folder_maps_yaml.py`,
      `test_level_scaler.py`. 4227 passed; the only failures are the
      9 pre-existing pygame-ce pixel-assert issues (blit_alpha + 8
      nineslice in `test_ui_tile_layout.py`), documented as the env
      baseline since phase 1 — not resolution-related, no
      expectations were changed. Every other watched file is green.
- [x] `tox -e lint` / `tox -e type` clean. ruff 0.15.22 format+check
      zero-diff after fixing upstream-merge drift in `scripts/`
      (commit `d16e0d2ce`); mypy at its documented 25-error
      pre-existing baseline (9 files, none in migrated code paths).
- [ ] Manual playtest per `CONTRIBUTING.md` convention: ~10 minutes from a
      new game, covering overworld movement, an NPC interaction, a wild
      encounter/combat, menu navigation, save/load.
- [x] Visual spot-check across map, combat, and menu states for any asset
      that still looks stretched/misaligned (a straggler that dodged
      Phase 1's literal cleanup or Phase 3's validation).
      Programmatic sweep 2026-07-23: all 1760 baseline PNGs are
      exactly 2x except 17 deliberate never-in-scope files (window
      icons `gfx/icon*.png`, legacy root `gfx/menu-*.png` 9-slice
      pieces, `tuxemon_wip_colorpalette.png` — none referenced by
      engine code); all 17 TSX declared sizes match their PNGs
      (note: `factory.tsx` writes its image path relative to
      `maps/`, which pytmx resolves fine); all 207 animation sheets
      divide evenly by their YAML frame sizes. Spot-renders of Taba
      Town, Spyder Paper Town, and the Candy Town inn are seam-free
      and unstretched.

## Exit criteria

- All of the above pass with no known regressions.
- Ready to merge per Phase 5's rollout plan.

## Notes

If any test needs its expectations updated for the new native resolution
(not just fixed), record that explicitly here rather than silently
loosening an assertion.
