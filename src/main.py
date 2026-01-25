#!/usr/bin/python3

# 1. CLEAN UP EVENT QUEUE HANDLER - SMALLER FUNCTIONS, CLEARER RESPONSIBILITY
# 2. REFACTOR RESPONSIBILITIES OF SUBCLASSES - DO WE NEED MEDIA HANDLER STILL?
# 3. MAKE CACHE HANDLING EXPLICIT, AND ABLE TO KEEP INTERNAL SCREENS IN MEMORY, WHILE OPTIMIZING DISPLAY FOR EVERYTHING ELSE
# 4. ADD WAITING SCREEN
# 5. EVALUATE ABILITY FOR GIF ANIMATIONS
# 6. ADD TEXT RENDERING FOR WAITING SCREENS
# 8. PEP8 - STRICT TYPING, FORMATTING, ETC.

import argparse
import json
from pathlib import Path

from eventqueue import EventQueue, BTN_NEXT, BTN_PREV
from framebuffer import Framebuffer
from images import ImageEntry


CFG_KEY_PINS = 'pins'
MY_NAME = 'IMVI - Python Image Viewer for Embedded Systems'
PATH_ASSETS = Path(__file__).parents[0] / 'assets'
PATH_CONFIG = Path('/etc/imvi')


def parse_args():
    parser = argparse.ArgumentParser(description=MY_NAME)
    parser.add_argument('-c', '--config', help='Override path to config file',
                        default=PATH_CONFIG / 'imvi.json')
    parser.add_argument('-p', '--path', action='append', help='Add a file path to display; can be named multiple times', default=[])
    parser.add_argument('-s', '--splash', help='Splash image to display on startup. Specifiying something that is not a valid image file will disable splash',
                        default=PATH_ASSETS / 'logo.png')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    return args


def read_config(path, verbose=False):
    if verbose:
        print('config:', args.config)
    with open(path, 'r') as f:
        cfg = json.load(f)
    if verbose:
        print(cfg)
    assert CFG_KEY_PINS in cfg
    return cfg


def get_framebuffer(verbose=False):
    framebuffer = Framebuffer.assign()
    if verbose:
        print(framebuffer)

    return framebuffer

def get_gpio_driver(config, verbose=False):
    try:
        from input import ButtonHandler
        handlers = {}
        for button in [BTN_PREV, BTN_NEXT]:
            handlers[button] = ButtonHandler(config[button], button)
            if verbose:
                print(handlers[button])
        return handlers
    except Exception as ex:
        if verbose:
            print('GPIO-Handlers failed!')
            print(ex, repr(ex))


def load_splash(path, fb, verbose=False):
    if verbose:
        print(f'splash {path}')
    if ImageEntry.is_valid_img(path):
        img = ImageEntry(None, path)
        print('...is valid')
        fb.load(img)
        print('...is loaded')
        fb.show(img)
        print('...is shown')
        return img


if __name__ == '__main__':
    print(MY_NAME)
    args = parse_args()
    cfg = read_config(Path(args.config), args.verbose)
    fb = get_framebuffer(args.verbose)
    btn = get_gpio_driver(cfg[CFG_KEY_PINS], args.verbose)
    splash = load_splash(Path(args.splash), fb, args.verbose)

    # set up central object
    eq = EventQueue(fb, btn, splash, args.verbose)
    
    # preload image files given as parameter
    for path in args.path:
        eq.cb_dev_mounted(Path(path))

    # Enter the main loop
    eq.loop()
