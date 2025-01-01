from PySide6.QtSerialPort import QSerialPort

class SerialConnectionSettings:
    def __init__(self, port_name: str):
        self.portName : str = port_name
        self.baudrate : int = 1000000
        self.dataBits : QSerialPort.DataBits = QSerialPort.DataBits.Data8
        self.parity : QSerialPort.Parity = QSerialPort.Parity.NoParity
        self.stopbits : QSerialPort.StopBits = QSerialPort.StopBits.OneStop
