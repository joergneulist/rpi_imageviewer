#!/usr/bin/python


def execute(command, file):
    while idx := command.index('#') != -1:
        command[idx] = file
    # TODO actually execute command and return result
    return None
