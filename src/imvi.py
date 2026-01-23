#!/usr/bin/python

# EVALUATE CACHE STRATEGIES
# ADD OVERVIEW MODE

import argparse
from collections import deque
import json
from pathlib import Path
from sys import argv, path
from time import sleep

from framebuffer import Framebuffer, get_size
from media import FileList
from usbmedia import USBMediaKeeper


CFG_KEY_PINS = 'pins'
BTN_NEXT = 'next'
BTN_PREV = 'prev'
MY_NAME = 'IMVI - Python Image Viewer for Embedded Systems'

def parse_args():
    parser = argparse.ArgumentParser(description=MY_NAME)
    parser.add_argument('-c', '--config', help='Override path to config file', default='/etc/imvi.json')
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug mode: implies -v, suppresses actual framebuffer output')
    parser.add_argument('-p', '--path', action='append', help='Add a file path to display; can be named multiple times', default=[])
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    args.verbose = args.debug or args.verbose
    return args


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
    def __init__(self, config, framebuffer, verbose=False):
        self.config = config
        self.verbose = verbose
        self.fileTracker = FileList()
        self.framebuffer = framebuffer
        if self.verbose: print(self.framebuffer)
        self.usbWatcher = USBMediaKeeper(self.cb_dev_mounted, self.cb_dev_unmounted)
        if self.verbose: print(self.usbWatcher)

        # register triggers for media control
        try:
            from input import ButtonHandler
            self.btn_handlers = {}
            for button in [BTN_PREV, BTN_NEXT]:
                self.btn_handlers[button] = ButtonHandler(self.config['pins'][button], button, self.cb_btn_short, self.cb_btn_long)
                if self.verbose: print(self.btn_handlers[button])
        except Exception:
            self.btn_handlers = None
            if self.verbose: print('GPIO-Handlers failed!')


    def update_view(self):
        if self.verbose: print('update view')
        self.fileTracker.view(self.framebuffer)


    def cb_btn_long(self, name):
        if self.verbose: print(f'long press {name}')
        if name == BTN_NEXT:
            self.fileTracker.next()
        elif name == BTN_PREV:
            self.fileTracker.prev()
        self.update_view()


    def cb_btn_short(self, name):
        if self.verbose: print(f'short press {name}')
        if name == BTN_NEXT:
            self.fileTracker.next()
        elif name == BTN_PREV:
            self.fileTracker.prev()
        self.update_view()


    def cb_dev_mounted(self, path):
        if self.verbose: print(f'usb device mounted on {path}')
        directories = deque([path])
        files = []
        while len(directories):
            curdir = directories.popleft()
            for node in curdir.iterdir():
                if node.is_dir():
                    directories.append(node)
                else:
                    files.append(node)
        self.fileTracker.load(path, files)
        self.update_view()


    def cb_dev_unmounted(self, path):
        if self.verbose: print(f'usb device {path} unmounted')
        self.fileTracker.unload(path)
        self.update_view()


if __name__ == '__main__':
    args = parse_args()
    config = read_config(Path(args.config))
    print(MY_NAME)
    print('config:', args.config)
    print(config)
    
    # set up central object
    main = StateMachine(config, Framebuffer.assign(0, args.debug), args.verbose)
    for path in args.path:
        main.cb_dev_mounted(Path(path))

    # This main loop does nothing. All the work is triggered by callbacks on buttons and udev events inside the state machine.
    while True:
        if main.verbose:
            with open('/proc/meminfo', 'r') as memory:
                use = {'MemTotal:': 'total', 'MemAvailable:': 'free'}
                for line in memory:
                    tokens = line.split()
                    if tokens[0] in use:
                        print(f'{use[tokens[0]]}: {get_size(int(tokens[1])*1024)}')

        # simulate gpio buttons for testing purposes
        input()
        main.cb_btn_short(BTN_NEXT)