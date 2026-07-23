# Graphics Enhancement Notes & Playbook

Originally exploratory notes (2026-07-22) on what "enhanced graphics" could
mean for Tuxemon. **Option 1 below was executed** as the HD sprite & tileset
upgrade epic (see `planning/phases/graphics-upgrade/` and ADRs 0001–0006):
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
| `convert_realesrgan_coreml.py` | one-time anime6B → Core ML build |
| `enhance_png_coreml.py` | local AI enhance (3c); CLI as hq2x |
| `enhance_animations_coreml.py` | drives the above over all db animations, model loaded once, frame cells from the YAMLs / 2 |

Cell-size choices that mattered: tilesets `--tile 16` (in-sheet neighbors
are not in-game neighbors), overworld sheets `--tile 16x32` (frame cells),
player combat sheets `--tile 64x64`, dialog borders `--tile 6` (nine-slice),
island sheets `--tile 96x57`; monster battle sheets whole-image
(transparent gutters isolate the cells); UI whole-image except
anything over 256px original, which needs a split
(`grass_background_240.png` → `--tile 140x112`, seam invisible thanks
to the low-frequency color restore). Original-art cell sizes — halve
current constants when sourcing from the baseline.

## Environment gotchas

- `hqx` needs **Pillow < 10** (`PIL.PyAccess` removed in 10); `rembg`
  will happily upgrade Pillow and silently break hqx — pin `pillow==9.5.0`
  in the scratch venv after installing anything. These are script-only
  deps: scratch venv, never `requirements.txt`.
- Core ML scripts (2026-07-23): once the model is built, no venv or
  scratch project is needed at all — enhancement runs with
  `uv run --no-project --with "coremltools>=9.0" --with numpy
  --with pillow python scripts/enhance_png_coreml.py ...` (3c ran
  every batch this way). torch is only needed for the one-time
  conversion (`uv run --no-project --with ... --with torch==2.7.0`).
  Never share an env with the hqx script (conflicting Pillow pins).
  Load models with compute units `ALL`: `CPU_ONLY` crashes the Core
  ML runtime (SIGTRAP). Model + weights live in
  `~/.cache/tuxemon-coreml/`, never the repo.
- Converted model input must be **8–512 px per side** (after the
  script's NN-2x pre-upscale, so 4–256 px original art). Both ends
  bite: a 280px-wide background needed `--tile 140x112`, and 2x2
  nine-slice pieces can't be enhanced at all (kept hq2x). **Pre-check
  every batch's sizes against these limits first** — one bad file
  raises and kills the rest of that `xargs` invocation, leaving the
  batch silently partial (3c lost 25 files this way before noticing).
- Batch with `find -print0 | xargs -0` (or
  `git ls-tree -r --name-only -z <tag> <dir> | ... | xargs -0`) —
  several tileset filenames contain spaces. Related zsh trap: unquoted
  variables neither word-split nor glob-expand (`$pat` with a `*`
  inside silently matches nothing) — pipe explicit lists, don't
  interpolate patterns.
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
   phase 3b outcome; pytmx `load_pygame` + blit visible layers works
   headless) and eyeball for seams/halos.
6. Whole-tree integrity sweep (phase 4 pattern): every PNG exactly 2x
   its baseline (the only legit exceptions: window icons, root
   `gfx/menu-*.png`, the WIP palette, `gfx/test/`); TSX declared
   sizes match their PNGs (note `factory.tsx` writes its image path
   relative to `maps/`, resolve with a fallback); animation sheets
   divide evenly by their YAML frame sizes.
7. A real playtest — the three content-px stragglers were all found by
   playing, not by any automated gate.

## If we enhance again (options ranked by what we know now)

- **Local AI upscale via Core ML** — CHOSEN (ADR-0006, phase 3c):
  Real-ESRGAN anime6B on the ANE, ~140 ms/monster, deterministic, no
  curation. The two defects found and fixed during the experiment:
  tiny features (eyes, markings) get smoothed away unless the input
  is NN-2x pre-upscaled first, and colors dim unless low-frequency
  color is restored from the original. `enhance_png_coreml.py`
  encodes both. Executed in full 2026-07-23: every category shipped
  AI-enhanced after a user-approved pilot playtest. Sole exception:
  the 24 2x2-px monster-slot nine-slice pieces (below the model's
  8px minimum input, nothing to enhance) keep their hq2x versions.
  Model limits to know: input must be 8-512 px per side (after the
  NN-2x pre-upscale), so whole-image works up to 256px originals;
  larger or smaller goes through `--tile`.
- **Another 2x bump** (128px monsters → 256px): repeat phases 1–3
  mechanically using the checklist above. Proven, boring, safe — and
  it recovers the smoothness the integer scaler currently eats (the
  AI pipeline re-runs from the same originals at any scale).
- **AI redraw / pre-rendered 3D style** (`prerender_sprite_ai.py`):
  quality ceiling is real but so is per-sprite curation (~1 min of
  compute + human eye each; seed/prompt pinning tames drift, doesn't
  eliminate it). A style switch is all-or-nothing per asset class
  (agnite's front carried the lone committed experiment through 3b;
  3c re-unified it with the batch pipeline by user decision) and
  would need an ADR superseding ADR-0006 before any batch.
- **xBR variants / other classical filters**: superseded by the Core
  ML path — same drop-in mechanics, lower ceiling.
