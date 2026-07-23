"""One-command AI pre-render pipeline for a Tuxemon battle sprite.

sprite slug in -> Ani2Real generation (HF Space, Gradio API) ->
rembg matte -> 128px cell -> front slot of the working-tree sheet.

Requires a Hugging Face login (``hf auth login``) for the Space's GPU
quota, plus ``requests``, ``rembg`` and Pillow — script-only deps, use
a scratch venv (see scripts/README.md and GRAPHICS.md).

Usage: python scripts/prerender_sprite_ai.py SLUG [SLUG ...] [--seed N]
"""

import argparse
import io
import json
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image
from rembg import remove

S = Path(__file__).parent
REPO = Path(__file__).resolve().parent.parent
BASE = "https://r3gm-ani2real-qwen-image-edit.hf.space/gradio_api"
TOKEN = (Path.home() / ".cache/huggingface/token").read_text().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

PROMPT = (
    "Transform picture 1 into a highly detailed 3D rendered creature "
    "figure, glossy toy-like materials, soft studio lighting, keeping "
    "the exact same pose, proportions, colors and design. Full body, "
    "centered, plain solid black background, no floor shadow."
)
NEGATIVE = (
    "low resolution, deformed limbs, extra limbs, oversaturated, "
    "flat 2d, anime style, cartoon outline, background scenery, floor"
)


def generate(slug: str, seed: int) -> Image.Image:
    sheet_path = f"mods/tuxemon/gfx/sprites/battle/{slug}-sheet.png"
    blob = subprocess.run(
        ["git", "-C", str(REPO), "show", f"pre-hd-baseline:{sheet_path}"],
        check=True,
        capture_output=True,
    ).stdout
    front = Image.open(io.BytesIO(blob)).convert("RGBA").crop((0, 0, 64, 64))
    bg = Image.new("RGBA", front.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(bg, front).convert("RGB")
    buf = io.BytesIO()
    flat.resize((1024, 1024), Image.NEAREST).save(buf, format="PNG")
    buf.seek(0)

    up = requests.post(
        f"{BASE}/upload",
        headers=HEADERS,
        files={"files": (f"{slug}.png", buf, "image/png")},
    )
    up.raise_for_status()
    server_path = up.json()[0]

    data = [
        [
            {
                "image": {
                    "path": server_path,
                    "meta": {"_type": "gradio.FileData"},
                },
                "caption": None,
            }
        ],
        PROMPT,
        NEGATIVE,
        seed,
        False,
        1024,
        4.0,
        35,
        None,
        0.5,
        None,
        0.5,
        None,
        0.5,
        False,
        "https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-8steps-V1.0-bf16.safetensors",
        1.0,
    ]
    r = requests.post(
        f"{BASE}/call/infer", headers=HEADERS, json={"data": data}
    )
    r.raise_for_status()
    event_id = r.json()["event_id"]
    print(f"[{slug}] event {event_id}, waiting...")

    result_url = None
    with requests.get(
        f"{BASE}/call/infer/{event_id}",
        headers=HEADERS,
        stream=True,
        timeout=600,
    ) as stream:
        for line in stream.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "null":
                continue
            parsed = json.loads(payload)
            if (
                isinstance(parsed, list)
                and parsed
                and isinstance(parsed[0], list)
            ):
                result_url = parsed[0][0]["image"]["url"]
    if result_url is None:
        raise RuntimeError(f"[{slug}] generation failed (no result in stream)")

    img = requests.get(result_url, headers=HEADERS)
    img.raise_for_status()
    return Image.open(io.BytesIO(img.content)).convert("RGB")


def to_cell(render: Image.Image) -> Image.Image:
    cut = remove(render)
    trimmed = cut.crop(cut.getbbox())
    scale = min(112 / trimmed.width, 112 / trimmed.height)
    resized = trimmed.resize(
        (round(trimmed.width * scale), round(trimmed.height * scale)),
        Image.LANCZOS,
    )
    cell = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    cell.paste(
        resized,
        ((128 - resized.width) // 2, 128 - resized.height - 4),
        resized,
    )
    return cell


def install(slug: str, cell: Image.Image) -> None:
    path = REPO / f"mods/tuxemon/gfx/sprites/battle/{slug}-sheet.png"
    sheet = Image.open(path).convert("RGBA")
    sheet.paste(Image.new("RGBA", (128, 128), (0, 0, 0, 0)), (0, 0))
    sheet.paste(cell, (0, 0), cell)
    sheet.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    for slug in args.slugs:
        t0 = time.time()
        render = generate(slug, args.seed)
        render.save(S / f"{slug}_prerender_raw.png")
        cell = to_cell(render)
        cell.save(S / f"{slug}_prerendered_128.png")
        install(slug, cell)
        print(f"[{slug}] done in {time.time() - t0:.0f}s -> sheet updated")


if __name__ == "__main__":
    main()
