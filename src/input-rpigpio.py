import RPi.GPIO as gpio
from time import time


SHORT_PRESS_TIME = 0.01
LONG_PRESS_TIME = 1.0

class ButtonHandler:
    @staticmethod
    def setup():
        gpio.setmode(gpio.BCM)
    
    def __init__(self, pin, name, cb_short, cb_long=None):
        self.name = name
        self.cb_short = cb_short
        self.cb_long = cb_long
        self.time_pressed = None
        
        gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(pin, gpio.RISING, callback=self._released, bouncetime=SHORT_PRESS_TIME)
        gpio.add_event_detect(pin, gpio.FALLING, callback=self._pressed, bouncetime=SHORT_PRESS_TIME)

    def _pressed(self):
        self.time_pressed = time()

    def _released(self):
        if self.time_pressed is not None:
            held = time() - self.time_pressed
            self.time_pressed = None
            if held >= LONG_PRESS_TIME and self.cb_long is not None:
                self.cb_long(self.name, held)
            else:
                self.cb_short(self.name, held)
