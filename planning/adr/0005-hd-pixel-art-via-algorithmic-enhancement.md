# ADR-0005: HD pixel art direction via algorithmic (hqx) enhancement

- Status: Superseded by
  [ADR-0006](0006-ai-enhancement-via-local-coreml-upscaler.md)
  (method and art direction; the migration/enhancement separability
  principle and the executed 3a/3b structure remain valid)
- Date: 2026-07-22
- Epic: HD sprite & tileset upgrade

## Context

ADR-0001 doubled every native-size constant, buying a 2x pixel budget per
asset — but the budget is empty until art fills it. Three directions were
compared on a real asset (Rockitten's 64x64 battle front, rendered at
identical on-screen size):

1. **Nearest-neighbor 2x only** — pixel-identical to today; the upgrade
   is invisible.
2. **HD pixel art** (hq2x into the doubled budget) — curves and outlines
   resolve, still hard-edged pixel art, same game identity.
3. **Smooth hi-res** (hq4x + Lanczos) — anti-aliased, no pixel grid; a
   style break that only pays off fully after *another* native-resolution
   doubling, since the renderer integer-scales 3x on screen
   (`scale_surface`, `tuxemon/graphics.py`).

A second structural observation: asset *migration* (making every file the
right 2x size so validation passes and the game boots) and asset
*enhancement* (making it look better) are fully separable. An enhanced
32x32 tile and an NN-doubled 32x32 tile are drop-in interchangeable.

## Decision

- **Art direction: HD pixel art.** Enhancement stays within the crisp
  pixel-art contract — no anti-aliased/painted style. Going hi-res later
  remains possible by repeating the ADR-0001 playbook; HD pixel art is a
  valid resting point on that path, not a dead end.
- **Method: algorithmic (hqx family, primarily hq2x)** applied to the
  original 16px-era art, with alpha-aware handling (color bleed into
  transparent pixels before filtering; alpha thresholded back to hard
  edges after). Chosen over AI-assisted redraw for consistency across all
  ~1,554 files and near-zero per-asset cost. A later selective redraw
  pass of high-visibility assets can layer on top without engine changes.
- **Phase 3 splits into 3a and 3b.** 3a: scripted NN 2x of everything +
  TMX/TSX map migration — restores a bootable `development` quickly.
  3b: hq2x enhancement, piloted on a starting-area slice, then batched
  category-by-category as same-size drop-in replacements.

## Consequences

- `development` becomes bootable again at the end of 3a, not at the end
  of all art production; 3b carries zero engine risk and can pause or
  stop per-category without leaving the game broken.
- Quality ceiling is bounded by what hqx can infer — it smooths, it does
  not add detail. Accepted trade-off; revisit per-category if the pilot
  disappoints (fallback per category is NN, which is never worse than
  today).
- Known risk for the pilot to resolve: hqx filters across neighboring
  pixels, so tileset sheets may grow seams at tile boundaries
  (in-sheet neighbors are not in-game neighbors). Per-tile filtering vs
  whole-sheet is decided during the 3b pilot.
- Tooling deps (`hqx`, which requires Pillow < 10 for `PIL.PyAccess`)
  are script-only: they live in a scratch venv, not `requirements.txt`,
  per `scripts/README.md`.
- ADR-0003's dependency ordering still governs 3a; enhancement order in
  3b is by visibility instead (player/starters/starting area first).
