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
from tcpclient import TCPClient
from udp import UDPServer

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
        self.init_ui()

        self.ui.comboBox_Interface.currentIndexChanged.connect(
            self.on_interface_selection_change)
        self.ui.button_Refresh.clicked.connect(self.on_refresh_button_clicked)

        self.ui.button_TcpClient.clicked.connect(
            self.on_tcp_client_connect_button_clicked
        )
        self.ui.button_TcpClientSend.clicked.connect(
            self.on_tcp_client_message_send
        )

        self.ui.button_TcpServer.clicked.connect(
            self.on_tcp_server_start_stop_button_clicked)
        self.ui.button_TcpServerSend.clicked.connect(
            self.on_tcp_server_message_send
        )

        self.ui.button_Udp.clicked.connect(
            self.on_udp_server_start_stop_button_clicked
        )
        self.ui.button_UdpSend.clicked.connect(
            self.on_udp_message_send
        )
        self.udp_send = UDPServer(
                '0.0.0.0',
                1234)

    def init_ui(self):
        # Interface
        self.update_network_interfaces()

        # TCP Client
        self.ui.textBrowser_TcpClientMessage.setEnabled(False)
        self.ui.lineEdit_TcpClientSend.setEnabled(False)
        self.ui.button_TcpClientSend.setEnabled(False)

        self.ui.lineEdit_TcpClientTargetIP.setText('192.168.1.132')
        self.ui.lineEdit_TcpClientTargetPort.setText('1234')

        # TCP Server
        self.ui.textBrowser_TcpServerMessage.setEnabled(False)
        self.ui.lineEdit_TcpServerSend.setEnabled(False)
        self.ui.button_TcpServerSend.setEnabled(False)

        self.ui.lineEdit_TcpServerListenPort.setText('1234')

        # UDP
        self.ui.lineEdit_UdpListenPort.setText('1234')
        self.ui.lineEdit_UdpTargetIP.setText('192.168.1.132')
        self.ui.lineEdit_UdpTargetPort.setText('1234')

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

    # TCP Client
    def on_tcp_client_connect_button_clicked(self):
        if self.ui.button_TcpClient.text() == 'Connect':
            self.ui.button_TcpClient.setEnabled(False)
            self.ui.lineEdit_TcpClientTargetIP.setEnabled(False)
            self.ui.lineEdit_TcpClientTargetPort.setEnabled(False)

            self.tcp_client_thread = QThread()
            self.tcp_client = TCPClient(
                self.ui.label_LocalIP.text(),
                int(self.ui.lineEdit_TcpClientTargetPort.text()))

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self.on_tcp_client_status_update)
            self.tcp_client.message.connect(self.on_tcp_client_message_ready)

            self.tcp_client.moveToThread(self.tcp_client_thread)

            self.tcp_client_thread.start()
        elif self.ui.button_TcpClient.text() == 'Disconnect':
            self.ui.button_TcpClient.setEnabled(False)
            self.tcp_client.close()

    def on_tcp_client_status_update(self, status, addr):
        print('tcp client status')
        if status == TCPClient.STOP:
            self.tcp_client.status.disconnect()
            self.tcp_client.message.disconnect()

            self.ui.button_TcpClient.setText('Connect')
            self.tcp_client_thread.quit()

            self.ui.lineEdit_TcpClientTargetIP.setEnabled(True)
            self.ui.lineEdit_TcpClientTargetPort.setEnabled(True)

            self.ui.textBrowser_TcpClientMessage.setEnabled(False)
            self.ui.lineEdit_TcpClientSend.setEnabled(False)
            self.ui.button_TcpClientSend.setEnabled(False)

        elif status == TCPClient.CONNECTED:
            self.ui.button_TcpClient.setText('Disconnect')

            self.ui.textBrowser_TcpClientMessage.setEnabled(True)
            self.ui.lineEdit_TcpClientSend.setEnabled(True)
            self.ui.button_TcpClientSend.setEnabled(True)

        self.ui.button_TcpClient.setEnabled(True)

    def on_tcp_client_message_ready(self, source, msg):
        self.ui.textBrowser_TcpClientMessage.append(msg)

    def on_tcp_client_message_send(self):
        self.tcp_client.send(self.ui.lineEdit_TcpClientSend.text())
        self.ui.lineEdit_TcpClientSend.clear()

    # TCP Server
    def on_tcp_server_start_stop_button_clicked(self):
        if self.ui.button_TcpServer.text() == 'Start':
            self.ui.button_TcpServer.setEnabled(False)
            self.ui.lineEdit_TcpServerListenPort.setEnabled(False)
            self.tcp_server_thread = QThread()
            self.tcp_server = TCPServer(
                self.ui.label_LocalIP.text(),
                int(self.ui.lineEdit_TcpServerListenPort.text()))

            self.tcp_server_thread.started.connect(self.tcp_server.start)
            self.tcp_server.status.connect(self.on_tcp_server_status_update)
            self.tcp_server.message.connect(self.on_tcp_server_message_ready)

            self.tcp_server.moveToThread(self.tcp_server_thread)

            self.tcp_server_thread.start()

        elif self.ui.button_TcpServer.text() == 'Stop':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.close()

        elif self.ui.button_TcpServer.text() == 'Disconnect':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.disconnect()

    def on_tcp_server_status_update(self, status, addr):
        if status == TCPServer.STOP:
            self.tcp_server.status.disconnect()
            self.tcp_server.message.disconnect()

            self.ui.button_TcpServer.setText('Start')
            # self.tcp_server_thread.terminate()
            self.tcp_server_thread.quit()

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)
            self.ui.lineEdit_TcpServerListenPort.setEnabled(True)

        elif status == TCPServer.LISTEN:
            self.ui.button_TcpServer.setText('Stop')

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)

        elif status == TCPServer.CONNECTED:
            self.ui.button_TcpServer.setText('Disconnect')

            self.ui.textBrowser_TcpServerMessage.setEnabled(True)
            self.ui.lineEdit_TcpServerSend.setEnabled(True)
            self.ui.button_TcpServerSend.setEnabled(True)
            # self.tcp_server.send('Hello World')

        self.ui.button_TcpServer.setEnabled(True)

    def on_tcp_server_message_ready(self, source, msg):
        self.ui.textBrowser_TcpServerMessage.append(msg)

    def on_tcp_server_message_send(self):
        self.tcp_server.send(self.ui.lineEdit_TcpServerSend.text())
        self.ui.lineEdit_TcpServerSend.clear()

    # UDP
    def on_udp_server_start_stop_button_clicked(self):
        if self.ui.button_Udp.text() == 'Start':
            self.ui.button_Udp.setEnabled(False)
            self.ui.lineEdit_UdpListenPort.setEnabled(False)
            self.udp_thread = QThread()
            self.udp_server = UDPServer(
                self.ui.label_LocalIP.text(),
                int(self.ui.lineEdit_UdpListenPort.text()))

            self.udp_thread.started.connect(self.udp_server.start)
            self.udp_server.status.connect(self.on_udp_server_status_update)
            self.udp_server.message.connect(self.on_udp_server_message_ready)

            self.udp_server.moveToThread(self.udp_thread)

            self.udp_thread.start()

        elif self.ui.button_Udp.text() == 'Stop':
            self.ui.button_Udp.setEnabled(False)
            self.udp_server.close()

    def on_udp_server_status_update(self, status, addr):
        if status == UDPServer.STOP:
            self.udp_server.status.disconnect()
            self.udp_server.message.disconnect()

            self.ui.button_Udp.setText('Start')
            # self.tcp_server_thread.terminate()
            self.udp_thread.quit()

            self.ui.lineEdit_UdpListenPort.setEnabled(True)

        elif status == UDPServer.LISTEN:
            self.ui.button_Udp.setText('Stop')

        self.ui.button_Udp.setEnabled(True)

    def on_udp_server_message_ready(self, source, msg):
        self.ui.textBrowser_UdpMessage.append(msg)

    def on_udp_message_send(self):
        self.udp_send.send(
            self.ui.lineEdit_UdpSend.text(),
            self.ui.lineEdit_UdpTargetIP.text(),
            int(self.ui.lineEdit_UdpTargetPort.text())
        )
        self.ui.lineEdit_UdpSend.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
