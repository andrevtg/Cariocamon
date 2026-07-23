# Phase 4: Validation

- Status: Not started
- Depends on: Phases 3a and 3b (complete)

## Goal

Confirm the fully-migrated game is correct and stable before rollout —
schema-valid, test-suite-green, and playable.

## Entry criteria

- Phase 3a complete (sizes/maps migrated) and Phase 3b complete (every
  category enhanced or recorded as kept-NN), each individually
  validated.

## Tasks

- [ ] Full schema validation pass across all mod data
      (`database/validator.py` / relevant `scripts/verify_*.py` /
      `scripts/validate_mod_data.py`).
- [ ] Run the full test suite (`pytest tests`), with particular attention
      to: `test_camera*`, `test_collision_manager.py`, `test_map*`,
      `test_sprite*`, `test_ui_tile_layout.py`, `test_ui_graphic_box.py`,
      `test_event_middleware_camera.py`, `test_event_loader_map.py`,
      `test_folder_maps_tmx.py`, `test_folder_maps_yaml.py`,
      `test_level_scaler.py`.
- [ ] `tox -e lint` / `tox -e type` clean.
- [ ] Manual playtest per `CONTRIBUTING.md` convention: ~10 minutes from a
      new game, covering overworld movement, an NPC interaction, a wild
      encounter/combat, menu navigation, save/load.
- [ ] Visual spot-check across map, combat, and menu states for any asset
      that still looks stretched/misaligned (a straggler that dodged
      Phase 1's literal cleanup or Phase 3's validation).

## Exit criteria

- All of the above pass with no known regressions.
- Ready to merge per Phase 5's rollout plan.

## Notes

If any test needs its expectations updated for the new native resolution
(not just fixed), record that explicitly here rather than silently
loosening an assertion.
