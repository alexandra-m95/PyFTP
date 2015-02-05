__author__ = 'alexandra'
import unittest
from ftp_core import CommandConnection
from ftp_core import Commands


class FTPTest(unittest.TestCase):
    """
        Функция возвращает True в случае удачного выполнения иначе False
    """
    comm_connection = None

    def test01_establish_connection(self):
        print("===Установка соединения===")
        FTPTest.comm_connection = CommandConnection("88.85.196.86")
        result = FTPTest.comm_connection.make_connection()
        self.assertTrue(result)

    def test02_noop(self):
        print("===NOOP===")
        Commands.noop(FTPTest.comm_connection)





