from PySide6 import QtCore
from PySide6.QtCore import QThread

from tcpserver import TCPServer
from tcpclient import TCPClient


class TcpHandler:
    """Manages TCP server and client UI interactions."""

    def setup_tcp(self):
        """Wire TCP signals/slots. Call from __init__ after UI is loaded."""
        self.ui.comboBoxTcpInterface.currentIndexChanged.connect(
            self._on_tcp_interface_change
        )
        self.ui.buttonTcpServerStart.clicked.connect(
            self._on_tcp_server_start_stop
        )
        self.ui.buttonTcpServerSend.clicked.connect(
            lambda: self._on_tcp_server_send()
        )
        self.ui.buttonTcpRefresh.clicked.connect(self.update_network_interfaces)
        self.ui.comboBoxTcpServerMessage.lineEdit().returnPressed.connect(
            self._on_tcp_server_send
        )

        self._tcp_server_send_timer = None
        self.ui.spinBoxTcpServerSendTimerInterval.valueChanged.connect(
            self._on_tcp_server_timer_interval_changed
        )
        self.ui.checkBoxTcpServerSendTimer.toggled.connect(
            self._on_tcp_server_timer_toggled
        )
        self.ui.checkBoxTcpServerEcho.setToolTip('Echo received messages back to client')

        self.ui.buttonTcpClientConnect.clicked.connect(
            self._on_tcp_client_connect
        )
        self.ui.buttonTcpClientSend.clicked.connect(
            lambda: self._on_tcp_client_send()
        )
        self.ui.comboBoxTcpClientMessage.lineEdit().returnPressed.connect(
            self._on_tcp_client_send
        )

        self._tcp_client_send_timer = None
        self.ui.spinBoxTcpClientSendTimerInterval.valueChanged.connect(
            self._on_tcp_client_timer_interval_changed
        )
        self.ui.checkBoxTcpClientSendTimer.toggled.connect(
            self._on_tcp_client_timer_toggled
        )

    def init_tcp_ui(self):
        """Set initial TCP UI state from config. Call from init_ui."""
        self.ui.groupBoxTcpServerMessage.setEnabled(False)
        self.ui.lineEditTcpServerPort.setText(
            self.config.get('TCP_Server_Port', '1234'))

        self.ui.groupBoxTcpClientMessage.setEnabled(False)
        self.ui.lineEditTcpTargetIp.setText(
            self.config.get('TCP_Client_IP', '127.0.0.1'))
        self.ui.lineEditTcpTargetPort.setText(
            self.config.get('TCP_Client_Port', '1234'))

        self.ui.buttonTcpRefresh.setToolTip('Refresh network interfaces')
        self.ui.checkBoxTcpServerSendTimer.setToolTip('Repeat last message on a timer')
        self.ui.checkBoxTcpClientSendTimer.setToolTip('Repeat last message on a timer')

    # --- TCP interface ---

    def _on_tcp_interface_change(self):
        import socket
        current_interface = self.ui.comboBoxTcpInterface.currentText()
        if current_interface in self.net_if:
            tcp_addr = ''
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    tcp_addr = tcp_addr + 'IPv4: ' + snicaddr.address + ' '
                    self.local_tcp_addr = snicaddr.address
            self.ui.labelTcpServerIp.setText(tcp_addr)
        else:
            return
        self.config['TcpInterface'] = self.ui.comboBoxTcpInterface.currentIndex()
        self.save_config()

    # --- TCP Server ---

    def _on_tcp_server_start_stop(self):
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
            self.tcp_server.status.connect(self._on_tcp_server_status)
            self.tcp_server.message.connect(self._on_tcp_server_message_ready)

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

    def _on_tcp_server_status(self, status, addr):
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
            self._set_groupbox_state(self.ui.groupBox_14, 'idle')
            self.ui.checkBoxTcpServerSendTimer.setChecked(False)

        elif status == TCPServer.LISTEN:
            self.ui.buttonTcpServerStart.setText('Stop')
            self.ui.groupBoxTcpServerMessage.setEnabled(False)
            self.status['TCP']['Server'] = '[SERVER] Listen on ' + \
                self.local_tcp_addr + ':' + \
                self.ui.lineEditTcpServerPort.text()
            self._set_groupbox_state(self.ui.groupBox_14, 'listening')
            self.ui.checkBoxTcpServerSendTimer.setChecked(False)

        elif status == TCPServer.CONNECTED:
            self.ui.buttonTcpServerStart.setText('Disconnect')
            self.ui.groupBoxTcpServerMessage.setEnabled(True)
            self.status['TCP']['Server'] = '[SERVER] Connected with ' + addr
            self._set_groupbox_state(self.ui.groupBox_14, 'connected')

        self.ui.buttonTcpServerStart.setEnabled(True)
        self.status['TCP']['Message'] = self.status['TCP']['Server'] + \
            ' ● ' + self.status['TCP']['Client']
        self.on_tab_changed()

    def _on_tcp_server_message_ready(self, source, msg):
        self._log_message('TCP Client', source, msg, incoming=True)
        if self.ui.checkBoxTcpServerEcho.isChecked():
            self.tcp_server.send(msg)
            self._log_message(
                'TCP Server',
                f'{self.local_tcp_addr}:{self.ui.lineEditTcpServerPort.text()}',
                msg)

    def _on_tcp_server_send(self, clear_message=True):
        self.tcp_server.send(self.ui.comboBoxTcpServerMessage.currentText())
        self._log_message(
            'TCP Server',
            f'{self.local_tcp_addr}:{self.ui.lineEditTcpServerPort.text()}',
            self.ui.comboBoxTcpServerMessage.currentText())
        if clear_message:
            self.ui.comboBoxTcpServerMessage.addItem(
                self.ui.comboBoxTcpServerMessage.currentText())
            self.ui.comboBoxTcpServerMessage.clearEditText()

    def _on_tcp_server_timer_interval_changed(self, val):
        if self._tcp_server_send_timer:
            self._tcp_server_send_timer.stop()
            self._tcp_server_send_timer.start(
                self.ui.spinBoxTcpServerSendTimerInterval.value())

    def _on_tcp_server_timer_toggled(self, val):
        if val:
            self._tcp_server_send_timer = QtCore.QTimer(self)
            self._tcp_server_send_timer.timeout.connect(
                lambda: self._on_tcp_server_send(False))
            self._tcp_server_send_timer.start(
                self.ui.spinBoxTcpServerSendTimerInterval.value())
        else:
            if self._tcp_server_send_timer:
                self._tcp_server_send_timer.stop()
                self._tcp_server_send_timer = None

    # --- TCP Client ---

    def _on_tcp_client_connect(self):
        if self.ui.buttonTcpClientConnect.text() == 'Connect':
            self.ui.buttonTcpClientConnect.setEnabled(False)
            self.ui.lineEditTcpTargetIp.setEnabled(False)
            self.ui.lineEditTcpTargetPort.setEnabled(False)

            self.tcp_client_thread = QThread()
            self.tcp_client = TCPClient(
                self.ui.lineEditTcpTargetIp.text(),
                int(self.ui.lineEditTcpTargetPort.text()))

            self.tcp_client_thread.started.connect(self.tcp_client.start)
            self.tcp_client.status.connect(self._on_tcp_client_status)
            self.tcp_client.message.connect(self._on_tcp_client_message_ready)

            self.tcp_client.moveToThread(self.tcp_client_thread)
            self.tcp_client_thread.start()

            self.config['TCP_Client_IP'] = self.ui.lineEditTcpTargetIp.text()
            self.config['TCP_Client_Port'] = self.ui.lineEditTcpTargetPort.text()
            self.save_config()

        elif self.ui.buttonTcpClientConnect.text() == 'Disconnect':
            self.ui.buttonTcpClientConnect.setEnabled(False)
            self.tcp_client.close()

    def _on_tcp_client_status(self, status, addr):
        if status == TCPClient.STOP:
            self.tcp_client.status.disconnect()
            self.tcp_client.message.disconnect()

            self.ui.buttonTcpClientConnect.setText('Connect')
            self.tcp_client_thread.quit()

            self.ui.lineEditTcpTargetIp.setEnabled(True)
            self.ui.lineEditTcpTargetPort.setEnabled(True)

            self.ui.groupBoxTcpClientMessage.setEnabled(False)
            self.status['TCP']['Client'] = '[CLIENT] Idle'
            self._set_groupbox_state(self.ui.groupBox_16, 'idle')
            self.ui.checkBoxTcpClientSendTimer.setChecked(False)

        elif status == TCPClient.CONNECTED:
            self.ui.buttonTcpClientConnect.setText('Disconnect')
            self.ui.groupBoxTcpClientMessage.setEnabled(True)
            self.status['TCP']['Client'] = '[CLIENT] Connected to ' + \
                self.ui.lineEditTcpTargetIp.text() + \
                ':' + self.ui.lineEditTcpTargetPort.text()
            self._set_groupbox_state(self.ui.groupBox_16, 'connected')

        self.ui.buttonTcpClientConnect.setEnabled(True)
        self.status['TCP']['Message'] = self.status['TCP']['Server'] + \
            ' ● ' + self.status['TCP']['Client']
        self.on_tab_changed()

    def _on_tcp_client_message_ready(self, source, msg):
        self._log_message('TCP Server', source, msg, incoming=True)

    def _on_tcp_client_send(self, clear_message=True):
        self.tcp_client.send(self.ui.comboBoxTcpClientMessage.currentText())
        self._log_message(
            'TCP Client', self.local_tcp_addr,
            self.ui.comboBoxTcpClientMessage.currentText())
        if clear_message:
            self.ui.comboBoxTcpClientMessage.addItem(
                self.ui.comboBoxTcpClientMessage.currentText())
            self.ui.comboBoxTcpClientMessage.clearEditText()

    def _on_tcp_client_timer_interval_changed(self, val):
        if self._tcp_client_send_timer:
            self._tcp_client_send_timer.stop()
            self._tcp_client_send_timer.start(
                self.ui.spinBoxTcpClientSendTimerInterval.value())

    def _on_tcp_client_timer_toggled(self, val):
        if val:
            self._tcp_client_send_timer = QtCore.QTimer(self)
            self._tcp_client_send_timer.timeout.connect(
                lambda: self._on_tcp_client_send(False))
            self._tcp_client_send_timer.start(
                self.ui.spinBoxTcpClientSendTimerInterval.value())
        else:
            if self._tcp_client_send_timer:
                self._tcp_client_send_timer.stop()
                self._tcp_client_send_timer = None
