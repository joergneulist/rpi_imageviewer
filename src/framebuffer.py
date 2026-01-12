import numpy as np
from PIL import Image, ImageOps
from sys import argv


def _read_config(filename):
    with open(filename, 'r') as fp:
        content = fp.readline()
        return [int(t) for t in content.strip().split(',') if t]


class Framebuffer(object):
    # Pi 1B has this framebuffer mode, that's what I've tested with
    # geometry 1920 1200 1920 1200 16
    # rgba 5/11,6/5,5/0,0/0
    def __init__(self, fbno=0):
        self.dev = f'/dev/fb{fbno}'
        config_dir = f'/sys/class/graphics/fb{fbno}/'
        self.size = tuple(_read_config(config_dir + 'virtual_size'))
        self.depth = _read_config(config_dir + 'bits_per_pixel')[0]
        self.map = np.memmap(self.dev, dtype=np.uint16, mode='r+')

    def __str__(self):
        args = (self.dev, self.size, self.depth)
        return '%s  size:%s  bits_per_pixel:%s' % args

    def show(self, file_path):
        image = Image.open(file_path)
        if image.width < image.height:
            image = image.transpose(Image.ROTATE_270)
        image = ImageOps.pad(image, (self.size[0], self.size[1]), color=(0, 0, 0))
        image = image.convert('I;16')
        self.map[:] = np.array(image)


if __name__ == '__main__':
    fb = Framebuffer()
    fb.show(argv[1])
