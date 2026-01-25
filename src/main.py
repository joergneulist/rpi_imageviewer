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

from eventqueue import EventQueue
from framebuffer import Framebuffer


CFG_KEY_PINS = 'pins'
MY_NAME = 'IMVI - Python Image Viewer for Embedded Systems'
PATH_ASSETS = Path(__file__).parents[0] / 'assets'
PATH_CONFIG = Path('/etc/imvi')


def parse_args():
    parser = argparse.ArgumentParser(description=MY_NAME)
    parser.add_argument('-c', '--config', help='Override path to config file',
                        default=PATH_CONFIG / 'imvi.json')
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug mode: implies -v, suppresses actual framebuffer output')
    parser.add_argument('-p', '--path', action='append', help='Add a file path to display; can be named multiple times', default=[])
    parser.add_argument('-s', '--splash', help='Splash image to display on startup. Specifiying something that is not a valid image file will disable splash',
                        default=PATH_ASSETS / 'logo.png')
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


def load_splash(fb, path):
    if fb.is_valid_img(path):
        buffer = fb.load(path)
        fb.show(buffer)
    

if __name__ == '__main__':
    args = parse_args()
    config = read_config(Path(args.config))
    print(MY_NAME)
    print('config:', args.config)
    print(config)
    
    # Create framebuffer adapter
    fb = Framebuffer.assign(0, args.debug)
    if args.verbose:
        print(fb)

    # Load splash image
    load_splash(fb,  Path(args.splash))

    # set up central object
    eq = EventQueue(config, fb, args.verbose)
    
    # preload image files given as parameter
    for path in args.path:
        eq.cb_dev_mounted(Path(path))

    # Enter the main loop
    eq.loop()
