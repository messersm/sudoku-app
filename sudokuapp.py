#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
import json
from os.path import join

# kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from sudokulib.action import ActionManager
from sudokulib.screen import CustomScreen, GameScreen, MenuScreen
# needed by sudoku.kv
from sudokulib.grid import SudokuGrid


STATEFILE = "state.json"


class SudokuApp(App):
    __events__ = list(App.__events__)
    __events__.append('on_settings_change')

    def build(self):
        self.use_kivy_settings = False

        self.actions = ActionManager()

        self.screens = ScreenManager(transition=FadeTransition())
        # self.screens.add_widget(MenuScreen())
        self.screens.add_widget(GameScreen())
        self.screens.add_widget(CustomScreen())

        return self.screens

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

    def on_config_change(self, config, section, key, value):
        self.dispatch('on_settings_change', section, key, value)


    def on_settings_change(self, section, key, value):
        # default handler (required)
        pass

    def save_state(self):
        filename = join(self.user_data_dir, STATEFILE)
        store = JsonStore(filename)

        for name in self.screens.screen_names:
            screen = self.screens.get_screen(name)
            screen.save_state(store)

    def on_pause(self):
        self.save_state()
        return True

    def on_stop(self):
        self.save_state()


if __name__ == '__main__':
    Builder.load_file("kv/sudoku.kv")
    Builder.load_file("kv/game.kv")
    Builder.load_file("kv/custom.kv")

    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '720')

    SudokuApp().run()
