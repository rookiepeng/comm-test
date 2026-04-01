class GpibHandler:
    """Manages GPIB/VISA UI interactions."""

    def setup_gpib(self):
        """Wire GPIB signals/slots. Call from __init__ after UI is loaded."""
        self.ui.buttonGpibRefresh.clicked.connect(self._update_gpib_interfaces)
        self.ui.buttonGpibOpen.clicked.connect(self._on_gpib_open_close)
        self.ui.buttonGpibSend.clicked.connect(self._on_gpib_send)
        self.ui.comboBoxGpibMessage.lineEdit().returnPressed.connect(
            self._on_gpib_send
        )

    def init_gpib_ui(self):
        """Set initial GPIB UI state from config. Call from init_ui."""
        self.ui.comboBoxGpibSendType.addItem('Query')
        self.ui.comboBoxGpibSendType.addItem('Write')
        self.ui.groupBox_GpibMessage.setEnabled(False)
        self.ui.buttonGpibRefresh.setToolTip('Refresh VISA/GPIB interfaces')
        self._update_gpib_interfaces()

    # --- GPIB interfaces ---

    def _update_gpib_interfaces(self):
        import pyvisa as visa
        try:
            self.gpib_manager = visa.ResourceManager()
            self.gpib_list = self.gpib_manager.list_resources()
        except visa.errors.VisaIOError:
            self.gpib_manager = None
            self.gpib_list = []
        except ValueError:
            self.gpib_manager = None
            self.gpib_list = []

        self.ui.labelGpibUnavailable.setVisible(self.gpib_manager is None)

        gpib_interface_idx = self.config.get('GPIBInterface', 0)
        self.ui.comboBoxGpibInterface.clear()
        for if_name in self.gpib_list:
            self.ui.comboBoxGpibInterface.addItem(if_name)

        self.config['GPIBInterface'] = self.ui.comboBoxGpibInterface.currentIndex()

        if len(self.gpib_list) > 0:
            self.gpib_interface = self.gpib_list[gpib_interface_idx]
            self.ui.buttonGpibOpen.setEnabled(True)
        else:
            self.gpib_interface = ''
            self.ui.buttonGpibOpen.setEnabled(False)

        self.save_config()

    # --- GPIB open/close ---

    def _on_gpib_open_close(self):
        if self.gpib_manager is None:
            return
        self.ui.buttonGpibOpen.setEnabled(False)
        if self.ui.buttonGpibOpen.text() == 'Open':
            self.device = self.gpib_manager.open_resource(
                self.ui.comboBoxGpibInterface.currentText())
            self.ui.buttonGpibOpen.setText('Close')
            self.ui.groupBox_GpibMessage.setEnabled(True)

            self.ui.comboBoxGpibInterface.setEnabled(False)
            self.ui.buttonGpibRefresh.setEnabled(False)

            self.status['GPIB']['Message'] = 'Connected to ' + \
                self.ui.comboBoxGpibInterface.currentText()
        elif self.ui.buttonGpibOpen.text() == 'Close':
            self.device.close()
            self.ui.buttonGpibOpen.setText('Open')
            self.ui.groupBox_GpibMessage.setEnabled(False)

            self.ui.comboBoxGpibInterface.setEnabled(True)
            self.ui.buttonGpibRefresh.setEnabled(True)

            self.status['GPIB']['Message'] = 'Idle'

        self.on_tab_changed()
        self.ui.buttonGpibOpen.setEnabled(True)

    # --- GPIB send ---

    def _on_gpib_send(self):
        if self.ui.comboBoxGpibSendType.currentText() == 'Write':
            self.device.write(self.ui.comboBoxGpibMessage.currentText())
            self._log_message('GPIB', 'local',
                              self.ui.comboBoxGpibMessage.currentText())
            self.ui.comboBoxGpibMessage.addItem(
                self.ui.comboBoxGpibMessage.currentText())
            self.ui.comboBoxGpibMessage.clearEditText()
        elif self.ui.comboBoxGpibSendType.currentText() == 'Query':
            output = self.device.query(
                self.ui.comboBoxGpibMessage.currentText())
            self._log_message('GPIB', 'local',
                              self.ui.comboBoxGpibMessage.currentText())
            self.ui.comboBoxGpibMessage.addItem(
                self.ui.comboBoxGpibMessage.currentText())
            self.ui.comboBoxGpibMessage.clearEditText()
            self._log_message(
                'GPIB', self.ui.comboBoxGpibInterface.currentText(),
                output, incoming=True)
