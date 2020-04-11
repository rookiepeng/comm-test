from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class UDP(QObject):
    status = pyqtSignal(int, object)
    message = pyqtSignal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2

    def __init__(self, ip, port):
        QObject.__init__(self)

        self.ip = ip
        self.port = port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.running = True

    @pyqtSlot()
    def start(self):
        try:
            self.tcp_socket.bind((self.ip, self.port))
        except OSError as err:
            print('emit tcp server error')
            self.status.emit(self.ERROR, '')
        else:
            while self.running:
                # Wait for a connection
                print('wait for a connection')
                self.status.emit(self.LISTEN, '')
                try:
                    data, addr = self.tcp_socket.recvfrom(4096)
                except OSError as err:
                    print(err)
                else:
                    if data:
                        # self.connection.sendall(data)
                        self.message.emit(addr, data.decode())
                    else:
                        break

    def send(self, msg):
        self.connection.sendall(msg.encode())

    def close(self):
        self.tcp_socket.close()
        self.running = False
        self.status.emit(self.ERROR, '')
        print('close socket')
