#!/usr/bin/python3

# EVALUATE CACHE STRATEGIES
# ADD OVERVIEW MODE

import argparse
from collections import deque
import json
from pathlib import Path
from sys import argv, path
from time import sleep, time

from framebuffer import Framebuffer, get_size
from media import FileList
from usbmedia import USBMediaKeeper


CFG_KEY_PINS = 'pins'
BTN_NEXT = 'next'
BTN_PREV = 'prev'
MY_NAME = 'IMVI - Python Image Viewer for Embedded Systems'

EVT_BUTTON = 'button'
EVT_BUTTON_LONG = 'long'
EVT_BUTTON_SHORT = 'short'

EVT_MEDIA = 'media'
EVT_MEDIA_LOAD = 'load'
EVT_MEDIA_UNLOAD = 'unload'

EVT_IMAGE = 'image'
EVT_IMAGE_TRIGGER = 'trigger'
EVT_IMAGE_READY = 'ready'

EVT_Q_EVT = 'evt'
EVT_Q_TYPE = 'type'
EVT_Q_PARAMS = 'params'


def parse_args():
    parser = argparse.ArgumentParser(description=MY_NAME)
    parser.add_argument('-c', '--config', help='Override path to config file', default='/etc/imvi/imvi.json')
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug mode: implies -v, suppresses actual framebuffer output')
    parser.add_argument('-p', '--path', action='append', help='Add a file path to display; can be named multiple times', default=[])
    parser.add_argument('-s', '--splash', help='Splash image to display on startup. Specifiying something that is not a valid image file will disable splash',
                        default=Path(__file__).parents[0] / 'assets/logo.png')
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
        self.event_queue = deque()
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
            if self.verbose:
                print('GPIO-Handlers failed!')
    
    def add_event(self, event, evtype, *evparams):
        if self.verbose:
            print(f'{time()} EVENTLOOP received event {event}: {evtype} with parameters {evparams}')
        self.event_queue.append({EVT_Q_EVT: event, EVT_Q_TYPE: evtype, EVT_Q_PARAMS: evparams})


    def get_event(self):
        if len(self.event_queue) == 0:
            return None, None, None
        evt = self.event_queue.popleft()
        if self.verbose:
            print(f'{time()} EVENTLOOP process event {evt[EVT_Q_EVT]}: {evt[EVT_Q_TYPE]} with parameters {evt[EVT_Q_PARAMS]}')
        return evt[EVT_Q_EVT], evt[EVT_Q_TYPE], evt[EVT_Q_PARAMS]


    def update_view(self):
        if self.verbose: print('update view')
        self.fileTracker.view(self.framebuffer)


    def loop(self):
        bored_since = time()
        while True:
            event, evtype, evparams = self.get_event()
            
            if event is None:
                # debug mode: simulate button inputs
                if self.btn_handlers is None and time() - bored_since > 10.0:
                    self.add_event(EVT_BUTTON, EVT_BUTTON_SHORT, BTN_NEXT)                    
                    bored_since = time()
                # empty queue -> let's catch up on sleep!
                sleep(0.1)
            
            elif event == EVT_BUTTON:
                if evparams[0] == BTN_NEXT:
                    self.fileTracker.next()
                elif evparams[0] == BTN_PREV:
                    self.fileTracker.prev()
                self.add_event(EVT_IMAGE, EVT_IMAGE_TRIGGER, self.fileTracker.get_file())
            
            elif event == EVT_IMAGE:
                if evtype == EVT_IMAGE_TRIGGER:
                    if len(evparams) == 0:
                        # TODO display waiting splash
                        pass
                    imgBitmap = self.framebuffer.prepare(evparams[0])
                    self.add_event(EVT_IMAGE, EVT_IMAGE_READY, imgBitmap)
                elif evtype == EVT_IMAGE_READY:
                    # TODO add caching
                    # TODO put image conversion in separate thread
                    self.framebuffer.show(evparams[0])
                else:
                    raise NotImplementedError(f'illegal event {event}: {evtype}, {evparams}')
            
            elif event == EVT_MEDIA:
                if evtype == EVT_MEDIA_LOAD:
                    self.fileTracker.load(evparams[0])
                    # TODO don't switch view if not necessary!
                    self.add_event(EVT_IMAGE, EVT_IMAGE_TRIGGER, self.fileTracker.get_file())
                elif evtype == EVT_MEDIA_UNLOAD:
                    self.fileTracker.unload(evparams[0])
                    # TODO don't switch view if not necessary!
                    self.add_event(EVT_IMAGE, EVT_IMAGE_TRIGGER, self.fileTracker.get_file())
                else:
                    raise NotImplementedError(f'illegal event {event}: {evtype}, {evparams}')

            else:
                raise NotImplementedError(f'illegal event {event}: {evtype}, {evparams}')
        

    def cb_btn_long(self, name):     self.add_event(EVT_BUTTON, EVT_BUTTON_LONG,  name)
    def cb_btn_short(self, name):    self.add_event(EVT_BUTTON, EVT_BUTTON_SHORT, name)
    def cb_dev_mounted(self, path):  self.add_event(EVT_MEDIA,  EVT_MEDIA_LOAD,   path)
    def cb_dev_unmounted(self, path):self.add_event(EVT_MEDIA,  EVT_MEDIA_UNLOAD, path)


if __name__ == '__main__':
    args = parse_args()
    config = read_config(Path(args.config))
    print(MY_NAME)
    print('config:', args.config)
    print(config)
    
    # load splash image
    fb = Framebuffer.assign(0, args.debug)
    splash = Path(args.splash)
    if FileList.is_valid(splash):
        buffer = fb.prepare(splash)
        fb.show(buffer)

    # set up central object
    main = StateMachine(config, fb, args.verbose)
    
    # preload image files given as parameter
    for path in args.path:
        main.cb_dev_mounted(Path(path))

    # Enter the main loop
    main.loop()
