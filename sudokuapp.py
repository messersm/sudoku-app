#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports

from random import choice

from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from sudokutools.examples import EXAMPLES
from sudokutools.sudoku import SudokuWithCandidates, VALID_NUMBERS

HARD_EXAMPLE = EXAMPLES[1][0]

from sudokulib.numberfield import NumberField
from sudokulib.fieldstate import Locked

class SudokuWidget(BoxLayout):
    pass

class WinPopup(Popup):
    grid = ObjectProperty(None)

class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.sudoku_won = False
        self.sudoku = None
        self.fields = {}
        self.selected_field = None

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                label = NumberField(coords=(x, y))
                self.add_widget(label)
                self.fields[(x, y)] = label

        self.new_sudoku()

    def sudoku_complete(self):
        if self.sudoku_won:
            return

        self.sudoku_won = True
        winpopup = WinPopup()
        winpopup.grid = self
        winpopup.open()

    # TODO: Move this code to sudokutools
    def check_complete(self):
        if self.sudoku.empty_coords():
            return False

        if self.sudoku.find_all_conflicts():
            return False

        return True

    def clear(self):
        for field in self.fields.values():
            if field.state != Locked:
                field.content = None

    def new_sudoku(self):
        self.sudoku_won = False

        if self.sudoku:
            self.lock_filled_fields(False)
        example = choice(EXAMPLES)[0]
        self.sudoku = SudokuWithCandidates.from_str(example)
        self.lock_filled_fields()
        self.sync_sudoku_to_gui()

    def enter_number(self, number):
        if self.selected_field:
            self.selected_field.input(number)

        if self.check_complete():
            self.sudoku_complete()

    def push_style(self, style, *coords):
        """Pushes a background style to all given coordinates."""

        for coord in coords:
            self.fields[coords].push(style)

    def pop_style(self, style, *coords):
        for coord in coords:
            self.fields[coords].pop(style)

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
                    candidates = self.sudoku.get_candidates((x, y))
                    self.fields[(x, y)].content = candidates
                elif item in VALID_NUMBERS or item is None:
                    self.fields[(x, y)].content = item

    def auto_candidates(self):
        if self.selected_field:
            field = self.selected_field
            candidates = self.sudoku.candidates(field.coords)
            field.content = candidates

    def solve(self):
        self.sudoku.solve()
        self.sync_sudoku_to_gui()

        if self.check_complete():
            self.sudoku_complete()

    def solve_field(self):
        if self.selected_field:
            self.sudoku.solve_field(self.selected_field.coords)
            self.sync_sudoku_to_gui()

        if self.check_complete():
            self.sudoku_complete()

class SudokuApp(App):
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')
    
    def build(self):
        return SudokuWidget()

if __name__ == '__main__':
    SudokuApp().run()
