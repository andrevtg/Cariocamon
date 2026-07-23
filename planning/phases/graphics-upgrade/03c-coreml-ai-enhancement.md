# Phase 3c: AI enhancement via local Core ML (replaces hq2x outputs)

- Status: Complete (2026-07-23)
- Depends on: Phase 3b (complete),
  [ADR-0006](../../adr/0006-ai-enhancement-via-local-coreml-upscaler.md)

## Goal

Replace the hq2x-enhanced assets from phase 3b with AI-enhanced
versions produced locally (Real-ESRGAN anime6B on Core ML), per
ADR-0006. Every output is a same-size drop-in replacement sourced from
the `pre-hd-baseline` originals — the game stays bootable throughout
and any category can stop at its hq2x version with no breakage.

Monsters are pre-validated: the user reviewed a 26-monster gallery
(2026-07-23) and chose the AI output over hq2x. Every other category
needs the in-game pilot gate below before its batch.

## Entry criteria

- Phase 3b complete (it is; see its Outcome note).
- Working tree clean on `development` (ADR-0004: no feature branches).
- Apple Silicon Mac with `uv` installed.

## Environment setup (once per machine)

```shell
# scratch project OUTSIDE the repo; never requirements.txt.
# Do NOT reuse the hqx venv (it pins Pillow 9.5; this needs none of that).
uv init scratch-coreml && cd scratch-coreml
uv add "coremltools>=9.0" "torch==2.7.0" numpy pillow

# one-time model build (~5 s; downloads 17.9 MB weights on first run,
# writes ~/.cache/tuxemon-coreml/realesrgan_anime6b_x4.mlpackage)
uv run python <repo>/scripts/convert_realesrgan_coreml.py
```

Gotchas (learned 2026-07-23, do not rediscover):

