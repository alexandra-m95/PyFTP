__author__ = 'alexandra'
import socket


class CommandConnection:
    def __init__(self, serv_address, port=21):
        self.serv_address = serv_address
        self.port = port
        self.command_socket = socket.socket()

    def make_connection(self):
        self.command_socket.connect((self.serv_address, self.port))
        self.reply = self.command_socket.recv(1024)

    def parse_reply(self):
        return (self.reply[:3], self.reply[4:])

    def send_cmd(self, cmd):
        pass

    def get_reply(self):
        pass



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
    def __init__(self):
        pass

    def login(self, user, passwd):
        pass

    def logout(self):
        pass

    def pwd(self):
        pass

    def noop(self):
        pass