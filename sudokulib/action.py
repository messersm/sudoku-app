# -*- coding: utf-8 -*-

from collections import namedtuple

from kivy.app import App
from kivy.event import EventDispatcher
from kivy.core.window import Window

KEYBOARD_ACTIONS = {
    ("numpad0", ()): "0",
    ('numpad1', ()): "1",
    ('numpad2', ()): "2",
    ('numpad3', ()): "3",
    ('numpad4', ()): "4",
    ('numpad5', ()): "5",
    ('numpad6', ()): "6",
    ('numpad7', ()): "7",
    ('numpad8', ()): "8",
    ('numpad9', ()): "9",

    ('0', ()): "0",
    ('1', ()): "1",
    ('2', ()): "2",
    ('3', ()): "3",
    ('4', ()): "4",
    ('5', ()): "5",
    ('6', ()): "6",
    ('7', ()): "7",
    ('8', ()): "8",
    ('9', ()): "9",

    ('backspace', ()): "delete",
    ('delete', ()): "delete",
    ('numpadenter', ()): "confirm",
    ('enter', ()): "confirm",

    ('right', ()): "next_field",
    ('left', ()): "prev_field",
    ('down', ()): "next_row",
    ('up', ()): 'prev_row',
}


class ActionManager(EventDispatcher):
    __events__ = ('on_action', )

    def __init__(self, **kwargs):
        super(ActionManager, self).__init__(**kwargs)

        app = App.get_running_app()

        self.keyboard = Window.request_keyboard(
            self.__on_keyboard_closed, app.root, 'text')
        self.keyboard.bind(on_key_down=self.on_keyboard)

    def __on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard)
        self.keyboard = None

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        keyname = keycode[1]

        name = KEYBOARD_ACTIONS.get((keyname, tuple(modifiers)), None)
        if name:
            self.dispatch('on_action', name)

    def on_action(self, action):
        """default handler (required)"""
        pass
