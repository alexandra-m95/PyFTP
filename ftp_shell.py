__author__ = 'alexandra'
import time
import sys
from ftp_core import *

def call_functions(ftp_server, port=21):
    commands = ("login", "cd", "get", "ls", "mdtm", "mkdir", "mv", "noop", "pwd", "quit", "rm", "rmdir", "send", "size")
    ftp_core = FTPCore(ftp_server, port)
    functions = (FTPCore.Commands.login, FTPCore.Commands.cd, FTPCore.Commands.get_file, FTPCore.Commands.ls,
    FTPCore.Commands.mdtm, FTPCore.Commands.mkdir, FTPCore.Commands.mv, FTPCore.Commands.noop,
    FTPCore.Commands.pwd, FTPCore.Commands.quit, FTPCore.Commands.rm, FTPCore.Commands.rmdir,
    FTPCore.Commands.send_file, FTPCore.Commands.size)
    functions_for_commands = dict(zip(commands, functions))
    good_connect_result = ftp_core.comm_connection.make_connection()
    if not good_connect_result:
        return
    while True:
        command_and_args = input("~ ").strip().split(" ")
        if command_and_args[0] in functions_for_commands:
            try:
                if command_and_args[0] == "quit":
                    if functions_for_commands.get(command_and_args[0])(ftp_core.comm_connection,
                                                                       *command_and_args[1:]):
                        break
                else:
                    functions_for_commands.get(command_and_args[0])(ftp_core.comm_connection,
                                                                    *command_and_args[1:])
            except (BrokenPipeError, OSError):
                print("Timeout.")
                break
        else:
            print("Command not found!")

call_functions("88.85.196.86")
