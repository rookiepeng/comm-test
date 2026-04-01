from PySide6.QtCore import QThread

try:
    from canbus import CanBus
    _CAN_AVAILABLE = True
except ImportError:
    _CAN_AVAILABLE = False


class CanHandler:
    """Manages CAN bus UI interactions."""

    def setup_can(self):
        """Wire CAN signals/slots. Call from __init__ after UI is loaded."""
        self.ui.buttonCanStart.clicked.connect(self._on_can_start_stop)
        self.ui.buttonCanSend.clicked.connect(self._on_can_send)
        self.ui.lineEditCanData.returnPressed.connect(self._on_can_send)

    def init_can_ui(self):
        """Set initial CAN UI state from config. Call from init_ui."""
        self.ui.groupBox_CanMessage.setEnabled(False)
        self.ui.lineEditCanChannel.setText(
            self.config.get('CAN_Channel', ''))
        self.ui.comboBoxCanBusType.setCurrentIndex(
            self.config.get('CAN_BusType_Idx', 0))
        self.ui.comboBoxCanBitrate.setCurrentIndex(
            self.config.get('CAN_Bitrate_Idx', 2))
        self.ui.checkBoxCanExtendedId.setToolTip('Use 29-bit extended CAN ID')

    # --- CAN ---

    def _on_can_start_stop(self):
        if self.ui.buttonCanStart.text() == 'Start':
            self.ui.buttonCanStart.setEnabled(False)
            self.ui.comboBoxCanBusType.setEnabled(False)
            self.ui.lineEditCanChannel.setEnabled(False)
            self.ui.comboBoxCanBitrate.setEnabled(False)

            if not _CAN_AVAILABLE:
                self.status['CAN']['Message'] = 'python-can not installed'
                self.on_tab_changed()
                self.ui.buttonCanStart.setEnabled(True)
                self.ui.comboBoxCanBusType.setEnabled(True)
                self.ui.lineEditCanChannel.setEnabled(True)
                self.ui.comboBoxCanBitrate.setEnabled(True)
                return

            self.can_thread = QThread()
            self.can_bus = CanBus(
                self.ui.comboBoxCanBusType.currentText(),
                self.ui.lineEditCanChannel.text(),
                self.ui.comboBoxCanBitrate.currentText()
            )
            self.can_thread.started.connect(self.can_bus.start)
            self.can_bus.status.connect(self._on_can_status)
            self.can_bus.message.connect(self._on_can_message_ready)
            self.can_bus.moveToThread(self.can_thread)
            self.can_thread.start()

            self.config['CAN_Channel'] = self.ui.lineEditCanChannel.text()
            self.config['CAN_BusType_Idx'] = self.ui.comboBoxCanBusType.currentIndex()
            self.config['CAN_Bitrate_Idx'] = self.ui.comboBoxCanBitrate.currentIndex()
            self.save_config()

        elif self.ui.buttonCanStart.text() == 'Stop':
            self.ui.buttonCanStart.setEnabled(False)
            self.can_bus.close()

    def _on_can_status(self, status, info):
        if status == CanBus.STOP:
            try:
                self.can_bus.status.disconnect()
                self.can_bus.message.disconnect()
            except Exception:
                pass
            self.ui.buttonCanStart.setText('Start')
            self.can_thread.quit()
            self.ui.comboBoxCanBusType.setEnabled(True)
            self.ui.lineEditCanChannel.setEnabled(True)
            self.ui.comboBoxCanBitrate.setEnabled(True)
            self.ui.groupBox_CanMessage.setEnabled(False)
            if info:
                self.status['CAN']['Message'] = f'Error: {info}'
            else:
                self.status['CAN']['Message'] = 'Idle'

        elif status == CanBus.CONNECTED:
            self.ui.buttonCanStart.setText('Stop')
            self.ui.groupBox_CanMessage.setEnabled(True)
            self.status['CAN']['Message'] = (
                f'Connected — {self.ui.comboBoxCanBusType.currentText()} '
                f'{self.ui.lineEditCanChannel.text()} '
                f'@ {self.ui.comboBoxCanBitrate.currentText()} bps'
            )

        self.ui.buttonCanStart.setEnabled(True)
        self.on_tab_changed()

    def _on_can_message_ready(self, arb_id, data):
        self._log_message('CAN RX', f'Arb ID: {arb_id}', data, incoming=True)

    def _on_can_send(self):
        arb_id = self.ui.lineEditCanArbId.text().strip()
        data = self.ui.lineEditCanData.text().strip()
        extended = self.ui.checkBoxCanExtendedId.isChecked()
        if not arb_id:
            return
        self.can_bus.send(arb_id, data, extended)
        self._log_message('CAN TX', f'Arb ID: {arb_id}', data)
