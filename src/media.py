from collections import deque


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


    def load(self, path):
        directories = deque([path])
        files = []
        while len(directories):
            for node in directories.popleft().iterdir():
                if node.is_dir():
                    directories.append(node)
                elif node.is_file() and node.suffix.lower() in SUPPORTED_FORMATS:
                    self.files.append((path, node))
        self.update()


    def unload(self, path):
        self.files = [entry for entry in self.files if entry[0] != path]
        self.update()
