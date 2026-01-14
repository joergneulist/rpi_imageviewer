import numpy as np
from PIL import Image, ImageOps
from sys import argv

CONFIGPATH = '/sys/class/graphics/{}/'
CURSORPATH = '/sys/class/graphics/fbcon/cursor'
DEVICEPATH = '/dev/{}'

def _read_config(filename):
    with open(filename, 'r') as fp:
        content = fp.readline()
        return [int(t) for t in content.strip().split(',') if t]


class Framebuffer(object):
    # Pi 1B has this framebuffer mode, that's what I've tested with
    # geometry 1920 1200 1920 1200 16
    # rgba 5/11,6/5,5/0,0/0
    def __init__(self, fbno=0):
        self.dev = f'fb{fbno}'
        self.get_fb_config()
        #self.disable_cursor() ONLY ROOT
        self.map = np.memmap(DEVICEPATH.format(self.dev), dtype=np.uint16, mode='w+', shape=reversed(self.size))

    def get_fb_config(self):
        config_dir = CONFIGPATH.format(self.dev)
        self.size = tuple(_read_config(config_dir + 'virtual_size'))
        self.depth = _read_config(config_dir + 'bits_per_pixel')[0]
        assert self.depth == 16, "Only 16bpp framebuffer is supported"

    def disable_cursor(self):
        with open(CURSORPATH, 'w') as fp:
            fp.write('0')

    def show(self, file_path):
        image = Image.open(file_path)
        if image.width < image.height:
            image = image.transpose(Image.ROTATE_270)
        image = ImageOps.pad(image, (self.size[0], self.size[1]), color=(0, 0, 0))
        
        npimg = np.array(image, dtype=np.uint16)
        r, g, b = npimg[:, :, 0], npimg[:, :, 1], npimg[:, :, 2]
        self.map[:] = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


if __name__ == '__main__':
    fb = Framebuffer()
    fb.show(argv[1])
    input()
