# Graphics Enhancement Options (exploratory notes)

Crude notes on what "enhanced graphics" could mean for Tuxemon and the rough
effort/risk of each, for future reference. Nothing here is planned or
committed — just a snapshot of the tradeoffs as of 2026-07-22.

Engine context: `pygame-ce`, tile maps via `pytmx`/`pyscroll`. Rendering is a
single global integer scale factor (`tuxemon/scaling.py`, `DISPLAY_CONTEXT.scale`
in `tuxemon/prepare.py`) computed from `config.resolution / NATIVE_RESOLUTION`
(`tuxemon/platform/const/sizes.py`, native res `256x144`, tile size `16x16`,
NPC sprite `16x32`, monster sprite `64x64`). All art is loaded and scaled up
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
