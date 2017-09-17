# kivy imports
from kivy.animation import Animation
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ObjectProperty

# local imports
from sudokutools.coord import surrounding_coords
from sudokulib.field import Field, HIGHLIGHT_COLORS

VALID_NUMBERS = set([1, 2, 3, 4, 5, 6, 7, 8, 9])


class SudokuGrid(GridLayout):
    __events__ = ('on_field_select', 'on_field_set')

    control = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.fields = {}
        self.selected_field = None

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                field = Field(coords=(x, y))
                field.bind(on_select=self.on_select)
                field.bind(on_set=self.on_set)
                self.add_widget(field)
                self.fields[(x, y)] = field

    def on_set(self, field, value):
        self.dispatch('on_field_set', field, value)

    def on_field_set(self, field, value):
        """default handler (required)"""
        pass

    @property
    def index(self):
        if not self.selected_field:
            return 0
        x, y = self.selected_field.coords
        return x + y * 9

    @index.setter
    def index(self, value):
        if value >= 81 or value < 0:
            value %= 81
        x, y = value % 9, value // 9
        self.fields[(x, y)].select()

    def select(self, obj):
        if isinstance(obj, Field):
            obj.select()
        elif obj == "next_field":
            x = self.index % 9
            if x == 8:
                self.index -= 8
            else:
                self.index += 1
        elif obj == "prev_field":
            x = self.index % 9
            if x == 0:
                self.index += 8
            else:
                self.index -= 1
        elif obj == "next_row":
            self.index += 9
        elif obj == "prev_row":
            self.index -= 9

    def on_select(self, field):
        self.dispatch('on_field_select', self.selected_field, field)
        if self.selected_field:
            self.selected_field.select(False)
        self.selected_field = field
        Logger.debug("SudokuGrid: Field at %s selected." % str(field.coords))

    def on_field_select(self, old, new):
        """default handler (required)"""
        pass

    def clear(self):
        for field in self.fields.values():
            if not field.locked:
                field.content = None

    def confirm_selected(self):
        if self.selected_field:
            self.selected_field.confirm()

    def enter_selected(self, number):
        if self.selected_field:
            self.selected_field.enter(number)

    def toggle_selected_candidate(self, number):
        if self.selected_field:
            self.selected_field.toggle_candidate(number)

    def lock_filled_fields(self, sudoku):
        """Lock every filled field in sudoku and unlock everything else."""
        for x in range(9):
            for y in range(9):
                if sudoku[x, y] in VALID_NUMBERS:
                    self.fields[(x, y)].lock(True)
                else:
                    self.fields[(x, y)].lock(False)

    def sync(self, sudoku, coords=None):
        if not coords:
            coords = [(x, y) for x in range(9) for y in range(9)]

        for (x, y) in coords:
            item = sudoku[x, y]
            field = self.fields[(x, y)]

            if not item:
                candidates = sudoku.candidates.get((x, y), None)
                field.content = candidates
            elif item in VALID_NUMBERS:
                field.content = item
