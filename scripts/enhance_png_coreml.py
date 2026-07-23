"""AI-enhance game art with a local Core ML Real-ESRGAN (phase 3c).

Drop-in successor to ``enhance_png_hq2x.py`` — same CLI contract:
reads the *original* 16px-era image from a git ref (default
``pre-hd-baseline``) and writes an enhanced version, exactly the size
of the 2x file it replaces, to the working tree (or ``--out-dir``).

Pipeline per image/cell (validated on monster battle sheets 2026-07):
nearest-neighbor 2x pre-upscale (keeps 1-2 px features — eyes, body
markings — from being smoothed away as noise), Real-ESRGAN anime6B x4
on the Apple Neural Engine, low-frequency color restore from the
original (alpha-normalized, prevents dimming/tint drift), Lanczos
down to the 2x target. The alpha channel goes through the model too;
fully opaque or fully transparent cells skip the passes they don't
need.

``--tile N`` (or ``--tile WxH``) enhances each cell of the source
independently, same semantics as the hq2x script. Cell sizes are
original-art sizes (halve the current constants).

Build the model first with ``scripts/convert_realesrgan_coreml.py``.
Deps (coremltools>=9, numpy, Pillow — no torch needed here) are
script-only: scratch uv project, never requirements.txt. Do NOT share
a venv with the hqx script (hqx needs Pillow<10; this one doesn't).
Load with compute units ALL — CPU_ONLY crashes (SIGTRAP).

Usage:
    python scripts/enhance_png_coreml.py \
        mods/tuxemon/gfx/sprites/battle/rockitten-sheet.png
    python scripts/enhance_png_coreml.py --tile 16 \
        mods/tuxemon/gfx/tilesets/core_outdoor.png
"""

import argparse
import io
import subprocess
import time
from pathlib import Path

import coremltools as ct
import numpy as np
from PIL import Image, ImageFilter

DEFAULT_MODEL = (
    Path.home()
    / ".cache"
    / "tuxemon-coreml"
    / "realesrgan_anime6b_x4.mlpackage"
)
COLOR_RESTORE_RADIUS = 6.0


def predict(model: ct.models.MLModel, arr: np.ndarray) -> np.ndarray:
    """(3,H,W) float32 in 0-1 -> (3,4H,4W) clipped to 0-1."""
    out = model.predict({"image": arr[None]})["upscaled"]
    return np.clip(out[0], 0.0, 1.0)


def to_img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray((arr * 255).round().astype(np.uint8), "RGBA")


def norm_blur(rgb: np.ndarray, a: np.ndarray, radius: float) -> np.ndarray:
    """Alpha-normalized gaussian blur of (H,W,3) rgb with (H,W) alpha."""
    pre = to_img(np.concatenate([rgb * a[..., None], a[..., None]], -1))
    blurred = (
        np.asarray(pre.filter(ImageFilter.GaussianBlur(radius))).astype(
            np.float32
        )
        / 255.0
    )
    wa = np.clip(blurred[..., 3], 1e-4, 1.0)
    return blurred[..., :3] / wa[..., None]


def color_restore(out_arr: np.ndarray, orig: Image.Image) -> np.ndarray:
    """Pull the original's low-frequency color back into the output."""
    orig_up = orig.resize(out_arr.shape[1::-1], Image.NEAREST)
    o = np.asarray(orig_up).astype(np.float32) / 255.0
    lf_orig = norm_blur(o[..., :3], o[..., 3], COLOR_RESTORE_RADIUS)
    lf_out = norm_blur(out_arr[..., :3], out_arr[..., 3], COLOR_RESTORE_RADIUS)
    fixed = out_arr.copy()
    fixed[..., :3] = np.clip(out_arr[..., :3] + lf_orig - lf_out, 0, 1)
    return fixed


def enhance_rgba(model: ct.models.MLModel, cell: Image.Image) -> Image.Image:
    """Original-size RGBA cell -> enhanced cell at exactly 2x its size."""
    target = (cell.width * 2, cell.height * 2)
    rgba = np.asarray(cell).astype(np.float32) / 255.0
    alpha_plane = rgba[..., 3]
    if not alpha_plane.any():  # fully transparent (tileset gaps)
        return Image.new("RGBA", target, (0, 0, 0, 0))

    nn2x = cell.resize(target, Image.NEAREST)
    up = np.asarray(nn2x).astype(np.float32) / 255.0
    up_rgb = predict(model, up[..., :3].transpose(2, 0, 1))
    if (alpha_plane == 1.0).all():  # fully opaque: skip the alpha pass
        up_a = np.ones(up_rgb.shape[1:], dtype=np.float32)
    else:
        a3 = np.repeat(up[..., 3:4].transpose(2, 0, 1), 3, axis=0)
        up_a = predict(model, a3).mean(axis=0)

    arr = np.concatenate([up_rgb, up_a[None]], 0).transpose(1, 2, 0)
    arr = color_restore(arr, cell)
    return to_img(arr).resize(target, Image.LANCZOS)


def enhance(
    model: ct.models.MLModel,
    img: Image.Image,
    tile: tuple[int, int] | None,
) -> Image.Image:
    """Enhance the whole image, or each ``tile``-sized cell alone."""
    img = img.convert("RGBA")
    if tile is None:
        return enhance_rgba(model, img)
    tw, th = tile
    out = Image.new("RGBA", (img.width * 2, img.height * 2), (0, 0, 0, 0))
    for ty in range(0, img.height, th):
        for tx in range(0, img.width, tw):
            cell = img.crop((tx, ty, tx + tw, ty + th))
            out.paste(enhance_rgba(model, cell), (tx * 2, ty * 2))
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
        help="enhance each cell independently: N (square) or WxH",
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        help="write outputs here instead of overwriting the input paths",
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()

    if not args.model.exists():
        raise SystemExit(
            f"model not found: {args.model}\n"
            "build it first: python scripts/convert_realesrgan_coreml.py"
        )
    model = ct.models.MLModel(
        str(args.model), compute_units=ct.ComputeUnit.ALL
    )

    for path in args.files:
        try:
            src = load_from_ref(args.ref, path.as_posix())
        except subprocess.CalledProcessError:
            print(f"skip (not in {args.ref}): {path}")
            continue
        t0 = time.perf_counter()
        result = enhance(model, src, args.tile)
        dest = args.out_dir / path.name if args.out_dir else path
        dest.parent.mkdir(parents=True, exist_ok=True)
        result.save(dest)
        print(
            f"{path} ({src.width}x{src.height}) -> {dest} "
            f"(coreml-ai, {time.perf_counter() - t0:.2f}s)"
        )


if __name__ == "__main__":
    main()
