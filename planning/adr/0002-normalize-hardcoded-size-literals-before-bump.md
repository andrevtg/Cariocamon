# ADR-0002: Normalize hardcoded size literals before touching the constants

- Status: Proposed
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

Several UI state files duplicate values from `sizes.py` as inline literals
instead of importing the constants:

- `tuxemon/states/monster_info.py:407` —
  `image_widget.translate(fxw(16 / 256), fxh(27 / 144))`, with `256`/`144`
  copy-pasted from `NATIVE_RESOLUTION` and `16` from a size constant.
- `tuxemon/states/item_menu.py:81`, `tuxemon/states/technique_menu.py:69`,
  `tuxemon/states/shop_base.py:83` — `scale_int(32)`, a magic number that
  isn't sourced from any named constant.
- `tuxemon/states/item_menu.py:100`, `shop_base.py:92`,
  `technique_menu.py:129` — fractional layout literals
  (`rect.width * 0.16`, `rect.height * 0.45`) copy-pasted across three files.
- `tuxemon/states/transition_mosaic.py:32-54` defines its own unrelated
  `tile_size: int = 10` (a mosaic-transition effect parameter, not a game
  tile) — a naming collision that risks a false-positive match during a
  later search-and-replace pass.

If ADR-0001's constant bump happens first, these sites silently keep their
old literal values and desync from the rest of the UI.

## Decision

Before changing any constant in `sizes.py`, sweep these sites (and any
others a grep for `256`, `144`, `16`, `32`, `24` in `tuxemon/states/` and
`tuxemon/ui/` turns up) and replace literals with references to the actual
`sizes.py` constants they were standing in for. Rename
`transition_mosaic.py`'s local `tile_size` to something unambiguous
(e.g. `mosaic_block_size`) so it can't be mistaken for a game-tile
reference.

## Consequences

- Makes ADR-0001's bump a single-source-of-truth change (edit `sizes.py`,
  everything downstream follows) instead of a grep-and-pray exercise.
- This phase touches only constant references, not rendering behavior — it
  should be visually a no-op and is safe to land independently, well before
  any asset work starts.
