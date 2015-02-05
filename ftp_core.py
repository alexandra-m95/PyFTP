__author__ = "alexandra"


import socket
import chardet
import sys


class CommandConnection:
    def __init__(self, serv_address, port=21):
        self.serv_address = serv_address
        self.port = port
        self.encoding = "UTF-8"
        self.connection_established = False
        self.command_socket = socket.socket()

    def make_connection(self):
        try:
            self.command_socket.connect((self.serv_address, self.port))
        except socket.error as sock_err:
            print(sock_err, file=sys.stderr)
            quit("Извините, не удаётся установить соединение")
        code, message = self.get_reply()
        if code == 220:
            print(message)
            return True
        else:
            print(code, message)
            quit("Извините, не удаётся установить соединение")
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
        code, message = int(code.decode(self.encoding)), message.decode(self.encoding)
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
    def login(command_connection, user, passwd):

        """
        USER NAME (USER)
        PASSWORD (PASS)
        :param user:
        :param passwd:
        """
        pass

    @staticmethod
    def cd(command_connection):
        """
        CWD
        :rtype : object
        """
        pass

    @staticmethod
    def logout(command_connection):
        pass

    @staticmethod
    def pwd(command_connection):
        pass

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
        print(code, message)