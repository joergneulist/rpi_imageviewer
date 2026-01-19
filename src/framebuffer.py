from mmap import mmap, ACCESS_WRITE
from PIL import Image, ImageOps
from sys import argv

CONFIGPATH = '/sys/class/graphics/{}/'
DEVICEPATH = '/dev/{}'

def _read_config(filename):
    with open(filename, 'r') as fp:
        content = fp.readline()
        return [int(t) for t in content.strip().split(',') if t]


class Framebuffer(object):
    # Raspbian Pi 1B has this framebuffer mode:
    # geometry 1920 1200 1920 1200 16
    # rgba 5/11,6/5,5/0,0/0
    # Buildroot gives me this:
    # geometry 1920 1200 1920 1200 32
    # rgba 8/16,8/8,8/0,0/24
    @staticmethod
    def assign(fbno=0):
        dev = f'fb{fbno}'
        config_dir = CONFIGPATH.format(dev)
        size = tuple(_read_config(config_dir + 'virtual_size'))
        depth = _read_config(config_dir + 'bits_per_pixel')[0]
        if depth == 32:
            return Framebuffer32(dev, size)
        else:
            raise ValueError(f'Unsupported framebuffer depth: {depth}')


    def __init__(self, dev, size):
        self.dev = dev
        self.size = size
        self.map = None
    
    def __str__(self):
        return f'<{type(self)} {self.dev} size={self.size}>'

    def show(self, file_path):
        image = Image.open(file_path)
        if image.width < image.height:
            image = image.transpose(Image.ROTATE_270)
        image = ImageOps.pad(image, (self.size[0], self.size[1]), color=(0, 0, 0))
        self.mmap(image)


class Framebuffer32(Framebuffer):
    def __init__(self, dev, size):
        super().__init__(dev, size)
        self.fbfile = open(DEVICEPATH.format(self.dev), 'r+b')
        self.map = mmap(self.fbfile.fileno(), 0, access=ACCESS_WRITE)
    
    def __del__(self):
        self.map.close()
        self.fbfile.close()

    def mmap(self, image):
        r, g, b = image.split()
        image = Image.merge('RGB', (b, g, r)).convert('RGBA')
        self.map[:] = image.tobytes()


if __name__ == '__main__':
    fb = Framebuffer.assign()
    print(fb)
    fb.show(argv[1])
    input()
