from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class TCPClient(QObject):
    status = pyqtSignal(int, object)
    message = pyqtSignal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2
    STOP = 3

    SIG_NORMAL = 0
    SIG_STOP = 1
    SIG_DISCONNECT = 2

    def __init__(self, ip, port):
        QObject.__init__(self)

        self.ip = ip
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.settimeout(1)

        self.signal = self.SIG_NORMAL

    @pyqtSlot()
    def start(self):
        try:
            self.tcp_socket.connect((self.ip, self.port))
        except OSError as err:
            self.status.emit(self.STOP, '')
        else:
            print('connected')
            self.status.emit(self.CONNECTED, self.ip)

            while True:
                if self.signal == self.SIG_NORMAL:
                    try:

                        data = self.tcp_socket.recv(4096)
                    except socket.timeout as t_out:
                        pass
                    else:
                        if data:
                            self.message.emit(self.ip, data.decode())
                        else:
                            break
                elif self.signal == self.SIG_DISCONNECT:
                    self.signal = self.SIG_NORMAL
                    self.tcp_socket.close()
                    break
        finally:
            self.status.emit(self.STOP, '')

    def send(self, msg):
        self.tcp_socket.sendall(msg.encode())

    def close(self):
        self.signal = self.SIG_DISCONNECT
