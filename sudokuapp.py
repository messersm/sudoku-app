#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
from random import choice
from os.path import join

# kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

# local imports
from sudokulib.grid import SudokuGrid

STATEFILE = "state.json"


class SudokuWidget(BoxLayout):
    grid = ObjectProperty(None)
    menu = ObjectProperty(None)
    info_label = ObjectProperty(None)

    def save_state(self, filename=STATEFILE):
        self.grid.save_state(filename=filename)


class SudokuApp(App):
    def build(self):
        self.sudoku_widget = SudokuWidget()
        self.statefilename = join(self.user_data_dir, STATEFILE)
        return self.sudoku_widget

    def on_pause(self):
        self.sudoku_widget.save_state(self.statefilename)
        return True

    def on_stop(self):
        self.sudoku_widget.save_state(self.statefilename)

if __name__ == '__main__':
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')

    SudokuApp().run()
