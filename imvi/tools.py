#!/usr/bin/python


def find(mylist, value):
    try:
        return mylist.index(value)
    except:
        return None


def execute(command, file):
    while (idx := find(command, '#')) is not None:
        command[idx] = file
    # TODO actually execute command and return result
    return None
