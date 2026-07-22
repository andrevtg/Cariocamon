# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
"""Validate the throwaway HD test assets against the doubled size
constants (ADR-0001, graphics-upgrade phase 2)."""

from tuxemon.database.registry import validator as has
from tuxemon.database.runtime import db  # noqa: F401  # side-effect import
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


def test_old_resolution_icon_fails_doubled_icon_size_check():
    old_icon = "gfx/ui/icons/party/party_icon01.png"
    assert not has.size(old_icon, ICON_SIZE)
