"""hq2x-enhance game art for the HD upgrade (ADR-0005, phase 3b).

Reads the *original* 16px-era image from a git ref (default
``pre-hd-baseline``) and writes an hq2x-filtered version — exactly the
size of the NN-doubled file it replaces — to the working tree.

Alpha handling: hqx operates on RGB, so sprite colors are first bled
into transparent pixels (stops halos), then the filtered alpha is
thresholded back to hard edges (keeps the pixel-art contract).

``--tile N`` (or ``--tile WxH``) filters each cell of the source
independently, so a cell's appearance never depends on its sheet
neighbors (which are not its in-game neighbors). Without it, the whole
image is filtered at once — right for standalone sprites, wrong for
tilesets/nine-slices with unrelated adjacent cells.

Requires ``hqx`` and ``Pillow < 10`` (``PIL.PyAccess``) — script-only
deps, use a scratch venv (see scripts/README.md).

Usage:
    python scripts/enhance_png_hq2x.py mods/tuxemon/sprites/ceo.png
    python scripts/enhance_png_hq2x.py --tile 16 \
        mods/tuxemon/gfx/tilesets/core_outdoor.png
"""

import argparse
import io
import subprocess
from pathlib import Path

import hqx
from PIL import Image

OFFSETS = [
    (dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)
]


def bleed(img: Image.Image, iterations: int = 4) -> Image.Image:
    """Fill transparent pixels with nearest opaque neighbor colors."""
    result = img
    for _ in range(iterations):
        base = result
        for dx, dy in OFFSETS:
            shifted = Image.new("RGBA", base.size, (0, 0, 0, 0))
            shifted.paste(base, (dx, dy))
            result = Image.alpha_composite(shifted, result)
    return result


def hq2x_rgba(img: Image.Image) -> Image.Image:
    """hq2x an RGBA image, keeping hard-edged alpha."""
    rgb = hqx.hq2x(bleed(img).convert("RGB"))
    a_channel = img.split()[3]
    a_rgb = hqx.hq2x(Image.merge("RGB", (a_channel,) * 3))
    alpha = a_rgb.split()[0].point(lambda v: 255 if v >= 128 else 0)
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def enhance(img: Image.Image, tile: tuple[int, int] | None) -> Image.Image:
    """hq2x the whole image, or each ``tile``-sized cell independently."""
    img = img.convert("RGBA")
    if tile is None:
        return hq2x_rgba(img)
    tw, th = tile
    out = Image.new("RGBA", (img.width * 2, img.height * 2), (0, 0, 0, 0))
    for ty in range(0, img.height, th):
        for tx in range(0, img.width, tw):
            cell = img.crop((tx, ty, tx + tw, ty + th))
            out.paste(hq2x_rgba(cell), (tx * 2, ty * 2))
    return out


def load_from_ref(ref: str, repo_path: str) -> Image.Image:
    """Load an image as stored at ``ref`` in git."""
    blob = subprocess.run(
        ["git", "show", f"{ref}:{repo_path}"],
        check=True,
        capture_output=True,
    ).stdout
    return Image.open(io.BytesIO(blob))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--ref", default="pre-hd-baseline")
    parser.add_argument(
        "--tile",
        type=lambda s: tuple(
            int(v) for v in (s.split("x") if "x" in s else (s, s))
        ),
        help="filter each cell independently: N (square) or WxH",
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        help="write outputs here instead of overwriting the input paths",
    )
    args = parser.parse_args()

    for path in args.files:
        src = load_from_ref(args.ref, path.as_posix())
        result = enhance(src, args.tile)
        dest = args.out_dir / path.name if args.out_dir else path
        dest.parent.mkdir(parents=True, exist_ok=True)
        result.save(dest)
        print(f"{path} ({src.width}x{src.height}) -> {dest} (hq2x)")


if __name__ == "__main__":
    main()
