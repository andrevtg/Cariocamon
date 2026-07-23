# ADR-0006: AI enhancement via local Core ML upscaler

- Status: Accepted
- Date: 2026-07-23
- Epic: HD sprite & tileset upgrade
- Supersedes: [ADR-0005](0005-hd-pixel-art-via-algorithmic-enhancement.md)
  (enhancement method and art-direction contract; its
  migration/enhancement separability principle and the executed 3a/3b
  structure remain valid history)

## Context

ADR-0005 chose hq2x for the 3b enhancement pass, explicitly accepting a
bounded quality ceiling ("it smooths, it does not add detail") and
rejecting AI-assisted approaches on cost/consistency grounds: the cloud
AI-redraw side test cost ~1 min + human curation per sprite, with
drift between runs.

A 2026-07-23 experiment changed those economics. Real-ESRGAN
`x4plus_anime_6B` (17.9 MB, BSD-3-Clause) converted to an FP16 Core ML
`mlprogram` runs on the Apple Neural Engine at ~26 ms per inference —
**~140 ms per monster sheet, ~1 minute for all 412**, deterministic
(same input always yields the same output, so there is no per-asset
curation and no drift). The full pipeline, validated per-category
against the two failure modes found during iteration (eyes dimming,
body markings erased):

1. nearest-neighbor 2x pre-upscale, so 1–2 px features read as
   structure rather than noise to the model;
2. anime6B x4 on RGB, plus a separate pass for the alpha channel;
3. alpha-normalized low-frequency color restore from the original
   (guarantees overall color/brightness fidelity);
4. Lanczos downsample to the exact 2x drop-in size.

The user reviewed a 26-monster gallery (fronts, backs, menu icons)
against the baseline and shipped hq2x versions and chose the AI output.

## Decision

- **Art direction: smooth detailed enhancement.** The crisp
  pixel-art contract of ADR-0005 is dropped as a hard requirement.
  Outputs have anti-aliased edges and painted-style shading. The
  change is judged per category via an in-game pilot (phase 3c), not
  assumed globally.
- **Method: local Core ML Real-ESRGAN anime6B**, the v2 pipeline
  above, implemented in `scripts/enhance_png_coreml.py` (model built
  once by `scripts/convert_realesrgan_coreml.py`). Same CLI contract
  as the hq2x script; sources remain the `pre-hd-baseline` originals.
- **Rollout: phase 3c**, mirroring 3b — monsters first (already
  user-validated), then a starting-area pilot slice of every other
  category, then per-category go/no-go and batch. **Fallback per
  category is keeping its hq2x output** — never NN — recorded in the
  phase file with the reason.

## Consequences

- The game may intentionally mix styles per asset class (e.g. AI
  monsters over hq2x borders) if the pilot rejects some categories;
  the pilot verdict is the arbiter of what mixes acceptably.
- Per GRAPHICS.md, smooth art below ~3x native wastes some of its
  smoothness under the integer scaler. Accepted: the AI output is
  still the best-looking option at current size, and a future
  native-res bump (repeat of ADR-0001) recovers the headroom — the
  pipeline re-runs from the same originals at any scale.
- Tooling is macOS/Apple-Silicon-only (Core ML). Acceptable: scripts
  are optional tooling, never required to play (scripts/README.md),
  and the enhanced PNGs in the repo are platform-neutral.
- Model weights and the converted `.mlpackage` live in
  `~/.cache/tuxemon-coreml/`, never in the repo. Script deps
  (coremltools, numpy, Pillow; torch only for conversion) live in a
  scratch uv project, never `requirements.txt` — and must not share a
  venv with the hqx script (conflicting Pillow pins).
- Rollback stays cheap: one commit per category on `development`
  (ADR-0004), plus an `hq2x-build` tag created before the first 3c
  commit for whole-build A/B comparison.
- Known runtime constraints, recorded from the experiment: loading
  the model with `CPU_ONLY` compute units crashes (SIGTRAP) — always
  use `ALL`; converted input shapes are flexible but capped at 512 px
  per side, so images larger than that are processed per-cell via
  `--tile` (every batch recipe already does).
