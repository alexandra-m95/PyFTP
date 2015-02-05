__author__ = 'alexandra'
import socket


class CommandConnection:
    def __init__(self, serv_address, port=21):
        self.serv_address = serv_address
        self.port = port
    def make_connection(self):
        pass

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