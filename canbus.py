"""
    Copyright (C) 2017 - PRESENT  Zhengyu Peng, https://zpeng.me

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
"""

from PySide6.QtCore import QObject, Signal

try:
    import can
    _CAN_AVAILABLE = True
except ImportError:
    _CAN_AVAILABLE = False


class CanBus(QObject):
    STOP = 0
    CONNECTED = 1

    status = Signal(int, str)
    message = Signal(str, str)

    def __init__(self, bustype, channel, bitrate):
        super().__init__()
        self.bustype = bustype
        self.channel = channel
        self.bitrate = int(bitrate)
        self._running = False
        self.bus = None

    def start(self):
        if not _CAN_AVAILABLE:
            self.status.emit(CanBus.STOP, 'python-can not installed')
            return
        try:
            kwargs = dict(
                bustype=self.bustype,
                channel=self.channel,
                bitrate=self.bitrate,
            )
            if self.bustype == 'vector':
                # Vector XL driver requires an app_name registered in
                # Vector Hardware Config. 'CANalyzer' is always present.
                # Channel must be a 0-based integer index.
                try:
                    kwargs['channel'] = int(self.channel)
                except ValueError:
                    pass
                kwargs['app_name'] = 'CANalyzer'
            self.bus = can.interface.Bus(**kwargs)
        except Exception as e:
            self.status.emit(CanBus.STOP, str(e))
            return

        self._running = True
        self.status.emit(CanBus.CONNECTED, self.channel)

        while self._running:
            try:
                msg = self.bus.recv(timeout=0.5)
            except Exception:
                break
            if msg is not None:
                arb_id = f'0x{msg.arbitration_id:03X}'
                data = ' '.join(f'{b:02X}' for b in msg.data)
                self.message.emit(arb_id, data)

        try:
            self.bus.shutdown()
        except Exception:
            pass
        self.bus = None
        self.status.emit(CanBus.STOP, '')

    def close(self):
        self._running = False

    def send(self, arb_id_str, data_str, extended=False):
        if self.bus is None:
            return
        try:
            arb_id = int(arb_id_str.strip(), 16)
            data = bytes(int(b, 16) for b in data_str.split() if b)
            msg = can.Message(
                arbitration_id=arb_id,
                data=data,
                is_extended_id=extended
            )
            self.bus.send(msg)
        except Exception:
            pass
