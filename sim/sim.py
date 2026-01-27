from io import BytesIO
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as kiImage
from pathlib import Path
from PIL import Image as pilImage

import sys
sys.path.insert(1, '../src/')

from eventqueue import EventQueue, BTN_NEXT, BTN_PREV
from framebuffer import Framebuffer
from images import ImageEntry
from input import LONG_PRESS_TIME


BTN_MOUNT = 'mount'
BTN_UMOUNT = 'unmount'
BTN_QUIT = 'quit'


def get_gpio_driver(config):
    try:
        from input import ButtonHandler
        handlers = {}
        for button in [BTN_PREV, BTN_NEXT]:
            handlers[button] = ButtonHandler(config[button], button)
        return handlers
    except Exception as ex:
        pass


def load_splash(path, fb):
    if ImageEntry.is_valid_img(path):
        img = ImageEntry(None, path)
        fb.load(img)
        fb.show(img)
        return img


class KivyApp(App):
    def __init__(self):
        self.loaded_path = None
        # TODO Framebuffer adapter fb = get_framebuffer(args.verbose)
        fb = None
        splash = load_splash(Path(__file__).parents[0] / 'assets' / 'logo.png', fb)
        # TODO button adapter
        btn = None

        # set up central object
        self.event_queue = EventQueue(fb, btn, splash)

        # Enter the main loop

    def _press(self, btn):
        self.time_pressed[btn.text] = time()

    def _release(self, btn):
        if self.time_pressed[btn.text] is not None:
            if btn.text in [BTN_NEXT, BTN_PREV]:
                held = time() - self.time_pressed[btn.text]
                if held > LONG_PRESS_TIME:
                    self.event_queue.cb_btn_long(btn.text)
                else:
                    self.event_queue.cb_btn_short(btn.text)

            elif btn.text == BTN_MOUNT:
                # TODO show file chooser
                self.loaded_path = None
                if self.loaded_path is not None:
                    self.btn_mount = BTN_UMOUNT
                    self.event_queue.cb_dev_mounted(self.loaded_path)

            elif btn.text == BTN_UMOUNT:
                if self.loaded_path is not None:
                    self.btn_mount = BTN_MOUNT
                    self.event_queue.cb_dev_unmounted(self.loaded_path)
                    self.loaded_path = None

            elif btn.text == BTN_QUIT:
                quit()

    def make_button(self, text):
        button = Button(text=text)
        button.bind(on_press=self._press, on_release=self._release)
        self.time_pressed[text] = None
        return button

    def show_pillow_image(self, image):
        data = BytesIO()
        image.save(data, format='png')
        data.seek(0)
        im = CoreImage(BytesIO(data.read()), ext='png')
        self.img.texture = im.texture

    def build(self):
        Window.size = (800, 700)
        self.title = 'IMVI SIM'
        
        self.img = kiImage(source='../assets/logo.png')

        button_layout = BoxLayout(orientation='horizontal')
        button_layout.add_widget(self.make_button(BTN_PREV))
        button_layout.add_widget(self.make_button(BTN_NEXT))
        self.btn_mount = self.make_button(BTN_MOUNT)
        button_layout.add_widget(self.btn_mount)
        button_layout.add_widget(self.make_button(BTN_QUIT))

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img)
        layout.add_widget(button_layout)
        return layout

app = KivyApp()
app.run()