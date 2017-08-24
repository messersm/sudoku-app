#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from sudokutools.sudoku import SudokuWithCandidates, HARD_EXAMPLE, VALID_NUMBERS


class SudokuWidget(BoxLayout):
    pass

class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.sudokus = [SudokuWithCandidates.from_str(HARD_EXAMPLE)]

        self.fields = {}
        self.selected_field = None

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                label = NumberField(coords=(x, y))
                self.add_widget(label)
                self.fields[(x, y)] = label

        self.sudokus[-1].set_candidates((0, 0), *VALID_NUMBERS)
        self.sync_sudoku_to_gui()
        self.lock_filled_fields()

    def current_sudoku(self):
        return self.sudokus[-1]

    def lock_filled_fields(self):
        for x in range(9):
            for y in range(9):
                if self.sudokus[-1][x, y] in VALID_NUMBERS:
                    self.fields[(x, y)].lock()

    def on_touch_down(self, touch):
        for field in self.fields.values():
            if field.collide_point(*touch.pos):
                if self.selected_field:
                    self.selected_field.toggle_select(False)

                if field == self.selected_field:
                    self.selected_field = None
                elif not field.locked:
                    self.selected_field = field
                    field.toggle_select(True)
                else:
                    self.selected_field = None

                # enter candidate edit mode
                if touch.is_double_tap:
                    pass

    def enter_number(self, number):
        print(self.size)

        if self.selected_field:
            coords = self.selected_field.coords
            self.sudokus[-1][coords] = number
            self.sync_sudoku_to_gui()

    def sync_sudoku_to_gui(self):
        sudoku = self.sudokus[-1]

        for x in range(9):
            for y in range(9):
                item = sudoku[x, y]
                if item is None:
                    candidates = sudoku.get_candidates((x, y))
                    if candidates:
                        self.fields[(x, y)].set_candidates(candidates)
                elif item in VALID_NUMBERS or item is None:
                    self.fields[(x, y)].set_number(item)

    def edit_candidates(self):
        pass

    def auto_candidates(self):
        if self.selected_field:
            (x, y) = self.selected_field.coords
            sudoku = self.current_sudoku()
            if sudoku[x, y] is None:
                candidates = sudoku.candidates((x, y))
                sudoku.set_candidates((x, y), *candidates)

            self.sync_sudoku_to_gui()

class NumberField(Label):
    DEFAULT_BGCOLOR = (1, 1, 1, 0)
    LOCKED_BGCOLOR = (0.8, 0.8, 0.8, 0.5)
    SELECTED_BGCOLOR = (0.8, 0.8, 1, 0.5)
    bgcolor = ListProperty(DEFAULT_BGCOLOR)

    DEFAULT_FONT_SIZE = "27sp"
    CANDIDATE_FONT_SIZE = "8sp"

    def __init__(self, coords=(-1, -1), locked=False, **kwargs):
        super(NumberField, self).__init__(**kwargs)
        self.coords = coords
        self.locked = locked

    def lock(self, locked=True):
        self.locked = locked

        if self.locked:
            self.bgcolor = self.LOCKED_BGCOLOR

    def toggle_select(self, selected=True):
        if selected:
            self.bgcolor = self.SELECTED_BGCOLOR
        else:
            self.bgcolor = self.DEFAULT_BGCOLOR

    def set_candidates(self, candidates):
        s = ""
        for n in VALID_NUMBERS:
            if n in candidates:
                s += str(n)
            else:
                s += '  '
            s += ' '
            if n % 3 == 0 and n < 9:
                s += '\n'

        self.font_size = self.CANDIDATE_FONT_SIZE
        self.text = s

    def set_number(self, number):
        self.font_size = self.DEFAULT_FONT_SIZE

        if number is None:
            self.text = ''
        else:
            self.text = str(number)


class SudokuApp(App):
    def build(self):
        return SudokuWidget()

if __name__ == '__main__':
    SudokuApp().run()