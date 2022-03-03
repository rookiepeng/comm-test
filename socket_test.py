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
from btserver import BluetoothServer
from btclient import BluetoothClient

import pyvisa as visa

QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class MyApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyApp, self).__init__()

        self.status = dict(
            TCP=dict(
                Server='[SERVER] Idle',
                Client='[CLIENT] Idle',
                Message='[SERVER] Idle ● [CLIENT] Idle'
            ),
            UDP=dict(
                Server='[SERVER] Idle',
                Message='[SERVER] Idle'
            ),
            Bluetooth=dict(
                Server='[SERVER] Idle',
                Client='[CLIENT] Idle',
                Message='[SERVER] Idle ● [CLIENT] Idle'
            ),
            GPIB=dict(
                Message='Idle'
            ),
            About=dict(
                Message=''
            )
        )

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
        ui_file.close()

        self.init_ui()

        # TCP server
        self.ui.comboBoxTcpInterface.currentIndexChanged.connect(
            self.on_tcp_interface_selection_change)
        self.ui.buttonTcpServerStart.clicked.connect(
            self.on_tcp_server_start_stop_button_clicked)
        self.ui.buttonTcpServerSend.clicked.connect(
            self.on_tcp_server_message_send
        )
        self.ui.buttonTcpRefresh.clicked.connect(
            self.on_refresh_button_clicked)
        self.ui.comboBoxTcpServerMessage.lineEdit().returnPressed.connect(
            self.on_tcp_server_message_send
        )

        # TCP client
        self.ui.buttonTcpClientConnect.clicked.connect(
            self.on_tcp_client_connect_button_clicked
        )
        self.ui.buttonTcpClientSend.clicked.connect(
            self.on_tcp_client_message_send
        )
        self.ui.comboBoxTcpClientMessage.lineEdit().returnPressed.connect(
            self.on_tcp_client_message_send
        )

        # UDP
        self.ui.comboBoxUdpInterface.currentIndexChanged.connect(
            self.on_udp_interface_selection_change)
        self.ui.buttonUdpRefresh.clicked.connect(
            self.on_refresh_button_clicked)
        self.ui.buttonUdpStart.clicked.connect(
            self.on_udp_server_start_stop_button_clicked
        )
        self.ui.buttonUdpSend.clicked.connect(
            self.on_udp_message_send
        )

        self.ui.comboBoxUdpMessage.lineEdit().returnPressed.connect(
            self.on_udp_message_send
        )
        self.udp_send = UDPServer(
            '0.0.0.0',
            1234)

        # Bluetooth server
        self.ui.buttonBtServerStart.clicked.connect(
            self.on_bt_server_start_stop_button_clicked)
        self.ui.buttonBtServerSend.clicked.connect(
            self.on_bt_server_message_send
        )
        self.ui.comboBoxBtServerMessage.lineEdit().returnPressed.connect(
            self.on_bt_server_message_send
        )

        # Bluetooth client
        self.ui.buttonBtClientConnect.clicked.connect(
            self.on_bt_client_connect_button_clicked
        )
        self.ui.buttonBtClientSend.clicked.connect(
            self.on_bt_client_message_send
        )
        self.ui.comboBoxBtClientMessage.lineEdit().returnPressed.connect(
            self.on_bt_client_message_send
        )

        # GPIB
        self.ui.button_GpibRefresh.clicked.connect(
            self.on_gpib_refresh_button_clicked)
        self.ui.button_gpib.clicked.connect(
            self.on_gpib_button_clicked
        )
        self.ui.button_GPIBSend.clicked.connect(
            self.on_gpib_message_send
        )
        self.ui.comboBox_GPIBSend.lineEdit().returnPressed.connect(
            self.on_gpib_message_send
        )

        self.ui.tabWidget.currentChanged.connect(
            self.on_tab_changed
        )

        self.ui.buttonClear.clicked.connect(
            self.ui.textBrowserMessage.clear
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
        self.update_gpib_interfaces()

        self.ui.tabWidget.setCurrentIndex(self.config.get('Tab_Index', 0))
        self.on_tab_changed()

        # TCP Server
        self.ui.groupBoxTcpServerMessage.setEnabled(False)
        tcp_server_port = self.config.get('TCP_Server_Port', '1234')
        self.ui.lineEditTcpServerPort.setText(tcp_server_port)

        # TCP Client
        self.ui.groupBoxTcpClientMessage.setEnabled(False)
        tcp_client_ip = self.config.get('TCP_Client_IP', '127.0.0.1')
        tcp_client_port = self.config.get('TCP_Client_Port', '1234')
        self.ui.lineEditTcpTargetIp.setText(tcp_client_ip)
        self.ui.lineEditTcpTargetPort.setText(tcp_client_port)

        # UDP
        udp_listen_port = self.config.get('UDP_Listen_Port', '1234')
        udp_target_ip = self.config.get('UDP_Target_IP', '127.0.0.1')
        udp_target_port = self.config.get('UDP_Target_Port', '1234')
        self.ui.lineEditUdpListenPort.setText(udp_listen_port)
        self.ui.lineEditUdpTargetIp.setText(udp_target_ip)
        self.ui.lineEditUdpTargetPort.setText(udp_target_port)

        # Bluetooth Server
        self.ui.lineEditBtHostMac.setText(
            self.config.get('Bluetooth_Server_MAC', ''))
        self.ui.lineEditBtServerPort.setText(
            self.config.get('Bluetooth_Server_Port', '11'))
        self.ui.groupBoxBtServerMessage.setEnabled(False)

        # Bluetooth Client
        self.ui.lineEditBtTargetMac.setText(
            self.config.get('Bluetooth_Client_MAC', ''))
        self.ui.lineEditBtTargetPort.setText(
            self.config.get('Bluetooth_Client_Port', '11'))
        self.ui.groupBoxBtClientMessage.setEnabled(False)

        # GPIO
        self.ui.comboBox_GPIB_SendType.addItem('Query')
        self.ui.comboBox_GPIB_SendType.addItem('Write')
        # self.ui.comboBox_GPIB_SendType.addItem('Write Binary')
        # self.ui.comboBox_GPIB_SendType.addItem('Query Binary')
        self.ui.groupBox_GpibMessage.setEnabled(False)

    def on_gpib_button_clicked(self):
        self.ui.button_gpib.setEnabled(False)
        if self.ui.button_gpib.text() == 'Open':
            self.device = self.gpib_manager.open_resource(
                self.ui.comboBox_GpibInterface.currentText())
            self.ui.button_gpib.setText('Close')
            self.ui.groupBox_GpibMessage.setEnabled(True)

            self.ui.comboBox_GpibInterface.setEnabled(False)
            self.ui.button_GpibRefresh.setEnabled(False)
        elif self.ui.button_gpib.text() == 'Close':
            self.device.close()
            self.ui.button_gpib.setText('Open')
            self.ui.groupBox_GpibMessage.setEnabled(False)

            self.ui.comboBox_GpibInterface.setEnabled(True)
            self.ui.button_GpibRefresh.setEnabled(True)

        self.ui.button_gpib.setEnabled(True)

    def update_gpib_interfaces(self):
        self.gpib_manager = visa.ResourceManager()
        self.gpib_list = self.gpib_manager.list_resources()

        gpib_interface_idx = self.config.get('GPIBInterface', 0)
        self.ui.comboBox_GpibInterface.clear()
        for if_name in self.gpib_list:
            self.ui.comboBox_GpibInterface.addItem(if_name)

        self.config['GPIBInterface'] = self.ui.comboBox_GpibInterface.currentIndex()

        if len(self.gpib_list) > 0:
            self.gpib_interface = self.gpib_list[gpib_interface_idx]
            self.ui.button_gpib.setEnabled(True)
        else:
            self.gpib_interface = ''
            self.ui.button_gpib.setEnabled(False)

        self.save_config()

    def update_network_interfaces(self):
        temp_net_if = psutil.net_if_addrs()
        self.net_if = psutil.net_if_addrs()

        tcp_interface_idx = self.config.get('TcpInterface', 0)
        self.ui.comboBoxTcpInterface.clear()

        udp_interface_idx = self.config.get('UdpInterface', 0)
        self.ui.comboBoxUdpInterface.clear()

        net_if_stats = psutil.net_if_stats()

        for _, netif in enumerate(temp_net_if):
            if not net_if_stats[netif].isup:
                self.net_if.pop(netif, None)
            else:
                self.ui.comboBoxTcpInterface.addItem(netif)
                self.ui.comboBoxUdpInterface.addItem(netif)

        if tcp_interface_idx >= self.ui.comboBoxTcpInterface.count():
            self.ui.comboBoxTcpInterface.setCurrentIndex(0)
            self.config['TcpInterface'] = 0
        else:
            self.ui.comboBoxTcpInterface.setCurrentIndex(tcp_interface_idx)

        if udp_interface_idx >= self.ui.comboBoxUdpInterface.count():
            self.ui.comboBoxUdpInterface.setCurrentIndex(0)
            self.config['UdpInterface'] = 0
        else:
            self.ui.comboBoxUdpInterface.setCurrentIndex(udp_interface_idx)

        tcp_addr = ''
        for snicaddr in self.net_if[self.ui.comboBoxTcpInterface.currentText()]:
            if snicaddr.family == socket.AF_INET:
                tcp_addr = tcp_addr + 'IPv4: ' + snicaddr.address + ' '
                self.local_tcp_addr = snicaddr.address
                break
            else:
                self.local_tcp_addr = '0.0.0.0'
            # elif snicaddr.family == socket.AF_INET6:
            #     tcp_addr = tcp_addr +'IPv6: ' + snicaddr.address + ' '
        self.ui.labelTcpServerIp.setText(tcp_addr)

        udp_addr = ''
        for snicaddr in self.net_if[self.ui.comboBoxUdpInterface.currentText()]:
            if snicaddr.family == socket.AF_INET:
                udp_addr = udp_addr + 'IPv4: ' + snicaddr.address + ' '
                self.local_udp_addr = snicaddr.address
                break
            else:
                self.local_udp_addr = '0.0.0.0'
            # elif snicaddr.family == socket.AF_INET6:
            #     udp_addr = udp_addr +'IPv6: ' + snicaddr.address + ' '
        self.ui.label_udp_host_address.setText(udp_addr)

        self.save_config()

    def on_tcp_interface_selection_change(self):
        current_interface = self.ui.comboBoxTcpInterface.currentText()

        if current_interface in self.net_if:
            tcp_addr = ''
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    tcp_addr = tcp_addr + 'IPv4: ' + snicaddr.address + ' '
                    self.local_tcp_addr = snicaddr.address
                # elif snicaddr.family == socket.AF_INET6:
                #     tcp_addr = tcp_addr +'IPv6: ' + snicaddr.address + ' '
            self.ui.labelTcpServerIp.setText(tcp_addr)
        else:
            return

        self.config['TcpInterface'] = self.ui.comboBoxTcpInterface.currentIndex()
        self.save_config()

    def on_udp_interface_selection_change(self):
        current_interface = self.ui.comboBoxUdpInterface.currentText()

        if current_interface in self.net_if:
            udp_addr = ''
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    udp_addr = udp_addr + 'IPv4: ' + snicaddr.address + ' '
                    self.local_udp_addr = snicaddr.address
                # elif snicaddr.family == socket.AF_INET6:
                #     udp_addr = udp_addr +'IPv6: ' + snicaddr.address + ' '
            self.ui.label_udp_host_address.setText(udp_addr)
        else:
            return

        self.config['UdpInterface'] = self.ui.comboBoxUdpInterface.currentIndex()
        self.save_config()

    def on_gpib_interface_selection_change(self):
        self.config['GPIBInterface'] = self.ui.comboBoxTcpInterface.currentIndex()

        if len(self.gpib_list) > 0:
            # self.local_tcp_addr = self.gpib_list[self.ui.comboBoxTcpInterface.currentIndex(
            # )]
            self.ui.button_gpib.setEnabled(True)
        else:
            # self.local_tcp_addr = ''
            self.ui.button_gpib.setEnabled(False)
        self.save_config()

    def on_gpib_message_send(self):
        if self.ui.comboBox_GPIB_SendType.currentText() == 'Write':
            self.device.write(self.ui.comboBox_GPIBSend.currentText())
            self.ui.textBrowserMessage.append(
                '<div><strong>— ' +
                '[GPIB] local' +
                ' —</strong></div>')
            self.ui.textBrowserMessage.append(
                '<div>' +
                self.ui.comboBox_GPIBSend.currentText() +
                '<br></div>')
            self.ui.comboBox_GPIBSend.addItem(
                self.ui.comboBox_GPIBSend.currentText())
            self.ui.comboBox_GPIBSend.clearEditText()
        elif self.ui.comboBox_GPIB_SendType.currentText() == 'Query':
            output = self.device.query(self.ui.comboBox_GPIBSend.currentText())
            self.ui.textBrowserMessage.append(
                '<div><strong>— ' +
                '[GPIB] local' +
                ' —</strong></div>')
            self.ui.textBrowserMessage.append(
                '<div>' +
                self.ui.comboBox_GPIBSend.currentText() +
                '<br></div>')
            self.ui.comboBox_GPIBSend.addItem(
                self.ui.comboBox_GPIBSend.currentText())
            self.ui.comboBox_GPIBSend.clearEditText()

            self.ui.textBrowserMessage.append(
                '<div style="color: #2196F3;><strong>— [GPIB] ' +
                self.ui.comboBox_GpibInterface.currentText() +
                ' —</strong></div>')
            self.ui.textBrowserMessage.append(
                '<div style="color: #2196F3;>' +
                output +
                '<br></div>')

    def on_refresh_button_clicked(self):
        self.update_network_interfaces()

    def on_gpib_refresh_button_clicked(self):
        self.update_gpib_interfaces()

    # TCP Client
    def on_tcp_client_connect_button_clicked(self):
        if self.ui.buttonTcpClientConnect.text() == 'Connect':
            self.ui.buttonTcpClientConnect.setEnabled(False)
            self.ui.lineEditTcpTargetIp.setEnabled(False)
            self.ui.lineEditTcpTargetPort.setEnabled(False)

            self.tcp_client_thread = QThread()
            self.tcp_client = TCPClient(
                self.ui.lineEditTcpTargetIp.text(),
                int(self.ui.lineEditTcpTargetPort.text()))

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self.on_tcp_client_status_update)
            self.tcp_client.message.connect(self.on_tcp_client_message_ready)

            self.tcp_client.moveToThread(self.tcp_client_thread)

            self.tcp_client_thread.start()

            self.config['TCP_Client_IP'] = self.ui.lineEditTcpTargetIp.text()
            self.config['TCP_Client_Port'] = self.ui.lineEditTcpTargetPort.text()
            self.save_config()

        elif self.ui.buttonTcpClientConnect.text() == 'Disconnect':
            self.ui.buttonTcpClientConnect.setEnabled(False)
            self.tcp_client.close()

    def on_tcp_client_status_update(self, status, addr):
        if status == TCPClient.STOP:
            self.tcp_client.status.disconnect()
            self.tcp_client.message.disconnect()

            self.ui.buttonTcpClientConnect.setText('Connect')
            self.tcp_client_thread.quit()

            self.ui.lineEditTcpTargetIp.setEnabled(True)
            self.ui.lineEditTcpTargetPort.setEnabled(True)

            self.ui.groupBoxTcpClientMessage.setEnabled(False)
            self.status['TCP']['Client'] = '[CLIENT] Idle'

        elif status == TCPClient.CONNECTED:
            self.ui.buttonTcpClientConnect.setText('Disconnect')

            self.ui.groupBoxTcpClientMessage.setEnabled(True)
            self.status['TCP']['Client'] = '[CLIENT] Connected to ' +\
                self.ui.lineEditTcpTargetIp.text() +\
                ':'+self.ui.lineEditTcpTargetPort.text()

        self.ui.buttonTcpClientConnect.setEnabled(True)
        self.status['TCP']['Message'] = self.status['TCP']['Server'] + \
            ' ● '+self.status['TCP']['Client']
        self.on_tab_changed()

    def on_tcp_client_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [TCP Server] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def on_tcp_client_message_send(self):
        self.tcp_client.send(self.ui.comboBoxTcpClientMessage.currentText())
        self.ui.textBrowserMessage.append(
            '<div><strong>— [TCP Client] ' +
            self.local_tcp_addr +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            self.ui.comboBoxTcpClientMessage.currentText() +
            '<br></div>')
        self.ui.comboBoxTcpClientMessage.addItem(
            self.ui.comboBoxTcpClientMessage.currentText())
        self.ui.comboBoxTcpClientMessage.clearEditText()

    # TCP Server
    def on_tcp_server_start_stop_button_clicked(self):
        if self.ui.buttonTcpServerStart.text() == 'Start':
            self.ui.buttonTcpServerStart.setEnabled(False)
            self.ui.lineEditTcpServerPort.setEnabled(False)
            self.ui.comboBoxTcpInterface.setEnabled(False)
            self.ui.buttonTcpRefresh.setEnabled(False)
            self.tcp_server_thread = QThread()
            self.tcp_server = TCPServer(
                self.local_tcp_addr,
                int(self.ui.lineEditTcpServerPort.text()))

            self.tcp_server_thread.started.connect(self.tcp_server.start)
            self.tcp_server.status.connect(self.on_tcp_server_status_update)
            self.tcp_server.message.connect(self.on_tcp_server_message_ready)

            self.tcp_server.moveToThread(self.tcp_server_thread)

            self.tcp_server_thread.start()

            self.config['TCP_Server_Port'] = self.ui.lineEditTcpServerPort.text()
            self.save_config()

        elif self.ui.buttonTcpServerStart.text() == 'Stop':
            self.ui.buttonTcpServerStart.setEnabled(False)
            self.tcp_server.close()

        elif self.ui.buttonTcpServerStart.text() == 'Disconnect':
            self.ui.buttonTcpServerStart.setEnabled(False)
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

            self.ui.buttonTcpServerStart.setText('Start')
            self.tcp_server_thread.quit()

            self.ui.groupBoxTcpServerMessage.setEnabled(False)
            self.ui.lineEditTcpServerPort.setEnabled(True)
            self.ui.comboBoxTcpInterface.setEnabled(True)
            self.ui.buttonTcpRefresh.setEnabled(True)
            self.status['TCP']['Server'] = '[SERVER] Idle'

        elif status == TCPServer.LISTEN:
            self.ui.buttonTcpServerStart.setText('Stop')

            self.ui.groupBoxTcpServerMessage.setEnabled(False)
            self.status['TCP']['Server'] = '[SERVER] Listen on ' +\
                self.local_tcp_addr+':' +\
                self.ui.lineEditTcpServerPort.text()

        elif status == TCPServer.CONNECTED:
            self.ui.buttonTcpServerStart.setText('Disconnect')

            self.ui.groupBoxTcpServerMessage.setEnabled(True)
            self.status['TCP']['Server'] = '[SERVER] Connected with '+addr

        self.ui.buttonTcpServerStart.setEnabled(True)
        self.status['TCP']['Message'] = self.status['TCP']['Server'] + \
            ' ● '+self.status['TCP']['Client']
        self.on_tab_changed()

    def on_tcp_server_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [TCP Client] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def on_tcp_server_message_send(self):
        self.tcp_server.send(self.ui.comboBoxTcpServerMessage.currentText())
        self.ui.textBrowserMessage.append(
            '<div><strong>— [TCP Server] ' +
            self.local_tcp_addr + ":"+self.ui.lineEditTcpServerPort.text() +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            self.ui.comboBoxTcpServerMessage.currentText() +
            '<br></div>')
        self.ui.comboBoxTcpServerMessage.addItem(
            self.ui.comboBoxTcpServerMessage.currentText())
        self.ui.comboBoxTcpServerMessage.clearEditText()

    # UDP
    def on_udp_server_start_stop_button_clicked(self):
        if self.ui.buttonUdpStart.text() == 'Start':
            self.ui.buttonUdpStart.setEnabled(False)
            self.ui.lineEditUdpListenPort.setEnabled(False)
            self.ui.comboBoxUdpInterface.setEnabled(False)
            self.ui.buttonUdpRefresh.setEnabled(False)
            self.udp_thread = QThread()
            self.udp_server = UDPServer(
                self.local_udp_addr,
                int(self.ui.lineEditUdpListenPort.text()))

            self.udp_thread.started.connect(self.udp_server.start)
            self.udp_server.status.connect(self.on_udp_server_status_update)
            self.udp_server.message.connect(self.on_udp_server_message_ready)

            self.udp_server.moveToThread(self.udp_thread)

            self.udp_thread.start()

            self.config['UDP_Listen_Port'] = self.ui.lineEditUdpListenPort.text()
            self.save_config()

        elif self.ui.buttonUdpStart.text() == 'Stop':
            self.ui.buttonUdpStart.setEnabled(False)
            self.udp_server.close()

    def on_udp_server_status_update(self, status, addr):
        if status == UDPServer.STOP:
            self.udp_server.status.disconnect()
            self.udp_server.message.disconnect()

            self.ui.buttonUdpStart.setText('Start')
            self.udp_thread.quit()

            self.ui.lineEditUdpListenPort.setEnabled(True)
            self.ui.comboBoxUdpInterface.setEnabled(True)
            self.ui.buttonUdpRefresh.setEnabled(True)
            self.status['UDP']['Server'] = '[SERVER] Idle'

        elif status == UDPServer.LISTEN:
            self.ui.buttonUdpStart.setText('Stop')
            self.status['UDP']['Server'] = '[SERVER] Listen on ' +\
                self.local_tcp_addr+':' +\
                self.ui.lineEditTcpServerPort.text()

        self.ui.buttonUdpStart.setEnabled(True)
        self.status['UDP']['Message'] = self.status['UDP']['Server']
        self.on_tab_changed()

    def on_udp_server_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [UDP] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def on_udp_message_send(self):
        self.udp_send.send(
            self.ui.comboBoxUdpMessage.currentText(),
            self.ui.lineEditUdpTargetIp.text(),
            int(self.ui.lineEditUdpTargetPort.text())
        )
        self.ui.textBrowserMessage.append(
            '<div><strong>— [UDP] ' +
            self.local_udp_addr +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            self.ui.comboBoxUdpMessage.currentText() +
            '<br></div>')
        self.ui.comboBoxUdpMessage.addItem(
            self.ui.comboBoxUdpMessage.currentText())
        self.ui.comboBoxUdpMessage.clearEditText()

        self.config['UDP_Target_IP'] = self.ui.lineEditUdpTargetIp.text()
        self.config['UDP_Target_Port'] = self.ui.lineEditUdpTargetPort.text()
        self.save_config()

    # Bluetooth Server
    def on_bt_server_start_stop_button_clicked(self):
        if self.ui.buttonBtServerStart.text() == 'Start':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.ui.lineEditBtServerPort.setEnabled(False)
            self.ui.lineEditBtHostMac.setEnabled(False)
            self.bt_server_thread = QThread()
            self.bt_server = BluetoothServer(
                self.ui.lineEditBtHostMac.text(),
                int(self.ui.lineEditBtServerPort.text()))

            self.bt_server_thread.started.connect(self.bt_server.start)
            self.bt_server.status.connect(self.on_bt_server_status_update)
            self.bt_server.message.connect(self.on_bt_server_message_ready)

            self.bt_server.moveToThread(self.bt_server_thread)

            self.bt_server_thread.start()

            self.config['Bluetooth_Server_MAC'] = self.ui.lineEditBtHostMac.text()
            self.config['Bluetooth_Server_Port'] = self.ui.lineEditBtServerPort.text(
            )
            self.save_config()

        elif self.ui.buttonBtServerStart.text() == 'Stop':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.bt_server.close()

        elif self.ui.buttonBtServerStart.text() == 'Disconnect':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.bt_server.disconnect()

    def on_bt_server_status_update(self, status, addr):
        if status == BluetoothServer.STOP:
            try:
                self.bt_server.status.disconnect()
            except Exception:
                pass
            try:
                self.bt_server.message.disconnect()
            except Exception:
                pass

            self.ui.buttonBtServerStart.setText('Start')
            self.bt_server_thread.quit()

            self.ui.groupBoxBtServerMessage.setEnabled(False)
            self.ui.lineEditBtServerPort.setEnabled(True)
            self.ui.lineEditBtHostMac.setEnabled(True)
            self.status['Bluetooth']['Server'] = '[SERVER] Idle'

        elif status == BluetoothServer.LISTEN:
            self.ui.buttonBtServerStart.setText('Stop')

            self.ui.groupBoxBtServerMessage.setEnabled(False)
            self.status['Bluetooth']['Server'] = '[SERVER] Listen on ' +\
                self.ui.lineEditBtHostMac.text()+' (' +\
                self.ui.lineEditBtServerPort.text()+')'

        elif status == BluetoothServer.CONNECTED:
            self.ui.buttonBtServerStart.setText('Disconnect')

            self.ui.groupBoxBtServerMessage.setEnabled(True)
            self.status['Bluetooth']['Server'] = '[SERVER] Connected to '+addr

        self.ui.buttonBtServerStart.setEnabled(True)
        self.status['Bluetooth']['Message'] = self.status['Bluetooth']['Server'] + \
            ' ● '+self.status['Bluetooth']['Client']
        self.on_tab_changed()

    def on_bt_server_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [Bluetooth Client] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def on_bt_server_message_send(self):
        self.bt_server.send(self.ui.comboBoxBtServerMessage.currentText())
        self.ui.textBrowserMessage.append(
            '<div><strong>— [Bluetooth Server] ' +
            self.ui.lineEditBtTargetMac.text() +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            self.ui.comboBoxBtServerMessage.currentText() +
            '<br></div>')
        self.ui.comboBoxBtServerMessage.addItem(
            self.ui.comboBoxBtServerMessage.currentText())
        self.ui.comboBoxBtServerMessage.clearEditText()

    # Bluetooth Client
    def on_bt_client_connect_button_clicked(self):
        if self.ui.buttonBtClientConnect.text() == 'Connect':
            self.ui.buttonBtClientConnect.setEnabled(False)
            self.ui.lineEditBtTargetMac.setEnabled(False)
            self.ui.lineEditBtTargetPort.setEnabled(False)

            self.bt_client_thread = QThread()
            self.bt_client = BluetoothClient(
                self.ui.lineEditBtTargetMac.text(),
                int(self.ui.lineEditBtTargetPort.text()))

            self.bt_client_thread.started.connect(self.bt_client.start)
            self.bt_client.status.connect(self.on_bt_client_status_update)
            self.bt_client.message.connect(self.on_bt_client_message_ready)

            self.bt_client.moveToThread(self.bt_client_thread)

            self.bt_client_thread.start()

            self.config['Bluetooth_Client_MAC'] = self.ui.lineEditBtTargetMac.text()
            self.config['Bluetooth_Client_Port'] = self.ui.lineEditBtTargetPort.text(
            )
            self.save_config()

        elif self.ui.buttonBtClientConnect.text() == 'Disconnect':
            self.ui.buttonBtClientConnect.setEnabled(False)
            self.bt_client.close()

    def on_bt_client_status_update(self, status, addr):
        if status == BluetoothClient.STOP:
            self.bt_client.status.disconnect()
            self.bt_client.message.disconnect()

            self.ui.buttonBtClientConnect.setText('Connect')
            self.bt_client_thread.quit()

            self.ui.lineEditBtTargetMac.setEnabled(True)
            self.ui.lineEditBtTargetPort.setEnabled(True)

            self.ui.groupBoxBtClientMessage.setEnabled(False)
            self.status['Bluetooth']['Client'] = '[CLIENT] Idle'

        elif status == BluetoothClient.CONNECTED:
            self.ui.buttonBtClientConnect.setText('Disconnect')

            self.ui.groupBoxBtClientMessage.setEnabled(True)
            self.status['Bluetooth']['Client'] = '[CLIENT] Connected to ' +\
                addr +\
                ' ('+self.ui.lineEditBtTargetPort.text()+')'

        self.ui.buttonBtClientConnect.setEnabled(True)
        self.status['Bluetooth']['Message'] = self.status['Bluetooth']['Server'] + \
            ' ● '+self.status['Bluetooth']['Client']
        self.on_tab_changed()

    def on_bt_client_message_ready(self, source, msg):
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;"><strong>— [Bluetooth Server] ' +
            source +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div style="color: #2196F3;">' +
            msg +
            '<br></div>')

    def on_bt_client_message_send(self):
        self.bt_client.send(self.ui.comboBoxBtClientMessage.currentText())
        self.ui.textBrowserMessage.append(
            '<div><strong>— [Bluetooth Client] ' +
            self.ui.lineEditBtHostMac.text() +
            ' —</strong></div>')
        self.ui.textBrowserMessage.append(
            '<div>' +
            self.ui.comboBoxBtClientMessage.currentText() +
            '<br></div>')
        self.ui.comboBoxBtClientMessage.addItem(
            self.ui.comboBoxBtClientMessage.currentText())
        self.ui.comboBoxBtClientMessage.clearEditText()

    def on_tab_changed(self):
        self.ui.status_bar.clearMessage()
        self.ui.status_bar.setStyleSheet('color: green')
        tab_name = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        self.ui.status_bar.showMessage(self.status[tab_name]['Message'])

        self.config['Tab_Index'] = self.ui.tabWidget.currentIndex()
        self.save_config()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    sys.exit(app.exec())
