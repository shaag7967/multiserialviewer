from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings


class SerialViewerSettingsWidget(QWidget):
    signal_settingsValidStateChanged: Signal = Signal(bool)
    signal_showNonPrintableAsHex = Signal(Qt.CheckState)

    def __init__(self, parent: QWidget, readOnly=False):
        super().__init__(parent)

        self.disabledPortNames = []
        self.settings: SerialViewerSettings = SerialViewerSettings()

        self.widget = createWidgetFromUiFile("serialViewerSettingsWidget.ui")
        self.widget.setParent(self)

        self.refreshListOfSerialPorts()
        self.populateBaudRateCombobox()
        self.populateDataBitsCombobox()
        self.populateParityCombobox()
        self.populateStopBitsCombobox()

        if readOnly:
            self.widget.pb_refresh.setVisible(False)
            self.widget.cb_portName.setEnabled(False)
            self.widget.cb_baudrate.setEnabled(False)
            self.widget.cb_dataSize.setEnabled(False)
            self.widget.cb_parity.setEnabled(False)
            self.widget.cb_stopBits.setEnabled(False)
        else:
            self.widget.cb_baudrate.setValidator(QRegularExpressionValidator(r'[0-9]+', self))
            self.widget.pb_refresh.clicked.connect(self.refreshListOfSerialPorts)
            self.widget.cb_portName.currentTextChanged.connect(self.updateSettingsValidState)
            self.widget.cb_baudrate.currentTextChanged.connect(self.updateSettingsValidState)

        self.widget.cb_showNonPrintableAsHex.checkStateChanged.connect(self.signal_showNonPrintableAsHex)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

    def setSerialViewerSettings(self, settings: SerialViewerSettings):
        self.settings = settings

        self.widget.cb_showNonPrintableAsHex.setCheckState(
            Qt.CheckState.Checked if self.settings.showNonPrintableCharsAsHex else Qt.CheckState.Unchecked)
        self.widget.cb_autoscrollActive.setCheckState(
            Qt.CheckState.Checked if self.settings.autoscrollActive else Qt.CheckState.Unchecked)
        self.widget.cb_autoscrollReactivate.setCheckState(
            Qt.CheckState.Checked if self.settings.autoscrollReactivate else Qt.CheckState.Unchecked)

        self.widget.ed_name.setText(self.settings.title)
        self.refreshListOfSerialPorts()
        self.widget.cb_baudrate.setCurrentText(str(self.settings.connection.baudrate))

        if (index := self.widget.cb_dataSize.findData(self.settings.connection.dataBits)) >= 0:
            self.widget.cb_dataSize.setCurrentIndex(index)
        if (index := self.widget.cb_parity.findData(self.settings.connection.parity)) >= 0:
            self.widget.cb_parity.setCurrentIndex(index)
        if (index := self.widget.cb_stopBits.findData(self.settings.connection.stopBits)) >= 0:
            self.widget.cb_stopBits.setCurrentIndex(index)

    def disablePorts(self, disabledPortNames: List[str]):
        self.disabledPortNames = disabledPortNames
        self.refreshListOfSerialPorts()

    @Slot()
    def refreshListOfSerialPorts(self):
        port_name_list = [p.portName() for p in QSerialPortInfo.availablePorts() if
                          p.portName() not in self.disabledPortNames]
        self.widget.cb_portName.clear()
        self.widget.cb_portName.addItems(port_name_list)

        self.widget.cb_portName.setEditText(self.settings.connection.portName)

    @Slot()
    def updateSettingsValidState(self):
        settingsAreValid = True
        if self.widget.cb_portName.currentText() in self.disabledPortNames:
            if self.settings.connection.portName != self.widget.cb_portName.currentText():
                settingsAreValid = False
        if len(self.widget.cb_portName.currentText()) == 0:
            settingsAreValid = False
        if len(self.widget.cb_baudrate.currentText()) == 0:
            settingsAreValid = False

        self.signal_settingsValidStateChanged.emit(settingsAreValid)

    def populateBaudRateCombobox(self):
        baudrates = ['9600', '38400', '115200', '256000', '1000000']
        self.widget.cb_baudrate.clear()
        self.widget.cb_baudrate.addItems(baudrates)
        self.widget.cb_baudrate.setCurrentText('115200')

    def populateDataBitsCombobox(self):
        self.widget.cb_dataSize.clear()
        self.widget.cb_dataSize.addItem("5", userData=QSerialPort.DataBits.Data5)
        self.widget.cb_dataSize.addItem("6", userData=QSerialPort.DataBits.Data6)
        self.widget.cb_dataSize.addItem("7", userData=QSerialPort.DataBits.Data7)
        self.widget.cb_dataSize.addItem("8", userData=QSerialPort.DataBits.Data8)
        self.widget.cb_dataSize.setCurrentText("8")

    def populateParityCombobox(self):
        self.widget.cb_parity.clear()
        self.widget.cb_parity.addItem("None", userData=QSerialPort.Parity.NoParity)
        self.widget.cb_parity.addItem("Even", userData=QSerialPort.Parity.EvenParity)
        self.widget.cb_parity.addItem("Odd", userData=QSerialPort.Parity.OddParity)
        self.widget.cb_parity.addItem("Mark", userData=QSerialPort.Parity.MarkParity)
        self.widget.cb_parity.addItem("Space", userData=QSerialPort.Parity.SpaceParity)
        self.widget.cb_parity.setCurrentText("None")

    def populateStopBitsCombobox(self):
        self.widget.cb_stopBits.clear()
        self.widget.cb_stopBits.addItem("1", userData=QSerialPort.StopBits.OneStop)
        self.widget.cb_stopBits.addItem("1.5", userData=QSerialPort.StopBits.OneAndHalfStop)
        self.widget.cb_stopBits.addItem("2", userData=QSerialPort.StopBits.TwoStop)
        self.widget.cb_stopBits.setCurrentText("1")

    def getName(self):
        return self.widget.ed_name.text()

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

    def getSettingShowNonPrintableAsHex(self) -> bool:
        return self.widget.cb_showNonPrintableAsHex.checkState() == Qt.CheckState.Checked