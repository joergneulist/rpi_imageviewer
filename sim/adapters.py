from collections import deque
from pathlib import Path
from threading import Lock, Thread
from time import sleep, time

from eventqueue import Event, EventEntry, EventQueue, BTN_NEXT, BTN_PREV
from framebuffer import Framebuffer
from images import ImageEntry


BTN_MOUNT = 'mount'
BTN_UMOUNT = 'unmount'
FB_TAG = 'kivy'
SIZE = (1024, 640)
SPLASH_PATH = Path(__file__).parents[1] / 'assets' / 'logo.png'


class FramebufferKivy(Framebuffer):
    def __init__(self, msg_queue):
        super().__init__(FB_TAG, SIZE)
        self.msg_queue = msg_queue
    
    def _encode(self, image):
        return image

    def _show(self, image_data):
        print(f'Displaying buffer {image_data.filepath}: {image_data.buffer is not None}')
        self.msg_queue.send(image_data.buffer)


class ButtonKivy:
    LONG_PRESS_TIME = 1.0

    def __init__(self, name, cb_short=None, cb_long=None):
        self.name = name
        self.cb_short = cb_short
        self.cb_long = cb_long
        self.time_pressed = None
            
    def set_callbacks(self, cb_short, cb_long=None):
        self.cb_short = cb_short
        self.cb_long = cb_long

    def __str__(self):
        return f'{str(type(self))}: {self.name} (GPIO {self.btn.pin})'

    def _pressed(self):
        self.time_pressed = time()

    def _released(self):
        if self.time_pressed is not None:
            if time() - self.time_pressed > self.LONG_PRESS_TIME:
                self.cb_long(self.name)
            else:
                self.cb_short(self.name)
            self.time_pressed = None


class ThreadMessageQueue(deque):
    def __init__(self, name, verbose=False):
        self.name = name
        self.verbose = verbose
        self.lock = Lock()
        self.callback = None
    
    def set_flag_callback(self, callback):
        self.callback = callback
    
    def send(self, message):
        with self.lock:
            self.append(message)
        if self.verbose:
            print(f'[{self.name}]  {type(message)} entered into queue')
            if issubclass(type(message), dict):
                print(message)
        if self.callback is not None:
            if self.verbose:
                print('notifying main thread')
            self.callback()
    
    def recv(self):
        with self.lock:
            if len(self) > 0:
                message = self.popleft()
                if self.verbose:
                    print(f'[{self.name}] received from queue')
                    if issubclass(type(message), dict):
                        print(message)
                return message


class IMVIAdapter(Thread):
    def __init__(self):
        super().__init__()
        self.msg_in = ThreadMessageQueue('main2thread', True)
        self.msg_out = ThreadMessageQueue('thread2main', True)
        fb = FramebufferKivy(self.msg_out)
        splash = ImageEntry(None, SPLASH_PATH) if ImageEntry.is_valid_img(SPLASH_PATH) else None
        print(SPLASH_PATH, ImageEntry.is_valid_img(SPLASH_PATH))
        self.btn = {name: ButtonKivy(name) for name in (BTN_PREV, BTN_NEXT)}
        self.eq = EventQueue(fb, self.btn, splash, True)
        
    def run(self):
        running = True
        while running:
            sleep(0.1)
            if (msg := self.msg_in.recv()) is not None:
                if msg['name'] in (BTN_PREV, BTN_NEXT):
                    if msg['press']:
                        self.btn[msg['name']]._pressed()
                    else:
                        self.btn[msg['name']]._released()
                elif msg['press']:
                    if msg['name'] == BTN_MOUNT:
                        self.eq.cb_dev_mounted(msg['param'])
                    elif msg['name'] == BTN_UMOUNT:
                        self.eq.cb_dev_unmounted(msg['param'])
                    else:
                        running = False
    
            self.eq.tick()
