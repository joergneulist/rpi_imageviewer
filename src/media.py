from collections import deque
from pathlib import Path


# Alphabetically ordered list of supported file suffixes
SUPPORTED_FORMATS = {'.bmp', '.gif', '.jpeg', '.jpg', '.png', '.tif', '.tiff', '.webp'}


class FileList:
    def __init__(self):
        self.files = []
        self.update()


    def update(self):
        self.n = len(self.files)
        self.active = 0


    def get_file(self):
        if len(self.files) > 0:
            return self.files[self.active][1]


    def next(self):
        if len(self.files) > 0:
            self.active = (self.active + 1) % len(self.files)


    def prev(self):
        if len(self.files) > 0:
            self.active = (self.active - 1) % len(self.files)


    def load(self, tag, file_list):
        for file in file_list:
            if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
                self.files.append((tag, file))
        self.update()


    def unload(self, tag):
        self.files = [entry for entry in self.files if entry[0] != tag]
        self.update()


    def view(self, fb):
        if filename := self.get_file():
            fb.show(filename)
