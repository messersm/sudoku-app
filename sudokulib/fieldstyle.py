COLORS = {
    "selected": (0, (0.5, 0.5, 1, 1)),
    "invalid": (1, (1, 0, 0, 1)),
    "influenced": (2, (0.7, 0.7, 1, 1)),
    "locked": (3, (0.8, 0.8, 0.8, 1)),
    "default": (4, (1, 1, 1, 1))
}

class FieldStyle(object):
    def __init__(self, field):
        self.field = field
        self.colors = [COLORS["default"]]

    def __update_field(self):
        self.colors.sort()
        priority, color = self.colors[0]
        self.field.bgcolor = color

    def push(self, (priority, color)):
        self.colors.append((priority, color))
        self.__update_field()

    def pop(self, (priority, color)):
        self.colors.remove((priority, color))
        self.__update_field()
