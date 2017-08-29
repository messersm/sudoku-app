#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard imports
from random import choice
from os.path import join

# kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout



# needed by sudoku.kv
from sudokulib.grid import SudokuGrid

STATEFILE = "state.json"

class SudokuWidget(BoxLayout):
    grid = ObjectProperty(None)
    menu = ObjectProperty(None)
    info_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SudokuWidget, self).__init__(**kwargs)

        # Add hardware keyboard support
        self.__keyboard = Window.request_keyboard(
            self.__on_keyboard_closed, self, 'text')

        if self.__keyboard.widget:
            # This is a virtual keyboard - throw it away
            self.__keyboard.release()
        else:
            self.__keyboard.bind(on_key_down=self.__on_keyboard_down)

        self.KEYS = {}
        for i in range(10):
            self.KEYS["%d" % i] = i
            self.KEYS["numpad%d" % i] = i

        self.KEYS["backspace"] = 0
        self.KEYS["delete"] = 0

    def __on_keyboard_closed(self):
        self.__keyboard.unbind(on_key_down=self.__on_keyboard_down)
        self.__keyboard = None

    def __on_keyboard_down(self, keyboard, keycode, text, modifiers):
        keyname = keycode[1]
        input = self.KEYS.get(keyname, None)
        if input is not None:
            self.grid.enter_number(input)

    def save_state(self, filename=STATEFILE):
        self.grid.save_state(filename=filename)

    def handle_button_input(self, btn, text):
        pass

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
