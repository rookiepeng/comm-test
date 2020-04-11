from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class TCPServer(QObject):
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

        self.running = True

    @pyqtSlot()
    def start(self):
        try:
            self.tcp_socket.bind((self.ip, self.port))
            self.tcp_socket.listen(1)

            while self.running:
                # Wait for a connection
                print('wait for a connection')
                self.status.emit(self.LISTEN, '')
                try:
                    self.connection, client_address = self.tcp_socket.accept()

                    self.status.emit(self.CONNECTED, client_address[0])

                    try:
                        # Receive the data in small chunks and retransmit it
                        while True:
                            data = self.connection.recv(4096)

                            if data:
                                # self.connection.sendall(data)
                                self.message.emit(
                                    client_address[0], data.decode())
                            else:
                                break
                    finally:
                        # Clean up the connection
                        print('close connection')
                        if self.connection is not None:
                            self.connection.close()
                except OSError as err:
                    print(err)
                    # if self.tcp_socket is None:
                    #     self.running = False
                    #     self.status.emit(self.ERROR, '')

        except OSError as err:
            # print(err)
            # raise

            print('emit tcp server error')
            self.status.emit(self.ERROR, '')

    def send(self, msg):
        self.connection.sendall(msg.encode())

    def disconnect(self):
        self.connection.close()
        self.connection = None
        print('close connection')

    def close(self):
        self.tcp_socket.close()
        self.running = False
        self.status.emit(self.ERROR, '')
        print('close socket')
