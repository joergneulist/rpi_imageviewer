from collections import deque
from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
from time import time


@dataclass
class ImageEntry:
    @staticmethod
    def is_valid_img(path):
        # set of supported file suffixes
        SUPPORTED_FORMATS = {'.bmp', '.gif', '.jpeg', '.jpg', '.png', '.tif', '.tiff', '.webp'}
        return path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS

    source: str
    filepath: str
    loadtime: float = None
    buffer: bytes = None
    
    def set_buffer(self, buffer):
        self.loadtime = time()
        self.buffer = buffer
    
    def flush_buffer(self):
        self.location = None
        self.buffer = None


class ImageBuffer:
    def __init__(self):
        self.img = deque()

    def next(self):
        self.img.rotate(-1)

    def prev(self):
        self.img.rotate(1)

    def get_current(self):
        if len(self.img) > 0:
            return self.img[0]
    
    def get_next_uncached(self):
        for img in self.img:
            if img.buffer is None:
                return img

    def add_path(self, path):
        directories = deque([path])
        while len(directories):
            for node in directories.popleft().iterdir():
                if node.is_dir():
                    directories.append(node)
                elif ImageEntry.is_valid_img(node):
                    self.img.append(ImageEntry(path, node))

    def drop_path(self, path):
        remaining = deque()
        for img in self.img:
            if img.source != path:
                remaining.append(img)
        self.img = remaining
