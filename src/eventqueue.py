
from collections import deque
from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
from time import sleep, time

from images import ImageBuffer
from usbmedia import USBMediaKeeper


BTN_NEXT = 'next'
BTN_PREV = 'prev'


class Event(Enum):
    Idle        = auto()
    ButtonShort = auto()
    ButtonLong  = auto()
    ImageLoad   = auto()
    ImageShow   = auto()
    MediaLoad   = auto()
    MediaUnload = auto()


@dataclass
class EventEntry:
    event: Event
    params: tuple


class EventQueue:
    def __init__(self, framebuffer, buttons, splash, verbose=False):
        self.event_queue = deque()
        self.verbose = verbose
        self.fallback_image = splash
        self.images = ImageBuffer()
        self.framebuffer = framebuffer
        self.usb = USBMediaKeeper(self.cb_dev_mounted, self.cb_dev_unmounted)

        # register triggers for media control
        self.buttons = buttons
        if buttons is not None:
            for button in self.buttons.values():
                button.set_callbacks(self.cb_btn_short, self.cb_btn_long)


    def process_idle_event(self, _):
        if (img := self.images.get_next_uncached()) is not None:
            self.add_event(Event.ImageLoad, img)
        else:
            # empty queue -> let's catch up on sleep!
            sleep(0.2)


    def process_button_short_event(self, name):
        if name == BTN_NEXT:
            self.images.next()
        elif name == BTN_PREV:
            self.image.prev()
        self.add_event(Event.ImageShow, self.images.get_current())


    def process_button_long_event(self, name):
        # TODO Implement different modes
        self.process_button_short_event(name)


    def process_image_load_event(self, img):
        self.framebuffer.load(img)


    def process_image_show_event(self, img):
        if img is not None:
            self.framebuffer.show(img)
        else:
            self.framebuffer.show(self.fallback_image)


    def process_media_load_event(self, path):
        self.images.add_path(path)
        # TODO don't switch view if not necessary!
        self.add_event(Event.ImageShow, self.images.get_current())


    def process_media_show_event(self, path):
        self.images.drop_path(path)
        # TODO don't switch view if not necessary!
        self.add_event(Event.ImageShow, self.images.get_current())


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

