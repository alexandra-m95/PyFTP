__author__ = "alexandra"


import unittest
import os
import sys

from ftp_core import FTPCore


class FTPTest(unittest.TestCase):
    """
        Функция возвращает True в случае удачного выполнения иначе False
    """
    FTPCoreInstance = None

    def test01_establish_connection(self):
        print("%19s:\t" % "Установка соединения", end="")
        FTPTest.FTPCoreInstance = FTPCore("88.85.196.86")
        self.assertTrue(FTPTest.FTPCoreInstance.comm_connection.make_connection())

    def test02_noop_before(self):
        print("%19s:\t" % "NOOP", end="")
        self.assertFalse(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test03_login(self):
        print("%19s:\t" % "USER+PASS", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.login(FTPTest.FTPCoreInstance.comm_connection,
                                                               "alexandra", "penguin123"))

    def test04_noop_after(self):
        print("%19s:\t" % "NOOP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test05_pwd(self):
        print("%19s:\t" % "PWD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.pwd(FTPTest.FTPCoreInstance.comm_connection))

    def test06_mv(self):
        print("%19s:\t" % "RNFR, RNTO", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mv(FTPTest.FTPCoreInstance.comm_connection, "sasha", "tux"))
        null, _stdout = mute_stdout()
        FTPTest.FTPCoreInstance.Commands.mv(FTPTest.FTPCoreInstance.comm_connection, "tux", "sasha")
        unmute_stdout(_stdout, null)

    def test07_mkdir(self):
        print("%19s:\t" % "MKD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mkdir(FTPTest.FTPCoreInstance.comm_connection, "penguin"))

    def test08_rmdir(self):
        print("%19s:\t" % "RMD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.rmdir(FTPTest.FTPCoreInstance.comm_connection, "penguin"))

    def test09_cd(self):
        print("%19s:\t" % "CD", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, "folder1"))

    def test10_cdup(self):
        print("%19s:\t" % "CDUP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.cd(FTPTest.FTPCoreInstance.comm_connection, ".."))

    def test11_size(self):
        print("%19s:\t" % "SIZE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.size(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

    def test12_mdtm(self):
        print("%19s:\t" % "MDTM", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.mdtm(FTPTest.FTPCoreInstance.comm_connection, "sasha"))

    def test13_retr(self):
        print("%19s:\t" % "RETR", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.get_file(FTPTest.FTPCoreInstance.comm_connection, "sasha"))
        os.remove("sasha")

    def test14_noop_after_data_con(self):
        print("%19s:\t" % "NOOP", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.noop(FTPTest.FTPCoreInstance.comm_connection))

    def test15_stor(self):
        print("%19s:\t" % "STOR", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.send_file(FTPTest.FTPCoreInstance.comm_connection, "LICENCE"))

    def test16_rm(self):
        print("%19s:\t" % "DELE", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.rm(FTPTest.FTPCoreInstance.comm_connection, "LICENCE"))

    def test17_list_1(self):
        print("%19s:\t" % "LIST", end="")
        print()
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.ls(FTPTest.FTPCoreInstance.comm_connection))

    def test17_list_2(self):
        print("%19s:\t" % "LIST", end="")
        print()
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.ls(FTPTest.FTPCoreInstance.comm_connection, "folder1"))

    def test19_quit(self):
        print("%19s:\t" % "QUIT", end="")
        self.assertTrue(FTPTest.FTPCoreInstance.Commands.quit(FTPTest.FTPCoreInstance.comm_connection))


def mute_stdout():
    _stdout = sys.stdout
    null = open(os.devnull, "w")
    sys.stdout = null
    return _stdout, null


def unmute_stdout(null, _stdout):
    sys.stdout = _stdout
    null.close()
