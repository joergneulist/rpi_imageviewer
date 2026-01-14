from collections import deque
from pathlib import Path


# Alphabetically ordered list of supported file suffixes
SUPPORTED_FORMATS = {'.bmp', '.gif', '.jpeg', '.jpg', '.png', '.tif', '.tiff', '.webp'}


class FileList:
    def __init__(self, cb_update):
        self.cb_update = cb_update
        self.files = []
        self.n = 0
        self.active = 0


    def get_file(self):
        if self.n:
            return self.files[self.active]


    def next(self):
        if self.n:
            self.active = (self.active + 1) % len(self.files)


    def prev(self):
        if self.n:
            self.active = (self.active - 1) % len(self.files)


    def clean_filelist(self, file_list):
        for file in file_list:
            if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
                yield file


    def load(self, file_list):
        active_file = self.get_file()

        self.files = file_list
        self.n = len(self.files)
        try:
            self.active = self.files.index(active_file)
            self.cb_update(self.n, True)
        except:
            self.active = 0
            self.cb_update(self.n, False)
 

    def view(self, fb):
        fb.show(self.get_file())
