#!/usr/bin/python


from collections import deque
import json
from pathlib import Path
from sys import argv
from time import sleep

from framebuffer import Framebuffer
from statemachine import StateMachine


MEDIA_PATH = Path('/media')

CFG_KEY_PINS = 'pins'


def read_config(path):
    # TODO better encapsulation and validation of config
    with open(path, 'r') as f:
        cfg = json.load(f)
    
    assert CFG_KEY_PINS in cfg
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
    config = read_config(Path(argv[1]))
    print('config:', config)
    
    # set up central state machine
    main = StateMachine(config, Framebuffer())
    
    # This main loop controls watching for file changes. The actual logic is
    # implemented in the State Machine, triggered by the button callbacks.
    filehash = 0
    while True:
        sleep(5)
        files = list(main.files.clean_filelist(gather_files(MEDIA_PATH)))
        new_filehash = hash(frozenset(files))
        if new_filehash != filehash:
            filehash = new_filehash
            print(f'found {len(files)} files, state {filehash}:', files)
            main.files.load(files)
