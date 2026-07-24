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
