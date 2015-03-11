__author__ = "alexandra"

import socket
import chardet
import sys
import getpass
import traceback
import os


class FTPCore:
    def __init__(self, serv_address, port=21):
        self.comm_connection = self.CommandConnection(serv_address, port)

    class CommandConnection:
        def __init__(self, serv_address, port):
            self.serv_address = serv_address
            self.port = port
            self.encoding = "UTF-8"
            self.connection_established = False
            self.command_socket = socket.socket()

        def make_connection(self):
            """
            Установка управляющего соединения с сервером.
            :return: True - установка прошла успешна, False - в противном случае.
            """
            try:
                self.command_socket.settimeout(15)
                self.command_socket.connect((self.serv_address, self.port))
            except (socket.error, OSError) as err:
                print(traceback.format_exception_only(type(err), err)[0])
                self.command_socket.close()
                return False
            code, message = self.get_reply()
            if code == 220:
                print(message)
                return True
            else:
                print("Can't establish connection.")
                return False

        def close_connection(self):
            """
            Закрытие управляющего соединения с сервером.

            """
            self.command_socket.close()

        @staticmethod
        def parse_reply(reply):
            """
            :param reply: Ответ сервера.
            :return: Код ответа и сообщение.
            """
            return reply[:3], reply[4:]

        def send_cmd(self, cmd):
            """
            Отправляет заданную команду серверу.
            :param cmd: команда.
            """
            self.command_socket.sendall((cmd + "\r\n").encode(self.encoding))

        def get_reply(self):
            """
            Получает код ответа сервера и сообщение, затем декодирует их.
            :return: кортеж: код и сообщение.
            """
            reply = self.command_socket.recv(8196)
            if reply == b'':
                raise AuthError("Server replies ended.")
            code, message = self.parse_reply(reply)
            self.encoding = chardet.detect(message)["encoding"]  # detect encoding
            code, message = int(code.decode(self.encoding)), message.decode(self.encoding).strip()
            return code, message

    class DataConnection:
        def make_connection(self, command_connection):
            """
            Устанавливает с сервером пассивное соединение передачи данных. Вызывает метод pasv класса
            Commands, который возвращает кортеж, где первое значение True (возможно установить
            пассивное соединение) или False (в противном случае), а также ip-адрес для
            подсоединения и порт.
            :param command_connection: Экземпляр класса CommandConnection.
            :return: True - удалось установить соединение. False - в противном случае.
            """
            pasv_success, ip_address, port = FTPCore.Commands.pasv(command_connection)
            if pasv_success:
                self.data_sock = socket.socket()
                self.data_sock.connect((ip_address, port))
                return True
            else:
                return False

        def close_connection(self):
            """
            Закрывает соединение данных с сервером.
            """
            self.data_sock.close()

        def send_data(self, data):
            """
            Отправляет данные серверу.
            :param data: данные.
            """
            self.data_sock.sendall(data)

        def get_data(self):
            """
            Получает данные из канала передачи данных.

            """
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
        def login(command_connection, username="anonymous", password="", debug=False):
            """
            Вызывает функции ввода логина и пароля, которые отправляют серверу команда USER и PASS.
            :param command_connection: Экземпляр класса CommandConnection.
            :param username: имя пользователя для залогинивания на сервере. Функция вызывается с
            данным параметром в debug-режиме, т.к. просьбы о вводе имени не будет.
            :param password: пароль для залогинивания на сервере. Аналогично, вызов с данным
            параметром происходит в debug-режиме.
            :param debug: включение debug-режима.
            :return: True - залогинивание прошло успешно. False - в противном случае.
            """

            def user():
                nonlocal username
                if not debug:
                    username = input("Пожалуйста введите имя пользователя[\"anonymous\"]: ")
                if username == "":
                    username = "anonymous"
                command_connection.send_cmd("USER " + username)
                return command_connection.get_reply()

            def passwd():
                nonlocal password
                if username is "anonymous":
                    password = "anonymous@"
                elif not debug:
                    password = getpass.getpass("Пожалуйста введите пароль: ")
                command_connection.send_cmd("PASS " + password)
                return command_connection.get_reply()

            u_code, u_message = user()
            if u_code == 331:
                p_code, p_message = passwd()
                if p_code == 230:
                    print("Welcome, " + username + "!")
                    return True
                else:
                    print("Error: " + p_message +
                          " Reply code: " + str(p_code) + ".")
                    return False

            else:
                print("Error: " + u_message +
                      " Reply code: " + str(u_code) + ".")
                return False

        @staticmethod
        def cd(command_connection, folder='', *_):
            """
            Отправляет команду CWD(переход в другой каталог) или CDUP(для перехода в каталог уровнем
            выше, если в качестве переметра задано "..")
            :param command_connection: Экземпляр класса CommandConnection.
            :param folder: каталог, в который необходимо перейти.
            :return: True - переход прошел успешно. False - в противно случае.
            """
            if folder == '':
                print("Invalid arguments number!")
                return False
            if folder == "..":
                command_connection.send_cmd("CDUP")
            else:
                command_connection.send_cmd("CWD " + folder)
            code, message = command_connection.get_reply()
            if code == 250:
                FTPCore.Commands.pwd(command_connection)
                return True
            else:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False

        @staticmethod
        def quit(command_connection, *_):
            """
            Отправляет команду QUIT для завершения управляющего соединения с сервером.
            :param command_connection: Экземпляр класса CommandConnection.
            :return: True - удалось успешно выйти. False - в противном случае.
            """
            command_connection.send_cmd("QUIT")
            code, message = command_connection.get_reply()
            if code == 221:
                print(message)
                return True
            else:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False

        @staticmethod
        def noop(command_connection, *_):
            """
            Отправляет серверу комадну NOOP.
            Выполнение данной команды ни на что ее влияет.
            Единственное полезное свойство - проверка/поддержание соединения.
            Возвращает "OK!"
            :param command_connection: Экземпляр класса CommandConnection.
            :return: True - все отлично и False в противном случае.
            """
            command_connection.send_cmd("NOOP")
            code, message = command_connection.get_reply()
            if code == 200:
                print("Good :)")
                return True
            else:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False

        @staticmethod
        def pwd(command_connection, *_):
            """
            Отправляет серверу команду PWD, которая возвращает текущий каталог.
            :param command_connection: Экземпляр класса CommandConnection.
            :return: True - удалось получить текущий каталог. False - в противном случае.
            """
            command_connection.send_cmd("PWD")
            code, message = command_connection.get_reply()
            if code == 257:
                print(message.replace('"', ''))
                return True
            else:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False

        @staticmethod
        def mkdir(command_connection, *directory_names):
            """
            Отправляет серверу команду MKD для создания каталогов.
            :param command_connection: Экземпляр класса CommandConnection.
            :param directory_names: именя для новых каталогов.
            :return: True - создание всех каталогов прошло успешно, False - в противном случае.
            """
            all_files_success = True
            for directory_name in directory_names:
                command_connection.send_cmd("MKD " + directory_name)
                code, message = command_connection.get_reply()
                if code == 257:
                    print(message)
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def rmdir(command_connection, *directory_names):
            """
            Отправляет команду RMD для удаления каталогов.
            :param command_connection: Экземпляр класса CommandConnection.
            :param directory_names: имена каталогов, каталогов, которые необходимо удалить.
            :return: True - удаление всех каталогов прошло успешно, False - в противном случае.
            """
            all_files_success = True
            for directory_name in directory_names:
                print(directory_name + ": ")
                command_connection.send_cmd("RMD " + directory_name)
                code, message = command_connection.get_reply()
                if code == 250:
                    print(message)
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def rm(command_connection, *file_names):
            """
            Отправляет команду DELE для удаления файлов.
            :param command_connection: Экземпляр класса CommandConnection.
            :param file_names: имена файлов, которые необходимо удалить.
            :return: True - все файлы удалось удались, False - в противном случае.
            """
            all_files_success = True
            for file_name in file_names:
                command_connection.send_cmd("DELE " + file_name)
                code, message = command_connection.get_reply()
                print(file_name + ":")
                if code == 250:
                    print(message)
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def mv(command_connection, original_file_name='', new_file_name='', *_):
            """
            Отправляет команду RNFR(переименование файла).
            :param command_connection: Экземпляр класса CommandConnection.
            :param original_file_name: первоначальное имя файла.
            :param new_file_name: новое имя файла.
            :return: True - файл удалось переименовать, False - в противном случае.
            """
            if original_file_name == '' or new_file_name == '':
                print("Error: Invalid arguments number!")
                return False
            command_connection.send_cmd("RNFR " + original_file_name)
            code, message = command_connection.get_reply()
            if code != 350:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False
            else:
                command_connection.send_cmd("RNTO " + new_file_name)
                code, message = command_connection.get_reply()
                if code == 250:
                    print(original_file_name + " -> " + new_file_name + " renamed.")
                    return True
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    return False

        @staticmethod
        def size(command_connection, *file_names):
            """
            Отправляет серверу команду SIZE для каждого из файлов для получения их размеров.
            :param command_connection: Экземпляр класса CommandConnection.
            :param file_names: имена файлов.
            :return: True - удалось получить размер каждого файла, False - в противном случае.
            """
            all_files_success = True
            for file_name in file_names:
                command_connection.send_cmd("SIZE " + file_name)
                code, message = command_connection.get_reply()
                if code == 213:
                    print(file_name + ": " + message)
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def mdtm(command_connection, *file_names):
            """
            Отправляет серверу команду MDTM для каждого из файлов для получения дат и времени
            их создания.
            :param command_connection: Экземпляр класса CommandConnection.
            :param file_names: имена файлов, размер которых необходимо получить.
            :return: True - удалось получить все размеры, False - в противном случае.
            """
            all_files_success = True
            for file_name in file_names:
                command_connection.send_cmd("MDTM " + file_name)
                code, message = command_connection.get_reply()
                print("File " + file_name + ":")
                if code == 213:
                    print("Date: " + message[:4] + "/" + message[4:6] + "/" + message[6:8] +
                          " Time: " + message[8:10] + ":" + message[10:12] + ":" + message[12:14])
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def pasv(command_connection):
            """
            Используется для установки пассивного режима передачи данных. Отправляет
            серверу команду PASV. Вызывается из метода DataConnection.make_connection.
            :param command_connection: Экземпляр класса CommandConnection.
            :return: Кортеж из элементов: True/False(возможно/невозможно установить соединение),
            ip-адрес, порт.
            """
            command_connection.send_cmd("PASV")
            code, message = command_connection.get_reply()
            if code == 227:
                message = message[message.find("(") + 1:message.rfind(")")]
                split_message = message.split(",")
                ip_address = "{}.{}.{}.{}".format(split_message[0], split_message[1],
                                                  split_message[2], split_message[3])
                port = 256 * int(split_message[4]) + int(split_message[5])
                return True, ip_address, port
            else:
                print("Error: " + message + " Reply code: " + str(code) + ".")
                return False, '', 0

        @staticmethod
        def get_file(command_connection, *file_names):
            """
            Получение файлов с сервера с помощью команды RETR.
            Если файл с каким-либо именем уже существует, то предлагается перезаписать файл.
            :param command_connection: Экземпляр класса CommandConnection.
            :param file_names: файлы, которые нужно получить.
            :return: True - все файлы удалось получить, False - в противном случае.
            """
            all_files_success = True
            for file_name in file_names:
                data_connection = FTPCore.DataConnection()
                make_con_success = data_connection.make_connection(command_connection)
                if not make_con_success:
                    print("Can't establish data connection.")
                    return False
                if os.path.exists(file_name):
                    user_reply = input("File with name '" + file_name +
                                       "' already exists. Do you want to overwrite? [y/n] ")
                    if user_reply != "y":
                        all_files_success = False
                        continue
                command_connection.send_cmd("RETR " + file_name)
                code, message = command_connection.get_reply()
                if code == 150:
                    print("Downloading.. 0%", end='')
                    current_bytes = 0
                    file_size = int(message[message.find("(") + 1:message.rfind(" ")])
                    file = open(file_name, "wb")
                    prev_bytes = 0
                    for data in data_connection.get_data():
                        file.write(data)
                        current_bytes += len(data)
                        prev_bytes = print_progress(prev_bytes, current_bytes, file_size,
                                                    "Downloading")
                    file.close()
                    trans_stat_сode, message = command_connection.get_reply()
                    if trans_stat_сode == 226:
                        print(message)
                        data_connection.close_connection()
                    else:
                        print("Error: " + message + " Reply code: " + str(code) + ".")
                        data_connection.close_connection()
                        all_files_success = False
                else:
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    data_connection.close_connection()
                    all_files_success = False
            return all_files_success

        @staticmethod
        def send_file(command_connection, *file_names):
            """
            Добавляет файлы на сервер с помощью командв STOR.
            :param command_connection: Экземпляр класса CommandConnection.
            :param file_names: имена файлов для загрузки.
            :return: True - все файлы удалось загрузить, False - в противном случае.
            """
            all_files_success = True
            for file_name in file_names:
                data_connection = FTPCore.DataConnection()
                make_con_success = data_connection.make_connection(command_connection)
                if not make_con_success:
                    print("Can't establish data connection.")
                    return False
                if not os.path.exists(file_name):
                    print("File " + file_name + " not found!")
                    all_files_success = False
                    continue
                command_connection.send_cmd("STOR " + file_name[file_name.rfind("/"):])
                code, message = command_connection.get_reply()
                if code == 150:
                    current_bytes = 0
                    file_size = os.path.getsize(file_name)
                    file = open(file_name, "rb")
                    prev_bytes = 0
                    while current_bytes < file_size:
                        data = file.read(1024)
                        data_connection.send_data(data)
                        current_bytes += 1024
                        prev_bytes = print_progress(prev_bytes, current_bytes, file_size, "Sending")
                    file.close()
                    data_connection.close_connection()
                    code, message = command_connection.get_reply()
                    if code == 226:
                        print("File " + file_name + " is upload")
                    else:
                        data_connection.close_connection()
                        print("Error: " + message + " Reply code: " + str(code) + ".")
                        all_files_success = False
                else:
                    data_connection.close_connection()
                    print("Error: " + message + " Reply code: " + str(code) + ".")
                    all_files_success = False
            return all_files_success

        @staticmethod
        def ls(command_connection, folder='', *_):

            """
            Отправляется серверу команду LIST, которая возвращает список файлов и папок в заданной
            директории с подробной информацией о каждом из них.
            :param command_connection:  Экземпляр класса CommandConnection.
            :param folder: папка, информацию о которой необходимо получить.
            :return: True - получение информации прошло успешно, False - в противном случае.
            """
            data_connection = FTPCore.DataConnection()
            make_con_success = data_connection.make_connection(command_connection)
            if not make_con_success:
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
                    data_connection.close_connection()
                    return True
            print("Error: " + message + " Reply code: " + str(code) + ".")
            data_connection.close_connection()
            return False

        @staticmethod
        def dir(command_connection, folder='', *_):

            """
            Отправляет серверу команду NLST, которая возвращает список файлов и папок в заданной
            директории.
            :param command_connection: Экземпляр класса CommandConnection.
            :param folder: папка, информацию о которой необходимо получить.
            :return: True - получение информации прошло успешно, False - в противном случае.
            """
            data_connection = FTPCore.DataConnection()
            make_con_success = data_connection.make_connection(command_connection)
            if not make_con_success:
                return False
            command_connection.send_cmd("NLST " + folder)
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
                    data_connection.close_connection()
                    return True
            print("Error: " + message + " Reply code: " + str(code) + ".")
            data_connection.close_connection()
            return False

        @staticmethod
        def help(*_):
            """
            Выводит все команды, которые возможно отправить серверу.
            """
            with open("help") as file:
                for line in file:
                    print(line)


def print_progress(prev_bytes, current_bytes, number_of_bytes, operation):
    """
    Используется для вывода прогресса загрузки файла на FTP-сервер или его скачивания.
    :param prev_bytes: количество полученных(отправленных) байтов на момент предыдущего вывода
    прогресс-бара.
    :param current_bytes: текущее количество полученных(отправленных) байтов.
    :param number_of_bytes: общее количество байтов, которые необходимо отправить(получить).
    :param operation: строка "Downloadind" или "Sending".
    :return: текущее количество полученных(отправленных) байтов.
    """
    current_ratio = current_bytes / number_of_bytes
    prev_ratio = prev_bytes / number_of_bytes
    if current_ratio >= prev_ratio + 0.02:
        sys.stdout.write("\r{}.. {}%".format(operation, int(current_ratio * 100)))
        sys.stdout.flush()
        prev_bytes = current_bytes
    if current_ratio >= 1.0:
        sys.stdout.write("\r{}.. 100%  \n".format(operation))
        sys.stdout.flush()
    return prev_bytes


class AuthError(Exception):
    pass

# Убрать ответ ls, nls, убрать там лишний пробел
# nls -> dir, поправить документацию к нему(указать, что это простая версия ls)
#