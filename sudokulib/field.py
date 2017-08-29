from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty

# local imports
from sudokutools.sudoku import VALID_NUMBERS
from sudokutools.coord import surrounding_coords

DEFAULT_FONT_SIZE = "27sp"
CANDIDATE_FONT_SIZE = "10sp"

BACKGROUND_COLORS = {
    "locked": (0, (0.8, 0.8, 0.8, 1)),
    "default": (1, (1, 1, 1, 1))
}

HIGHLIGHT_COLORS = {
    "selected": (0, (0.5, 0.5, 1, 1)),
    "invalid": (1, (1, 0, 0, 1)),
    "influenced": (2, (0.7, 0.7, 1, 1)),
    "default": (3, (1, 1, 1, 0))
}


class Field(Label):
    """Represents on visible field in the sudoku grid.
    """
    background_color = ListProperty(BACKGROUND_COLORS["default"][1])
    highlight_color = ListProperty(HIGHLIGHT_COLORS["default"][1])

    DEFAULT_BORDER_COLOR = (0.5, 0.5, 0.5, 1)
    THICK_BORDER_COLOR = (0, 0, 0, 1)
    left_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    bottom_border_color = ListProperty(DEFAULT_BORDER_COLOR)

    DEFAULT_BORDER_WIDTH = 1
    THICK_BORDER_WIDTH = 1.5
    left_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    bottom_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)

    def __init__(self, coords=(-1, -1), **kwargs):
        super(Field, self).__init__(**kwargs)
        self.coords = coords

        # highlight
        self.__highlights = [HIGHLIGHT_COLORS["default"]]

        # state
        self.__locked = False
        self.__selected = False
        self.__content = None

        # select border style
        (x, y) = coords
        if x % 3 == 0:
            self.left_border_color = self.THICK_BORDER_COLOR
            self.left_border_width = self.THICK_BORDER_WIDTH

        if y % 3 == 2:
            self.bottom_border_color = self.THICK_BORDER_COLOR
            self.bottom_border_width = self.THICK_BORDER_WIDTH

    def __show_candidates(self):
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

    def __show_number(self):
        self.font_size = DEFAULT_FONT_SIZE
        if not self.content:
            self.text = ''
        else:
            self.text = str(self.content)

    def __update_highlight_color(self):
        self.__highlights.sort()
        self.highlight_color = self.__highlights[0][1]

    def add_highlight(self, name):
        highlight = HIGHLIGHT_COLORS[name]
        self.__highlights.append(highlight)
        self.__update_highlight_color()

    def remove_highlight(self, name):
        highlight = HIGHLIGHT_COLORS[name]
        self.__highlights.remove(highlight)
        self.__update_highlight_color()

    def reset_highlight(self):
        self.__highlights = [HIGHLIGHT_COLORS["default"]]

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        self.__content = value
        sudoku = self.parent.sudoku

        if value is None or value == 0:
            sudoku[self.coords] = 0
            sudoku.set_candidates(self.coords, None)
            self.__show_number()

        elif isinstance(value, list):
            sudoku[self.coords] = 0
            sudoku.set_candidates(self.coords, value)
            self.__show_candidates()
            
        elif isinstance(value, int):
            sudoku[self.coords] = value
            sudoku.set_candidates(self.coords, None)
            self.__show_number()

    def lock(self, locked=True):
        self.__locked = locked

        if locked:
            self.select(False)
            self.background_color = BACKGROUND_COLORS["locked"][1]
        else:
            self.background_color = BACKGROUND_COLORS["default"][1]

    @property
    def locked(self):
        return self.__locked

    @property
    def selected(self):
        return self.__selected

    def select(self, selected=True):
        if selected:
            if not self.__selected:
                self.parent.selected_field = self
                self.add_highlight("selected")
                for coord in surrounding_coords(self.coords, include=False):
                    self.parent.fields[coord].add_highlight("influenced")
        else:
            if self.__selected:
                self.remove_highlight("selected")
                for coord in surrounding_coords(self.coords, include=False):
                    self.parent.fields[coord].remove_highlight("influenced")

                if self.parent.sudoku.find_conflicts(self.coords):
                    self.add_highlight("invalid")
                else:
                    # Yep, that's ugly.
                    while HIGHLIGHT_COLORS["invalid"] in self.__highlights:
                        self.remove_highlight("invalid")

        self.__selected = selected

    def input(self, inp):
        if self.__selected:
            # clear
            if inp == 0:
                self.content = 0
            # candidate input mode
            elif isinstance(self.content, list):
                candidates = self.content
                if inp in candidates:
                    candidates.remove(inp)
                else:
                    candidates.append(inp)

                self.content = candidates
            # number input mode
            else:
                self.content = [inp]

    def on_touch_down(self, touch):
        # do nothing, when locked
        if self.__locked:
            return

        if self.collide_point(*touch.pos):
            if self.selected:
                if isinstance(self.content, list) and len(self.content) == 1:
                    self.content = self.content[0]
                    self.select(False)
            else:
                self.select(True)

        # only unselect, if the grid is touched.
        elif self.parent.collide_point(*touch.pos):
            self.select(False)
