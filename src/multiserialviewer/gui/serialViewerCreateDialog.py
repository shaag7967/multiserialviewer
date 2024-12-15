from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Slot
import serial.tools.list_ports
import serial

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
        port_name_list = [p.device for p in serial.tools.list_ports.comports() if
                          p.device not in self.disabled_port_names]
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
        self.connectWidget.cb_dataSize.addItem(str(serial.FIVEBITS), userData=serial.FIVEBITS)
        self.connectWidget.cb_dataSize.addItem(str(serial.SIXBITS), userData=serial.SIXBITS)
        self.connectWidget.cb_dataSize.addItem(str(serial.SEVENBITS), userData=serial.SEVENBITS)
        self.connectWidget.cb_dataSize.addItem(str(serial.EIGHTBITS), userData=serial.EIGHTBITS)
        self.connectWidget.cb_dataSize.setCurrentIndex(3)

    def populateParityCombobox(self):
        self.connectWidget.cb_parity.clear()
        self.connectWidget.cb_parity.addItem(serial.PARITY_NAMES[serial.PARITY_NONE], userData=serial.PARITY_NONE)
        self.connectWidget.cb_parity.addItem(serial.PARITY_NAMES[serial.PARITY_EVEN], userData=serial.PARITY_EVEN)
        self.connectWidget.cb_parity.addItem(serial.PARITY_NAMES[serial.PARITY_ODD], userData=serial.PARITY_ODD)
        self.connectWidget.cb_parity.addItem(serial.PARITY_NAMES[serial.PARITY_MARK], userData=serial.PARITY_MARK)
        self.connectWidget.cb_parity.addItem(serial.PARITY_NAMES[serial.PARITY_SPACE], userData=serial.PARITY_SPACE)
        self.connectWidget.cb_parity.setCurrentIndex(0)

    def populateStopBitsCombobox(self):
        self.connectWidget.cb_stopBits.clear()
        self.connectWidget.cb_stopBits.addItem(str(serial.STOPBITS_ONE), userData=serial.STOPBITS_ONE)
        self.connectWidget.cb_stopBits.addItem(str(serial.STOPBITS_ONE_POINT_FIVE),
                                               userData=serial.STOPBITS_ONE_POINT_FIVE)
        self.connectWidget.cb_stopBits.addItem(str(serial.STOPBITS_TWO), userData=serial.STOPBITS_TWO)
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

    def getBaudrate(self):
        return self.connectWidget.cb_baudrate.currentText()

    def getDataBits(self):
        return self.connectWidget.cb_dataSize.currentData()

    def getParity(self):
        return self.connectWidget.cb_parity.currentData()

    def getStopBits(self):
        return self.connectWidget.cb_stopBits.currentData()