- Load the model with compute units `ALL` (the script's default).
  `CPU_ONLY` crashes the Core ML runtime with SIGTRAP.
- Model input is capped at 512 px per side — anything larger goes
  through `--tile` (all recipes below already do).
- zsh does not word-split unquoted variables — pipe slug/file lists
  through `xargs`, and use `find -print0 | xargs -0` for tileset
  filenames with spaces.
- `git show <ref>:<path>` needs repo-relative paths; run the enhance
  script from the repo root.

## Tasks

- [x] **Prep** — tag the current build for A/B and rollback:
      `git tag hq2x-build` (before the first 3c commit; keep the tag).
      Done 2026-07-23.
- [ ] **Stage 1: monster battle sheets** (412 files, whole-image, no
  `--tile`; transparent gutters isolate the cells; ~1 s each):

  ```shell
  git ls-tree -r --name-only pre-hd-baseline \
      "mods/tuxemon/gfx/sprites/battle/*-sheet.png" \
    | xargs python scripts/enhance_png_coreml.py
  ```

  - [x] Decide agnite: **unify with the AI pass** (user verdict
        2026-07-23) — the 3b Ani2Real exception is dropped; agnite's
        sheet is regenerated from `pre-hd-baseline` like the rest.
  - [x] Verify (gates below), spot-check a battle in-game, commit
        (`Enhance monster battle sheets with Core ML AI (phase 3c)`).
        All 412 sheets regenerated 2026-07-23; gates 1–4 green
        (tests at the 9-failure baseline, HD size checks pass, 263
        maps load). In-game battle spot-check approved by the user
        ("it is great"). Committed.
- [ ] **Stage 2: pilot slice, uncommitted** — same slice as 3b so the
      comparison is apples-to-apples. Apply to working tree and have
      the user playtest (walk Paper Town, dialog, one battle, menus):
  - [x] core_outdoor / core_set pieces / core_buildings tilesets
        (`--tile 16`)
  - [x] adventurer + ceo + shopkeeper overworld sheets
        (`--tile 16x32`, from `mods/tuxemon/sprites/`)
  - [x] one player combat sheet (`--tile 64x64`):
        `gfx/sprites/player/adventurer.png`
  - [x] `mods/tuxemon/gfx/borders/borders.png` (`--tile 6`) — watch
        nine-slice corners
  - [x] one island sheet (`--tile 96x57`):
        `gfx/ui/island_sheet/grass_island_sheet.png`
  - [x] potion + tuxeball items (whole-image)
  - [x] one multi-frame animation from `db/animation/*.yaml`
        (per-frame cells = current YAML `frame_x/y` / 2) — watch for
        frame-to-frame shimmer in motion, not stills. Picked
        `animations/technique/bubbleattack.png` (4 frames, 64x64
        original cells, `--tile 64x64`).
        All 12 pilot files applied to the working tree 2026-07-23,
        uncommitted; sizes verified identical to the hq2x files they
        replace, HD size validation test green.
  - [x] Specific questions the pilot must answer: tile seams on real
        maps? smooth style acceptable on terrain (only monsters are
        pre-judged)? borders corners intact? animation stable?
        **Pilot verdict (user, 2026-07-23): all seven categories
        look good — full go for every Stage 3 batch.** (The playtest
        also surfaced unrelated stale event scripts in the water
        mini-game maps, fixed in separate commits.)
- [x] **Stage 3: go/no-go per category** — record each verdict here;
      fallback is keeping that category's hq2x output (never NN).
      All categories: GO (pilot verdict). Shipped 2026-07-23, one
      commit each — see Outcome below for counts and exceptions.
      Batch survivors in visibility order, one commit per category,
      re-running the schema validator after each:
      tilesets 77 (`--tile 16`) → overworld sheets 208 (`--tile
      16x32`) + static objects 24 (whole) → player combat sheets 357
      (`--tile 64x64`) + flairs (whole) → UI 258 with islands
      (`--tile 96x57`) and borders (`--tile 6`) special-cased →
      items 177, bubbles 12, overlay/cursor 4 (whole) → animations
      207 (per-frame cells from the YAMLs / 2).
      Compute is trivial (worst single file ~43 s; whole pass well
      under an hour) — re-running after a verdict change is free.
- [x] **Docs close-out** — update `GRAPHICS.md` "If we enhance again"
      ranking to reflect what 3c actually shipped; append the Outcome
      note here; confirm ATTRIBUTIONS.md needs nothing (outputs are
      algorithmic derivatives of the same CC-licensed art, as 3b
      recorded; the model itself is BSD-3-Clause tooling, not shipped
      content). Done 2026-07-23; ATTRIBUTIONS.md confirmed unchanged.

## Verification gates (unchanged from the playbook)

1. `db.load(validate=True)` after every category.
2. Full `pytest tests` — baseline is 9 pre-existing failures
   (blit_alpha + 8 nineslice) as of 2026-07-23, plus
   `tests/tuxemon/test_hd_asset_size_validation.py` green.
3. Headless boot clean (`SDL_VIDEODRIVER=dummy` +
   `pygame.display.set_mode`).
4. All 263 maps through `TMXMapLoader`.
5. Taba Town spot-render from raw gids — eyeball seams/halos
   (scratch script pattern in the 3b outcome).
6. Real playtest — 3b's stragglers were only ever found by playing.

## Exit criteria

- Every category either AI-enhanced or recorded here as "kept hq2x"
  with the pilot reason.
- All six gates green; one commit per shipped category on
  `development`; `hq2x-build` tag pushed nowhere but kept locally.

## Notes

- Scripts: `scripts/enhance_png_coreml.py` (same CLI as the hq2x
  script) and `scripts/convert_realesrgan_coreml.py`. Both smoke-
  tested 2026-07-23: rockitten sheet (matches the user-approved
  gallery output), a 1024x2048 tileset per-16px-cell, borders
  per-6px-cell.
- Pipeline rationale (why NN2x pre-upscale + color restore) and the
  experiment record live in ADR-0006.
- The 26-monster QA gallery pattern (baseline vs hq2x vs AI, zoom,
  alpha checkerboard) is worth regenerating for pilot judgment; the
  builder script from the experiment session can be recreated from
  this spec if needed.

### Outcome (2026-07-23)

Executed start-to-finish in one session, same day as planned. All
categories shipped AI-enhanced, one commit each:

- Stage 1 monsters: 412 battle sheets (`3b0c65f5d`); agnite's 3b
  Ani2Real exception dropped by user decision — unified with the AI
  pass.
- Pilot (12 files) accepted by user playtest: all seven categories GO.
- Stage 3: tilesets 76 (`7473d9bd6` — the plan said 77; actual
  baseline count is 76), overworld 208 + static objects 24
  (`7b7d86ff9`), player combat 357 + flairs 1 (`c7203d86f`), UI 234 +
  islands 24 + borders 6 (`037155c26`), items 177 + bubbles 12 +
  overlay/cursor 4 (`053a55892`), animations 207 (`812046f8b`).

Deviations and exceptions:

- Kept hq2x: the 24 2x2-px monster-slot nine-slice pieces
  (`gfx/ui/monster/pieces/`) — the Core ML model requires 8-512 px
  per side after the NN-2x pre-upscale, and 2x2 flat-color fragments
  have nothing to enhance anyway. Everything else is AI.
- `grass_background_240.png` (280px wide, over the 512 cap after
  pre-upscale) went through `--tile 140x112`; no visible seam (the
  color-restore pass keeps low frequencies continuous).
- No scratch uv project needed: `uv run --no-project --with
  coremltools --with numpy --with pillow` suffices (enhance script
  needs no torch; model already built in `~/.cache/tuxemon-coreml/`).
- Animations ran via a one-shot driver loading the model once and
  reusing `enhance()` from the script, cell sizes from the YAMLs / 2;
  all 207 PNGs matched a YAML entry exactly.

Verification: validator green after every category; full suite at the
9-failure pre-existing baseline (4227 passed) with the HD size tests
green; headless boot clean; 263 maps load; Taba Town spot-render
seam-free; user playtested battles, both mini-games, dialogs, menus.

Unrelated finds fixed along the way (own commits, not 3c content):
stale event scripts in `water_underwater.tmx` (`105c13e64`,
`d33795839`) and broken music slugs across seven maps (`cc57004f9`) —
engine/content drift the playtest surfaced, all pre-dating 3c.
`hq2x-build` tag kept locally for A/B.
