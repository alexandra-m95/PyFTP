__author__ = "alexandra"


import unittest

from ftp_core import FTPCore


class FTPTest(unittest.TestCase):
    """
        Функция возвращает True в случае удачного выполнения иначе False
    """
    FTPCoreInstance = None

    def test01_establish_connection(self):
        print("%20s:\t" % "Установка соединения", end="")
        FTPTest.FTPCoreInstance = FTPCore("88.85.196.86")
        self.assertTrue(FTPTest.FTPCoreInstance.comm_connection.make_connection())

    def test02_noop_before(self):
        print("%20s:\t" % "NOOP", end="")
        self.assertFalse(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test03_login(self):
        print("%20s:\t" % "USER+PASS", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.login(FTPTest.FTPCoreInstance.comm_connection,
                                                               "alexandra", "penguin123"))

    def test04_noop_after(self):
        print("%20s:\t" % "NOOP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test05_pwd(self):
        print("%20s:\t" % "PWD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.pwd(FTPTest.FTPCoreInstance.comm_connection))

    def test06_mv(self):
        print("%20s:\t" % "RNFR, RNTO", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mv(FTPTest.FTPCoreInstance.comm_connection, "sasha", "tux"))
        FTPTest.FTPCoreInstance.Commands.mv(FTPTest.FTPCoreInstance.comm_connection, "tux", "sasha")

    def test07_mkdir(self):
        print("%20s:\t" % "MKD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mkdir(FTPTest.FTPCoreInstance.comm_connection, "penguin"))

    def test08_rmdir(self):
        print("%20s:\t" % "RMD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.rmdir(FTPTest.FTPCoreInstance.comm_connection, "penguin"))

    def jffghtest09_rm(self):                               # сделать после закачивания файла
        print("%20s:\t" % "DELE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.rm(FTPTest.FTPCoreInstance.comm_connection, "lol"))

    def test10_cd(self):
        print("%20s:\t" % "CD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, "folder1"))

    def test11_cdup(self):
        print("%20s:\t" % "CDUP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, ".."))

    def test12_size(self):
        print("%20s:\t" % "SIZE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.size(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

    def test13_mdtm(self):
        print("%20s:\t" % "MDTM", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mdtm(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

   # def test14_pasv(self):
   #     print("%20s:\t" % "PASV", end="")
   #     self.assertTrue(FTPTest.FTPCoreInstance.Commands.pasv(FTPTest.FTPCoreInstance.comm_connection))

    def test15_retr(self):
        print("%20s:\t" % "RETR", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.get_file(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

  #  def test16_stor(self):
  #      print("%20s:\t" % "STOR", end="")
  #      self.assertTrue(FTPTest.FTPCoreInstance.Commands.send_file(FTPTest.FTPCoreInstance.comm_connection, "olol"))

    def test18__connection(self):
        print("%20s:\t" % "Установка соединения", end="")
        FTPTest.FTPCoreInstance = FTPCore("127.0.0.0")
        self.assertFalse(FTPTest.FTPCoreInstance.comm_connection.make_connection())







