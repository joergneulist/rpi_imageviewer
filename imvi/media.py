#!/usr/bin/python


from collections import deque
from pathlib import Path

from imvi.tools import execute


class FileList:
    def __init__(self, config):
        self.config = config
        self.files = []
        self.n = 0
        self.viewed = 0


    def get_file(self):
        if self.n:
            return self.files[self.viewed]


    def next(self):
        if self.n:
            self.viewed = (self.viewed + 1) % len(self.files)


    def prev(self):
        if self.n:
            self.viewed = (self.viewed - 1) % len(self.files)


    def clean_filelist(self, file_list):
        for file in file_list:
            if file.is_file() and file.suffix.lower() in self.config:
                yield file


    def load(self, file_list):
        view_list = []
        for file in file_list:
            cfg = self.config[file.suffix.lower()]
            if 'prep_pre' in cfg:
                result = execute(cfg['prep_pre'], file)
                if cfg['prep_post'] == 'add_list':
                    for prep_file in result:
                        view_list.append(Path(prep_file))
            else:
                view_list.append(file)

        self.replace(view_list)


    def replace(self, file_list):
        active_file = self.files.get_file()

        self.files = file_list
        self.n = len(self.files)
        try:
            self.viewed = self.files.index(active_file)
        except:
            self.viewed = 0
