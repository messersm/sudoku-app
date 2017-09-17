# kivy imports
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

# local imports
from sudokutools.coord import surrounding_coords
from sudokutools.generate import SudokuGenerator
from sudokutools.solve import solve
from sudokutools.sudoku import Sudoku

from sudokulib.secret import get_secret

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
            self.grid.toggle_selected_candidate(int(action))
        elif action == "confirm":
            self.grid.confirm_selected()
        elif action == "delete":
            self.grid.delete_selected()
        else:
            Logger.info("GameScreen: Unhandled action: %s" % action)

    def save_state(self, store):
        store.put("game", stack=[sud.to_full_str() for sud in self.stack])

    def restore_state(self, store):
        try:
            stack = store.get("game")["stack"]
        except KeyError:
            stack = []

        if stack:
            for s in stack:
                self.stack.append(Sudoku.from_full_str(s))
            self.__prepare_game()
        else:
            self.new_game()

    def __prepare_game(self):
        self.__stack_index = len(self.stack) - 1
        self.solution = solve(self.sudoku, inplace=False)
        self.grid.sync(self.sudoku)
        self.grid.lock_filled_fields(self.stack[0])

    def new_game(self):
        self.stack = [SudokuGenerator.create()]
        self.__prepare_game()

class MenuScreen(BaseScreen):
    pass


class CustomScreen(BaseScreen):
    grid = ObjectProperty(None)
    code_input = ObjectProperty(None)

    NUMBERS = [str(i) for i in range(10)]

    def __init__(self, **kwargs):
        super(CustomScreen, self).__init__(**kwargs)
        self.grid.bind(on_field_select=self.on_field_select)
        self.grid.bind(on_field_set=self.on_field_set)
        self.sudoku = Sudoku()

    def update_from_code_input(self):
        s = get_secret(self.code_input.text)
        if s:
            self.sudoku = Sudoku.from_str(s)
        else:
            self.sudoku = Sudoku.from_str(self.code_input.text)
        self.grid.sync(self.sudoku)

    def on_field_set(self, grid, field, value):
        if isinstance(value, list):
            self.sudoku.candidates[field.coords] = value
            self.sudoku[field.coords] = 0
        else:
            self.sudoku.candidates[field.coords] = None
            self.sudoku[field.coords] = value

    def on_field_select(self, grid, old, new):
        # pass
        return
        if old:
            for coord in surrounding_coords(old, include=False):
                self.grid.fields[coord].remove_highlight("surrounding")
        if new:
            for coord in surrounding_coords(new, include=False):
                self.grid.fields[coord].add_highlight("surrounding")

    def on_action(self, action, **kwargs):
        if action in self.NUMBERS:
            self.grid.enter_selected(int(action))
            self.grid.index += 1
        elif action == "delete":
            self.grid.enter_selected(0)
        elif action == "confirm":
            self.grid.confirm_selected()
            self.grid.index += 1
        elif action in ("next_field", "prev_field", "next_row", "prev_row"):
            self.grid.select(action)
        else:
            Logger.info("CustomScreen: Unhandled action: %s" % action)

    def clear(self):
        pass

    def play(self):
        pass
