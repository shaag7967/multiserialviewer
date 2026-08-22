"""Reads a serial port - through MultiSerialViewer if it captures the port.

If MultiSerialViewer runs with an enabled "Serial data server", the data comes
from there and the port stays open in MultiSerialViewer. Otherwise the port is
opened directly (needs pyserial).

    python readSerialData.py COM6 115200

The same without writing a script: 'multiserialviewer-client COM6'
"""

import sys

from multiserialviewer.client import SerialDataClient, getPortsOccupiedByMsv

portName = sys.argv[1] if len(sys.argv) > 1 else 'COM6'
baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

print(f'ports occupied by MultiSerialViewer: {getPortsOccupiedByMsv() or "-"}')

with SerialDataClient(portName, baudrate) as client:
    print(f'reading from {client.description}, press Ctrl+C to stop')
    try:
        while True:
            receivedData = client.read()
            if not receivedData:
                print('\n--- end of stream (the port is free now) ---')
                break
            sys.stdout.write(receivedData.decode(errors='replace'))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
