"""
    Copyright (C) 2017 - 2021  Zhengyu Peng, https://zpeng.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    ----------

    `                      `
    -:.                  -#:
    -//:.              -###:
    -////:.          -#####:
    -/:.://:.      -###++##:
    ..   `://:-  -###+. :##:
           `:/+####+.   :##:
    .::::::::/+###.     :##:
    .////-----+##:    `:###:
     `-//:.   :##:  `:###/.
       `-//:. :##:`:###/.
         `-//:+######/.
           `-/+####/.
             `+##+.
              :##:
              :##:
              :##:
              :##:
              :##:
               .+:

"""

from PySide6.QtCore import QObject, Signal, Slot
import socket


class BluetoothServer(QObject):
    status = Signal(int, object)
    message = Signal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2
    STOP = 3

    SIG_NORMAL = 0
    SIG_STOP = 1
    SIG_DISCONNECT = 2

    def __init__(self, mac, port):
        QObject.__init__(self)

        self.mac = mac
        self.port = port
        self.bt_socket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.bt_socket.settimeout(1)

        self.signal = self.SIG_NORMAL

    @Slot()
    def start(self):
        try:
            self.bt_socket.bind((self.mac, self.port))
            self.bt_socket.listen(1)
        except OSError as err:
            print(err)
            # print('emit tcp server error')
            # self.status.emit(self.STOP, '')
            pass
        else:
            self.status.emit(self.LISTEN, '')
            while True:
                # Wait for a connection
                if self.signal == self.SIG_NORMAL:
                    # print('wait for a connection')
                    # self.status.emit(self.LISTEN, '')
                    try:
                        self.connection, addr = self.bt_socket.accept()
                        self.connection.settimeout(1)
                    except socket.timeout as t_out:
                        pass
                    else:
                        self.status.emit(
                            self.CONNECTED, addr[0]+' ('+str(addr[1])+')')

                        while True:
                            # print('waiting for data')
                            if self.signal == self.SIG_NORMAL:
                                try:
                                    data = self.connection.recv(4096)
                                except socket.timeout as t_out:
                                    pass
                                else:
                                    if data:
                                        self.message.emit(
                                            addr[0]+' ('+str(addr[1])+')',
                                            data.decode())
                                    else:
                                        self.status.emit(self.LISTEN, '')
                                        break
                            elif self.signal == self.SIG_DISCONNECT:
                                self.signal = self.SIG_NORMAL
                                self.connection.close()
                                self.status.emit(self.LISTEN, '')
                                break

                elif self.signal == self.SIG_STOP:
                    self.bt_socket.close()
                    break
        finally:
            self.status.emit(self.STOP, '')

    def send(self, msg):
        self.connection.sendall(msg.encode())

    def disconnect(self):
        self.signal = self.SIG_DISCONNECT

    def close(self):
        self.signal = self.SIG_STOP
