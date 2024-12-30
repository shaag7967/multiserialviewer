from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class SerialViewerSettingsWidget(QWidget):
    signal_settingsValidStateChanged: Signal = Signal(bool)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.disabledPortNames = []

        self.widget = createWidgetFromUiFile("serialViewerSettingsWidget.ui")
        self.widget.setParent(self)

        self.widget.cb_baudrate.setValidator(QRegularExpressionValidator(r'[0-9]+', self))
        self.refreshListOfSerialPorts()
        self.populateBaudRateCombobox()
        self.populateDataBitsCombobox()
        self.populateParityCombobox()
        self.populateStopBitsCombobox()

        self.widget.pb_refresh.clicked.connect(self.refreshListOfSerialPorts)
        self.widget.cb_portName.currentTextChanged.connect(self.updateSettingsValidState)
        self.widget.cb_baudrate.currentTextChanged.connect(self.updateSettingsValidState)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

    def disablePorts(self, disabledPortNames: List[str]):
        self.disabledPortNames = disabledPortNames
        self.refreshListOfSerialPorts()

    @Slot()
    def refreshListOfSerialPorts(self):
        port_name_list = [p.portName() for p in QSerialPortInfo.availablePorts() if
                          p.portName() not in self.disabledPortNames]
        self.widget.cb_portName.clear()
        self.widget.cb_portName.addItems(port_name_list)

    @Slot()
    def updateSettingsValidState(self):
        validState = len(self.widget.cb_portName.currentText()) > 0 and \
                                  len(self.widget.cb_baudrate.currentText()) > 0
        self.signal_settingsValidStateChanged.emit(validState)


    def populateBaudRateCombobox(self):
        baudrates = ['9600', '38400', '115200', '256000', '1000000']
        self.widget.cb_baudrate.clear()
        self.widget.cb_baudrate.addItems(baudrates)
        self.widget.cb_baudrate.setCurrentIndex(4)

    def populateDataBitsCombobox(self):
        self.widget.cb_dataSize.clear()
        self.widget.cb_dataSize.addItem("5", userData=QSerialPort.DataBits.Data5)
        self.widget.cb_dataSize.addItem("6", userData=QSerialPort.DataBits.Data6)
        self.widget.cb_dataSize.addItem("7", userData=QSerialPort.DataBits.Data7)
        self.widget.cb_dataSize.addItem("8", userData=QSerialPort.DataBits.Data8)
        self.widget.cb_dataSize.setCurrentIndex(3)

    def populateParityCombobox(self):
        self.widget.cb_parity.clear()
        self.widget.cb_parity.addItem("None", userData=QSerialPort.Parity.NoParity)
        self.widget.cb_parity.addItem("Even", userData=QSerialPort.Parity.EvenParity)
        self.widget.cb_parity.addItem("Odd", userData=QSerialPort.Parity.OddParity)
        self.widget.cb_parity.addItem("Mark", userData=QSerialPort.Parity.MarkParity)
        self.widget.cb_parity.addItem("Space", userData=QSerialPort.Parity.SpaceParity)
        self.widget.cb_parity.setCurrentIndex(0)

    def populateStopBitsCombobox(self):
        self.widget.cb_stopBits.clear()
        self.widget.cb_stopBits.addItem("1", userData=QSerialPort.StopBits.OneStop)
        self.widget.cb_stopBits.addItem("1.5", userData=QSerialPort.StopBits.OneAndHalfStop)
        self.widget.cb_stopBits.addItem("2", userData=QSerialPort.StopBits.TwoStop)
        self.widget.cb_stopBits.setCurrentIndex(0)

    def getName(self):
        name = self.widget.ed_name.text()
        if name == '':
            name = self.getPortName()
        return name

    def getPortName(self):
        return self.widget.cb_portName.currentText()

    def getBaudrate(self) -> int:
        return int(self.widget.cb_baudrate.currentText())

    def getDataBits(self):
        return self.widget.cb_dataSize.currentData()

    def getParity(self):
        return self.widget.cb_parity.currentData()

    def getStopBits(self):
        return self.widget.cb_stopBits.currentData()
