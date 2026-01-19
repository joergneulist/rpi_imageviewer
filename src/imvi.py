#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from sys import argv, path
from time import sleep

from framebuffer import Framebuffer
from media import FileList
from statemachine import StateMachine
from usbmedia import USBMediaKeeper


CFG_KEY_PINS = 'pins'


def read_config(path):
    # TODO better encapsulation and validation of config
    with open(path, 'r') as f:
        cfg = json.load(f)
    
    assert CFG_KEY_PINS in cfg
    return cfg

class Main():
    def __init__(self, config):
        self.framebuffer = Framebuffer.assign()
        self.files = FileList()
        self.states = StateMachine(config, self.files, self.framebuffer)
        self.watcher = USBMediaKeeper(self.dev_mounted, self.dev_unmounted)
    
    def dev_mounted(self, path):
        directories = deque([path])
        files = []
        while len(directories):
            dir = directories.popleft()
            for node in dir.iterdir():
                if node.is_dir():
                    directories.append(node)
                else:
                    files.append(node)
        self.files.load(path, files)

    def dev_unmounted(self, path):
        self.files.unload(path)


if __name__ == '__main__':
    config = read_config(Path(argv[1]))
    print('config:', config)
    
    # set up central object
    main = Main(config)

    # This main loop does nothing. All the work is triggered by callbacks on buttons and udev events.
    while True:
        sleep(5)