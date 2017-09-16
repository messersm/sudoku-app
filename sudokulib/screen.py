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
        self.screens = app.screens
        app.bind(on_settings_change=self.on_settings_change)
        app.actions.bind(on_action=self.__on_action)

    def on_settings_change(self, app, section, key, value):
        pass

    def __on_action(self, manager, action):
        if self.screens.current == self.name:
            self.on_action(action)

    def on_action(self, action):
        pass

    def save_state(self, state):
        """Called, when the app pauses or stops."""
        pass

    def restore_state(self, state):
        """Called, when this screen is instanciated"""
        pass


class GameScreen(BaseScreen):
    grid = ObjectProperty(None)
    NUMBERS = [str(i) for i in range(10)]

    def on_action(self, action):
        if action in self.NUMBERS:
            self.grid.enter_number(int(action))


class MenuScreen(BaseScreen):
    pass


class CustomScreen(BaseScreen):
    grid = ObjectProperty(None)
