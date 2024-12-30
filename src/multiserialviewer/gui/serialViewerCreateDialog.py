from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Qt
from typing import List

from multiserialviewer.gui.serialViewerSettingsWidget import SerialViewerSettingsWidget


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

    def getName(self):
        return self.settingsWidget.getName()

    def getPortName(self):
        return self.settingsWidget.getPortName()

    def getBaudrate(self) -> int:
        return self.settingsWidget.getBaudrate()

    def getDataBits(self):
        return self.settingsWidget.getDataBits()

    def getParity(self):
        return self.settingsWidget.getParity()

    def getStopBits(self):
        return self.settingsWidget.getStopBits()
