"""Module that handles abstracted keyboard input.

The ActionManager dispatches events of type 'on_action'.
A action is a simple string, which is dispatched, when certain keyboard
inputs (as defined in KEYBOARD_ACTIONS) are registered.

KEYBOARD_ACTIONS is a a dictionary, which maps (keyname, modifiers) pairs
to action strings. E.g. the entry ("space", ()): "fire" will dispatch a
"fire" action, if space (without modifiers) is pressed.

Simple modify the KEYBOARD_ACTIONS dictionary in oder to change
the app behaviour.

Usage:

First create an ActionManager in your app with:

    class MyApp(App):
        def build(self):
            self.actions = ActionManager()

Then bind your widget (screen, ...) to the 'on_action' events from
the ActionManager:

    class MyWidget(Widget):
        def __init__(self, **kwargs):
            app = App.get_running_app()
            app.actions.bind(on_action=self.on_action)

        def on_action(self, manager, action):
            pass

Note: If you're using screens, please be aware, that actions are send to
all running screens.
"""

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
        """Create a keyboard object and bind the manager to the keyboard.
        """
        super(ActionManager, self).__init__(**kwargs)

        app = App.get_running_app()

        self.keyboard = Window.request_keyboard(
            self.__on_keyboard_closed, app.root, 'text')
        self.keyboard.bind(on_key_down=self.on_keyboard)

    def __on_keyboard_closed(self):
        # Not closing the keyboard - we still need it.
        pass

    def on_keyboard(self, keyboard, keycode, text, modifiers):
        """Dispatch an on_action event,
        if the provided input matches an action in KEYBOARD_ACTIONS.
        """
        keyname = keycode[1]

        name = KEYBOARD_ACTIONS.get((keyname, tuple(modifiers)), None)
        if name:
            self.dispatch('on_action', name)

    def on_action(self, action):
        """default handler (required)"""
        pass
