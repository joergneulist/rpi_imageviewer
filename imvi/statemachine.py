#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from time import sleep

from button import ButtonHandler
from media import FileList
from tools import execute


BTN_STEP = 'step'
BTN_MODE = 'mode'

LONG_HOLD_TIME_SEC = 3


class StateMachine:
    def __init__(self, config):
        self.config = config
        self.files = FileList(config['types'])
        self.state = 'idle'

        # register triggers for media control
        self.btn_mode = ButtonHandler(self.config['pins'][BTN_MODE], BTN_MODE, self.cb_short, LONG_HOLD_TIME_SEC, self.cb_long)
        self.btn_step = ButtonHandler(self.config['pins'][BTN_STEP], BTN_STEP, self.cb_short, LONG_HOLD_TIME_SEC, self.cb_long)


    def cb_long(self, name, duration):
        print(f'long press: {name} pressed for {duration} seconds')


    def cb_short(self, name, duration):
        print(f'short press: {name} pressed for {duration} seconds')
