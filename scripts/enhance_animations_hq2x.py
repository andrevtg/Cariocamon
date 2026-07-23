"""Batch-hq2x animation strips with per-animation frame cells.

Reads mods/tuxemon/db/animation/*.yaml (frame sizes are the doubled
values; the original cell = value // 2) and runs
scripts/enhance_png_hq2x.py with the matching --tile per file, so
filtering never bleeds across frame boundaries.

Run with the same scratch venv as enhance_png_hq2x.py (hqx needs
Pillow < 10) plus PyYAML.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
VENV_PY = sys.executable

jobs = defaultdict(list)  # (tile_w, tile_h) -> [paths]
for yml in (REPO / "mods/tuxemon/db/animation").glob("*.yaml"):
    for entry in yaml.safe_load(yml.read_text()):
        rel = (
            Path("mods/tuxemon/animations")
            / entry["file"]
            / (entry["slug"] + ".png")
        )
        if not (REPO / rel).exists():
            print("missing sheet:", rel)
            continue
        tile = (entry["frame_x"] // 2, entry["frame_y"] // 2)
        jobs[tile].append(str(rel))

failures = 0
for (tw, th), paths in sorted(jobs.items()):
    print(f"--tile {tw}x{th}: {len(paths)} files")
    result = subprocess.run(
        [
            VENV_PY,
            str(REPO / "scripts/enhance_png_hq2x.py"),
            "--tile",
            f"{tw}x{th}",
            *paths,
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    ok = result.stdout.count("(hq2x)")
    if ok != len(paths):
        failures += len(paths) - ok
        print(result.stdout[-500:], result.stderr[-500:])
print(f"done, {failures} failures")
