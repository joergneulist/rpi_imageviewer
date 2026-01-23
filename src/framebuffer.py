from mmap import mmap, ACCESS_WRITE
from pathlib import Path
from PIL import Image, ImageOps
from sys import argv

CONFIGPATH = '/sys/class/graphics/{}/'
DEVICEPATH = '/dev/{}'

def _read_config(filename):
    with open(filename, 'r') as fp:
        content = fp.readline()
        return [int(t) for t in content.strip().split(',') if t]


def get_size(size):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if size < factor:
            return f"{size:.2f} {unit}B"
        size /= factor


class Framebuffer(object):
    # Raspbian Pi 1B has this framebuffer mode:
    # geometry 1920 1200 1920 1200 16
    # rgba 5/11,6/5,5/0,0/0
    # Buildroot gives me this:
    # geometry 1920 1200 1920 1200 32
    # rgba 8/16,8/8,8/0,0/24
    @staticmethod
    def assign(fbno=0, debug=False):
        dev = f'fb{fbno}'
        config_dir = Path(CONFIGPATH.format(dev))
        size = (1024, 768)
        depth = 0
        if not debug:
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
        self.buffers = [None]
        self.map = None
    
    def __str__(self):
        return f'<{str(type(self))}: {self.dev} size={self.size}>'

    def prepare(self, file_path):
        image = Image.open(file_path)
        if image.width < image.height:
            image = image.transpose(Image.ROTATE_270)
        image = ImageOps.pad(image, (self.size[0], self.size[1]), color=(0, 0, 0))
        image.filename = file_path
        
        # TODO implement ROUND-ROBIN cache somehow
        self.buffers[0] = self.encode(image)
        return 0


class Framebuffer32(Framebuffer):
    def __init__(self, dev, size):
        super().__init__(dev, size)
        self.fbfile = open(Path(DEVICEPATH.format(self.dev)), 'r+b')
        self.map = mmap(self.fbfile.fileno(), size[0]*size[1]*4, access=ACCESS_WRITE)
    
    def __del__(self):
        self.map.close()
        self.fbfile.close()

    def encode(self, image):
        r, g, b, a = image.convert('RGBA').split()
        return Image.merge('RGBA', (b, g, r, a)).tobytes()

    def show(self, buffer_idx):
        self.map[:] = self.buffer[buffer_idx]


class FramebufferNull(Framebuffer):
    def __init__(self, dev, size):
        super().__init__(dev, size)
    
    def encode(self, image):
        print(image.filename, image.format, image.mode, image.size)
        print(image.info)
        r, g, b, a = image.convert('RGBA').split()
        image = Image.merge('RGBA', (b, g, r, a))
        print(f'Size: {get_size(len(image.tobytes()))}')
        return 0

    def show(self, buffer_idx):
        print(f'Displaying buffer {buffer_idx}')

if __name__ == '__main__':
    fb = Framebuffer.assign()
    print(fb)
    fb.show(argv[1])
    input()
