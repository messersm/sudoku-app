# standard imports
from os.path import join
from random import choice

# kivy imports
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.storage.jsonstore import JsonStore

# local imports
from sudokulib.field import Field
from sudokulib.popup import CallbackPopup

from sudokutools.analyzer import SudokuAnalyzer
from sudokutools.solve import CalculateCandidates, solve
from sudokutools.sudoku import VALID_NUMBERS, Sudoku
from sudokutools.examples import EXAMPLES

STATEFILE = "state.json"


class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.sudoku_won = False
        self.sudoku = None
        self.orig = None
        self.solution = None
        self.fields = {}
        self.selected_field = None

        self.__in_edit_custom = False

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                field = Field(coords=(x, y))
                self.add_widget(field)
                self.fields[(x, y)] = field

        filename = join(App.get_running_app().user_data_dir, STATEFILE)
        self.restore_state(filename=filename)
        if not self.sudoku:
            self.new_sudoku()

    def edit_custom_sudoku(self):
        if self.__in_edit_custom:
            self.check_edit_custom_sudoku()
        else:
            self.begin_edit_custom_sudoku()

    def begin_edit_custom_sudoku(self):
        self.__in_edit_custom = True

        if self.sudoku:
            self.lock_filled_fields(False)

        self.sudoku = Sudoku()
        self.sync_sudoku_to_gui()

    def check_edit_custom_sudoku(self):
        ret = SudokuAnalyzer.is_unique(self.sudoku)

        if ret is None:
            error = CallbackPopup(
                title="Error: Sudoku is not valid.",
                text="Your Sudoku has no solution.",
                callbacks=[("Back", lambda: None)])
            error.open()
        elif ret is False:
            warning = CallbackPopup(
                title="Warning: Sudoku is not unique",
                text="Your Sudoku has multiple solutions.",
                callbacks=[
                    ("Back", lambda: None),
                    ("Play anyway!", self.end_edit_custom_sudoku)])
            warning.open()
        elif ret is True:
            self.end_edit_custom_sudoku()

    def end_edit_custom_sudoku(self):
        self.__in_edit_custom = False
        self.lock_filled_fields(True)
        self.orig = self.sudoku.copy()

    def sudoku_complete(self):
        if self.sudoku_won:
            return

        self.sudoku_won = True
        winpopup = CallbackPopup(
            title="Sudoku complete",
            text="Congratulations, you have won!",
            callbacks=[
                ("Back", lambda: None),
                ("New Sudoku", self.new_sudoku)])
        winpopup.open()

    # TODO: Move this code to sudokutools
    def check_complete(self):
        if self.sudoku.empty:
            return False

        if SudokuAnalyzer.find_all_conflicts(self.sudoku):
            return False

        return True

    def clear(self):
        for field in self.fields.values():
            if not field.locked:
                field.content = None

    def new_sudoku(self):
        self.sudoku_won = False

        if self.sudoku:
            self.lock_filled_fields(False)

        example = choice(EXAMPLES)[0]
        self.sudoku = Sudoku.from_str(example)
        self.orig = self.sudoku.copy()
        self.solution = solve(self.sudoku, inplace=False)
        self.lock_filled_fields()
        self.sync_sudoku_to_gui()

    def enter_number(self, number):
        if self.selected_field:
            self.selected_field.input(number)

        if self.check_complete():
            self.sudoku_complete()

    def lock_filled_fields(self, locked=True):
        for x in range(9):
            for y in range(9):
                if self.sudoku[x, y] in VALID_NUMBERS:
                    self.fields[(x, y)].lock(locked)

    def sync_sudoku_to_gui(self):
        for x in range(9):
            for y in range(9):
                item = self.sudoku[x, y]
                if not item:
                    candidates = self.sudoku.candidates.get((x, y), None)
                    self.fields[(x, y)].content = candidates
                elif item in VALID_NUMBERS or item is None:
                    self.fields[(x, y)].content = item

    def auto_candidates(self):
        if self.selected_field:
            field = self.selected_field
            candidates = CalculateCandidates.call(self.sudoku, field.coords)
            field.content = candidates

    def solve(self):
        self.sudoku = self.solution
        self.sync_sudoku_to_gui()

        if self.check_complete():
            self.sudoku_complete()

    def solve_field(self):
        if self.selected_field:
            coords = self.selected_field.coords
            self.sudoku[coords] = self.solution[coords]
            self.sync_sudoku_to_gui()

        if self.check_complete():
            self.sudoku_complete()

    def save_state(self, filename=STATEFILE):
        if self.sudoku:
            store = JsonStore(filename)
            current_str = self.sudoku.to_str(row_sep='', column_sep='')
            orig_str = self.orig.to_str(row_sep='', column_sep='')
            store.put('sudoku', orig=orig_str, current=current_str)

    def restore_state(self, filename=STATEFILE):
        store = JsonStore(filename)
        if 'sudoku' in store:
            self.orig = Sudoku.from_str(store['sudoku']['orig'])
            self.sudoku = self.orig
            self.lock_filled_fields()
            self.sudoku = Sudoku.from_str(store['sudoku']['current'])
            self.solution = solve(self.sudoku, inplace=False)
            self.sync_sudoku_to_gui()