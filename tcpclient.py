from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class TCPClient(QObject):
    status = pyqtSignal(int, object)
    message = pyqtSignal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2

    def __init__(self, ip, port):
        QObject.__init__(self)

        self.ip = ip
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @pyqtSlot()
    def start(self):
        try:
            self.tcp_socket.connect((self.ip, self.port))
            print('connected')

            self.status.emit(self.CONNECTED, self.ip)

            try:
                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.tcp_socket.recv(16)

                    if data:
                        self.message.emit(self.ip, data.decode())
                    else:
                        break
            finally:
                # Clean up the connection
                print('close connection')
                self.tcp_socket.close()
        except:
            print('emit error')
            self.status.emit(self.ERROR, '')

    def send(self, msg):
        self.tcp_socket.sendall(msg.encode())

    def close(self):
        self.tcp_socket.close()
        print('close socket')
