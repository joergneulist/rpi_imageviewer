from subprocess import Popen, run
from time import time


def find(mylist, value):
    try:
        return mylist.index(value)
    except:
        return None


def insert_file(command, file):
    cmd = command.copy()
    while (idx := find(cmd, '#')) is not None:
        command[idx] = file
    return cmd


class Executor:
    @staticmethod
    def run(command, file):
        result = run(insert_file(command, file), capture_output=True, text=True)
        return result.stdout.strip().splitlines()

    def __init__(self):
        self.file = None
        self.process = None

    def __del__(self):
        self.kill()

    def kill(self):
        if self.process is not None:
            print(f'killing process {self.process.pid}')
            now = time.time()
            self.process.terminate()
            self.process.wait()
            print(f'-> dead after {time.time() - now:.2f} seconds')
            self.process = None

    def launch(self, args):
        print(f'launching {args}')
        self.process = Popen(args)
        print(f'-> process {self.process.pid}')

    def replace(self, command, file):
        if self.process is not None:
            if self.file == file:
                return
            self.kill()

        self.file = file
        self.launch(insert_file(command, file))
