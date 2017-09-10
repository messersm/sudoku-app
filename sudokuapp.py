#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
import json

# kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

from sudokulib.screen import GameScreen, MenuScreen
# needed by sudoku.kv
from sudokulib.grid import SudokuGrid


STATEFILE = "state.json"

class GameWidget(BoxLayout):
    grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.__app_config = App.get_running_app().config


class SudokuApp(App):
    __events__ = list(App.__events__)
    __events__.append('on_settings_change')

    def build(self):
        self.use_kivy_settings = False

        self.keyboard = Window.request_keyboard(
            self.__on_keyboard_closed, self, 'text')
        self.keyboard.bind(on_key_down=self.on_keyboard)

        self.screens = ScreenManager(transition=FadeTransition())
        self.screens.add_widget(MenuScreen())
        self.screens.add_widget(GameScreen())

        # self.sudoku_widget = SudokuWidget()
        # self.statefilename = join(self.user_data_dir, STATEFILE)
        return self.screens

    def __on_keyboard_closed(self):
        self.__keyboard.unbind(on_key_down=self.__on_keyboard_down)
        self.__keyboard = None

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
        defaults = self.__read_default_settings()
        for section, section_defaults in defaults.items():
            config.setdefaults(section, section_defaults)

    def build_settings(self, settings):
        settings.add_json_panel("Settings", self.config, "settings.json")

    def on_config_change(self, config, section, key, value):
        self.dispatch('on_settings_change', section, key, value)

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        pass

    def on_settings_change(self, section, key, value):
        # default handler (required)
        pass

    def __save_state(self):
        pass

    def on_pause(self):
        for name in self.screens.screen_names:
            screen = self.screens.get_screen(name)
            screen.update_state(state)
        return True

    def on_stop(self):
        # self.sudoku_widget.save_state(self.statefilename)
        pass

if __name__ == '__main__':
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')

    SudokuApp().run()
