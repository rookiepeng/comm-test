# CommProbe

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/res/commprobe.png" width="128">

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

## Run

```bash
python commprobe.py
```

Settings are persisted automatically to `config.json` in the working directory.

## Build (PyInstaller)

```bash
pyinstaller commprobe.spec
```

## Usage

Select a protocol tab — **TCP**, **UDP**, **Bluetooth**, **CAN**, or **GPIB** — to begin testing.
Incoming and outgoing messages are shown in a timestamped log panel on the right.

### TCP

Both a **Server** and a **Client** are available on the same tab.

- Server listens on a selected network interface and port.
- **Echo** option: automatically sends received messages back to the connected client.
- **Send timer**: repeat the last message at a configurable interval (ms).

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/docs/TCP.png" width="800">

### UDP

- Listens on a selected network interface and port.
- Sends to a configurable target IP and port.
- **Send timer**: repeat the last message at a configurable interval (ms).

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/docs/UDP.png" width="800">

### Bluetooth

Both a **Server** and a **Client** are available on the same tab.

- Server binds to a local MAC address and RFCOMM port.
- Client connects to a remote MAC address and RFCOMM port.

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/docs/Bluetooth.png" width="800">

### CAN

Supports **socketcan**, **PCAN**, **Vector**, **Kvaser**, and **virtual** interfaces via [python-can](https://python-can.readthedocs.io/).

- Select the bus type, enter the channel, and choose a bitrate.
- **Extended ID**: toggle to use 29-bit extended CAN IDs.
- Channel format varies by bus type:
  | Bus type   | Channel format example         |
  |------------|-------------------------------|
  | socketcan  | `can0`                        |
  | pcan       | `PCAN_USBBUS1`                |
  | vector     | `0` (0-based index)           |
  | kvaser     | `0` (0-based index)           |
  | virtual    | `0`                           |

For **Vector** hardware the app registers under the `CANalyzer` application name in Vector Hardware Config.

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/docs/CAN.png" width="800">

### GPIB

Requires NI-VISA or pyvisa-py. If no VISA library is detected, a warning is shown in the GPIB tab.

- Select a VISA resource from the list and click **Open**.
- Send mode: **Query** (write + read response) or **Write** (write only).

<img src="https://raw.githubusercontent.com/rookiepeng/comm-probe/master/docs/GPIB.png" width="800">
