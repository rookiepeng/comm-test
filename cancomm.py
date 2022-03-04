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

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import can


class CanComm(QObject):
    detections = pyqtSignal(bool, bool)

    # Vector box
    # bus = can.interface.Bus(bustype='vector', app_name='CANalyzer', channel=[
    #     0], bitrate=500000, data_bitrate=2000000, fd=True, can_filters=[{"can_id": 0x500, "can_mask": 0xFFF}, {"can_id": 0x502, "can_mask": 0xFFF}])

    # PCAN FD box
    bus = can.interface.Bus(bustype='pcan',
                            channel='PCAN_USBBUS1',
                            fd=True,
                            f_clock=20000000,
                            nom_brp=5,
                            nom_tseg1=5,
                            nom_tseg2=2,
                            nom_sjw=1,
                            data_brp=2,
                            data_tseg1=3,
                            data_tseg2=1,
                            data_sjw=1,
                            can_filters=[{"can_id": 0x500, "can_mask": 0xFFF},
                                         {"can_id": 0x502, "can_mask": 0xFFF}])

    on_msg = can.Message(arbitration_id=0x20,
                         data=[1, 0, 0, 0, 0, 0, 0, 0],
                         is_extended_id=False)
    off_msg = can.Message(arbitration_id=0x20,
                          data=[0, 0, 0, 0, 0, 0, 0, 0],
                          is_extended_id=False)

    left_indicator = False
    right_indicator = False
    is_radar_on = False
    count = 0

    @pyqtSlot()
    def set_radar(self, status):
        if status:
            self.send_msg(self.on_msg)
            self.count = 0
        else:
            self.send_msg(self.off_msg)
            self.left_indicator = False
            self.right_indicator = False
            self.count = 0

    @pyqtSlot()
    def start(self):
        new_left_indicator = False
        new_right_indicator = False
        while 1:
            msg = self.bus.recv(0.5)
            if msg is not None:
                if msg.arbitration_id == 0x0500:
                    if msg.data[0] == 128:
                        new_left_indicator = False
                    elif msg.data[0] == 129:
                        new_left_indicator = True
                elif msg.arbitration_id == 0x0502:
                    if msg.data[0] == 128:
                        new_right_indicator = False
                    elif msg.data[0] == 129:
                        new_right_indicator = True

                if self.count > 3:
                    self.left_indicator = new_left_indicator
                    self.right_indicator = new_right_indicator
                    self.detections.emit(
                        self.left_indicator, self.right_indicator)
                self.count += 1

            # print(msg)

    def send_msg(self, msg):
        try:
            self.bus.send(msg)
            print("Message sent on {}".format(self.bus.channel_info))
        except can.CanError:
            print("Message NOT sent")