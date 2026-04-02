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
import os
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

import psutil
import socket
from pathlib import Path
import json
from datetime import datetime

from handlers import TcpHandler, UdpHandler, BluetoothHandler, CanHandler, GpibHandler
from style import APP_STYLESHEET

__version__ = "v5.2"


class MyApp(
    QtWidgets.QMainWindow,
    TcpHandler,
    UdpHandler,
    BluetoothHandler,
    CanHandler,
    GpibHandler,
):

    def __init__(self):
        super(MyApp, self).__init__()

        self.net_if = {}
        self.local_tcp_addr = "0.0.0.0"
        self.local_udp_addr = "0.0.0.0"

        self.status = dict(
            TCP=dict(
                Server="[SERVER] Idle",
                Client="[CLIENT] Idle",
                Message="[SERVER] Idle ● [CLIENT] Idle",
            ),
            UDP=dict(Server="[SERVER] Idle", Message="[SERVER] Idle"),
            Bluetooth=dict(
                Server="[SERVER] Idle",
                Client="[CLIENT] Idle",
                Message="[SERVER] Idle ● [CLIENT] Idle",
            ),
            CAN=dict(Message="Idle"),
            GPIB=dict(Message="Idle"),
            About=dict(Message=""),
        )

        config_file = Path("config.json")
        if config_file.exists():
            self.config = json.load(open("config.json", "r"))
        else:
            self.config = dict()
            json.dump(self.config, open("config.json", "w+"))

        ui_file = QFile("mainwindow.ui")
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.init_ui()

        # Wire protocol handlers
        self.setup_tcp()
        self.setup_udp()
        self.setup_bluetooth()
        self.setup_can()
        self.setup_gpib()

        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.ui.buttonClear.clicked.connect(self.ui.textBrowserMessage.clear)
        self.ui.buttonClear.setToolTip("Clear message log")

        self.ui.show()

    def save_config(self):
        try:
            json.dump(self.config, open("config.json", "w+"))
        except PermissionError:
            pass

    def init_ui(self):
        self.update_network_interfaces()

        self.ui.tabWidget.setCurrentIndex(self.config.get("Tab_Index", 0))
        self.on_tab_changed()

        self.ui.label_AppVersion.setText(__version__)

        self.init_tcp_ui()
        self.init_udp_ui()
        self.init_bluetooth_ui()
        self.init_can_ui()
        self.init_gpib_ui()

        # Splitter between tab panel and message browser
        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        central_layout = self.ui.centralWidget().layout()
        splitter.addWidget(self.ui.tabWidget)
        splitter.addWidget(self.ui.groupBox_3)
        splitter.setSizes([480, 440])
        splitter.setHandleWidth(6)
        while central_layout.count():
            central_layout.takeAt(0)
        central_layout.addWidget(splitter)

        # Initialize groupbox border states
        for gb in (
            self.ui.groupBox_14,
            self.ui.groupBox_16,
            self.ui.groupBox_15,
            self.ui.groupBox_8,
            self.ui.groupBox_17,
            self.ui.groupBox_10,
        ):
            self._set_groupbox_state(gb, "idle")

    def _set_groupbox_state(self, groupbox, state):
        _COLORS = {
            "idle": "#bdbdbd",
            "listening": "#FF9800",
            "connected": "#4CAF50",
            "error": "#F44336",
        }
        color = _COLORS.get(state, "#bdbdbd")
        groupbox.setStyleSheet(
            f"QGroupBox {{ border: 1px solid {color}; border-radius: 4px; margin: 3px; margin-top: 10px; padding: 2px; }} "
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}"
        )

    def _log_message(self, label, source, msg, incoming=False):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        ts_html = f'<span style="color:#90A4AE;font-size:small;">[{ts}]</span>'
        if incoming:
            self.ui.textBrowserMessage.append(
                f'<div style="color:#2196F3;">{ts_html} <strong>&#8595; [{label}] {source}</strong><br>{msg}</div>'
            )
        else:
            self.ui.textBrowserMessage.append(
                f"<div>{ts_html} <strong>&#8593; [{label}] {source}</strong><br>{msg}</div>"
            )

    def update_network_interfaces(self):
        temp_net_if = psutil.net_if_addrs()
        self.net_if = psutil.net_if_addrs()

        tcp_interface_idx = self.config.get("TcpInterface", 0)
        self.ui.comboBoxTcpInterface.clear()

        udp_interface_idx = self.config.get("UdpInterface", 0)
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
            self.config["TcpInterface"] = 0
        else:
            self.ui.comboBoxTcpInterface.setCurrentIndex(tcp_interface_idx)

        if udp_interface_idx >= self.ui.comboBoxUdpInterface.count():
            self.ui.comboBoxUdpInterface.setCurrentIndex(0)
            self.config["UdpInterface"] = 0
        else:
            self.ui.comboBoxUdpInterface.setCurrentIndex(udp_interface_idx)

        tcp_addr = ""
        for snicaddr in self.net_if[self.ui.comboBoxTcpInterface.currentText()]:
            if snicaddr.family == socket.AF_INET:
                tcp_addr = tcp_addr + "IPv4: " + snicaddr.address + " "
                self.local_tcp_addr = snicaddr.address
                break
            else:
                self.local_tcp_addr = "0.0.0.0"

        self.ui.labelTcpServerIp.setText(tcp_addr)

        udp_addr = ""
        for snicaddr in self.net_if[self.ui.comboBoxUdpInterface.currentText()]:
            if snicaddr.family == socket.AF_INET:
                udp_addr = udp_addr + "IPv4: " + snicaddr.address + " "
                self.local_udp_addr = snicaddr.address
                break
            else:
                self.local_udp_addr = "0.0.0.0"

        self.ui.labelUdpHostAddress.setText(udp_addr)
        self.save_config()

    def on_tab_changed(self):
        self.ui.status_bar.clearMessage()
        self.ui.status_bar.setStyleSheet("color: green")
        tab_name = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        self.ui.status_bar.showMessage(self.status[tab_name]["Message"])

        self.config["Tab_Index"] = self.ui.tabWidget.currentIndex()
        self.save_config()


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        os.chdir(sys._MEIPASS)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MyApp()
    sys.exit(app.exec())
