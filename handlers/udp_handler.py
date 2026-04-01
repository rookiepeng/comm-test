from PySide6 import QtCore
from PySide6.QtCore import QThread

from udp import UDPServer


class UdpHandler:
    """Manages UDP server and client UI interactions."""

    def setup_udp(self):
        """Wire UDP signals/slots. Call from __init__ after UI is loaded."""
        self.ui.comboBoxUdpInterface.currentIndexChanged.connect(
            self._on_udp_interface_change
        )
        self.ui.buttonUdpRefresh.clicked.connect(self.update_network_interfaces)
        self.ui.buttonUdpStart.clicked.connect(self._on_udp_server_start_stop)
        self.ui.buttonUdpSend.clicked.connect(
            lambda: self._on_udp_send()
        )
        self.ui.comboBoxUdpMessage.lineEdit().returnPressed.connect(
            self._on_udp_send
        )
        self.udp_send = UDPServer('0.0.0.0', 1234)

        self._udp_send_timer = None
        self.ui.spinBoxUdpSendTimerInterval.valueChanged.connect(
            self._on_udp_timer_interval_changed
        )
        self.ui.checkBoxUdpSendTimer.toggled.connect(
            self._on_udp_timer_toggled
        )

    def init_udp_ui(self):
        """Set initial UDP UI state from config. Call from init_ui."""
        self.ui.lineEditUdpListenPort.setText(
            self.config.get('UDP_Listen_Port', '1234'))
        self.ui.lineEditUdpTargetIp.setText(
            self.config.get('UDP_Target_IP', '127.0.0.1'))
        self.ui.lineEditUdpTargetPort.setText(
            self.config.get('UDP_Target_Port', '1234'))

        self.ui.buttonUdpRefresh.setToolTip('Refresh network interfaces')
        self.ui.checkBoxUdpSendTimer.setToolTip('Repeat last message on a timer')

    # --- UDP interface ---

    def _on_udp_interface_change(self):
        import socket
        current_interface = self.ui.comboBoxUdpInterface.currentText()
        if current_interface in self.net_if:
            udp_addr = ''
            for snicaddr in self.net_if[current_interface]:
                if snicaddr.family == socket.AF_INET:
                    udp_addr = udp_addr + 'IPv4: ' + snicaddr.address + ' '
                    self.local_udp_addr = snicaddr.address
            self.ui.labelUdpHostAddress.setText(udp_addr)
        else:
            return
        self.config['UdpInterface'] = self.ui.comboBoxUdpInterface.currentIndex()
        self.save_config()

    # --- UDP Server ---

    def _on_udp_server_start_stop(self):
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
            self.udp_server.status.connect(self._on_udp_server_status)
            self.udp_server.message.connect(self._on_udp_server_message_ready)

            self.udp_server.moveToThread(self.udp_thread)
            self.udp_thread.start()

            self.config['UDP_Listen_Port'] = self.ui.lineEditUdpListenPort.text()
            self.save_config()

        elif self.ui.buttonUdpStart.text() == 'Stop':
            self.ui.buttonUdpStart.setEnabled(False)
            self.udp_server.close()

    def _on_udp_server_status(self, status, addr):
        if status == UDPServer.STOP:
            self.udp_server.status.disconnect()
            self.udp_server.message.disconnect()

            self.ui.buttonUdpStart.setText('Start')
            self.udp_thread.quit()

            self.ui.lineEditUdpListenPort.setEnabled(True)
            self.ui.comboBoxUdpInterface.setEnabled(True)
            self.ui.buttonUdpRefresh.setEnabled(True)
            self.status['UDP']['Server'] = '[SERVER] Idle'
            self._set_groupbox_state(self.ui.groupBox_15, 'idle')

        elif status == UDPServer.LISTEN:
            self.ui.buttonUdpStart.setText('Stop')
            self.status['UDP']['Server'] = '[SERVER] Listen on ' + \
                self.local_udp_addr + ':' + \
                self.ui.lineEditUdpListenPort.text()
            self._set_groupbox_state(self.ui.groupBox_15, 'listening')

        self.ui.buttonUdpStart.setEnabled(True)
        self.status['UDP']['Message'] = self.status['UDP']['Server']
        self.on_tab_changed()

    def _on_udp_server_message_ready(self, source, msg):
        self._log_message('UDP Server', source, msg, incoming=True)

    # --- UDP Send ---

    def _on_udp_send(self, clear_message=True):
        self.udp_send.send(
            self.ui.comboBoxUdpMessage.currentText(),
            self.ui.lineEditUdpTargetIp.text(),
            int(self.ui.lineEditUdpTargetPort.text())
        )
        self._log_message(
            'UDP Client', self.local_udp_addr,
            self.ui.comboBoxUdpMessage.currentText())
        if clear_message:
            self.ui.comboBoxUdpMessage.addItem(
                self.ui.comboBoxUdpMessage.currentText())
            self.ui.comboBoxUdpMessage.clearEditText()

            self.config['UDP_Target_IP'] = self.ui.lineEditUdpTargetIp.text()
            self.config['UDP_Target_Port'] = self.ui.lineEditUdpTargetPort.text()
            self.save_config()

    def _on_udp_timer_interval_changed(self, val):
        if self._udp_send_timer:
            self._udp_send_timer.stop()
            self._udp_send_timer.start(
                self.ui.spinBoxUdpSendTimerInterval.value())

    def _on_udp_timer_toggled(self, val):
        if val:
            self._udp_send_timer = QtCore.QTimer(self)
            self._udp_send_timer.timeout.connect(
                lambda: self._on_udp_send(False))
            self._udp_send_timer.start(
                self.ui.spinBoxUdpSendTimerInterval.value())
        else:
            if self._udp_send_timer:
                self._udp_send_timer.stop()
                self._udp_send_timer = None
