from gpiozero import Button
from time import sleep, time


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
            self.time_pressed = False
    
    def _pressed(self):
        self.time_pressed = time()

    def _released(self):
        if self.time_pressed is not None:
            self.cb_short(self.name, time() - self.time_pressed)
            self.time_pressed = None


def cb_long(name, duration):
    print(f'long press: {name} pressed for {duration} seconds')

def cb_short(name, duration):
    print(f'short press: {name} pressed for {duration} seconds')


a = ButtonHandler(2, 'step', cb_short, 3, cb_long)
b = ButtonHandler(3, 'mode', cb_short, 3, cb_long)
input()
