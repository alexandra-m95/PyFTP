__author__ = "alexandra"

import socket
import chardet
import sys
import getpass
import traceback


class FTPCore:
    DATA_PASSIVE = False
    DATA_ACTIVE = True

    data_connection_type = None

    def __init__(self, serv_address, port=21, data_con_type=DATA_PASSIVE):
        FTPCore.data_connetion_type = data_con_type
        self.comm_connection = self.CommandConnection(serv_address, port, data_con_type)

    class CommandConnection:
        def __init__(self, serv_address, port, data_con_type):
            self.serv_address = serv_address
            self.port = port
            self.data_con_type = data_con_type # Активное или пассивное соединение
            self.encoding = "UTF-8"
            self.connection_established = False
            self.command_socket = socket.socket()

        def make_connection(self):
            try:
                self.command_socket.settimeout(3)
                self.command_socket.connect((self.serv_address, self.port))
            except (socket.error, OSError) as err:
                print("Извините, не удаётся установить соединение.")
                # твоя задача - вывести минимальный трейсбек с номером ошибки и сообщением
                # в виде
                #    Ошибка: Connection timed out. Код ответа: 110.
                #    Ошибка: Transport endpoint is not connected. Код ответа: 107.
                # у сокета есть параметр - время ожидания. Его нужно задать небольшим чтобы не ждать ответов сервера по пол минуты
                print(traceback.format_exception_only(type(err), err)[0])
                self.command_socket.close()
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

        def make_connection(self, command_connection):
            if FTPCore.data_connection_type == FTPCore.DATA_PASSIVE:
                result, ip_address, port = FTPCore.Commands.pasv(command_connection)
                if result:
                    self.data_sock = socket.socket()
                    self.data_sock.connect((ip_address, port))
                else:
                    print("Соединение невозможно.")
                return self
            elif FTPCore.data_connection_type == FTPCore.DATA_ACTIVE:
                pass

        def close_connection(self):
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

        @staticmethod # АТАТА, СДЕЛАТЬ
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
        def get_file(command_connection, file_name):
            data_connection = FTPCore.DataConnection()
            data_connection.make_connection(command_connection)
            command_connection.send_cmd("RETR " + file_name)
            code, message = command_connection.get_reply()
            print(code, message)

        @staticmethod
        def send_file(command_connection, file_name):
            command_connection.send_cmd("STOR " + file_name)
            code, message = command_connection.get_reply()
            print(code, message)






        # PASV (переход в пассивный режим, для установки соединения данных)
        # PORT (переход в активный режим, для установки соединения данных)
        # RETR (скачать файл с сервера)
        # STOR (закачать файл на сервер)
        # LIST



