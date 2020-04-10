# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread

import psutil
import socket

# import os
import time
from pathlib import Path
import json

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        super(QtWidgets.QMainWindow, self).__init__()

        """Load UI"""
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.update_network_interfaces()

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_change)
        self.ui.button_Refresh.clicked.connect(self.on_refresh_button_clicked)

    def update_network_interfaces(self):
        self.ui.comboBox_Interface.clear()
        self.net_if = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        net_names = list(self.net_if.keys())

        for if_name in net_names:
            if not net_if_stats[if_name].isup:
                self.net_if.pop(if_name, None)
            else:
                self.ui.comboBox_Interface.addItem(if_name)

        self.ui.comboBox_Interface.setCurrentIndex(0)
        current_interface = self.ui.comboBox_Interface.currentText()

        for snicaddr in self.net_if[current_interface]:
            if snicaddr.family == socket.AF_INET:
                ipv4_add = snicaddr.address
                break
            else:
                ipv4_add = '0.0.0.0'

        self.ui.label_LocalIP.setText(ipv4_add)

    def on_interface_selection_change(self):
        current_interface = self.ui.comboBox_Interface.currentText()

        if current_interface in self.net_if:
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    ipv4_add = snicaddr.address
                    break
                else:
                    ipv4_add = '0.0.0.0'
        else:
            return

        self.ui.label_LocalIP.setText(ipv4_add)

    def on_refresh_button_clicked(self):
        self.update_network_interfaces()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
