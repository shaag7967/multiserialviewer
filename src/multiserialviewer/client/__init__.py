"""Read access to the serial data received by MultiSerialViewer.

    from multiserialviewer.client import SerialDataClient

Importing this package does not pull in PySide6 - only the standard library is
needed (pyserial in addition, if the serial port shall be opened directly).
"""

from multiserialviewer.client.serialDataClient import SerialDataClient, getPortsOccupiedByMsv

__all__ = ['SerialDataClient', 'getPortsOccupiedByMsv']
