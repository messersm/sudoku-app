# kivy imports
from kivy.animation import Animation
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty

# local imports
from sudokulib.field import Field, HIGHLIGHT_COLORS
from sudokulib.popup import CallbackPopup

from sudokutools.analyze import SudokuAnalyzer
from sudokutools.solve import CalculateCandidates, solve
from sudokutools.sudoku import VALID_NUMBERS, Sudoku


class SudokuGrid(GridLayout):
    control = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.fields = {}
        self.selected_field = None

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                field = Field(coords=(x, y))
                self.add_widget(field)
                self.fields[(x, y)] = field

    @property
    def solution(self):
        return self.control.solution

    @property
    def sudoku(self):
        return self.control.sudoku

    def play_win_animation(self, on_complete=None):
        color1 = HIGHLIGHT_COLORS["selected"][1]
        color2 = HIGHLIGHT_COLORS["default"][1]

        fields = [self.fields[(x, y)] for y in range(9) for x in range(9)]
        last_field = fields.pop()

        wait = 0
        for field in fields:
            anim = Animation(duration=wait)
            anim += Animation(highlight_color=color1, duration=0.5)
            anim += Animation(highlight_color=color2, duration=0.5)
            anim.start(field)
            wait += 0.05

        last_anim = Animation(duration=wait)
        last_anim += Animation(highlight_color=color1, duration=0.5)
        last_anim += Animation(highlight_color=color2, duration=0.5)

        last_anim.bind(on_complete=on_complete)
        last_anim.start(last_field)

    def display_win_popup(self):
        winpopup = CallbackPopup(
            title="Sudoku complete",
            text="Congratulations, you have won!",
            callbacks=[
                ("Back", lambda: None),
                ("New Sudoku", self.new_sudoku)])
        winpopup.open()

    def clear(self):
        for field in self.fields.values():
            if not field.locked:
                field.content = None

    def load(self, orig, sudoku=None):
        for field in self.fields.values():
            field.reset()

        self.orig = orig
        if not sudoku:
            self.sudoku = orig.copy()
        else:
            self.sudoku = sudoku
        self.solution = self.sudoku.copy()
        solve(self.solution)

        self.sudoku_won = SudokuAnalyzer.is_complete(self.sudoku)
        self.lock_filled_fields()
        self.sync_sudoku_to_gui()

        # self.id_label.text = "id: %s" % self.sudoku.to_base62()

    def enter_number(self, number):
        if self.selected_field:
            self.selected_field.input(number)

    def lock_filled_fields(self, locked=True):
        for x in range(9):
            for y in range(9):
                if self.orig[x, y] in VALID_NUMBERS:
                    self.fields[(x, y)].lock(locked)

    def sync(self, sudoku, coords=None):
        if not coords:
            coords = [(x, y) for x in range(9) for y in range(9)]

        for (x, y) in coords:
            item = sudoku[x, y]
            if not item:
                candidates = sudoku.candidates.get((x, y), None)
                self.fields[(x, y)].content = candidates
            elif item in VALID_NUMBERS or item is None:
                self.fields[(x, y)].content = item
