from subprocess import Popen, run


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
    def get_stdout(command, file):
        result = run(insert_file(command, file), capture_output=True, text=True)
        return result.stdout.strip().splitlines()

    def __init__(self):
        self.file = None
        self.process = None

    def __del__(self):
        self.kill()

    def kill(self):
        if self.process is not None:
            self.process.kill()
            self.process = None

    def launch(self, args):
        self.process = Popen(args)

    def replace(self, command, file):
        if self.process is not None:
            if self.file == file:
                return
            self.kill()

        self.file = file
        self.launch(insert_file(command, file))

