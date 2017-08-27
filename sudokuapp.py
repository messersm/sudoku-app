#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
from random import choice

# kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore

STATEFILE = "state.json"

# local imports
from sudokulib.numberfield import NumberField
from sudokulib.fieldstate import Locked

from sudokutools.examples import EXAMPLES
from sudokutools.sudoku import SudokuWithCandidates, VALID_NUMBERS


class SudokuWidget(BoxLayout):
    grid = ObjectProperty(None)
    menu = ObjectProperty(None)
    info_label = ObjectProperty(None)

    def save_state(self, filename=STATEFILE):
        self.grid.save_state(filename=filename)

class WinPopup(Popup):
    grid = ObjectProperty(None)


class CustomErrorPopup(Popup):
    grid = ObjectProperty(None)


class CustomWarningPopup(Popup):
    grid = ObjectProperty(None)


class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        self.sudoku_won = False
        self.sudoku = None
        self.orig = None
        self.fields = {}
        self.selected_field = None

        self.__in_edit_custom = False

        # mind the order here - it's important
        for y in range(9):
            for x in range(9):
                label = NumberField(coords=(x, y))
                self.add_widget(label)
                self.fields[(x, y)] = label

        self.restore_state()
        if not self.sudoku:
            self.new_sudoku()

    def edit_custom_sudoku(self):
        if self.__in_edit_custom:
            self.check_edit_custom_sudoku()
        else:
            self.begin_edit_custom_sudoku()

    def begin_edit_custom_sudoku(self):
        self.__in_edit_custom = True

        if self.sudoku:
            self.lock_filled_fields(False)

        self.sudoku = SudokuWithCandidates()
        self.sync_sudoku_to_gui()

    def check_edit_custom_sudoku(self):
        ret = self.sudoku.is_unique()

        if ret is None:
            error = CustomErrorPopup()
            error.grid = self
            error.open()
        elif ret is False:
            warning = CustomWarningPopup()
            warning.grid = self
            warning.open()
        elif ret is True:
            self.end_edit_custom_sudoku()

    def end_edit_custom_sudoku(self):
        self.__in_edit_custom = False
        self.lock_filled_fields(True)
        self.orig = self.sudoku.copy()

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
        self.orig = self.sudoku.copy()
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

    def save_state(self, filename=STATEFILE):
        if self.sudoku:
            store = JsonStore(filename)
            current_str = self.sudoku.to_str(row_sep='', column_sep='')
            orig_str = self.orig.to_str(row_sep='', column_sep='')
            store.put('sudoku', orig=orig_str, current=current_str)

        print('save called')

    def restore_state(self, filename=STATEFILE):
        store = JsonStore(filename)
        if 'sudoku' in store:
            self.orig = SudokuWithCandidates.from_str(store['sudoku']['orig'])
            self.sudoku = self.orig
            self.lock_filled_fields()
            self.sudoku = SudokuWithCandidates.from_str(store['sudoku']['current'])
            self.sync_sudoku_to_gui()

        print("restore called")


class SudokuApp(App):
    def build(self):
        self.sudoku_widget = SudokuWidget()
        return self.sudoku_widget

    def on_pause(self):
        self.sudoku_widget.save_state(filename=STATEFILE)

    def on_stop(self):
        self.sudoku_widget.save_state(filename=STATEFILE)

    def on_resume(self):
        self.sudoku_widget.info_label.text = "Debug: Resumed from on_pause()."

if __name__ == '__main__':
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')

    app = SudokuApp()

    try:
        app.run()
    except:
        # try to save some state, if possible.
        app.on_stop()
        raise
