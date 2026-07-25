# Upstream fixes

Log of engine bugs found in this fork whose root cause exists in upstream
Tuxemon (`Tuxemon/Tuxemon`), as opposed to bugs introduced by fork work
(HD graphics epic, Cariocamon content). One entry per fix.

Why this exists:

- **Upstreaming**: each entry is a candidate PR to upstream; the entry tracks
  whether it was sent and merged.
- **Merge reconciliation**: when pulling from upstream, check this list — if
  upstream fixed the same bug differently, the merge must reconcile the two
  fixes instead of silently keeping both halves.

Keep entries short: symptom, root cause, fix commit. Git history holds the
full diff and rationale; this file adds the upstream-vs-fork attribution and
PR status that git doesn't capture.

## Entries

### 2026-07-24 — Shop soft-locks when ESC pressed at quantity picker

- **Symptom**: game freezes (input dead, still rendering) after cancelling
  the shop quantity picker with ESC; leftover item description text drawn on
  the world layer.
- **Root cause** (both present in upstream `development`):
  1. `QuantityPickerState.process_event` treated `buttons.B` as cancel but
     not `buttons.BACK`/`MENU_CANCEL`, so ESC fell through to the shop menu
     below the picker.
  2. `Menu.close()` / `PygameMenuState._on_close()` called
     `client.pop_state()` with no argument, popping the *top* state (the
     picker) instead of the closing menu — stranding the shop menu in
     CLOSING, where it consumes all input forever.
- **Fix**: picker cancels on B/BACK/MENU_CANCEL; closing menus pop
  themselves explicitly (`pop_state(self)`).
- **Commit**: `1ed84d995`; tests in
  `tests/tuxemon/test_menu_close_and_picker_cancel.py`.
- **Upstream status**: not sent yet.

### 2026-07-23 — Missing set_environment on seven encounter maps

- **Symptom**: `random_encounter` aborts with "No environment defined"
  when a battle starts on a map that never loaded an environment
  (environments persist across maps, so these maps only worked when
  entered from one that had set an environment).
- **Root cause**: seven maps with encounter events lack a
  `set_environment` event of their own (verified upstream: e.g.
  `water_lower_village`, `water_outskirts`, `rubberduck_route_01` have
  zero `set_environment` in `upstream/development`).
- **Fix**: added the standard `set_environment X` event (guarded by
  `not environment_is X`) to each map.
- **Commit**: `6bbe31994`.
- **Upstream status**: not sent yet.

### 2026-07-23 — Broken music references across seven maps

- **Symptom**: `play_music` fails (and its `music_playing` guard mismatch
  re-fires it every frame) on seven maps.
- **Root cause**: `play_music`/`music_playing` parameters reference slugs
  that don't exist in the db — raw filenames (`lunar_joyride.mp3`,
  `legend_bofie/all-the-tea-in-china.mp3`, `Come and Find Me.ogg`), a
  wrong variant (`music_dizzy_spells` vs `music_night_dizzy_spells`), and
  a track deleted upstream in PR #3025 (`music_valor_heroes`). All still
  present in `upstream/development`.
- **Fix**: repointed all seven maps at valid db slugs.
- **Commit**: `cc57004f9`.
- **Upstream status**: not sent yet.

### 2026-07-23 — Stale event scripts in water_underwater map

- **Symptom**: every event on the map fails each frame while underwater;
  `set_environment` and `play_music` re-fire every frame because their
  guards can never match.
- **Root cause**: the map's scripts predate several engine renames, all
  still present in `upstream/development`: `has_monster` missing the
  `<character>` parameter, removed `player_facing_tile` condition,
  `button_pressed K_RETURN` (pygame constants no longer accepted),
  environment slug `water` instead of `underwater`, and music slug
  `music_come_find_me` instead of `music_come_and_find_me`.
- **Fix**: updated all conditions/actions to current engine syntax and
  valid slugs.
- **Commits**: `105c13e64`, `d33795839`.
- **Upstream status**: not sent yet.
