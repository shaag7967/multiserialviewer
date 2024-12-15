import serial


class SerialConnectionSettings:
    def __init__(self, port_name: str):
        self.portName = port_name
        self.baudrate = 1000000
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 0.5
