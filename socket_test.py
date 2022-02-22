"""
    Copyright (C) 2017 - PRESENT  Zhengyu Peng, https://zpeng.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    ----------

    `                      `
    -:.                  -#:
    -//:.              -###:
    -////:.          -#####:
    -/:.://:.      -###++##:
    ..   `://:-  -###+. :##:
           `:/+####+.   :##:
    .::::::::/+###.     :##:
    .////-----+##:    `:###:
     `-//:.   :##:  `:###/.
       `-//:. :##:`:###/.
         `-//:+######/.
           `-/+####/.
             `+##+.
              :##:
              :##:
              :##:
              :##:
              :##:
               .+:

"""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread, QFile
from PySide6.QtUiTools import QUiLoader

import psutil
import socket

from pathlib import Path
import json

from tcpserver import TCPServer
from tcpclient import TCPClient
from udp import UDPServer

import pyvisa as visa

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyApp, self).__init__()

        self.status_message = ['● Idle', '● Idle',
                               '● Idle', '● Idle', '● Idle', '']

        config_file = Path('config.json')

        if config_file.exists():
            self.config = json.load(open('config.json', 'r'))
        else:
            self.config = dict()
            json.dump(self.config, open('config.json', 'w+'))

        """Load UI"""
        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        # self.ui = uic.loadUi('mainwindow.ui', self)
        ui_file.close()
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
        self.ui.lineEdit_TcpClientSend.returnPressed.connect(
            self.on_tcp_client_message_send
        )

        self.ui.button_TcpServer.clicked.connect(
            self.on_tcp_server_start_stop_button_clicked)
        self.ui.button_TcpServerSend.clicked.connect(
            self.on_tcp_server_message_send
        )
        self.ui.lineEdit_TcpServerSend.returnPressed.connect(
            self.on_tcp_server_message_send
        )

        self.ui.button_Udp.clicked.connect(
            self.on_udp_server_start_stop_button_clicked
        )
        self.ui.button_UdpSend.clicked.connect(
            self.on_udp_message_send
        )
        self.ui.lineEdit_UdpSend.returnPressed.connect(
            self.on_udp_message_send
        )
        self.udp_send = UDPServer(
            '0.0.0.0',
            1234)

        self.ui.button_gpib.clicked.connect(
            self.on_gpib_button_clicked
        )

        self.ui.tabWidget.currentChanged.connect(
            self.on_tab_changed
        )

        self.ui.show()

    def save_config(self):
        try:
            json.dump(self.config, open('config.json', 'w+'))
        except PermissionError as err:
            pass

    def init_ui(self):
        # Interface
        self.update_network_interfaces()

        self.ui.tabWidget.setCurrentIndex(self.config.get('Tab_Index', 0))
        self.on_tab_changed(self.config.get('Tab_Index', 0))

        # TCP Client
        self.ui.textBrowser_TcpClientMessage.setEnabled(False)
        self.ui.lineEdit_TcpClientSend.setEnabled(False)
        self.ui.button_TcpClientSend.setEnabled(False)

        tcp_client_ip = self.config.get('TCP_Client_IP', '127.0.0.1')
        tcp_client_port = self.config.get('TCP_Client_Port', '1234')
        self.ui.lineEdit_TcpClientTargetIP.setText(tcp_client_ip)
        self.ui.lineEdit_TcpClientTargetPort.setText(tcp_client_port)

        # TCP Server
        self.ui.textBrowser_TcpServerMessage.setEnabled(False)
        self.ui.lineEdit_TcpServerSend.setEnabled(False)
        self.ui.button_TcpServerSend.setEnabled(False)

        tcp_server_port = self.config.get('TCP_Server_Port', '1234')
        self.ui.lineEdit_TcpServerListenPort.setText(tcp_server_port)

        # UDP
        udp_listen_port = self.config.get('UDP_Listen_Port', '1234')
        udp_target_ip = self.config.get('UDP_Target_IP', '127.0.0.1')
        udp_target_port = self.config.get('UDP_Target_Port', '1234')
        self.ui.lineEdit_UdpListenPort.setText(udp_listen_port)
        self.ui.lineEdit_UdpTargetIP.setText(udp_target_ip)
        self.ui.lineEdit_UdpTargetPort.setText(udp_target_port)

        # GPIO
        self.ui.comboBox_GPIB_SendType.addItem('Write ASCII')
        self.ui.comboBox_GPIB_SendType.addItem('Query ASCII')
        self.ui.comboBox_GPIB_SendType.addItem('Write Binary')
        self.ui.comboBox_GPIB_SendType.addItem('Query Binary')
        self.ui.textBrowser_GPIBMessage.setEnabled(False)
        self.ui.comboBox_GPIB_SendType.setEnabled(False)
        self.ui.lineEdit_GPIBSend.setEnabled(False)
        self.ui.button_GPIBSend.setEnabled(False)

    def on_gpib_button_clicked(self):
        self.ui.button_gpib.setEnabled(False)
        if self.ui.button_gpib.text() == 'Open device':
            self.device = self.gpib_manager.open_resource(
                self.ui.comboBox_Interface.currentText())
            self.ui.button_gpib.setText('Close device')
        elif self.ui.button_gpib.text() == 'Close device':
            self.device.close()
            self.ui.button_gpib.setText('Open device')

        self.ui.button_gpib.setEnabled(True)

    def update_network_interfaces(self):
        self.net_if = psutil.net_if_addrs()

        self.gpib_manager = visa.ResourceManager()
        self.gpib_list = self.gpib_manager.list_resources()

        if self.ui.tabWidget.currentIndex() < 3:
            interface_idx = self.config.get('Interface', 0)
            self.ui.comboBox_Interface.clear()

            net_names = list(self.net_if.keys())
            net_if_stats = psutil.net_if_stats()

            for if_name in net_names:
                if not net_if_stats[if_name].isup:
                    self.net_if.pop(if_name, None)
                else:
                    self.ui.comboBox_Interface.addItem(if_name)

            if interface_idx >= self.ui.comboBox_Interface.count():
                self.ui.comboBox_Interface.setCurrentIndex(0)
            else:
                self.ui.comboBox_Interface.setCurrentIndex(interface_idx)

            current_interface = self.ui.comboBox_Interface.currentText()
            self.config['Interface'] = self.ui.comboBox_Interface.currentIndex()

            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    ipv4_add = snicaddr.address
                    break
                else:
                    ipv4_add = '0.0.0.0'

            self.ui.label_LocalIP.setText(ipv4_add)

            self.save_config()
        elif self.ui.tabWidget.currentIndex() == 5:
            interface_idx = self.config.get('GPIBInterface', 0)
            self.ui.comboBox_Interface.clear()

            for if_name in self.gpib_list:
                self.ui.comboBox_Interface.addItem(if_name)

            if interface_idx >= self.ui.comboBox_Interface.count():
                self.ui.comboBox_Interface.setCurrentIndex(0)
            else:
                self.ui.comboBox_Interface.setCurrentIndex(interface_idx)

            self.config['GPIBInterface'] = self.ui.comboBox_Interface.currentIndex()

            if len(self.gpib_list) > 0:
                self.ui.label_LocalIP.setText(self.gpib_list[interface_idx])
                self.ui.button_gpib.setEnabled(True)
            else:
                self.ui.label_LocalIP.setText('')
                self.ui.button_gpib.setEnabled(False)

            self.save_config()

    def on_interface_selection_change(self):
        if self.ui.tabWidget.currentIndex() < 3:
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
            self.config['Interface'] = self.ui.comboBox_Interface.currentIndex()
            self.save_config()
        elif self.ui.tabWidget.currentIndex() == 5:
            self.config['GPIBInterface'] = self.ui.comboBox_Interface.currentIndex()

            if len(self.gpib_list) > 0:
                self.ui.label_LocalIP.setText(
                    self.gpib_list[self.ui.comboBox_Interface.currentIndex()])
                self.ui.button_gpib.setEnabled(True)
            else:
                self.ui.label_LocalIP.setText('')
                self.ui.button_gpib.setEnabled(False)

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
                self.ui.lineEdit_TcpClientTargetIP.text(),
                int(self.ui.lineEdit_TcpClientTargetPort.text()))

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self.on_tcp_client_status_update)
            self.tcp_client.message.connect(self.on_tcp_client_message_ready)

            self.tcp_client.moveToThread(self.tcp_client_thread)

            self.tcp_client_thread.start()

            self.config['TCP_Client_IP'] = self.ui.lineEdit_TcpClientTargetIP.text()
            self.config['TCP_Client_Port'] = self.ui.lineEdit_TcpClientTargetPort.text()
            self.save_config()

        elif self.ui.button_TcpClient.text() == 'Disconnect':
            self.ui.button_TcpClient.setEnabled(False)
            self.tcp_client.close()

    def on_tcp_client_status_update(self, status, addr):
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
            self.status_message[0] = '● Idle'
            if self.ui.tabWidget.currentIndex() == 0:
                self.on_tab_changed(0)

        elif status == TCPClient.CONNECTED:
            self.ui.button_TcpClient.setText('Disconnect')

            self.ui.textBrowser_TcpClientMessage.setEnabled(True)
            self.ui.lineEdit_TcpClientSend.setEnabled(True)
            self.ui.button_TcpClientSend.setEnabled(True)
            self.status_message[0] = '● Connected to ' +\
                self.ui.label_LocalIP.text() +\
                ':'+self.ui.lineEdit_TcpClientTargetPort.text()
            if self.ui.tabWidget.currentIndex() == 0:
                self.on_tab_changed(0)

        self.ui.button_TcpClient.setEnabled(True)

    def on_tcp_client_message_ready(self, source, msg):
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;"><strong>----- ' +
            source +
            ' -----</strong></span></p>')
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;">' +
            msg +
            '</span></p>')

    def on_tcp_client_message_send(self):
        self.tcp_client.send(self.ui.lineEdit_TcpClientSend.text())
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;"><strong>----- ' +
            'this' +
            ' -----</strong></p>')
        self.ui.textBrowser_TcpClientMessage.append(
            '<p style="text-align: center;">' +
            self.ui.lineEdit_TcpClientSend.text() +
            '</p>')
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

            self.config['TCP_Server_Port'] = self.ui.lineEdit_TcpServerListenPort.text()
            self.save_config()

        elif self.ui.button_TcpServer.text() == 'Stop':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.close()

        elif self.ui.button_TcpServer.text() == 'Disconnect':
            self.ui.button_TcpServer.setEnabled(False)
            self.tcp_server.disconnect()

    def on_tcp_server_status_update(self, status, addr):
        if status == TCPServer.STOP:
            try:
                self.tcp_server.status.disconnect()
            except Exception:
                pass
            try:
                self.tcp_server.message.disconnect()
            except Exception:
                pass

            self.ui.button_TcpServer.setText('Start')
            self.tcp_server_thread.quit()

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)
            self.ui.lineEdit_TcpServerListenPort.setEnabled(True)
            self.status_message[1] = '● Idle'
            if self.ui.tabWidget.currentIndex() == 1:
                self.on_tab_changed(1)

        elif status == TCPServer.LISTEN:
            self.ui.button_TcpServer.setText('Stop')

            self.ui.textBrowser_TcpServerMessage.setEnabled(False)
            self.ui.lineEdit_TcpServerSend.setEnabled(False)
            self.ui.button_TcpServerSend.setEnabled(False)
            self.status_message[1] = '● Listen on ' +\
                self.ui.label_LocalIP.text()+':' +\
                self.ui.lineEdit_TcpServerListenPort.text()
            if self.ui.tabWidget.currentIndex() == 1:
                self.on_tab_changed(1)

        elif status == TCPServer.CONNECTED:
            self.ui.button_TcpServer.setText('Disconnect')

            self.ui.textBrowser_TcpServerMessage.setEnabled(True)
            self.ui.lineEdit_TcpServerSend.setEnabled(True)
            self.ui.button_TcpServerSend.setEnabled(True)
            self.status_message[1] = '● Connected to '+addr
            if self.ui.tabWidget.currentIndex() == 1:
                self.on_tab_changed(1)
            # self.tcp_server.send('Hello World')

        self.ui.button_TcpServer.setEnabled(True)

    def on_tcp_server_message_ready(self, source, msg):
        self.ui.textBrowser_TcpServerMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;"><strong>----- ' +
            source +
            ' -----</strong></span></p>')
        self.ui.textBrowser_TcpServerMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;">' +
            msg +
            '</span></p>')

    def on_tcp_server_message_send(self):
        self.tcp_server.send(self.ui.lineEdit_TcpServerSend.text())
        self.ui.textBrowser_TcpServerMessage.append(
            '<p style="text-align: center;"><strong>----- ' +
            'this' +
            ' -----</strong></p>')
        self.ui.textBrowser_TcpServerMessage.append(
            '<p style="text-align: center;">' +
            self.ui.lineEdit_TcpServerSend.text() +
            '</p>')
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

            self.config['UDP_Listen_Port'] = self.ui.lineEdit_UdpListenPort.text()
            self.save_config()

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
            self.status_message[2] = '● Idle'
            if self.ui.tabWidget.currentIndex() == 2:
                self.on_tab_changed(2)

        elif status == UDPServer.LISTEN:
            self.ui.button_Udp.setText('Stop')
            self.status_message[2] = '● Listen on ' +\
                self.ui.label_LocalIP.text()+':' +\
                self.ui.lineEdit_TcpServerListenPort.text()
            if self.ui.tabWidget.currentIndex() == 2:
                self.on_tab_changed(2)

        self.ui.button_Udp.setEnabled(True)

    def on_udp_server_message_ready(self, source, msg):
        self.ui.textBrowser_UdpMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;"><strong>----- ' +
            source +
            ' -----</strong></span></p>')
        self.ui.textBrowser_UdpMessage.append(
            '<p style="text-align: center;"><span style="color: #2196F3;">' +
            msg +
            '</span></p>')

    def on_udp_message_send(self):
        self.udp_send.send(
            self.ui.lineEdit_UdpSend.text(),
            self.ui.lineEdit_UdpTargetIP.text(),
            int(self.ui.lineEdit_UdpTargetPort.text())
        )
        self.ui.textBrowser_UdpMessage.append(
            '<p style="text-align: center;"><strong>----- ' +
            'this' +
            ' -----</strong></p>')
        self.ui.textBrowser_UdpMessage.append(
            '<p style="text-align: center;">' +
            self.ui.lineEdit_UdpSend.text() +
            '</p>')
        self.ui.lineEdit_UdpSend.clear()

        self.config['UDP_Target_IP'] = self.ui.lineEdit_UdpTargetIP.text()
        self.config['UDP_Target_Port'] = self.ui.lineEdit_UdpTargetPort.text()
        self.save_config()

    def on_tab_changed(self, index):
        self.update_network_interfaces()
        self.ui.status_bar.clearMessage()
        self.ui.status_bar.setStyleSheet('color: green')
        self.ui.status_bar.showMessage(self.status_message[index])

        self.config['Tab_Index'] = self.ui.tabWidget.currentIndex()
        self.save_config()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    sys.exit(app.exec())
