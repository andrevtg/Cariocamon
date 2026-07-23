"""AI-enhance all animation sheets per-frame (phase 3c pattern).

Core ML counterpart of ``enhance_animations_hq2x.py``: drives
``enhance_png_coreml.py``'s pipeline over every animation listed in
``mods/tuxemon/db/animation/*.yaml``, loading the model once. Cell
size per sheet is the current YAML ``frame_x``/``frame_y`` divided by
2 (original-art size), sourced from the ``pre-hd-baseline`` tag.

Run from the repo root. Deps (script-only, never requirements.txt):
    uv run --no-project --with "coremltools>=9.0" --with numpy \
        --with pillow --with pyyaml \
        python scripts/enhance_animations_coreml.py
"""

import glob
import sys
import time
from pathlib import Path

import coremltools as ct
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from enhance_png_coreml import DEFAULT_MODEL, enhance, load_from_ref

BASELINE_REF = "pre-hd-baseline"


def main() -> None:
    """Enhance every animation sheet listed in the db YAMLs."""
    model = ct.models.MLModel(
        str(DEFAULT_MODEL), compute_units=ct.ComputeUnit.ALL
    )

    frames: dict[str, tuple[int, int]] = {}
    for yf in glob.glob("mods/tuxemon/db/animation/*.yaml"):
        for e in yaml.safe_load(open(yf)) or []:
            path = f"mods/tuxemon/animations/{e['file']}/{e['slug']}.png"
            frames[path] = (e["frame_x"] // 2, e["frame_y"] // 2)

    for path, tile in sorted(frames.items()):
        src = load_from_ref(BASELINE_REF, path)
        t0 = time.perf_counter()
        enhance(model, src, tile).save(path)
        print(
            f"{path} ({src.width}x{src.height}, "
            f"tile {tile[0]}x{tile[1]}) "
            f"(coreml-ai, {time.perf_counter() - t0:.2f}s)"
        )
    print(f"{len(frames)} animations done")


if __name__ == "__main__":
    main()
