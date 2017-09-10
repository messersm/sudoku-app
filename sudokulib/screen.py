# kivy imports
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

# local imports
from sudokutools.sudoku import Sudoku


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)

        app = App.get_running_app()
        app.bind(on_settings_change=self.on_settings_change)
        app.keyboard.bind(on_key_down=self.on_keyboard)

    def on_settings_change(self, app, section, key, value):
        pass

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        pass

    def save_state(self, state):
        """Called, when the app pauses or stops."""
        pass

    def restore_state(self, state):
        """Called, when this screen is instanciated"""
        pass


class GameScreen(BaseScreen):
    KEYS = {
        "numpad0": "0",
        "numpad1": "1",
        "numpad2": "2",
        "numpad3": "3",
        "numpad4": "4",
        "numpad5": "5",
        "numpad6": "6",
        "numpad7": "7",
        "numpad8": "8",
        "numpad9": "9",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "backspace": "0",
        "delete": "0",
        "enter": "confirm"
    }

    grid = ObjectProperty(None)

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        keyname = keycode[1]
        input = self.KEYS.get(keyname, None)
        if input is not None:
            self.grid.enter_number(input)


class MenuScreen(BaseScreen):
    pass


class CustomScreen(BaseScreen):
    grid = ObjectProperty(None)
