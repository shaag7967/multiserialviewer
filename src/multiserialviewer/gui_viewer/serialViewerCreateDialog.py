from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Qt
from typing import List

from multiserialviewer.gui_viewer.serialViewerSettingsWidget import SerialViewerSettingsWidget
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings, SerialConnectionSettings


class SerialViewerCreateDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Create SerialViewer")

        self.settingsWidget: SerialViewerSettingsWidget = SerialViewerSettingsWidget(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                          Qt.Orientation.Horizontal, self)

        self.settingsWidget.signal_settingsValidStateChanged.connect(
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.settingsWidget)
        layout.addStretch()
        layout.addWidget(self.buttonBox)

    def disablePorts(self, disabledPortNames: List[str]):
        self.settingsWidget.disablePorts(disabledPortNames)

    def getSerialViewerSettings(self) -> SerialViewerSettings:
        serialViewerSettings: SerialViewerSettings = SerialViewerSettings()
        serialViewerSettings.title = self.settingsWidget.getName()

        serialViewerSettings.connection = SerialConnectionSettings()
        serialViewerSettings.connection.portName = self.settingsWidget.getPortName()
        serialViewerSettings.connection.baudrate = self.settingsWidget.getBaudrate()
        serialViewerSettings.connection.dataBits = self.settingsWidget.getDataBits()
        serialViewerSettings.connection.parity = self.settingsWidget.getParity()
        serialViewerSettings.connection.stopBits = self.settingsWidget.getStopBits()

        return serialViewerSettings
