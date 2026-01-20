#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from sys import argv, path
from time import sleep

from framebuffer import Framebuffer
from input import ButtonHandler
from media import FileList
from usbmedia import USBMediaKeeper


CFG_KEY_PINS = 'pins'
BTN_NEXT = 'next'
BTN_PREV = 'prev'


def read_config(path):
    # TODO better encapsulation and validation of config
    with open(path, 'r') as f:
        cfg = json.load(f)
    
    assert CFG_KEY_PINS in cfg
    return cfg


class StateMachine:
    '''State machine for the image viewer
    
    Full State Machine TODO. Currently, the two buttons just step through the images backwards and forwards.
    '''
    IDLE = 'idle'
    VIEW = 'view'
    INFO = 'info'
    
    def __init__(self, config):
        self.config = config
        self.framebuffer = Framebuffer.assign()
        self.fileTracker = FileList()
        self.usbWatcher = USBMediaKeeper(self.cb_dev_mounted, self.cb_dev_unmounted)
        self.task = None

        # register triggers for media control
        self.btn_handlers = {}
        for button in [BTN_PREV, BTN_NEXT]:
            self.btn_handlers[button] = ButtonHandler(self.config['pins'][button], button, self.cb_btn_short, self.cb_btn_long)


    def update_view(self):
        print(f'Viewing file {self.fileTracker.active + 1}: {self.fileTracker.get_file()}')
        self.fileTracker.view(self.framebuffer)


    def cb_btn_long(self, name, duration):
        if name == BTN_NEXT:
            self.fileTracker.next()
        elif name == BTN_PREV:
            self.fileTracker.prev()
        self.update_view()


    def cb_btn_short(self, name, duration):
        if name == BTN_NEXT:
            self.fileTracker.next()
        elif name == BTN_PREV:
            self.fileTracker.prev()
        self.update_view()

    
    def cb_dev_mounted(self, path):
        directories = deque([path])
        files = []
        while len(directories):
            dir = directories.popleft()
            for node in dir.iterdir():
                if node.is_dir():
                    directories.append(node)
                else:
                    files.append(node)
        self.fileTracker.load(path, files)
        self.update_view()


    def cb_dev_unmounted(self, path):
        self.fileTracker.unload(path)
        self.update_view()


if __name__ == '__main__':
    config = read_config(Path(argv[1] if len(argv) > 1 else 'config.json'))
    print('config:', config)
    
    # set up central object
    main = StateMachine(config)

    # This main loop does nothing. All the work is triggered by callbacks on buttons and udev events.
    while True:
        sleep(5)