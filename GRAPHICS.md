# Graphics Enhancement Notes & Playbook

Originally exploratory notes (2026-07-22) on what "enhanced graphics" could
mean for Tuxemon. **Option 1 below was executed** as the HD sprite & tileset
upgrade epic (see `planning/phases/graphics-upgrade/` and ADRs 0001–0005):
native resolution doubled to `512x288`, every asset 2x'd and hq2x-enhanced.
The second half of this file is the playbook for doing another pass.

Engine context: `pygame-ce`, tile maps via `pytmx`/`pyscroll`. Rendering is a
single global integer scale factor (`tuxemon/scaling.py`, `DISPLAY_CONTEXT.scale`
in `tuxemon/prepare.py`) computed from `config.resolution / NATIVE_RESOLUTION`
(`tuxemon/platform/const/sizes.py`, native res `512x288`, tile size `32x32`,
NPC sprite `32x64`, monster sprite `128x128`). All art is loaded and scaled up
uniformly at that one factor — there's no shader/lighting pipeline.

## 1. Higher-res sprites/tilesets

Swap in larger/more detailed pixel art for monsters, NPCs, and tiles.

- Mechanically closest to a pure asset swap: `load_and_scale()` in
  `tuxemon/graphics.py` already scales whatever art it's given.
- Real cost is that all art shares one native pixel grid (`TILE_SIZE`,
  `SPRITE_SIZE`, `MONSTER_SIZE`, etc. in `sizes.py`) and one global scale
  factor — you can't quietly mix old and new resolution assets; a bump has
  to happen consistently across tilesets, sprite sheets, and UI/icon art at
  once, or things misalign on the tile grid.
- Effort: **medium** — mostly art production + updating the native size
  constants, not new engine code. Risk is mostly consistency/scope
  (every asset category touched), not architecture.

## 2. Lighting/shader-style effects

Dynamic lighting, color grading, screen-space effects.

- `pygame-ce` has no shader pipeline; this isn't in the engine today.
- Would require either faking it with surface blend modes / precomputed
  light maps (limited, CPU-bound) or moving to a GL-backed renderer
  (e.g. `moderngl`) alongside/instead of pygame's software blitting.
- Effort: **high** — this is the only option that's a genuine architecture
  change, not additive work.

## 3. Particle/VFX polish

Better combat hit effects, weather, screen shake.

- Partial infrastructure already exists: `tuxemon/weather.py`, combat
  animations in `tuxemon/states/combat_animations.py`, camera shake in
  `tuxemon/camera/` (`CAMERA_SHAKE_RANGE` in `sizes.py`).
- Effort: **medium** — additive on top of existing systems, doesn't touch
  core scaling/rendering assumptions.

## 4. Resolution/scaling improvements

Smoother scaling, higher native resolution, better fullscreen/HiDPI handling.

- Touches `tuxemon/scaling.py` (`DefaultScaling`/`ResolutionScaling`) and
  display setup in `tuxemon/prepare.py`.
- Non-integer or per-axis scaling would affect pixel-perfect tile alignment
  and any UI code that assumes the current integer scale.
- Effort: **medium** — contained to a few files, but changes assumptions
  relied on throughout states/UI code.

---

# Playbook: what we learned doing the 2x upgrade (2026-07)

Everything below was learned the hard way during the graphics-upgrade epic.
Details live in `planning/phases/graphics-upgrade/*.md` (each phase has an
Outcome note); this is the condensed recipe.

## The two golden rules

1. **Migration and enhancement are separable.** Making every asset the
   *right size* (validation, bootability) is mechanical and scriptable;
   making it *look better* is a same-size drop-in replacement afterwards,
   with zero engine risk. Never bundle them.
2. **Always work from the original art.** The `pre-hd-baseline` git tag
   holds the last old-resolution assets. Enhancement filters are applied
   to originals (`git show pre-hd-baseline:<path>`), never re-applied to
   already-processed files. Keep that tag forever; create an equivalent
   tag before any future pass.

## Every place a pixel value lives (the straggler checklist)

A resolution bump must touch ALL of these — each one was missed at least
once and found by crash or playtest:

- `tuxemon/platform/const/sizes.py` constants and `FONT_SIZE_*` in
  `platform/const/graphics.py`.
- Literal args to `fix_native_x`/`fix_native_y`/`scale_int`/`scale_tuple`
  across the UI states (~190 call sites in phase 2).
