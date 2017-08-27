
from kivy.uix.gridlayout import  GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.properties import ListProperty, NumericProperty

from fieldstate import Unselected, InputNumber
from fieldstyle import FieldStyle

from sudokutools.sudoku import VALID_NUMBERS

DEFAULT_FONT_SIZE = "27sp"
CANDIDATE_FONT_SIZE = "10sp"

BACKGROUND_COLORS = {
    "locked": (0.8, 0.8, 0.8, 1),
    "default": (1, 1, 1, 1)
}

HIGHLIGHT_COLORS = {
    "selected": (0.5, 0.5, 1, 1),
    "invalid": (1, 0, 0, 1),
    "influenced": (0.7, 0.7, 1, 1),
    "default": (1, 1, 1, 0)
}


class NumberChooser(GridLayout):
    number_font_size = DEFAULT_FONT_SIZE
    candidate_font_size = CANDIDATE_FONT_SIZE

    def __init__(self, field, **kwargs):
        self.field = field
        super(NumberChooser, self).__init__(**kwargs)


class NumberField(Label):
    """Represents on visible field in the sudoku grid.

    select(True / False)
    lock(True / False)
    input(number)

    """

    background_color = ListProperty(BACKGROUND_COLORS["default"])
    highlight_color = ListProperty(HIGHLIGHT_COLORS["default"])

    DEFAULT_BORDER_COLOR = (0.5, 0.5, 0.5, 1)
    THICK_BORDER_COLOR = (0, 0, 0, 1)
    left_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    bottom_border_color = ListProperty(DEFAULT_BORDER_COLOR)

    DEFAULT_BORDER_WIDTH = 1
    THICK_BORDER_WIDTH = 1.5
    left_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    bottom_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)

    def __init__(self, coords=(-1, -1), **kwargs):
        super(NumberField, self).__init__(**kwargs)
        self.coords = coords

        self.__content = None
        self.state = Unselected
        self.style = FieldStyle(self)

        # select border style
        (x, y) = coords
        if x % 3 == 0:
            self.left_border_color = self.THICK_BORDER_COLOR
            self.left_border_width = self.THICK_BORDER_WIDTH

        if y % 3 == 2:
            self.bottom_border_color = self.THICK_BORDER_COLOR
            self.bottom_border_width = self.THICK_BORDER_WIDTH

    @property
    def sudoku(self):
        return self.parent.sudoku

    def __set_highlight(self, name):
        self.highlight_color = HIGHLIGHT_COLORS[name]

    def show_candidates(self):
        self.font_size = CANDIDATE_FONT_SIZE

        s = ""

        try:
            for n in VALID_NUMBERS:
                if n in self.content:
                    s += str(n)
                else:
                    s += '  '
                s += ' '
                if n % 3 == 0 and n < 9:
                    s += '\n'
            self.text = s
        # got None
        except TypeError:
            self.text = ''

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = value
        if value is None:
            self.sudoku[self.coords] = 0
            self.sudoku.set_candidates(self.coords, None)
            self.show_number()

        elif isinstance(value, list):
            self.sudoku[self.coords] = 0
            self.sudoku.set_candidates(self.coords, value)
            self.show_candidates()
            
        elif isinstance(value, int):
            self.sudoku[self.coords] = value
            self.sudoku.set_candidates(self.coords, None)
            self.show_number()

    def show_number(self):
        self.font_size = DEFAULT_FONT_SIZE
        if not self.content:
            self.text = ''
        else:
            self.text = str(self.content)

    def lock(self, locked=True):
        self.state.on_lock(self, locked)

    def select(self, selected=True):
        self.state.on_select(self, selected)

    def input(self, inp):
        self.state.on_input(self, inp)

    def on_touch_down(self, touch):
        # chooser = NumberChooser(self)
        # self.add_widget(chooser)
        # return
        self.state.on_touch_down(self, touch)

    def set_state(self, state):
        if not state == self.state:
            self.state.on_exit(self)
            self.state = state
            self.state.on_enter(self)
