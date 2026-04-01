# CommProbe

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/res/commprobe.png" width="128">

A multi-protocol communication testing tool built with Python and PySide6.
Supports TCP, UDP, Bluetooth, CAN, and GPIB.

## Dependencies

- [PySide6](https://pypi.org/project/PySide6/)
- [psutil](https://pypi.org/project/psutil/)
- [python-can](https://pypi.org/project/python-can/) *(optional, for CAN support)*
- [pyvisa](https://pypi.org/project/PyVISA/) *(optional, for GPIB support)*
- [pyvisa-py](https://pypi.org/project/PyVISA-py/) *(optional, pure-Python VISA backend)*

Install all at once:

```bash
pip install -r requirements.txt
```

## Usage

Select a protocol tab — **TCP**, **UDP**, **Bluetooth**, **CAN**, or **GPIB** — to begin testing.

### TCP

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/docs/TCP.png" width="800">

### UDP

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/docs/UDP.png" width="800">

### Bluetooth

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/docs/Bluetooth.png" width="800">

### CAN

Supports socketcan, PCAN, Vector, Kvaser, and virtual interfaces via [python-can](https://python-can.readthedocs.io/).

For **Vector** hardware, enter the 0-based channel index (e.g. `0`) in the Channel field. The app registers under the `CANalyzer` application name in Vector Hardware Config.

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/docs/CAN.png" width="800">

### GPIB

Requires NI-VISA or pyvisa-py. If no VISA library is detected, a warning is shown in the GPIB tab.

<img src="https://raw.githubusercontent.com/rookiepeng/comm-test/master/docs/GPIB.png" width="800">
