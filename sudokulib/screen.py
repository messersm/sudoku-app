# kivy imports
from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

# local imports
from sudokutools.sudoku import Sudoku
from sudokutools.generate import SudokuGenerator
from sudokutools.solve import solve


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

    def save_state(self, store):
        """Called, when the app pauses or stops."""
        pass

    def restore_state(self, store):
        """Called, when this screen is instanciated"""
        pass


class GameScreen(BaseScreen):
    grid = ObjectProperty(None)
    slider = ObjectProperty(None)
    stack = ListProperty()
    NUMBERS = [str(i) for i in range(10)]

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.__stack_index = 0

    @property
    def sudoku(self):
        return self.stack[self.__stack_index]

    def on_action(self, action):
        if action in self.NUMBERS:
            self.grid.enter_number(int(action))

    def restore_state(self, store):
        try:
            stack = store.get("game")["stack"]
        except KeyError:
            stack = []

        if stack:
            for s in stack:
                self.stack.append(Sudoku.from_full_str(s))
        else:
            self.stack.append(SudokuGenerator.create())

        self.__stack_index = len(self.stack) - 1
        self.solution = solve(self.sudoku.copy())
        self.grid.sync(self.sudoku)

    def save_state(self, store):
        store.put("game", stack=[sud.to_full_str() for sud in self.stack])


class MenuScreen(BaseScreen):
    pass


class CustomScreen(BaseScreen):
    grid = ObjectProperty(None)
