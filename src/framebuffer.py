from mmap import mmap, ACCESS_WRITE
from pathlib import Path
from PIL import Image, ImageOps
from sys import argv

CONFIGPATH = '/sys/class/graphics/{}/'
DEVICEPATH = '/dev/{}'


# Raspbian on Pi 1B has this framebuffer mode:
# geometry 1920 1200 1920 1200 16
# rgba 5/11,6/5,5/0,0/0
# Buildroot gives me this:
# geometry 1920 1200 1920 1200 32
# rgba 8/16,8/8,8/0,0/24

def _read_config(filename):
    with open(filename, 'r') as fp:
        content = fp.readline()
        return [int(t) for t in content.strip().split(',') if t]


class Framebuffer(object):
    @staticmethod
    def assign(fbno=0):
        dev = f'fb{fbno}'
        config_dir = Path(CONFIGPATH.format(dev))
        size = (1024, 768)
        depth = 0
        try:
            size = tuple(_read_config(config_dir / 'virtual_size'))
            depth = _read_config(config_dir / 'bits_per_pixel')[0]
        except Exception:
            pass

        if depth == 0:
            return FramebufferNull(dev, size)
        elif depth == 32:
            return Framebuffer32(dev, size)
        else:
            raise ValueError(f'Unsupported framebuffer depth: {depth}')


    def __init__(self, dev, size):
        self.dev = dev
        self.size = size
        self.map = None
        self.showing = None

    def __str__(self):
        return f'<{str(type(self))}: {self.dev} size={self.size}>'

    def load(self, image_data):
        if image_data is not None and image_data.buffer is None:
            image = Image.open(image_data.filepath)
            if image.width < image.height:
                image = image.transpose(Image.ROTATE_270)
            image = ImageOps.pad(image, (self.size[0], self.size[1]), color=(0, 0, 0))
            image_data.set_buffer(self._encode(image))

    def show(self, image_data):
        if self.showing != image_data:
            self.showing = image_data
        if image_data is not None:
            if image_data.buffer is None:
                self.load(image_data)
            self._show(image_data)


class Framebuffer32(Framebuffer):
    def __init__(self, dev, size):
        super().__init__(dev, size)
        self.fbfile = open(Path(DEVICEPATH.format(self.dev)), 'r+b')
        self.map = mmap(self.fbfile.fileno(), size[0]*size[1]*4, access=ACCESS_WRITE)
    
    def __del__(self):
        self.map.close()
        self.fbfile.close()

    def _encode(self, image):
        r, g, b, a = image.convert('RGBA').split()
        return Image.merge('RGBA', (b, g, r, a)).tobytes()

    def _show(self, image_data):
        self.map[:] = image_data.buffer


class FramebufferNull(Framebuffer):
    def __init__(self, dev, size):
        super().__init__(dev, size)
    
    def _encode(self, image):
        print(image.format, image.mode, image.size)
        print(image.info)
        r, g, b, a = image.convert('RGBA').split()
        image = Image.merge('RGBA', (b, g, r, a))
        return 0

    def _show(self, image_data):
        print('Displaying buffer of')
        print(image_data)
