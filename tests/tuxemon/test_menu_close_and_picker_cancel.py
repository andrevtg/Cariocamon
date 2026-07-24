# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from functools import partial
from unittest.mock import Mock

import pytest

from tuxemon.menu.menu import Menu, PygameMenuState
from tuxemon.platform.const import buttons, intentions
from tuxemon.platform.events import PlayerInput
from tuxemon.states.quantity import QuantityPickerState


def pressed_event(button):
    event = PlayerInput(button, value=1)
    event.hold_time = 1
    return event


def make_menu_mock():
    menu = Mock(spec=Menu)
    menu.state_controller = Mock()
    menu.state_controller.is_interactive.return_value = True
    menu.client = Mock()
    return menu


def make_picker_mock():
    picker = Mock(spec=QuantityPickerState)
    picker.client = Mock()
    return picker


class TestMenuClosePopsItself:
    def test_close_without_animation_pops_the_menu_itself(self):
        menu = make_menu_mock()
        menu.animate_close.return_value = None

        Menu.close(menu)

        menu.client.pop_state.assert_called_once_with(menu)

    def test_close_with_animation_schedules_pop_of_the_menu_itself(self):
        menu = make_menu_mock()
        animation = Mock()
        menu.animate_close.return_value = animation

        Menu.close(menu)

        scheduled = animation.schedule.call_args[0][0]
        assert isinstance(scheduled, partial)
        assert scheduled.func == menu.client.pop_state
        assert scheduled.args == (menu,)

    def test_close_when_not_interactive_does_not_pop_any_state(self):
        menu = make_menu_mock()
        menu.state_controller.is_interactive.return_value = False

        Menu.close(menu)

        menu.client.pop_state.assert_not_called()

    def test_pygame_menu_on_close_pops_the_state_itself(self):
        state = Mock(spec=PygameMenuState)
        state.state_controller = Mock()
        state.client = Mock()
        state.animate_close.return_value = None

        PygameMenuState._on_close(state)

        state.client.pop_state.assert_called_once_with(state)


class TestQuantityPickerCancelButtons:
    @pytest.mark.parametrize(
        "button",
        [
            pytest.param(buttons.B, id="b_button"),
            pytest.param(buttons.BACK, id="back_button"),
            pytest.param(intentions.MENU_CANCEL, id="menu_cancel"),
        ],
    )
    def test_cancel_button_pops_the_picker_and_consumes_event(self, button):
        picker = make_picker_mock()

        result = QuantityPickerState.process_event(
            picker, pressed_event(button)
        )

        assert result is None
        picker.client.pop_state.assert_called_once_with()

    def test_a_button_confirms_the_selection(self):
        picker = make_picker_mock()

        result = QuantityPickerState.process_event(
            picker, pressed_event(buttons.A)
        )

        assert result is None
        picker._confirm.assert_called_once_with()
