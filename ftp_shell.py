__author__ = 'alexandra'
from ftp_core import *


def call_functions(ftp_server, port=21):
    """
    Вызывает функцию установки управляющего соединения с FTP-сервером. Если установка проходит
    успешно, то начинается цикл обработки команд пользователя и вызова соотвествующих функций до
    тех пор, пока пользователь не введет команду "quit".
    :param ftp_server: адрес FTP-сервера.
    :param port: порт, к которому будет происходить попытка подключения.
    """
    commands = ("login", "cd", "get", "ls", "mdtm", "mkdir", "mv", "noop", "pwd", "quit", "rm",
                "rmdir", "send", "size", "dir", "help")
    ftp_core = FTPCore(ftp_server, port)
    functions = (ftp_core.Commands.login, ftp_core.Commands.cd, ftp_core.Commands.get_file, ftp_core.Commands.ls,
                 ftp_core.Commands.mdtm, ftp_core.Commands.mkdir, ftp_core.Commands.mv, ftp_core.Commands.noop,
                 ftp_core.Commands.pwd, ftp_core.Commands.quit, ftp_core.Commands.rm, ftp_core.Commands.rmdir,
                 ftp_core.Commands.send_file, ftp_core.Commands.size, ftp_core.Commands.dir, ftp_core.Commands.help)
    functions_for_commands = dict(zip(commands, functions))
    good_connect_result = ftp_core.comm_connection.make_connection()
    if not good_connect_result:
        return
    while True:
        command_and_args = input("~ ").strip().split(" ")
        if command_and_args[0] in functions_for_commands:
            try:
                functions_for_commands.get(command_and_args[0])(ftp_core.comm_connection,
                                                                *command_and_args[1:])
                if command_and_args[0] == "quit":
                    break
            except (BrokenPipeError, OSError, AuthError) as err:
                print(traceback.format_exception_only(type(err), err)[0])
                FTPCore.CommandConnection.close_connection(ftp_core.comm_connection)
                break
        else:
            print("Command not found!")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        call_functions(sys.argv[1])
    elif len(sys.argv) > 2 and sys.argv[2].isdigit():
        call_functions(sys.argv[1], int(sys.argv[2]))
    else:
        print("Для запуска программы необходимо обязательно ввести адрес сервера, к которому вы\n"
              "желаете подключиться. Также можно ввести необязательный второй параметр: номер \nпорта."
              " Если он будет опущен, то подключение будет происходить к порту по\nумолчанию(21-ый).")
