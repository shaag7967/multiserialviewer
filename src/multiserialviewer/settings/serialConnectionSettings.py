from PySide6.QtSerialPort import QSerialPort

class SerialConnectionSettings:
    def __init__(self, portName: str = ''):
        self.portName : str = portName
        self.baudrate : int = 1
        self.dataBits : QSerialPort.DataBits = QSerialPort.DataBits.Data8
        self.parity : QSerialPort.Parity = QSerialPort.Parity.NoParity
        self.stopBits : QSerialPort.StopBits = QSerialPort.StopBits.OneStop
