from PySide6.QtCore import QThread

from btserver import BluetoothServer
from btclient import BluetoothClient


class BluetoothHandler:
    """Manages Bluetooth server and client UI interactions."""

    def setup_bluetooth(self):
        """Wire Bluetooth signals/slots. Call from __init__ after UI is loaded."""
        self.ui.buttonBtServerStart.clicked.connect(
            self._on_bt_server_start_stop
        )
        self.ui.buttonBtServerSend.clicked.connect(
            self._on_bt_server_send
        )
        self.ui.comboBoxBtServerMessage.lineEdit().returnPressed.connect(
            self._on_bt_server_send
        )

        self.ui.buttonBtClientConnect.clicked.connect(
            self._on_bt_client_connect
        )
        self.ui.buttonBtClientSend.clicked.connect(
            self._on_bt_client_send
        )
        self.ui.comboBoxBtClientMessage.lineEdit().returnPressed.connect(
            self._on_bt_client_send
        )

    def init_bluetooth_ui(self):
        """Set initial Bluetooth UI state from config. Call from init_ui."""
        self.ui.lineEditBtHostMac.setText(
            self.config.get('Bluetooth_Server_MAC', ''))
        self.ui.lineEditBtServerPort.setText(
            self.config.get('Bluetooth_Server_Port', '11'))
        self.ui.groupBoxBtServerMessage.setEnabled(False)

        self.ui.lineEditBtTargetMac.setText(
            self.config.get('Bluetooth_Client_MAC', ''))
        self.ui.lineEditBtTargetPort.setText(
            self.config.get('Bluetooth_Client_Port', '11'))
        self.ui.groupBoxBtClientMessage.setEnabled(False)

    # --- Bluetooth Server ---

    def _on_bt_server_start_stop(self):
        if self.ui.buttonBtServerStart.text() == 'Start':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.ui.lineEditBtServerPort.setEnabled(False)
            self.ui.lineEditBtHostMac.setEnabled(False)
            self.bt_server_thread = QThread()
            self.bt_server = BluetoothServer(
                self.ui.lineEditBtHostMac.text(),
                int(self.ui.lineEditBtServerPort.text()))

            self.bt_server_thread.started.connect(self.bt_server.start)
            self.bt_server.status.connect(self._on_bt_server_status)
            self.bt_server.message.connect(self._on_bt_server_message_ready)

            self.bt_server.moveToThread(self.bt_server_thread)
            self.bt_server_thread.start()

            self.config['Bluetooth_Server_MAC'] = self.ui.lineEditBtHostMac.text()
            self.config['Bluetooth_Server_Port'] = self.ui.lineEditBtServerPort.text()
            self.save_config()

        elif self.ui.buttonBtServerStart.text() == 'Stop':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.bt_server.close()

        elif self.ui.buttonBtServerStart.text() == 'Disconnect':
            self.ui.buttonBtServerStart.setEnabled(False)
            self.bt_server.disconnect()

    def _on_bt_server_status(self, status, addr):
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
            self._set_groupbox_state(self.ui.groupBox_17, 'idle')

        elif status == BluetoothServer.LISTEN:
            self.ui.buttonBtServerStart.setText('Stop')
            self.ui.groupBoxBtServerMessage.setEnabled(False)
            self.status['Bluetooth']['Server'] = '[SERVER] Listen on ' + \
                self.ui.lineEditBtHostMac.text() + ' (' + \
                self.ui.lineEditBtServerPort.text() + ')'
            self._set_groupbox_state(self.ui.groupBox_17, 'listening')

        elif status == BluetoothServer.CONNECTED:
            self.ui.buttonBtServerStart.setText('Disconnect')
            self.ui.groupBoxBtServerMessage.setEnabled(True)
            self.status['Bluetooth']['Server'] = '[SERVER] Connected to ' + addr
            self._set_groupbox_state(self.ui.groupBox_17, 'connected')

        self.ui.buttonBtServerStart.setEnabled(True)
        self.status['Bluetooth']['Message'] = self.status['Bluetooth']['Server'] + \
            ' ● ' + self.status['Bluetooth']['Client']
        self.on_tab_changed()

    def _on_bt_server_message_ready(self, source, msg):
        self._log_message('Bluetooth Client', source, msg, incoming=True)

    def _on_bt_server_send(self):
        self.bt_server.send(self.ui.comboBoxBtServerMessage.currentText())
        self._log_message(
            'Bluetooth Server', self.ui.lineEditBtHostMac.text(),
            self.ui.comboBoxBtServerMessage.currentText())
        self.ui.comboBoxBtServerMessage.addItem(
            self.ui.comboBoxBtServerMessage.currentText())
        self.ui.comboBoxBtServerMessage.clearEditText()

    # --- Bluetooth Client ---

    def _on_bt_client_connect(self):
        if self.ui.buttonBtClientConnect.text() == 'Connect':
            self.ui.buttonBtClientConnect.setEnabled(False)
            self.ui.lineEditBtTargetMac.setEnabled(False)
            self.ui.lineEditBtTargetPort.setEnabled(False)

            self.bt_client_thread = QThread()
            self.bt_client = BluetoothClient(
                self.ui.lineEditBtTargetMac.text(),
                int(self.ui.lineEditBtTargetPort.text()))

            self.bt_client_thread.started.connect(self.bt_client.start)
            self.bt_client.status.connect(self._on_bt_client_status)
            self.bt_client.message.connect(self._on_bt_client_message_ready)

            self.bt_client.moveToThread(self.bt_client_thread)
            self.bt_client_thread.start()

            self.config['Bluetooth_Client_MAC'] = self.ui.lineEditBtTargetMac.text()
            self.config['Bluetooth_Client_Port'] = self.ui.lineEditBtTargetPort.text()
            self.save_config()

        elif self.ui.buttonBtClientConnect.text() == 'Disconnect':
            self.ui.buttonBtClientConnect.setEnabled(False)
            self.bt_client.close()

    def _on_bt_client_status(self, status, addr):
        if status == BluetoothClient.STOP:
            self.bt_client.status.disconnect()
            self.bt_client.message.disconnect()

            self.ui.buttonBtClientConnect.setText('Connect')
            self.bt_client_thread.quit()

            self.ui.lineEditBtTargetMac.setEnabled(True)
            self.ui.lineEditBtTargetPort.setEnabled(True)

            self.ui.groupBoxBtClientMessage.setEnabled(False)
            self.status['Bluetooth']['Client'] = '[CLIENT] Idle'
            self._set_groupbox_state(self.ui.groupBox_10, 'idle')

        elif status == BluetoothClient.CONNECTED:
            self.ui.buttonBtClientConnect.setText('Disconnect')
            self.ui.groupBoxBtClientMessage.setEnabled(True)
            self.status['Bluetooth']['Client'] = '[CLIENT] Connected to ' + \
                addr + ' (' + self.ui.lineEditBtTargetPort.text() + ')'
            self._set_groupbox_state(self.ui.groupBox_10, 'connected')

        self.ui.buttonBtClientConnect.setEnabled(True)
        self.status['Bluetooth']['Message'] = self.status['Bluetooth']['Server'] + \
            ' ● ' + self.status['Bluetooth']['Client']
        self.on_tab_changed()

    def _on_bt_client_message_ready(self, source, msg):
        self._log_message('Bluetooth Server', source, msg, incoming=True)

    def _on_bt_client_send(self):
        self.bt_client.send(self.ui.comboBoxBtClientMessage.currentText())
        self._log_message(
            'Bluetooth Client', self.ui.lineEditBtHostMac.text(),
            self.ui.comboBoxBtClientMessage.currentText())
        self.ui.comboBoxBtClientMessage.addItem(
            self.ui.comboBoxBtClientMessage.currentText())
        self.ui.comboBoxBtClientMessage.clearEditText()
