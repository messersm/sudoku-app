# kivy imports
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

# sudokutools imports
from sudokutools.sudoku import Sudoku
from sudokutools.generate import generate
from sudokutools.solvers import solve
from sudokutools.solve import find_conflicts

# local imports
from sudokulib.secret import get_secret
from sudokulib.popup import CallbackPopup


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)

        app = App.get_running_app()
        self.screens = app.screens
        app.bind(on_settings_change=self.on_settings_change)
        # TODO: This fails for some reason.
        # app.actions.bind(on_action=self.__on_action)
        self.config = app.config

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


class GridScreen(BaseScreen):
    """Represents a screen with a SudokuGrid"""

    grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GridScreen, self).__init__(**kwargs)
        self.grid.bind(on_field_select=self.on_field_select)
        self.grid.bind(on_field_set=self.on_field_set)
        self.sudoku = None
        self.orig = None
        self.solution = None

    def on_field_set(self, grid, field, value):
        if isinstance(value, list):
            self.sudoku.set_candidates(*field.coords, value)
            self.sudoku.set_number(*field.coords, 0)
        else:
            self.sudoku.set_candidates(*field.coords, (value,))
            self.sudoku.set_number(*field.coords, value)

        if find_conflicts(self.sudoku, *field.coords):
            field.add_highlight("conflicts")
        else:
            field.remove_highlight("conflicts")

    def on_field_select(self, grid, old, new):
        if old:
            for coord in self.sudoku.surrounding_of(*old.coords, include=False):
                self.grid.fields[coord].remove_highlight("surrounding")
        if new:
            for coord in self.sudoku.surrounding_of(*new.coords, include=False):
                self.grid.fields[coord].add_highlight("surrounding")


class GameScreen(GridScreen):
    grid = ObjectProperty(None)
    # slider = ObjectProperty(None)
    # stack = ListProperty()
    NUMBERS = [str(i) for i in range(10)]

    def on_field_set(self, grid, field, value):
        super(GameScreen, self).on_field_set(grid, field, value)

        if len(list(self.sudoku.empty())) == 0 and not find_conflicts(self.sudoku):
            winpopup = CallbackPopup(
                title="Sudoku complete",
                text="Congratulations, you have won!",
                callbacks=[
                    ("Back", lambda: None),
                    ("New Sudoku", self.new_game)])
            winpopup.open()

    def on_action(self, action):
        if action in self.NUMBERS:
            self.grid.toggle_selected_candidate(int(action))
        elif action == "confirm":
            self.grid.confirm_selected()
        elif action == "delete":
            self.grid.enter_selected(0)
        elif action in ("next_field", "prev_field", "next_row", "prev_row"):
            self.grid.select(action)
        else:
            Logger.info("GameScreen: Unhandled action: %s" % action)

    def save_state(self, store):
        store.put(
            "game",
            orig=self.orig.encode(include_candidates=True),
            sudoku=self.sudoku.encode(include_candidates=True))

    def restore_state(self, store):
        try:
            orig = Sudoku.decode(store.get("game")["orig"])
            sudoku = Sudoku.decode(store.get("game")["sudoku"])
            self.new_game(orig, sudoku)
        except KeyError:
            self.new_game()

    def new_game(self, orig=None, sudoku=None):
        if orig is None or sudoku is None:
            self.orig = generate()
            self.sudoku = self.orig.copy()
        else:
            self.orig = orig
            self.sudoku = sudoku
        self.solution = solve(self.sudoku)
        self.grid.sync(self.sudoku)
        self.grid.lock_filled_fields(self.orig)
        self.grid.select(None)


class MenuScreen(BaseScreen):
    pass


class CustomScreen(GridScreen):
    code_input = ObjectProperty(None)
    NUMBERS = [str(i) for i in range(10)]

    def update_from_code_input(self):
        s = get_secret(self.code_input.text)
        if s:
            self.sudoku = Sudoku.from_str(s)
        else:
            self.sudoku = Sudoku.from_str(self.code_input.text)
        self.grid.sync(self.sudoku)

    def on_action(self, action, **kwargs):
        if action in self.NUMBERS:
            self.grid.enter_selected(int(action))
            # self.grid.index += 1 <- make this an option?
        elif action == "delete":
            self.grid.enter_selected(0)
        elif action == "confirm":
            self.grid.confirm_selected()
            # self.grid.index += 1
        elif action in ("next_field", "prev_field", "next_row", "prev_row"):
            self.grid.select(action)
        else:
            Logger.info("CustomScreen: Unhandled action: %s" % action)

    def play(self):
        unique = SudokuAnalyzer.is_unique(self.sudoku)
        if unique is None:
            popup = CallbackPopup(
                title="Sudoku cannot be solved",
                text="Your Sudoku cannot be solved.",
                callbacks=[
                    ("Too bad, let me fix that.", lambda: None)])
            popup.open()
        elif unique is False:
            popup = CallbackPopup(
                title="Sudoku is not unique",
                text="Your Sudoku has multiple solutions.",
                callbacks=[
                    ("Too bad, let me fix that.", lambda: None),
                    ("Play anyway!", self._transfer_to_game)])
            popup.open()
        else:
            self._transfer_to_game()

    def _transfer_to_game(self):
        app = App.get_running_app()
        app.screens.current = "game"
        app.screens.current_screen.new_game(self.sudoku, self.sudoku)
        self.sudoku = Sudoku()
        self.grid.sync(self.sudoku)

    def make_unique(self):
        sol1 = self.sudoku.copy()
        Bruteforce.call(sol1)
        sol2 = self.sudoku.copy()
        Bruteforce.call(sol2, reverse=True)
        SudokuGenerator.fix_non_unique(self.sudoku, sol1, sol2)
        self.grid.sync(self.sudoku)

    def save_state(self, store):
        store.put("custom", sudoku=self.sudoku.encode())

    def restore_state(self, store):
        try:
            self.sudoku = Sudoku.decode(store.get("custom")["sudoku"])
        except KeyError:
            self.sudoku = Sudoku()

        self.grid.sync(self.sudoku)

# TODO:
#  - fix red fields, that are locked on load
