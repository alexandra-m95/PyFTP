__author__ = "alexandra"

import socket
import chardet
import sys
import getpass
import traceback
import os


class FTPCore:
    DATA_PASSIVE = False
    DATA_ACTIVE = True

    data_connection_type = None

    def __init__(self, serv_address, port=21, data_con_type=DATA_PASSIVE):
        FTPCore.data_connection_type = data_con_type
        self.comm_connection = self.CommandConnection(serv_address, port, data_con_type)

    class CommandConnection:
        def __init__(self, serv_address, port, data_con_type):
            self.serv_address = serv_address
            self.port = port
            self.data_con_type = data_con_type
            self.encoding = "UTF-8"
            self.connection_established = False
            self.command_socket = socket.socket()

        def make_connection(self):
            try:
                self.command_socket.settimeout(3)
                self.command_socket.connect((self.serv_address, self.port))
            except (socket.error, OSError) as err:
                print("Извините, не удаётся установить соединение.")
                print(traceback.format_exception_only(type(err), err)[0])
                self.command_socket.close()
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

        def make_connection(self, command_connection):
            if FTPCore.data_connection_type == FTPCore.DATA_PASSIVE:
                pasv_success, ip_address, port = FTPCore.Commands.pasv(command_connection)
                if pasv_success:
                    self.data_sock = socket.socket()
                    self.data_sock.connect((ip_address, port))
                    return True
                else:
                    print("Соединение невозможно.")
                    return False
            elif FTPCore.data_connection_type == FTPCore.DATA_ACTIVE:
                self.data_sock = socket.socket()
                self.data_sock.bind(("", 0))
                host = self.data_sock.getsockname()[0]
                port = self.data_sock.getsockname()[1]
                port_success = FTPCore.Commands.port(command_connection, host, port)
                if port_success:
                    # Принимаем соединение с сервера
                    # data_sock закрываем и подменяем ссылку на принятый con
                    pass
                    return True
                else:
                    return False

        def close_connection(self):
            self.data_sock.close()

        def send_data(self, data):
            self.data_sock.sendall(data)

        def get_data(self):
            while True:
                data = self.data_sock.recv(1024)
                if not data == b"":
                    yield data
                else:
                    break

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
                    print("Добро пожаловать, " + username + "!")
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
        def cd(command_connection, folder):
            """
            CWD
            """
            if folder == "..":
                command_connection.send_cmd("CDUP")
            else:
                command_connection.send_cmd("CWD " + folder)
            code, message = command_connection.get_reply()
            if code == 250:
                FTPCore.Commands.pwd(command_connection)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def quit(command_connection):
            command_connection.send_cmd("QUIT")
            code, message = command_connection.get_reply()
            if code == 221:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

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
            if code == 257:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def mkdir(command_connection, directory_name):
            command_connection.send_cmd("MKD " + directory_name)
            code, message = command_connection.get_reply()
            if code == 257:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False


        @staticmethod
        def rmdir(command_connection, directory_name):
            command_connection.send_cmd("RMD " + directory_name)
            code, message = command_connection.get_reply()
            if code == 250:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def rm(command_connection, file_name):
            command_connection.send_cmd("DELE " + file_name)
            code, message = command_connection.get_reply()
            if code == 250:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def mv(command_connection, original_file_name, new_file_name):
            command_connection.send_cmd("RNFR " + original_file_name)
            code, message = command_connection.get_reply()
            if code != 350:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False
            else:
                command_connection.send_cmd("RNTO " + new_file_name)
                code, message = command_connection.get_reply()
                if code == 250:
                    print(original_file_name + " -> " + new_file_name + " renamed.")
                    return True
                else:
                    print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                    return False

        @staticmethod
        def size(command_connection, file_name):
            command_connection.send_cmd("SIZE " + file_name)
            code, message = command_connection.get_reply()
            if code == 213:
                print(message)
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def mdtm(command_connection, file_name):
            command_connection.send_cmd("MDTM " + file_name)
            code, message = command_connection.get_reply()
            if code == 213:
                print("Дата: " + message[:4] + "/" + message[4:6] + "/" + message[6:8] +
                      " Время: " + message[8:10] + ":" + message[10:12] + ":" + message[12:14])
                return True
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False

        @staticmethod
        def pasv(command_connection):
            command_connection.send_cmd("PASV")
            code, message = command_connection.get_reply()
            if code == 227:
                message = message[message.find("(") + 1:message.rfind(")")]
                split_message = message.split(",")
                ip_address = "{}.{}.{}.{}".format(split_message[0], split_message[1], split_message[2], split_message[3])
                port = 256 * int(split_message[4]) + int(split_message[5])
                return True, ip_address, port
            else:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                return False, '', 0

        @staticmethod
        def port(command_connection, host, port):
            a1a2a3a4 = host.split(".")
            p5 = port >> 8
            p6 = port - (p5 << 8)
            port_args = a1a2a3a4 + [str(p5), str(p6)]
            print("PORT " + ",".join(port_args))
            command_connection.send_cmd("PORT " + ",".join(port_args))
            code, message = command_connection.get_reply()
            if code == 200:
                return True
            elif port == 500:
                print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
                print("Подключитесь в пассивном режиме")
                return False
            else:
                return False

        @staticmethod
        def get_file(command_connection, file_name):
            data_connection = FTPCore.DataConnection()
            make_con_success = data_connection.make_connection(command_connection)
            if not make_con_success:
                print("Извините, не удаётся установить соединение данных.")
                return False
            command_connection.send_cmd("RETR " + file_name)
            code, message = command_connection.get_reply()
            if code == 150:
                current_bytes = 0
                number_of_bytes = int(message[message.find("(") + 1:message.rfind(" ")])
                file = open(file_name , "wb")
                for data in data_connection.get_data():
                    file.write(data)
                    current_bytes += len(data)  # for progressbar
                file.close()
                trans_stat_сode, message = command_connection.get_reply()
                if trans_stat_сode == 226:
                    print(message)
                    data_connection.close_connection()
                    return True
            print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
            data_connection.close_connection()
            return False

        @staticmethod
        def send_file(command_connection, file_name):
            if not os.path.exists(file_name):
                print("File not found!")
                return False
            data_connection = FTPCore.DataConnection()
            make_con_success = data_connection.make_connection(command_connection)
            if not make_con_success:
                print("Извините, не удаётся установить соединение данных.")
                return False
            command_connection.send_cmd("STOR " + file_name)
            code, message = command_connection.get_reply()
            if code == 150:
                current_bytes = 0
                file_size = os.path.getsize(file_name)
                file = open(file_name, "rb")
                while current_bytes < file_size:
                    data = file.read(1024)
                    data_connection.send_data(data)
                    current_bytes += 1024
                file.close()
                data_connection.close_connection()
                code, message = command_connection.get_reply()
                if code == 226:
                    print("File is upload")
                    return True
            data_connection.close_connection()
            print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
            return False

        @staticmethod
        def ls(command_connection, folder=""):
            data_connection = FTPCore.DataConnection()
            make_con_success = data_connection.make_connection(command_connection)
            if not make_con_success:
                print("Извините, не удаётся установить соединение данных.")
                return False
            command_connection.send_cmd("LIST " + folder)
            code, message = command_connection.get_reply()
            if code == 150:
                current_bytes = 0
                folder_content = bytearray()
                for data in data_connection.get_data():
                    folder_content += data
                    current_bytes += len(folder_content)
                folder_content = folder_content.decode()
                print(folder_content)
                trans_stat_сode, message = command_connection.get_reply()
                if trans_stat_сode == 226:
                    print(message)
                    data_connection.close_connection()
                    return True
            print("Ошибка: " + message + " Код ответа: " + str(code) + ".")
            data_connection.close_connection()
            return False

# Залить на гитхаб
# Progress bar
# Shell
# Привести все выводы к единому виду
# Почистить код
# Keep alive
# Забанить google translate




