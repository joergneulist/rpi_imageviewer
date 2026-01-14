#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from time import sleep

from input import ButtonHandler
from media import FileList


BTN_NEXT = 'next'
BTN_PREV = 'prev'


class StateMachine:
    '''State machine for the image viewer
    
    Full State Machine TODO. Currently, the two buttons just step through the images backwards and forwards.
    '''
    IDLE = 'idle'
    VIEW = 'view'
    INFO = 'info'
    
    def __init__(self, config, framebuffer):
        self.config = config
        self.framebuffer = framebuffer
        self.files = FileList(self.cb_media_update)
        self.state = StateMachine.IDLE
        self.task = None

        # register triggers for media control
        self.btn_handlers = {}
        for button in [BTN_PREV, BTN_NEXT]:
            self.btn_handlers[button] = ButtonHandler(self.config['pins'][button], button, self.cb_btn_short, self.cb_btn_long)


    def update_view(self):
        if self.state == StateMachine.IDLE:
            print('State: IDLE - no media loaded')
        elif self.state == StateMachine.VIEW:
            print(f'State: VIEW - viewing file {self.files.active + 1}/{self.files.n}: {self.files.get_file()}')
            self.files.view(self.framebuffer)


    def cb_btn_long(self, name, duration):
        print(f'long press: {name} pressed for {duration} seconds')
        if name == BTN_NEXT:
            self.files.next()
        elif name == BTN_PREV:
            self.files.prev()
        self.update_view()


    def cb_btn_short(self, name, duration):
        print(f'short press: {name} pressed for {duration} seconds')
        if name == BTN_NEXT:
            self.files.next()
        elif name == BTN_PREV:
            self.files.prev()
        self.update_view()


    def cb_media_update(self, count, persistent):
        print(f'media updated: {count} files, persistent={persistent}')
        # Switch state appropriately - unless the currently viewed file is still present:
        if count == 0:
            self.state = StateMachine.IDLE
        else:
            if self.state == StateMachine.IDLE or not persistent:
                self.state = StateMachine.VIEW
        self.update_view()
