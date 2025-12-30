from gpiozero import Button
from time import time


SHORT_PRESS_TIME = 0.1
LONG_PRESS_TIME = 1.0

class ButtonHandler:
    def __init__(self, gpio, name, cb_short, cb_long=None):
        self.name = name
        self.cb_short = cb_short
        self.cb_long = cb_long
        self.time_pressed = None
        
        self.btn = Button(
            gpio,
            bounce_time=SHORT_PRESS_TIME,
            hold_time = LONG_PRESS_TIME)
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
