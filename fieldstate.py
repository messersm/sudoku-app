"""

FieldState
 - Locked
 - Unselected
 - Selected
    - InputNumber
    - InputCandidates
"""

from fieldstyle import COLORS
from sudokutools.sudoku import VALID_NUMBERS

class FieldState(object):
    @classmethod
    def on_input(cls, field, number):
        pass

    @classmethod
    def on_touch_down(cls, field, touch):
        pass

    @classmethod
    def on_enter(cls, field):
        pass

    @classmethod
    def on_exit(cls, field):
        pass

    @classmethod
    def on_lock(cls, field, locked=True):
        pass

    @classmethod
    def on_select(cls, field, selected=True):
        pass

class Unselected(FieldState):
    @classmethod
    def on_touch_down(cls, field, touch):
        super(Unselected, cls).on_touch_down(field, touch)
        
        if field.collide_point(*touch.pos):
            if not field.content or isinstance(field.content, int):
                field.set_state(InputNumber)
            else:
                field.set_state(InputCandidates)


    @classmethod
    def on_lock(cls, field, locked=True):
        if locked:
            field.set_state(Locked)

    @classmethod
    def on_select(cls, field, selected=True):
        if selected:
            field.set_state(InputNumber)

class Locked(FieldState):
    @classmethod
    def on_enter(cls, field):
        field.style.push(COLORS["locked"])

    @classmethod
    def on_exit(cls, field):
        field.style.pop(COLORS["locked"])

    @classmethod
    def on_lock(cls, field, locked=True):
        if not locked:
            field.set_state(Unselected)

class Selected(FieldState):
    @classmethod
    def on_touch_down(cls, field, touch):
        if field.collide_point(*touch.pos):
            # change input state on double tap
            if touch.is_double_tap:
                if field.state == InputNumber:
                    field.set_state(InputCandidates)
                else:
                    field.set_state(InputNumber)
                    
        # only unselect, if touch was in grid
        elif field.parent.collide_point(*touch.pos):
            field.set_state(Unselected)

    @classmethod
    def on_enter(cls, field):
        field.style.push(COLORS["selected"])
        field.parent.selected_field = field
        cls._show_influenced(field, True)

    @classmethod
    def on_exit(cls, field):
        field.style.pop(COLORS["selected"])
        cls._show_influenced(field, False)

    @classmethod
    def _show_influenced(cls, field, show=True):
        for coord in field.sudoku.surrounding_coords(field.coords):
            color = COLORS["influenced"]
            if show:
                field.parent.fields[coord].style.push(color)
            else:
                field.parent.fields[coord].style.pop(color)

    @classmethod
    def on_lock(cls, field, locked=True):
        if locked:
            field.set_state(Locked)

class InputNumber(Selected):
    @classmethod
    def on_input(cls, field, number):
        super(InputNumber, cls).on_input(field, number)
        
        if number in VALID_NUMBERS:
            field.content = number
        else:
            field.content = None
            field.set_state(Unselected)

class InputCandidates(Selected):
    @classmethod
    def on_enter(cls, field):
        super(InputCandidates, cls).on_enter(field)

        if field.content is None or isinstance(field.content, int):
            field.content = list(VALID_NUMBERS)

    @classmethod
    def on_input(cls, field, number):
        if number in VALID_NUMBERS:
            candidates = list(field.content)
            if number in candidates:
                candidates.remove(number)
                field.content = candidates
            else:
                candidates.append(number)
                field.content = candidates
        else:
            field.content = None
            field.set_state(Unselected)
