from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Slot
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class SerialViewerCreateDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Create SerialViewer")
        self.disabled_port_names = []

        self.connectWidget = createWidgetFromUiFile("createSerialViewerDialog.ui")

        self.refreshListOfSerialPorts()
        self.populateBaudRateCombobox()
        self.populateDataBitsCombobox()
        self.populateParityCombobox()
        self.populateStopBitsCombobox()

        self.connectWidget.pb_refresh.clicked.connect(self.refreshListOfSerialPorts)
        self.connectWidget.buttonBox.accepted.connect(self.accept)
        self.connectWidget.buttonBox.rejected.connect(self.reject)

        QVBoxLayout(self).addWidget(self.connectWidget)

    def disablePorts(self, disabled_port_names: list):
        self.disabled_port_names = disabled_port_names
        self.refreshListOfSerialPorts()

    @Slot()
    def refreshListOfSerialPorts(self):
        port_name_list = [p.portName() for p in QSerialPortInfo.availablePorts() if
                          p.portName() not in self.disabled_port_names]
        self.connectWidget.cb_portName.clear()
        self.connectWidget.cb_portName.addItems(port_name_list)

        ok_button_enabled_state = len(port_name_list) > 0
        self.connectWidget.buttonBox.button(QDialogButtonBox.Ok).setEnabled(ok_button_enabled_state)

    def populateBaudRateCombobox(self):
        baudrates = ['9600', '38400', '115200', '256000', '1000000']
        self.connectWidget.cb_baudrate.clear()
        self.connectWidget.cb_baudrate.addItems(baudrates)
        self.connectWidget.cb_baudrate.setCurrentIndex(4)

    def populateDataBitsCombobox(self):
        self.connectWidget.cb_dataSize.clear()
        self.connectWidget.cb_dataSize.addItem("5", userData=QSerialPort.DataBits.Data5)
        self.connectWidget.cb_dataSize.addItem("6", userData=QSerialPort.DataBits.Data6)
        self.connectWidget.cb_dataSize.addItem("7", userData=QSerialPort.DataBits.Data7)
        self.connectWidget.cb_dataSize.addItem("8", userData=QSerialPort.DataBits.Data8)
        self.connectWidget.cb_dataSize.setCurrentIndex(3)

    def populateParityCombobox(self):
        self.connectWidget.cb_parity.clear()
        self.connectWidget.cb_parity.addItem("None", userData=QSerialPort.Parity.NoParity)
        self.connectWidget.cb_parity.addItem("Even", userData=QSerialPort.Parity.EvenParity)
        self.connectWidget.cb_parity.addItem("Odd", userData=QSerialPort.Parity.OddParity)
        self.connectWidget.cb_parity.addItem("Mark", userData=QSerialPort.Parity.MarkParity)
        self.connectWidget.cb_parity.addItem("Space", userData=QSerialPort.Parity.SpaceParity)
        self.connectWidget.cb_parity.setCurrentIndex(0)

    def populateStopBitsCombobox(self):
        self.connectWidget.cb_stopBits.clear()
        self.connectWidget.cb_stopBits.addItem("1", userData=QSerialPort.StopBits.OneStop)
        self.connectWidget.cb_stopBits.addItem("1.5", userData=QSerialPort.StopBits.OneAndHalfStop)
        self.connectWidget.cb_stopBits.addItem("2", userData=QSerialPort.StopBits.TwoStop)
        self.connectWidget.cb_stopBits.setCurrentIndex(0)

    def getName(self):
        name = self.connectWidget.ed_name.text()
        if name == '':
            name = self.getPortName()
        elif self.getPortName() not in name:
            name = '{} ({})'.format(name, self.getPortName())
        return name

    def getPortName(self):
        return self.connectWidget.cb_portName.currentText()

    def getBaudrate(self) -> int:
        return int(self.connectWidget.cb_baudrate.currentText())

    def getDataBits(self):
        return self.connectWidget.cb_dataSize.currentData()

    def getParity(self):
        return self.connectWidget.cb_parity.currentData()

    def getStopBits(self):
        return self.connectWidget.cb_stopBits.currentData()
