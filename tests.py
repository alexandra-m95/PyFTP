__author__ = "alexandra"


import unittest

from ftp_core import CommandConnection
from ftp_core import Commands


class FTPTest(unittest.TestCase):
    """
        Функция возвращает True в случае удачного выполнения иначе False
    """
    comm_connection = None

    def test01_establish_connection(self):
        print("%20s:\t" % "Установка соединения", end="")
        FTPTest.comm_connection = CommandConnection("192.168.0.7")
        self.assertTrue(FTPTest.comm_connection.make_connection())

    def test02_noop_before(self):
        print("%20s:\t" % "NOOP", end="")
        self.assertFalse(Commands.noop(FTPTest.comm_connection))

    def test03_login(self):
        print("%20s:\t" % "USER+PASS", end="")
        self.assertTrue(Commands.login(FTPTest.comm_connection, "alexandra", "penguin123"))

    def test04_noop_after(self):
        print("%20s:\t" % "NOOP", end="")
        self.assertTrue(Commands.noop(FTPTest.comm_connection))

    def test05_pwd(self):
        print("%20s:\t" % "PWD", end="")
        Commands.pwd(FTPTest.comm_connection)  # не тестировано

    def test06__connection(self):
        print("%20s:\t" % "Установка соединения", end="")
        FTPTest.comm_connection = CommandConnection("88.85.0.0")
        self.assertTrue(FTPTest.comm_connection.make_connection())






