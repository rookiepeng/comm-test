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

from tcpserver import TCPServer

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        super(QtWidgets.QMainWindow, self).__init__()

        self.reconnect = False

        """Load UI"""
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.update_network_interfaces()

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_change)
        self.ui.button_Refresh.clicked.connect(self.on_refresh_button_clicked)

        self.ui.button_TcpServer.clicked.connect(
            self.on_tcp_server_start_stop_button_clicked)

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

    def on_tcp_server_start_stop_button_clicked(self):
        if self.ui.button_TcpServer.text() == 'Start':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server_thread = QThread()
            self.tcp_server = TCPServer(self.ui.label_LocalIP.text(), 505)

            self.tcp_server_thread.started.connect(self.tcp_server.start)
            self.tcp_server.status.connect(self.on_tcp_server_status_update)

            self.tcp_server.moveToThread(self.tcp_server_thread)

            self.tcp_server_thread.start()

        elif self.ui.button_TcpServer.text() == 'Stop':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.close()

        elif self.ui.button_TcpServer.text() == 'Disconnect':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.disconnect()
            self.reconnect = True

    def on_tcp_server_status_update(self, status, addr):
        if status == TCPServer.ERROR:
            self.tcp_server.status.disconnect()
            self.ui.button_TcpServer.setText('Start')
            self.tcp_server_thread.terminate()
            if self.reconnect:
                self.reconnect = False
                self.on_tcp_server_start_stop_button_clicked()
        elif status == TCPServer.LISTEN:
            self.ui.button_TcpServer.setText('Stop')
        elif status == TCPServer.CONNECTED:
            self.ui.button_TcpServer.setText('Disconnect')
            # self.tcp_server.send('Hello World')

        self.ui.button_TcpServer.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
