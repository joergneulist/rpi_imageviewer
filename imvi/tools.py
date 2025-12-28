from subprocess import run

def find(mylist, value):
    try:
        return mylist.index(value)
    except:
        return None


def execute(command, file):
    while (idx := find(command, '#')) is not None:
        command[idx] = file
    result = run(command, capture_output=True, text=True)
    return result.stdout.strip().splitlines()
