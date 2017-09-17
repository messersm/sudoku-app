from kivy.app import App
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

DEFAULT_FONT_SIZE = "27sp"
CANDIDATE_FONT_SIZE = "10sp"

BACKGROUND_COLORS = {
    "locked": (0, (0.8, 0.8, 0.8, 1)),
    "default": (1, (1, 1, 1, 1))
}

OPTIONAL_HIGHLIGHT_COLORS = {
    "conflicts": (1, (1, 0, 0, 1)),
    "incorrect": (2, (1, 0.4, 0.4, 1)),
    "surrounding": (3, (0.7, 0.7, 1, 0.5)),
}

HIGHLIGHT_COLORS = {
    "selected": (0, (0.5, 0.5, 1, 0.7)),
    "default": (4, (1, 1, 1, 0))
}

HIGHLIGHT_COLORS.update(OPTIONAL_HIGHLIGHT_COLORS)

class Field(Label):
    __events__ = ('on_select', 'on_set')

    """Represents on visible field in the sudoku grid.
    """
    background_color = ListProperty(BACKGROUND_COLORS["default"][1])
    highlight_color = ListProperty(HIGHLIGHT_COLORS["default"][1])

    DEFAULT_BORDER_COLOR = (0.5, 0.5, 0.5, 1)
    THICK_BORDER_COLOR = (0, 0, 0, 1)
    left_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    right_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    top_border_color = ListProperty(DEFAULT_BORDER_COLOR)
    bottom_border_color = ListProperty(DEFAULT_BORDER_COLOR)

    DEFAULT_BORDER_WIDTH = 1
    THICK_BORDER_WIDTH = 1.5
    left_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    right_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    top_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)
    bottom_border_width = NumericProperty(DEFAULT_BORDER_WIDTH)

    def __init__(self, coords=(-1, -1), **kwargs):
        super(Field, self).__init__(**kwargs)
        self.coords = coords

        # app config access
        app = App.get_running_app()
        self.__app_config = app.config
        app.bind(on_settings_change=self.on_settings_change)

        # highlight
        self.__highlights = ["default"]

        # state
        self.__locked = False
        self.__selected = False
        self.__content = None

        # select border style
        (x, y) = coords
        if x == 0:
            self.left_border_color = self.THICK_BORDER_COLOR
            self.left_border_width = self.THICK_BORDER_WIDTH

        if x % 3 == 2:
            self.right_border_color = self.THICK_BORDER_COLOR
            self.right_border_width = self.THICK_BORDER_WIDTH

        if y == 0:
            self.top_border_color = self.THICK_BORDER_COLOR
            self.top_border_width = self.THICK_BORDER_WIDTH

        if y % 3 == 2:
            self.bottom_border_color = self.THICK_BORDER_COLOR
            self.bottom_border_width = self.THICK_BORDER_WIDTH

    def __show_candidates(self):
        self.font_size = CANDIDATE_FONT_SIZE

        s = ""

        try:
            for n in range(1, 10):
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
        used_highlights = []
        for name in self.__highlights:
            if name in OPTIONAL_HIGHLIGHT_COLORS:
                if self.__app_config.get("highlight", name) == "1":
                    used_highlights.append(HIGHLIGHT_COLORS[name])
            else:
                used_highlights.append(HIGHLIGHT_COLORS[name])

        used_highlights.sort()
        self.highlight_color = used_highlights[0][1]

    def reset(self):
        self.lock(False)
        self.select(False)
        self.reset_highlight()
        self.__update_highlight_color()

    def add_highlight(self, name):
        # YES: we want multiple times the same value
        self.__highlights.append(name)
        self.__update_highlight_color()

    def remove_highlight(self, name):
        if name in self.__highlights:
            self.__highlights.remove(name)
            self.__update_highlight_color()

    def reset_highlight(self):
        self.__highlights = ["default"]

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, value):
        if value is None:
            value = 0

        self.__content = value

        if isinstance(value, list):
            self.__show_candidates()
        else:
            self.__show_number()

        self.dispatch('on_set', value)

    def on_set(self, value):
        """default handler (required)"""
        pass

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
            self.dispatch("on_select")
            self.add_highlight("selected")
        else:
            self.remove_highlight("selected")

    def on_select(self):
        pass

    def enter(self, number):
        self.content = number

    def confirm(self):
        if isinstance(self.content, list):
            if len(self.content) == 1:
                self.content = self.content[0]

    def toggle_candidate(self, number):
        if isinstance(self.content, list):
            candidates = self.content
            if number in candidates:
                candidates.remove(number)
            else:
                candidates.append(number)

            self.content = candidates
        else:
            self.content = [number]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.select()
            if touch.is_double_tap:
                self.confirm()

    def on_settings_change(self, app, section, key, value):
        self.__update_highlight_color()
