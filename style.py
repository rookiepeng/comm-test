APP_STYLESHEET = """
    QPushButton {
        background-color: #1976D2;
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 3px;
        min-width: 55px;
    }
    QPushButton:hover {
        background-color: #1565C0;
    }
    QPushButton:pressed {
        background-color: #0D47A1;
    }
    QPushButton:disabled {
        background-color: #B0BEC5;
        color: #78909C;
    }

    /* Send buttons — blue (default, already inherited) */

    /* Start / Connect / Open buttons — teal */
    QPushButton#buttonTcpServerStart,
    QPushButton#buttonTcpClientConnect,
    QPushButton#buttonUdpStart,
    QPushButton#buttonBtServerStart,
    QPushButton#buttonBtClientConnect,
    QPushButton#buttonCanStart,
    QPushButton#buttonGpibOpen {
        background-color: #00796B;
    }
    QPushButton#buttonTcpServerStart:hover,
    QPushButton#buttonTcpClientConnect:hover,
    QPushButton#buttonUdpStart:hover,
    QPushButton#buttonBtServerStart:hover,
    QPushButton#buttonBtClientConnect:hover,
    QPushButton#buttonCanStart:hover,
    QPushButton#buttonGpibOpen:hover {
        background-color: #00695C;
    }
    QPushButton#buttonTcpServerStart:pressed,
    QPushButton#buttonTcpClientConnect:pressed,
    QPushButton#buttonUdpStart:pressed,
    QPushButton#buttonBtServerStart:pressed,
    QPushButton#buttonBtClientConnect:pressed,
    QPushButton#buttonCanStart:pressed,
    QPushButton#buttonGpibOpen:pressed {
        background-color: #004D40;
    }

    /* Refresh buttons — grey */
    QPushButton#buttonTcpRefresh,
    QPushButton#buttonUdpRefresh,
    QPushButton#buttonGpibRefresh {
        background-color: #546E7A;
        min-width: 28px;
        padding: 4px 6px;
    }
    QPushButton#buttonTcpRefresh:hover,
    QPushButton#buttonUdpRefresh:hover,
    QPushButton#buttonGpibRefresh:hover {
        background-color: #455A64;
    }
    QPushButton#buttonTcpRefresh:pressed,
    QPushButton#buttonUdpRefresh:pressed,
    QPushButton#buttonGpibRefresh:pressed {
        background-color: #37474F;
    }

    /* Clear button — amber */
    QPushButton#buttonClear {
        background-color: #F57C00;
    }
    QPushButton#buttonClear:hover {
        background-color: #E65100;
    }
    QPushButton#buttonClear:pressed {
        background-color: #BF360C;
    }

    /* Toggle buttons — Echo and Repeat */
    QPushButton#checkBoxTcpServerEcho,
    QPushButton#checkBoxTcpServerSendTimer,
    QPushButton#checkBoxTcpClientSendTimer,
    QPushButton#checkBoxUdpSendTimer {
        background-color: transparent;
        color: #546E7A;
        border: 1px solid #90A4AE;
        padding: 3px 10px;
        margin: 1px;
    }
    QPushButton#checkBoxTcpServerEcho:hover,
    QPushButton#checkBoxTcpServerSendTimer:hover,
    QPushButton#checkBoxTcpClientSendTimer:hover,
    QPushButton#checkBoxUdpSendTimer:hover {
        background-color: #ECEFF1;
        border-color: #607D8B;
        color: #37474F;
    }
    QPushButton#checkBoxTcpServerEcho:checked,
    QPushButton#checkBoxTcpServerSendTimer:checked,
    QPushButton#checkBoxTcpClientSendTimer:checked,
    QPushButton#checkBoxUdpSendTimer:checked {
        background-color: #2E7D32;
        color: white;
        border: 1px solid #1B5E20;
    }
    QPushButton#checkBoxTcpServerEcho:checked:hover,
    QPushButton#checkBoxTcpServerSendTimer:checked:hover,
    QPushButton#checkBoxTcpClientSendTimer:checked:hover,
    QPushButton#checkBoxUdpSendTimer:checked:hover {
        background-color: #1B5E20;
    }
    QTextBrowser {
        font-family: Consolas, "Courier New", monospace;
        font-size: 12px;
        border: 1px solid #c8c8c8;
        border-radius: 4px;
    }
"""
