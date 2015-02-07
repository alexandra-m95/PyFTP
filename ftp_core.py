__author__ = "alexandra"

import socket
import chardet
import sys
import getpass


class CommandConnection:
    def __init__(self, serv_address, port=21):
        self.serv_address = serv_address
        self.port = port
        self.encoding = "UTF-8"
        self.connection_established = False
        self.command_socket = socket.socket()

    def make_connection(self):
        try:
            self.command_socket.settimeout(5)
            self.command_socket.connect((self.serv_address, self.port))
        except (socket.error, OSError) as err:
            print("Извините, не удаётся установить соединение.")
            # твоя задача - вывести минимальный трейсбек с номером ошибки и сообщением
            # в виде
            #    Ошибка: Connection timed out. Код ответа: 110.
            #    Ошибка: Transport endpoint is not connected. Код ответа: 107.
            # у сокета есть параметр - время ожидания. Его нужно задать небольшим чтобы не ждать ответов сервера по пол минуты
            print(err)
            # Сокет как и файл в случае ошибок нужно закрывать.
            return False
        code, message = self.get_reply()
        if code == 220:
            print(message)
            return True
        else:
            print("Извините, не удаётся установить соединение")
            return False

    def close_connection(self):
        self.command_socket.close()

    def parse_reply(self, reply):
        return reply[:3], reply[4:]

    def send_cmd(self, cmd):
        self.command_socket.sendall((cmd + "\r\n").encode(self.encoding))

    def get_reply(self):
        reply = self.command_socket.recv(8196)
        code, message = self.parse_reply(reply)
        self.encoding = chardet.detect(message)["encoding"]  # detect encoding
        code, message = int(code.decode(self.encoding)), message.decode(self.encoding).strip()
        return code, message


class DataConnection:
    def __init__(self):
        pass

    def make_connection(self):
        pass

    def receive_connection(self):
        pass

    def send_data(self):
        pass

    def get_data(self):
        pass


class Commands:
    """
    Все команды описаны в документе RFC 959 в главе 4.
    URL: https://tools.ietf.org/html/rfc959
    """

    @staticmethod
    def login(command_connection, username="anonymous", password=""):
        """
        USER NAME (USER)
        PASSWORD (PASS)
        """
        def user():
            nonlocal username
            # username = input("Пожалуйста введите имя пользователя: ")
            command_connection.send_cmd("USER " + username)
            return command_connection.get_reply()

        def passwd():
            nonlocal password
            # password = getpass.getpass("Пожалуйста введите пароль: ")
            command_connection.send_cmd("PASS " + password)
            return command_connection.get_reply()

        u_code, u_message = user()
        if u_code == 331:  # "Укажите свой пароль"
            p_code, p_message = passwd()
            if p_code == 230:  # Удачная авторизация
                print("Добро пожаловать, " + username)
                return True
            else:
                print("Ошибка: " + p_message +
                      " Код ответа: " + str(p_code) + ".")
                return False
        else:
            print("Ошибка: " + u_message +
                  " Код ответа: " + str(u_code) + ".")
            return False


    @staticmethod
    def cd(command_connection, folder=""):
        """
        CWD
        """
        if folder == "":
            folder = input("Пожалуйста, введите имя директории: ")
        command_connection.send_cmd("CWD" + folder)
        code, message = command_connection.get_reply()
        print(code, message)


    @staticmethod
    def quit(command_connection):
        command_connection.send_cmd("QUIT")

    @staticmethod
    def noop(command_connection):
        """
        NOOP (NOOP)
        Выполнение данной команды ни на что ее влияет.
        Единственное полезное свойство - проверка/поддержание соединения.
        Возвращает "OK!"
        """
        command_connection.send_cmd("NOOP")
        code, message = command_connection.get_reply()
        if code == 200:
            print("Всё хорошо :)")
            return True
        else:
            print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
            return False

    @staticmethod
    def pwd(command_connection):
        command_connection.send_cmd("PWD")
        code, message = command_connection.get_reply()
        print(code, message)
