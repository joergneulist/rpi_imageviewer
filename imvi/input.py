from gpiozero import Button
from time import time
from pynput import keyboard


class ButtonHandler:
    def __init__(self, gpio, name, cb_short, hold=3, cb_long=None):
        self.name = name
        self.cb_short = cb_short
        self.cb_long = cb_long
        self.time_pressed = None
        
        self.btn = Button(gpio, bounce_time=0.1, hold_time = hold)
        self.btn.when_held = self._held
        self.btn.when_pressed = self._pressed
        self.btn.when_released = self._released

    def _held(self):
        if self.time_pressed is not None:
            self.cb_long(self.name, time() - self.time_pressed)
            self.time_pressed = None

    def _pressed(self):
        self.time_pressed = time()

    def _released(self):
        if self.time_pressed is not None:
            self.cb_short(self.name, time() - self.time_pressed)
            self.time_pressed = None


class KeyboardHandler:
    def __init__(self, handler_list):
        self.listener = keyboard.Listener(on_press=self.key_event)
        self.keys = {}
        for handler in handler_list:
            key = handler.key
            if len(handler.key) > 1:
                key = getattr(keyboard.Key, handler['key'])
            self.keys[key] = { 'name': handler['name'], 'cb': handler['callback'] }
                

    def key_event(self, key):
        if key in self.keys:
            self.keys[key]['cb'](self.keys[key]['name'], 0)
