# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
"""Validate the throwaway HD test assets against the doubled size
constants (ADR-0001, graphics-upgrade phase 2), plus the lazily-loaded
battle sheets whose sizes are only checked at runtime (phase 3a)."""

import pygame
import pytest

from tuxemon.constants.asset_loader import fetch_asset
from tuxemon.database.registry import validator as has
from tuxemon.database.runtime import db
from tuxemon.platform.const.sizes import ICON_SIZE, TILE_SIZE

HD_TEST_TILE = "gfx/test/hd_test_tile.png"
HD_TEST_NPC_SHEET = "gfx/test/hd_test_npc.png"
HD_TEST_ICON = "gfx/test/hd_test_icon.png"

# One NPC overworld sheet is 3 columns x 4 rows of frame-sized cells;
# at the doubled 32x64 frame size a full sheet is 96x256.
HD_NPC_SHEET_SIZE = (96, 256)


def test_throwaway_hd_tile_matches_doubled_tile_size():
    assert has.size(HD_TEST_TILE, TILE_SIZE)


def test_throwaway_hd_icon_matches_doubled_icon_size():
    assert has.size(HD_TEST_ICON, ICON_SIZE)


def test_throwaway_hd_npc_sheet_matches_doubled_sheet_size():
    assert has.size(HD_TEST_NPC_SHEET, HD_NPC_SHEET_SIZE)


def test_wrong_size_asset_fails_icon_size_check():
    wrong_size_image = HD_TEST_TILE  # 32x32, not the 14x14 icon size
    assert not has.size(wrong_size_image, ICON_SIZE)


@pytest.fixture(scope="module")
def loaded_db():
    saved = {table: dict(rows) for table, rows in db.database.items()}
    db.load(validate=False)
    yield db
    db.database.clear()
    db.database.update(saved)


def test_island_sheets_match_environment_frame_sizes(loaded_db):
    for slug in loaded_db.database["environment"]:
        graphics = loaded_db.lookup(slug, table="environment").battle_graphics
        expected = (graphics.island_width * 2, graphics.island_height)
        assert has.size(graphics.island_sheet, expected), (
            f"Island sheet for environment '{slug}' "
            f"('{graphics.island_sheet}') is not {expected}"
        )


def test_combat_sheets_match_npc_template_frame_sizes(loaded_db):
    checked = set()
    for slug in loaded_db.database["npc"]:
        template = loaded_db.lookup(slug, table="npc").template
        file = f"gfx/sprites/player/{template.combat_sheet}.png"
        if file in checked:
            continue
        checked.add(file)
        expected = (
            template.combat_frame_width * 2,
            template.combat_frame_height,
        )
        assert has.size(file, expected), (
            f"Combat sheet '{file}' (NPC '{slug}') is not {expected}"
        )


def test_animation_sheets_divide_evenly_by_declared_frame_size(loaded_db):
    for slug in loaded_db.database["animation"]:
        animation = loaded_db.lookup(slug, table="animation")
        path = fetch_asset(
            "animations", f"{animation.file}/{animation.slug}.png"
        )
        width, height = pygame.image.load(path).get_size()
        assert (
            width % animation.frame_x == 0 and height % animation.frame_y == 0
        ), (
            f"Animation '{slug}' sheet is {width}x{height}, not divisible "
            f"by declared frame {animation.frame_x}x{animation.frame_y}"
        )
