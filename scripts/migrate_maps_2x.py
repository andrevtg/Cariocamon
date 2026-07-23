"""Rewrite TMX/TSX pixel-unit metadata for the 2x HD upgrade (ADR-0005).

Doubles every pixel-valued attribute while leaving tile-unit values
(map width/height, gids, tile ids, tilecount, columns) untouched:

- ``<map>``: ``tilewidth``, ``tileheight``
- ``<tileset>`` (embedded or .tsx): ``tilewidth``, ``tileheight``,
  ``margin``, ``spacing``
- ``<image>``: ``width``, ``height``
- ``<object>``: ``x``, ``y``, ``width``, ``height``
- ``<polyline>``/``<polygon>``: every number in ``points``

Purely textual (regex on the matched tag only), so file formatting and
attribute order are preserved. Idempotence is NOT guaranteed — run once.

Usage:
    python scripts/migrate_maps_2x.py mods/tuxemon/maps/*.tmx
    python scripts/migrate_maps_2x.py mods/tuxemon/gfx/tilesets/*.tsx
"""

import argparse
import re
from pathlib import Path

TAG_ATTRS = {
    "map": ("tilewidth", "tileheight"),
    "tileset": ("tilewidth", "tileheight", "margin", "spacing"),
    "image": ("width", "height"),
    "object": ("x", "y", "width", "height"),
}

TAG_RE = re.compile(r"<(map|tileset|image|object|polyline|polygon)\b[^>]*>")
POINTS_RE = re.compile(r'\bpoints="([^"]*)"')
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _double(num: str) -> str:
    """Double a numeric string, keeping integers integral."""
    value = float(num) * 2
    return str(int(value)) if value.is_integer() else str(value)


def _rewrite_tag(match: re.Match[str]) -> str:
    tag_text = match.group(0)
    name = match.group(1)
    for attr in TAG_ATTRS.get(name, ()):
        tag_text = re.sub(
            rf'\b{attr}="(-?\d+(?:\.\d+)?)"',
            lambda m: f'{attr}="{_double(m.group(1))}"',
            tag_text,
        )
    if name in ("polyline", "polygon"):
        tag_text = POINTS_RE.sub(
            lambda m: 'points="{}"'.format(
                NUM_RE.sub(lambda n: _double(n.group(0)), m.group(1))
            ),
            tag_text,
        )
    return tag_text


def migrate(path: Path) -> bool:
    """Rewrite one file; return True if it changed."""
    text = path.read_text(encoding="utf-8")
    new_text = TAG_RE.sub(_rewrite_tag, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    changed = 0
    for path in args.files:
        if migrate(path):
            changed += 1
        else:
            print(f"unchanged: {path}")
    print(f"{changed}/{len(args.files)} files rewritten")


if __name__ == "__main__":
    main()
