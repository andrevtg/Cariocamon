"""Build the local Core ML upscaler used by enhance_png_coreml.py.

Downloads the Real-ESRGAN ``x4plus_anime_6B`` weights (17.9 MB,
BSD-3-Clause) on first run and converts them to an FP16 ``mlprogram``
with flexible input shapes (8..512 px per side), written to
``~/.cache/tuxemon-coreml/realesrgan_anime6b_x4.mlpackage``.
One-time step, ~5 s on an M3 Max; re-run only to rebuild the cache.

Script-only deps (never requirements.txt), scratch uv project::

    uv init scratch-coreml && cd scratch-coreml
    uv add "coremltools>=9.0" "torch==2.7.0" numpy pillow
    uv run python <repo>/scripts/convert_realesrgan_coreml.py

Known gotcha: the converted model crashes (SIGTRAP) under
``ComputeUnit.CPU_ONLY`` — always load with ``ALL`` (ANE/GPU).

Usage:
    python scripts/convert_realesrgan_coreml.py [--cache-dir DIR]
"""

import argparse
import time
import urllib.request
from pathlib import Path

import coremltools as ct
import torch
import torch.nn.functional as F
from torch import nn

WEIGHTS_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/"
    "v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
)
DEFAULT_CACHE = Path.home() / ".cache" / "tuxemon-coreml"
PACKAGE_NAME = "realesrgan_anime6b_x4.mlpackage"


class ResidualDenseBlock(nn.Module):
    def __init__(self, num_feat: int = 64, num_grow_ch: int = 32):
        super().__init__()
        self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv3 = nn.Conv2d(
            num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1
        )
        self.conv4 = nn.Conv2d(
            num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1
        )
        self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, num_feat: int, num_grow_ch: int = 32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        return out * 0.2 + x


class RRDBNet(nn.Module):
    """RealESRGAN x4plus_anime_6B generator (6 RRDB blocks)."""

    def __init__(
        self,
        num_in_ch: int = 3,
        num_out_ch: int = 3,
        num_feat: int = 64,
        num_block: int = 6,
        num_grow_ch: int = 32,
    ):
        super().__init__()
        self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
        self.body = nn.Sequential(
            *[RRDB(num_feat, num_grow_ch) for _ in range(num_block)]
        )
        self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.conv_first(x)
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(
            self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest"))
        )
        feat = self.lrelu(
            self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest"))
        )
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    weights = args.cache_dir / "realesrgan_x4plus_anime_6b.pth"
    if not weights.exists():
        print(f"downloading weights -> {weights}")
        urllib.request.urlretrieve(WEIGHTS_URL, weights)

    model = RRDBNet()
    state = torch.load(weights, map_location="cpu")
    model.load_state_dict(state["params_ema"], strict=True)
    model.eval()

    t0 = time.time()
    traced = torch.jit.trace(model, torch.rand(1, 3, 128, 128))
    side = ct.RangeDim(lower_bound=8, upper_bound=512, default=128)
    mlmodel = ct.convert(
        traced,
        inputs=[ct.TensorType(name="image", shape=(1, 3, side, side))],
        outputs=[ct.TensorType(name="upscaled")],
        convert_to="mlprogram",
        compute_precision=ct.precision.FLOAT16,
        minimum_deployment_target=ct.target.macOS14,
    )
    dest = args.cache_dir / PACKAGE_NAME
    mlmodel.save(str(dest))
    print(f"converted in {time.time() - t0:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
