__author__ = "alexandra"


import unittest
import os

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
                                                                "alexandra", "penguin123", True))

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


    def test09_cd(self):
        print("%20s:\t" % "CD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, "folder1"))

    def test10_cdup(self):
        print("%20s:\t" % "CDUP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, ".."))

    def test11_size(self):
        print("%20s:\t" % "SIZE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.size(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

    def test12_mdtm(self):
        print("%20s:\t" % "MDTM", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mdtm(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

    def test13_noop_after_data_con(self):
        print("%20s:\t" % "NOOP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test14_stor(self):
        print("%20s:\t" % "STOR", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.send_file(FTPTest.FTPCoreInstance.comm_connection, "Test/7777log"))

    def test15_retr(self):
        print("%20s:\t" % "RETR", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.get_file(FTPTest.FTPCoreInstance.comm_connection, "7777log"))
        os.remove("7777log")

    def test16_rm(self):
        print("%20s:\t" % "DELE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.rm(FTPTest.FTPCoreInstance.comm_connection, "7777log"))

    def test17_list_1(self):
        print("%20s:\t" % "LIST", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.ls(FTPTest.FTPCoreInstance.comm_connection))

    def test18_list_2(self):
        print("%20s:\t" % "NLST", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.ls(FTPTest.FTPCoreInstance.comm_connection, "folder1"))

    def test19_quit(self):
        print("%20s:\t" % "QUIT", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.quit(FTPTest.FTPCoreInstance.comm_connection))

    def test20_connection(self):
        print("%20s:\t" % "Установка соединения", end="")
        FTPTest.FTPCoreInstance = FTPCore("127.0.0.0")
        self.assertFalse(FTPTest.FTPCoreInstance.comm_connection.make_connection())
