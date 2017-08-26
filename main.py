#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
from functools import wraps
from collections import namedtuple

from kivy.app import App
from kivy.config import Config
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from sudokutools.sudoku import SudokuWithCandidates, \
    HARD_EXAMPLE, VALID_NUMBERS

from numberfield import NumberField

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

        self.sync_sudoku_to_gui()
        self.lock_filled_fields()

    def enter_number(self, number):
        if self.selected_field:
            self.selected_field.input(number)

    def push_style(self, style, *coords):
        """Pushes a background style to all given coordinates."""

        for coord in coords:
            self.fields[coords].push(style)

    def pop_style(self, style, *coords):
        for coord in coords:
            self.fields[coords].pop(style)

    @property
    def sudoku(self):
        return self.sudokus[-1]

    def lock_filled_fields(self):
        for x in range(9):
            for y in range(9):
                if self.sudokus[-1][x, y] in VALID_NUMBERS:
                    self.fields[(x, y)].lock()

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

    def solve_field(self):
        if self.selected_field:
            self.sudoku.solve_field(self.selected_field.coords)
            self.sync_sudoku_to_gui()

class SudokuApp(App):
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')
    
    def build(self):
        return SudokuWidget()

if __name__ == '__main__':
    SudokuApp().run()
