from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import socket


class TCPServer(QObject):
    status = pyqtSignal(int, object)
    message = pyqtSignal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2
    STOP = 3

    SIG_NORMAL = 0
    SIG_STOP = 1
    SIG_DISCONNECT = 2

    stop_flag = False

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
            self.tcp_socket.bind((self.ip, self.port))
            self.tcp_socket.listen(1)
        except OSError as err:
            print('emit tcp server error')
            self.status.emit(self.STOP, '')
        else:
            while True:
                # Wait for a connection
                if self.signal == self.SIG_NORMAL:
                    print('wait for a connection')
                    self.status.emit(self.LISTEN, '')
                    try:
                        self.connection, client_address = self.tcp_socket.accept()
                        self.connection.settimeout(1)
                    except socket.timeout as t_out:
                        pass
                        # if self.tcp_socket is None:
                        #     self.running = False
                        #     self.status.emit(self.ERROR, '')
                    except OSError as err:
                        print(err)
                    else:
                        self.status.emit(self.CONNECTED, client_address[0])

                        while True:
                            print('waiting for data')
                            if self.signal == self.SIG_NORMAL:
                                try:
                                    data = self.connection.recv(4096)
                                except socket.timeout as t_out:
                                    pass
                                else:
                                    if data:
                                        # self.connection.sendall(data)
                                        self.message.emit(
                                            client_address[0], data.decode())
                                    else:
                                        break
                            elif self.signal == self.SIG_DISCONNECT:
                                self.signal = self.SIG_NORMAL
                                self.connection.close()
                                # self.receiving = False
                                break
                    # finally:
                    #     # Clean up the connection
                        # print('close connection')
                    #     if self.connection is not None:

                elif self.signal == self.SIG_STOP:
                    self.tcp_socket.close()
                    # self.running = False

                    print('close socket')
                    break
        finally:
            self.status.emit(self.STOP, '')

    def send(self, msg):
        self.connection.sendall(msg.encode())

    def disconnect(self):
        # self.connection.close()
        # self.connection = None
        # print('close connection')
        self.signal = self.SIG_DISCONNECT

    def close(self):
        # self.tcp_socket.close()
        # self.running = False
        # self.stop_flag = True
        # # self.status.emit(self.ERROR, '')
        # print('close socket')
        # dummpy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # dummpy_socket.connect((self.ip, self.port))
        # print('connect to server')

        self.signal = self.SIG_STOP
