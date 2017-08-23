#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivy.properties import ListProperty

from kivy.graphics import Color, Line, Rectangle

class SudokuWidget(BoxLayout):
    pass

class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super(SudokuGrid, self).__init__(rows=9, cols=9)

        for x in range(9):
            for y in range(9):
                self.add_widget(NumberLabel(text="%d" % ((x + y) % 9 + 1)))

class NumberLabel(Label):
    DEFAULT_BGCOLOR = (1, 1, 1, 0)
    PROTECTED_BGCOLOR = (0.8, 0.8, 0.8, 0.5)
    SELECTED_BGCOLOR = (0.8, 0.8, 1, 0.5)

    bgcolor = ListProperty(DEFAULT_BGCOLOR)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # enter cadidate editor
            if touch.is_double_tap:
                pass
            else:
                self.bgcolor = self.SELECTED_BGCOLOR
            return True

class SudokuApp(App):
    def build(self):
        return SudokuWidget()

if __name__ == '__main__':
    SudokuApp().run()