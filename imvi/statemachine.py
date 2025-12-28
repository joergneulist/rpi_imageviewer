#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from time import sleep

from input import ButtonHandler, KeyboardHandler
from media import FileList
from tools import execute


BTN_STEP = 'step'
BTN_MODE = 'mode'

LONG_HOLD_TIME_SEC = 3


class StateMachine:
    '''State machine for the image viewer

    States are:
    - IDLE: no media loaded
    - VIEW: view images
    - INFO: select from list of images

    State transitions:
    - idle -> viewing: load media
    - viewing -> idle: unload media
    - viewing -> viewing: step button [short press: forward, long press: backward]
    - viewing -> browsing: mode button [short or long press]
    - browsing -> browsing: step button cycles through current depth, mode cycles depth
    - browsing -> viewing: mode button [long press]
    '''
    IDLE = 'idle'
    VIEW = 'view'
    INFO = 'info'
    
    def __init__(self, config):
        self.config = config
        self.files = FileList(config['types'], self.cb_media_update)
        self.state = StateMachine.IDLE

        # register triggers for media control
        self.btn_handlers = {}
        key_handler_config = []
        for button in [BTN_MODE, BTN_STEP]:
            self.btn_handlers[button] = ButtonHandler(self.config['pins'][button], button, self.cb_btn_short, LONG_HOLD_TIME_SEC, self.cb_btn_long)
            key_handler_config += [
                { 'key': self.config['keybindings'][button][0], 'name': button, 'callback': self.cb_btn_short },
                { 'key': self.config['keybindings'][button][1], 'name': button, 'callback': self.cb_btn_long },
            ]
        self.key_handler = KeyboardHandler(key_handler_config)


    def update_view(self):
        if self.state == StateMachine.IDLE:
            print('State: IDLE - no media loaded')
        elif self.state == StateMachine.VIEW:
            current_file = self.files.get_file()
            print(f'State: VIEW - viewing file {self.files.viewed + 1}/{self.files.n}: {current_file}')
        elif self.state == StateMachine.INFO:
            print(f'State: INFO - browsing {self.files.n} files, currently at {self.files.viewed + 1}')
            for file in self.files.files:
                print(f' - {file}')


    def cb_btn_long(self, name, duration):
        print(f'long press: {name} pressed for {duration} seconds')
        if name == BTN_STEP:
            self.files.prev()
        elif name == BTN_MODE:
            if self.state == StateMachine.VIEW:
                self.state = StateMachine.INFO
            elif self.state == StateMachine.INFO:
                self.state = StateMachine.VIEW
        self.update_view()


    def cb_btn_short(self, name, duration):
        print(f'short press: {name} pressed for {duration} seconds')
        if name == BTN_STEP:
            self.files.next()
        elif name == BTN_MODE:
            if self.state == StateMachine.VIEW:
                self.state = StateMachine.INFO
            elif self.state == StateMachine.INFO:
                self.state = StateMachine.VIEW
        self.update_view()


    def cb_media_update(self, count, persistent):
        print(f'media updated: {count} files, persistent={persistent}')
        # Switch state appropriately - unless the currently viewed file is still present:
        if count == 0:
            self.state = StateMachine.IDLE
        else:
            if not persistent:
                self.state = StateMachine.VIEW
