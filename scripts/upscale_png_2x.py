"""Upscale PNG images to 2x using nearest-neighbor interpolation.

Utility for the HD graphics upgrade (ADR-0001): produces placeholder
assets at the doubled native sizes from existing old-resolution art.

Usage:
    python scripts/upscale_png_2x.py SRC [SRC ...] -o OUT_DIR
    python scripts/upscale_png_2x.py SRC --in-place

Requires Pillow (already a project dependency).
"""

import argparse
from pathlib import Path

from PIL import Image


def upscale_2x(src: Path, dest: Path) -> None:
    """Write a nearest-neighbor 2x upscale of ``src`` to ``dest``."""
    with Image.open(src) as image:
        doubled = image.resize(
            (image.width * 2, image.height * 2), Image.NEAREST
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        doubled.save(dest)
    print(f"{src} ({image.size[0]}x{image.size[1]}) -> {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("-o", "--out-dir", type=Path)
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="overwrite each source file with its 2x upscale",
    )
    args = parser.parse_args()

    if not args.in_place and args.out_dir is None:
        parser.error("either --out-dir or --in-place is required")

    for src in args.sources:
        dest = src if args.in_place else args.out_dir / src.name
        upscale_2x(src, dest)


if __name__ == "__main__":
    main()
