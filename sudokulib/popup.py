from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class CallbackPopup(Popup):
    def __init__(self, text='', callbacks=list(), **kwargs):
        super(CallbackPopup, self).__init__(**kwargs)

        buttons = BoxLayout(orientation="horizontal", size_hint_y=0.2)
        for (btn_text, callback) in callbacks:
            btn = Button(text=btn_text)
            btn.callback = callback
            btn.bind(on_release=self.__run_callback)
            buttons.add_widget(btn)

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text=text, size_hint_y=0.8))
        layout.add_widget(buttons)

        self.add_widget(layout)

    def __run_callback(self, btn):
        btn.callback()
        self.dismiss()