from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class UDPServer(QObject):
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
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(1)

        self.signal = self.SIG_NORMAL

    @pyqtSlot()
    def start(self):
        try:
            self.udp_socket.bind((self.ip, self.port))
        except OSError as err:
            self.status.emit(self.STOP, '')
        else:
            while True:
                if self.signal == self.SIG_NORMAL:
                    self.status.emit(self.LISTEN, '')
                    try:
                        data, addr = self.udp_socket.recvfrom(4096)
                    except socket.timeout as t_out:
                        pass
                    else:
                        if data:
                            self.message.emit(
                                addr[0]+':'+str(addr[1]), data.decode())
                        else:
                            break
                elif self.signal == self.SIG_STOP:
                    self.signal = self.SIG_NORMAL
                    self.udp_socket.close()
                    break
        finally:
            self.status.emit(self.STOP, '')

    def send(self, msg, ip, port):
        self.udp_socket.sendto(msg.encode(), (ip, port))

    def close(self):
        self.signal = self.SIG_STOP
