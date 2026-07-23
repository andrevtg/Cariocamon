# Phase 3b: HD pixel-art enhancement (hq2x)

- Status: Not started
- Depends on: Phase 3a (complete),
  [ADR-0005](../../adr/0005-hd-pixel-art-via-algorithmic-enhancement.md)

## Goal

Fill the doubled pixel budget with actual visual improvement: hq2x
enhancement of the original 16px-era art, keeping the crisp HD-pixel-art
style per ADR-0005. Every output is a same-size drop-in replacement for
its Phase 3a NN counterpart — the game stays bootable throughout and
the phase can pause per-category with no breakage.

## Entry criteria

- Phase 3a complete: everything correctly sized, maps migrated, game
  boots.

## Tasks

- [ ] **Enhancement script** — `scripts/enhance_png_hq2x.py`: hq2x with
      alpha-aware handling (bleed RGB into transparent pixels before
      filtering; threshold the filtered alpha back to hard edges).
      Source pixels come from the *original* art at the
      `pre-hd-baseline` tag (`git show pre-hd-baseline:<path>`), not
      from the NN-doubled files. Deps (`hqx`, Pillow < 10) live in a
      scratch venv, not `requirements.txt` (script-only, per
      `scripts/README.md`).
- [ ] **Pilot: starting-area slice** — Taba Town tileset(s), player
      sheets, 2–3 NPC sheets, the three starters' battle sheets, dialog
      border + a handful of core UI icons. Evaluate in-game (walk,
      dialog, one battle, menus). Specifically resolve:
  - [ ] Tileset seams: hqx filters across in-sheet neighbors that are
        not in-game neighbors — compare whole-sheet vs per-tile
        filtering, pick one, record here.
  - [ ] Nine-slice borders and tiny icons (7px/9px): keep hq2x only if
        it doesn't distort slice edges / readability; fallback is NN
        (never worse than today).
- [ ] **Go/no-go per category** — record pilot verdict here, then batch
      the surviving categories in visibility order: tilesets, NPC
      overworld, battle/monster sheets, UI/items/borders/bubbles.
      One commit per category, visual spot-check each.
- [ ] Re-run the schema validator after each category (sizes must be
      unchanged — this guards against script bugs, not new sizes).

## Exit criteria

- Every category either enhanced or explicitly recorded here as
  "kept NN" with the reason.
- Validator green; test suite at baseline; visual spot-check of map,
  battle, and menu states shows no seams, halos, or distorted UI.

## Notes

- hq2x smooths, it does not invent detail — the quality ceiling is
  bounded (ADR-0005 accepts this). A future selective AI/manual redraw
  of high-visibility assets can layer on top with no engine change.
- Enhanced assets are algorithmic derivatives of the existing CC-licensed
  art: existing `ATTRIBUTIONS.md` entries still apply; nothing new to
  attribute (confirm during Phase 5 close-out).
