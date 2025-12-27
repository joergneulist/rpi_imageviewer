#!/usr/bin/python


from collections import deque
from pathlib import Path
import time


MEDIA_PATH = Path('/media')


class FileViewer:
    @staticmethod
    def _clean_list(file_list):
        return file_list

    def __init__(self, file_list, active_file=None, list_is_clean=False):
        if list_is_clean:
            self.files = file_list
        else:
            self.files = self._clean_list(file_list)
        self.n = len(self.files)
        try:
            self.viewed = self.field.index(active_file)
        except:
            self.viewed = 0
        self.display()

    def display(self):
        print(f'show #{self.viewed}: {self.get_file()}')

    def get_file(self):
        if self.n:
            return self.files[self.viewed]

    def next(self):
        if self.n:
            self.viewed = (self.viewed + 1) % len(self.files)

    def prev(self):
        if self.n:
            self.viewed = (self.viewed + len(self.files) - 1) % len(self.files)

    def replace(self, file_list):
        files = self._clean_list(file_list)
        if self.files != files:
            return FileViewer(files, active_file=self.get_file(), list_is_clean=True)


def gather_files(path):
    directories = deque([path])
    files = []
    while len(directories):
        dir = directories.popleft()
        for node in dir.iterdir():
            if node.is_dir():
                directories.append(node)
            else:
                files.append(node)
    return files


if __name__ == '__main__':
    # register triggers for media control
    # TODO

    view = FileViewer([])
    while True:
        time.sleep(5)
        new_view = view.replace(gather_files(MEDIA_PATH))
        if new_view:
            print('file list replaced')
            view = new_view

