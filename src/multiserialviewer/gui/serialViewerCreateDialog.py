from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class SerialViewerCreateDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Create SerialViewer")
        self.disabled_port_names = []

        self.settingsWidget = createWidgetFromUiFile("serialViewerSettings.ui")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                          Qt.Orientation.Horizontal, self)

        self.settingsWidget.cb_baudrate.setValidator(QRegularExpressionValidator(r'[0-9]+', self))
        self.refreshListOfSerialPorts()
        self.populateBaudRateCombobox()
        self.populateDataBitsCombobox()
        self.populateParityCombobox()
        self.populateStopBitsCombobox()

        self.settingsWidget.pb_refresh.clicked.connect(self.refreshListOfSerialPorts)
        self.settingsWidget.cb_portName.currentTextChanged.connect(self.updateOkButtonEnableState)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.settingsWidget)
        layout.addStretch()
        layout.addWidget(self.buttonBox)

    def disablePorts(self, disabled_port_names: list):
        self.disabled_port_names = disabled_port_names
        self.refreshListOfSerialPorts()

    @Slot()
    def refreshListOfSerialPorts(self):
        port_name_list = [p.portName() for p in QSerialPortInfo.availablePorts() if
                          p.portName() not in self.disabled_port_names]
        self.settingsWidget.cb_portName.clear()
        self.settingsWidget.cb_portName.addItems(port_name_list)

    @Slot()
    def updateOkButtonEnableState(self):
        ok_button_enabled_state = len(self.settingsWidget.cb_portName.currentText()) > 0
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok_button_enabled_state)

    def populateBaudRateCombobox(self):
        baudrates = ['9600', '38400', '115200', '256000', '1000000']
        self.settingsWidget.cb_baudrate.clear()
        self.settingsWidget.cb_baudrate.addItems(baudrates)
        self.settingsWidget.cb_baudrate.setCurrentIndex(4)

    def populateDataBitsCombobox(self):
        self.settingsWidget.cb_dataSize.clear()
        self.settingsWidget.cb_dataSize.addItem("5", userData=QSerialPort.DataBits.Data5)
        self.settingsWidget.cb_dataSize.addItem("6", userData=QSerialPort.DataBits.Data6)
        self.settingsWidget.cb_dataSize.addItem("7", userData=QSerialPort.DataBits.Data7)
        self.settingsWidget.cb_dataSize.addItem("8", userData=QSerialPort.DataBits.Data8)
        self.settingsWidget.cb_dataSize.setCurrentIndex(3)

    def populateParityCombobox(self):
        self.settingsWidget.cb_parity.clear()
        self.settingsWidget.cb_parity.addItem("None", userData=QSerialPort.Parity.NoParity)
        self.settingsWidget.cb_parity.addItem("Even", userData=QSerialPort.Parity.EvenParity)
        self.settingsWidget.cb_parity.addItem("Odd", userData=QSerialPort.Parity.OddParity)
        self.settingsWidget.cb_parity.addItem("Mark", userData=QSerialPort.Parity.MarkParity)
        self.settingsWidget.cb_parity.addItem("Space", userData=QSerialPort.Parity.SpaceParity)
        self.settingsWidget.cb_parity.setCurrentIndex(0)

    def populateStopBitsCombobox(self):
        self.settingsWidget.cb_stopBits.clear()
        self.settingsWidget.cb_stopBits.addItem("1", userData=QSerialPort.StopBits.OneStop)
        self.settingsWidget.cb_stopBits.addItem("1.5", userData=QSerialPort.StopBits.OneAndHalfStop)
        self.settingsWidget.cb_stopBits.addItem("2", userData=QSerialPort.StopBits.TwoStop)
        self.settingsWidget.cb_stopBits.setCurrentIndex(0)

    def getName(self):
        name = self.settingsWidget.ed_name.text()
        if name == '':
            name = self.getPortName()
        return name

    def getPortName(self):
        return self.settingsWidget.cb_portName.currentText()

    def getBaudrate(self) -> int:
        return int(self.settingsWidget.cb_baudrate.currentText())

    def getDataBits(self):
        return self.settingsWidget.cb_dataSize.currentData()

    def getParity(self):
        return self.settingsWidget.cb_parity.currentData()

    def getStopBits(self):
        return self.settingsWidget.cb_stopBits.currentData()