- `tuxemon/db.py` pydantic defaults — including the **lazily-validated**
  ones that neither boot nor the test suite exercises:
  `MonsterSpritesModel` rects, `NpcTemplateModel` frame +
  `combat_frame_width/height`, `BattleGraphicsModel`
  `island_width/height` + offsets + `trainer_exit_offset`,
  `BattleHudModel` offsets.
- Content files: `mods/tuxemon/db/animation/*.yaml` (`frame_x`/`frame_y`),
  `mods/combat_layouts.yaml` (`LAYOUT_COORDINATES` — lives at `mods/`
  root, NOT under `db/`), map TMX (`tilewidth`/`tileheight`, object
  x/y/w/h, polyline points, embedded tilesets) and tileset TSX files.
- `tests/tuxemon/test_folder_maps_tmx.py` `MULTIPLIER`.
- Not pixel values (leave alone): monster `height`/`weight` (biometric),
  window icons, `tuxemon_wip_colorpalette.png`, `gfx/test/`.

Regression tests guarding the lazy paths live in
`tests/tuxemon/test_hd_asset_size_validation.py` (island sheets, combat
sheets, animation frame divisibility) — extend them for anything new.

## Tooling (all in `scripts/`)

| Script | Purpose |
| --- | --- |
| `upscale_png_2x.py` | NN 2x (mechanical migration placeholder) |
| `migrate_maps_2x.py` | TMX/TSX px-attribute rewrite. NOT idempotent — run once |
| `enhance_png_hq2x.py` | hq2x from the baseline tag; `--tile N` / `--tile WxH` for per-cell filtering |
| `enhance_animations_hq2x.py` | drives the above with per-animation frame cells from the db YAMLs |
| `prerender_sprite_ai.py` | AI pre-render pipeline: Ani2Real Space → rembg matte → fitted sheet cell |

Cell-size choices that mattered: tilesets `--tile 16` (in-sheet neighbors
are not in-game neighbors), overworld sheets `--tile 16x32` (frame cells),
player combat sheets `--tile 64x64`, dialog borders `--tile 6` (nine-slice),
island sheets `--tile 96x57`; monster battle sheets whole-image
(transparent gutters isolate the cells). Original-art cell sizes — halve
current constants when sourcing from the baseline.

## Environment gotchas

- `hqx` needs **Pillow < 10** (`PIL.PyAccess` removed in 10); `rembg`
  will happily upgrade Pillow and silently break hqx — pin `pillow==9.5.0`
  in the scratch venv after installing anything. These are script-only
  deps: scratch venv, never `requirements.txt`.
- Batch with `find -print0 | xargs -0` — several tileset filenames
  contain spaces.
- `git show <tag>:<path>` needs repo-relative paths.
- Headless verification needs `SDL_VIDEODRIVER=dummy` **plus**
  `pygame.display.set_mode(...)` for pytmx surface conversion.

## Verification gates (run after each category, all after a full pass)

1. `db.load(validate=True)` — exact-size schema checks.
2. Full `pytest tests` — baseline is 9 pre-existing failures
   (blit_alpha + 8 nineslice) as of 2026-07-23.
3. Headless boot ~20s with zero error lines — but remember **boot proves
   nothing about battle assets**; also smoke the lazy paths (island +
   combat sheets for all content, or just run the regression tests).
4. Load all 263 maps through `TMXMapLoader`.
5. Spot-render a map region from raw gids (scratch script pattern in
   phase 3b outcome) and eyeball for seams/halos.
6. A real playtest — the three content-px stragglers were all found by
   playing, not by any automated gate.

## If we enhance again (options ranked by what we know now)

- **Another 2x bump** (128px monsters → 256px): repeat phases 1–3
  mechanically using the checklist above. Proven, boring, safe.
- **Better filters than hq2x** (xBR variants, or AI upscalers tuned for
  pixel art): pure 3b-style drop-in pass — pilot on the starting-area
  slice first, judge in-game, then batch. No engine work at all.
- **AI redraw / pre-rendered 3D style** (`prerender_sprite_ai.py`):
  quality ceiling is real but so is per-sprite curation (~1 min of
  compute + human eye each; seed/prompt pinning tames drift, doesn't
  eliminate it). A style switch is all-or-nothing per asset class
  (agnite's front is the lone committed experiment) and deserves an ADR
  superseding ADR-0005 before any batch.
- **Smooth/painted hi-res**: still gated on another native-res bump —
  the renderer integer-scales 3x on screen, so painted art below
  ~3x native wastes its smoothness.
