#!/usr/bin/env python

from __future__ import division

import logging
import json
import random

from kivy import metrics
from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.uix.widget import Widget


# Used for logging
APPNAME = "SudokuApp"


# DO NOTE: class order is VERY important here!
class ImageButton(ButtonBehavior, Image):
    pass


class LabelButton(ButtonBehavior, Label):
    pass


class SudokuGrid(AnchorLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(anchor_x='left', anchor_y='top', **kwargs)

        self.fields = [[None] * 9 for i in range(9)]
        self._grid = GridLayout(rows=9, cols=9)
        self.add_widget(self._grid)

        for i in range(81):
            row = i // 9
            col = i % 9
            field = Field(row, col)
            field.set_number((row, col))
            self._grid.add_widget(field)
            self.fields[row][col] = field


class FieldSelector(Widget):
    pass


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self, 'text')

    def on_enter(self):
        Logger.debug("%s: Entering screen: '%s'" % (APPNAME, self.name))
        self._keyboard.bind(on_key_down=self.on_keyboard)

    def on_leave(self):
        Logger.debug("%s: Leaving screen: '%s'" % (APPNAME, self.name))
        self._keyboard.unbind(on_key_down=self.on_keyboard)

    def _on_keyboard_closed(self):
        # keep the (hardware) keyboard
        pass

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        keyname = keycode[1]
        Logger.debug("%s: Key pressed: '%s'" % (APPNAME, keyname))


class ScreenWithGrid(BaseScreen):
    """Screen, that 'implements' standard signals received from the grid.
    """
    def on_field_tap(self, field, touch):
        pass

    def on_field_double_tap(self, field, touch):
        pass

    def on_candidate_tap(self, candidate, touch):
        pass

    def on_candidate_double_tap(self, candidate, touch):
        pass


class GameScreen(ScreenWithGrid):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.selector = FieldSelector()
        # self.add_widget(self.selector)


class Field(AnchorLayout):
    """A Field in the sudoku grid."""

    def __init__(self, row, col, **kwargs):
        """Create a new Field Widget

        :param row: the row position of the field
        :param col: the column position of the field
        :param kwargs: Handed to the parent class
        """
        super(Field, self).__init__(anchor_x='right', anchor_y='top', **kwargs)
        self.row = row
        self.col = col

        self.number = NumberLabel(text="bla")
        self.candidates = GridLayout(rows=3, cols=3)
        for i in range(9):
            self.candidates.add_widget(CandidateLabel(i+1))

        self.add_widget(self.number)
        self.add_widget(self.candidates)

    def set_number(self, num):
        """Set the field to the number num and make it visible.
        """
        self.candidates.opacity = 0
        self.number.opacity = 1
        self.number.text = str(num)

    def set_candidates(self, candidates):
        """Set the field to the given candidates and make them visible.
        """
        self.number.opacity = 0
        self.candidates.opacity = 1

        for child in self.candidates.children:
            if child.number in candidates:
                child.opacity = 1
            else:
                child.opacity = 0

    def on_touch_down(self, touch):
        """Send the current screen a message when being touch.

        Make sure, your screen implements these methods, if you
        use this label:
            Screen.on_field_tap(self, field_widget, touch)
            Screen.on_candidate_double_tap(self, field_widget, touch)
        """
        if self.collide_point(touch.x, touch.y):
            screen = App.get_running_app().root.current_screen
            if touch.is_double_tap:
                screen.on_field_double_tap(self, touch)
            else:
                screen.on_field_tap(self, touch)


class ConfigurableLabel(Label):
    """Label that can be configured using the application config.

    Right now this only supports font sizes.
    """
    SECTION = "NOSECTION"
    FONT_SIZE_KEY = "number_font_size"

    def __init__(self, **kwargs):
        super(ConfigurableLabel, self).__init__(**kwargs)
        app = App.get_running_app()
        self.font_size = metrics.sp(
            app.config.get(self.SECTION, self.FONT_SIZE_KEY))
        app.config.add_callback(self.on_config_change,
            self.SECTION, self.FONT_SIZE_KEY)

    def on_config_change(self, section, key, value):
        """Update the font size, when the config changes.

        This only gets called, if SECTION->FONT_SIZE_KEY changes.
        """
        self.font_size = metrics.sp(value)


class NumberLabel(ConfigurableLabel):
    """A Label representing the (big) number in a field."""
    SECTION = "visuals"
    FONT_SIZE_KEY = "number_font_size"


class CandidateLabel(Label):
    """A Label representing a single candidate in a field."""
    SECTION = "visuals"
    FONT_SIZE_KEY = "candidate_font_size"

    def __init__(self, number, **kwargs):
        """Create a new candidate label.

         Also sets and updates the font size according to
         visuals->candidate_font_size in the config.
        """
        super(CandidateLabel, self).__init__(**kwargs)
        self.number = number
        self.text = str(self.number)

    def on_touch_down(self, touch):
        """Send the current screen a message when being touch.

        Make sure, your screen implements these methods, if you
        use this label:
            Screen.on_candidate_tap(self, candidate_label, touch)
            Screen.on_candidate_double_tap(self, candidate_label, touch)
        """
        if self.collide_point(touch.x, touch.y):
            screen = App.get_running_app().root.current_screen
            if touch.is_double_tap:
                screen.on_candidate_double_tap(self, touch)
            else:
                screen.on_candidate_tap(self, touch)


class SudokuApp(App):
    settings_cls = SettingsWithNoMenu

    def __read_default_settings(self):
        defaults = {}

        with open("settings.json") as f:
            data = json.load(f)
        for setting in data:
            section = setting.get("section", "")
            if setting["type"] != "title":
                section_defaults = defaults.get(section, {})
                section_defaults[setting["key"]] = setting["default"]
                defaults[section] = section_defaults

        return defaults

    def build_config(self, config):
        super(SudokuApp, self).build_config(config)

        defaults = self.__read_default_settings()
        for section, section_defaults in defaults.items():
            config.setdefaults(section, section_defaults)

    def build_settings(self, settings):
        settings.add_json_panel("Settings", self.config, "settings.json")

    def display_settings(self, settings):
        # self.root is the screenmanager
        if not self.root.has_screen("settings"):
            Logger.debug("%s: Creating settings screen" % APPNAME)
            settings_screen = Factory.SettingsScreen()
            settings_screen.ids.box.add_widget(settings)
            self.root.add_widget(settings_screen)

        settings_screen = self.root.get_screen("settings")
        settings_screen.last_screen = self.root.current
        self.root.current = "settings"
        return True


if __name__ == '__main__':
    Logger.setLevel(logging.DEBUG)
    SudokuApp().run()
