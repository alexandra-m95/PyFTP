__author__ = 'alexandra'
import unittest
from ftp_core import CommandConnection

class Test01_make_connection(unittest.TestCase):
    def test01_establish_connection(self):
        comm_connection = CommandConnection("88.85.196.86")
        comm_connection.make_connection()





