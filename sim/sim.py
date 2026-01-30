from io import BytesIO
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as kiImage
from kivy.uix.popup import Popup
from concurrent.futures import Future
from PIL import Image as pilImage

from adapters import IMVIAdapter, BTN_MOUNT, BTN_NEXT, BTN_PREV, BTN_UMOUNT, SIZE


BTN_QUIT = 'quit'
BUTTON_HEIGHT = 100


class PathPicker(Popup):
    def __init__(self, callback):
        self.callback = callback
        btn_select = Button(text='Select', size_hint=(1, None), height=BUTTON_HEIGHT)
        btn_select.bind(on_release=self._button)
        btn_cancel = Button(text='Cancel', size_hint=(1, None), height=BUTTON_HEIGHT)
        btn_cancel.bind(on_release=self._button)

        btn_layout = BoxLayout(size_hint=(1, None), height=BUTTON_HEIGHT)
        btn_layout.add_widget(btn_select)
        btn_layout.add_widget(btn_cancel)
        self.chooser = FileChooserListView(path='.', dirselect=True)

        content = BoxLayout(orientation='vertical')
        content.add_widget(self.chooser)
        content.add_widget(btn_layout)

        super().__init__(title='Select directory', content=content, auto_dismiss=False)
        self.open()


    def _button(self, button):
        path = None
        if button.text == 'Select':
            sel = self.chooser.selection
            path = sel[0] if sel else self.chooser.path
        self.dismiss()
        self.callback(path)


class KivyApp(App):
    def __init__(self, msg_outgoing, msg_incoming):
        super().__init__()
        self.msg_out = msg_outgoing
        self.msg_in = msg_incoming
        self.loaded_path = None
        self.msg_in.set_flag_callback(lambda: Clock.schedule_once(lambda dt: self.receive()))
    
    def receive(self):
        if (msg := self.msg_in.recv()) is not None:
            self.show_pillow_image(msg)

    def _press(self, btn):
        if btn.text == BTN_MOUNT:
            # show file chooser modal and handle selection asynchronously
            popup = PathPicker(self._select_path)
        elif btn.text == BTN_UMOUNT:
            if self.loaded_path is not None:
                # reset mount button text and notify adapter
                self.btn_mount.text = BTN_MOUNT
                self.msg_out.send({'press': True, 'name': BTN_UMOUNT, 'param': self.loaded_path})
                self.loaded_path = None
        elif btn.text == BTN_QUIT:
            quit()
        else:
            self.msg_out.send({'press': False, 'name': btn.text})

    def _release(self, btn):
        self.msg_out.send({'press': False, 'name': btn.text})

    def _select_path(self, path):
            self.loaded_path = path
            if self.loaded_path is not None:
                # reset mount button text and notify adapter
                self.btn_mount.text = BTN_UMOUNT
                self.msg_out.send({'press': True, 'name': BTN_MOUNT, 'param': self.loaded_path})

    def make_button(self, text):
        button = Button(text=text, size_hint=(1, None), height=BUTTON_HEIGHT)
        button.bind(on_press=self._press, on_release=self._release)
        return button

    def show_pillow_image(self, image):
        data = BytesIO()
        image.save(data, format='png')
        data.seek(0)
        im = CoreImage(BytesIO(data.read()), ext='png')
        self.img.texture = im.texture

    def build(self):
        Window.size = (SIZE[0], SIZE[1] + BUTTON_HEIGHT)
        self.title = 'IMVI SIM'
        self.img = kiImage(size_hint=(None, None), height=SIZE[1], width=SIZE[0])
        self.show_pillow_image(pilImage.new(mode='1', size=SIZE))

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


adapt = IMVIAdapter()
app = KivyApp(adapt.msg_in, adapt.msg_out)
adapt.start()
app.run()
adapt.join()
