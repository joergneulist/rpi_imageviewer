from collections import deque
from pathlib import Path
from subprocess import run


def list_find(mylist, value):
    try:
        return mylist.index(value)
    except:
        return None


def execute(command, file):
    args = command.copy()
    while (idx := list_find(args, '#')) is not None:
        args[idx] = file

    result = run(args, capture_output=True, text=True)
    return result.stdout.strip().splitlines()


class FileList:
    def __init__(self, config, cb_update):
        self.config = config
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
            if file.is_file() and file.suffix.lower() in self.config:
                yield file


    def load(self, file_list):
        view_list = []
        for file in file_list:
            cfg = self.config[file.suffix.lower()]
            if 'prep_pre' in cfg:
                pass
#                result = execute(cfg['prep_pre'], file)
#                if cfg['prep_post'] == 'add_list':
#                    for prep_file in result:
#                        view_list.append(Path(prep_file))
            else:
                view_list.append(file)

        self.replace(view_list)


    def replace(self, file_list):
        active_file = self.get_file()

        self.files = file_list
        self.n = len(self.files)
        try:
            self.active = self.files.index(active_file)
            self.cb_update(self.n, True)
        except:
            self.active = 0
            self.cb_update(self.n, False)
 

    def view(self):
        file = self.get_file()
        cfg = self.config[file.suffix.lower()]
        execute(cfg['view'], file)
