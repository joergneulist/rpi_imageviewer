
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from time import sleep, time

from media import FileList
from usbmedia import USBMediaKeeper


BTN_NEXT = 'next'
BTN_PREV = 'prev'


class Event(Enum):
    Idle        =  0
    ButtonShort = 11
    ButtonLong  = 12
    ImageLoad   = 21
    ImageShow   = 22
    MediaLoad   = 31
    MediaUnload = 32


@dataclass
class EventEntry:
    event: Event
    params: tuple


class EventQueue:
    def __init__(self, config, framebuffer, verbose=False):
        self.event_queue = deque()
        self.config = config
        self.verbose = verbose
        self.fileTracker = FileList()
        self.framebuffer = framebuffer
        self.bored_since = time()

        # register triggers for media control
        try:
            from input import ButtonHandler
            self.btn_handlers = {}
            for button in [BTN_PREV, BTN_NEXT]:
                self.btn_handlers[button] = ButtonHandler(self.config['pins'][button], button, self.cb_btn_short, self.cb_btn_long)
                if self.verbose:
                    print(self.btn_handlers[button])
        except Exception:
            self.btn_handlers = None
            if self.verbose:
                print('GPIO-Handlers failed!')


    def process_idle_event(self, _):
        # empty queue -> let's catch up on sleep!
        sleep(0.1)

        # debug mode: simulate button inputs
        if self.btn_handlers is None and time() - self.bored_since > 10.0:
            self.add_event(Event.ButtonShort, BTN_NEXT)                    
            self.bored_since = time()


    def process_button_short_event(self, name):
        if name == BTN_NEXT:
            self.fileTracker.next()
        elif name == BTN_PREV:
            self.fileTracker.prev()
        self.add_event(Event.ImageLoad, self.fileTracker.get_file())


    def process_button_long_event(self, name):
        # TODO Implement different modes
        self.process_button_short_event(name)


    def process_image_load_event(self, path):
        if path is not None:
            buffer = self.framebuffer.load(path)
            self.add_event(Event.ImageShow, buffer)


    def process_image_show_event(self, buffer):
        self.framebuffer.show(buffer)


    def process_media_load_event(self, path):
        self.fileTracker.load(path)
        # TODO don't switch view if not necessary!
        self.add_event(Event.ImageShow, self.fileTracker.get_file())


    def process_media_show_event(self, path):
        self.fileTracker.unload(path)
        # TODO don't switch view if not necessary!
        self.add_event(Event.ImageShow, self.fileTracker.get_file())


    def add_event(self, event, *params):
        if self.verbose:
            print(f'{time()} EVENTLOOP received event {event} with parameters {params}')
        self.event_queue.append(EventEntry(event, *params))


    def get_event(self):
        if len(self.event_queue) == 0:
            return EventEntry(Event.Idle, ())
        evt = self.event_queue.popleft()
        if self.verbose:
            print(f'{time()} EVENTLOOP process event {evt.event} with parameters {evt.params}')
        return evt


    def loop(self):
        while True:
            EVT_HANDLERS = {
                Event.Idle:        self.process_idle_event,
                Event.ButtonShort: self.process_button_short_event,
                Event.ButtonLong:  self.process_button_long_event,
                Event.ImageLoad:   self.process_image_load_event,
                Event.ImageShow:   self.process_image_show_event,
                Event.MediaLoad:   self.process_media_load_event,
                Event.MediaUnload: self.process_media_show_event
            }
            next_task = self.get_event()
            EVT_HANDLERS[next_task.event](next_task.params)


    def cb_btn_long(self, name):     self.add_event(Event.ButtonLong,  name)
    def cb_btn_short(self, name):    self.add_event(Event.ButtonShort, name)
    def cb_dev_mounted(self, path):  self.add_event(Event.MediaLoad,   path)
    def cb_dev_unmounted(self, path):self.add_event(Event.MediaUnload, path)

