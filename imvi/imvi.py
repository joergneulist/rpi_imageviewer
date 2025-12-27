#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from time import sleep

from statemachine import StateMachine


MEDIA_PATH = Path('/media')
CONFIG_PATH = Path('etc/config.json')


CFG_KEY_PINS = 'pins'
CFG_KEY_TYPES = 'types'
CFG_KEY_VIEW = 'view'


def read_config(path):
    # TODO better encapsulation and validation of config
    with open(path, 'r') as f:
        cfg = json.load(f)
    
    assert CFG_KEY_PINS in cfg
    assert CFG_KEY_TYPES in cfg
    assert CFG_KEY_VIEW in cfg
    
    return cfg


def gather_files(path):
    directories = deque([path])
    files = []
    while len(directories):
        dir = directories.popleft()
        for node in dir.iterdir():
            if node.is_dir():
                directories.append(node)
            else:
                files.append(node)
    return files


if __name__ == '__main__':
    config = read_config(CONFIG_PATH)
    print('config:', config)
    
    # set up central state machine
    main = StateMachine(config)
    
    # This main loop controls watching for file changes. The actual logic is
    # implemented in the State Machine, triggered by the button callbacks.
    filestate = 0
    while True:
        sleep(5)
        files = list(main.files.clean_filelist(gather_files(MEDIA_PATH)))
        new_filestate = hash(frozenset(files))
        if new_filestate != filestate:
            filestate = new_filestate
            print(f'found {len(files)} files, state {filestate}:', files)
            main.files.load(files)
    
    print('exiting imvi main loop')
