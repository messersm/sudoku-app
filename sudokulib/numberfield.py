
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty

from fieldstate import Unselected, InputNumber
from fieldstyle import FieldStyle

from sudokutools.sudoku import VALID_NUMBERS

DEFAULT_FONT_SIZE = "27sp"
CANDIDATE_FONT_SIZE = "10sp"

class NumberField(Label):
    background_color = ListProperty((1, 1, 1, 1))
    highlight_color = ListProperty((1, 1, 1, 0))

    DEFAULT_BORDER_COLOR = (0.5, 0.5, 0.5, 1)
    THICK_BORDER_COLOR = (0, 0, 0, 1)
    left_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    bottom_border_color = ListProperty(DEFAULT_BORDER_COLOR)

    DEFAULT_BORDER_WIDTH = 1
    THICK_BORDER_WIDTH = 1.5
    left_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    bottom_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)

    def __init__(self, coords=(-1, -1), locked=False, **kwargs):
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
        self.state.on_touch_down(self, touch)

    def set_state(self, state):
        if not state == self.state:
            self.state.on_exit(self)
            self.state = state
            self.state.on_enter(self)
