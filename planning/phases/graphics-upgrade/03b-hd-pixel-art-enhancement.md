# Phase 3b: HD pixel-art enhancement (hq2x)

- Status: In progress (pilot applied to working tree, awaiting user
  verdict)
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

- [x] **Enhancement script** — `scripts/enhance_png_hq2x.py`: hq2x with
      alpha-aware handling (bleed RGB into transparent pixels before
      filtering; threshold the filtered alpha back to hard edges).
      Source pixels come from the *original* art at the
      `pre-hd-baseline` tag (`git show pre-hd-baseline:<path>`), not
      from the NN-doubled files. Deps (`hqx`, Pillow < 10 for
      `PIL.PyAccess`) live in a scratch venv, not `requirements.txt`
      (script-only, per `scripts/README.md`). Supports `--tile N` /
      `--tile WxH` per-cell filtering.
- [ ] **Pilot: starting-area slice** — APPLIED to working tree
      (uncommitted), awaiting user verdict: core_outdoor /
      core_set pieces / core_buildings tilesets (`--tile 16`),
      adventurer + ceo + shopkeeper overworld sheets (`--tile 16x32`),
      battle sheets (whole-image) for rockitten + fruitera + bamboon
      plus the Paper Town intro/starter monsters and first wild
      (agnite, lambert, nut, tweesher, propellercat),
      borders.png (`--tile 6`), potion + tuxeball items (whole-image).
      Schema validation green with pilot applied. Evaluate in-game
      (walk, dialog, one battle, menus).
  - [x] Tileset seams: resolved — **per-tile filtering** (`--tile 16`).
        Rendered a Taba Town region from real map gids in both modes:
        pixel-diff is negligible and neither shows seams, so the mode
        that can't cross-contaminate unrelated sheet neighbors wins.
        Overworld sprite sheets get per-frame (`16x32`) for the same
        reason; battle sheets are filtered whole (transparent gutters
        isolate the cells).
  - [ ] Nine-slice borders and tiny icons (7px/9px): hq2x slightly
        rounds the border's outer corners — flagged for user judgment;
        fallback is NN (never worse than today).
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
