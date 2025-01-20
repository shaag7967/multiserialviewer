from PySide6.QtCore import QObject, Slot, Qt

from multiserialviewer.application.serialViewerController import SerialViewerController
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings


class SerialViewerControllerPool(QObject):
    def __init__(self):
        super(SerialViewerControllerPool, self).__init__()
        self.__controller: list[SerialViewerController] = []

    def entries(self):
        return self.__controller

    def count(self):
        return len(self.__controller)

    def getUsedPorts(self) -> list[str]:
        return [ctrl.getPortName() for ctrl in self.__controller]

    def setHighlighterSettings(self, entries: list[TextHighlighterSettings]):
        for ctrl in self.__controller:
            ctrl.view.setHighlighterSettings(entries)

    def add(self, ctrl: SerialViewerController):
        self.__controller.append(ctrl)

    def resetReceivedData(self):
        for ctrl in self.__controller:
            ctrl.clearAll()

    def startCapture(self) -> bool:
        startedCount = 0
        ctrl: SerialViewerController
        for ctrl in self.__controller:
            if ctrl.startCapture():
                startedCount += 1

        return startedCount == self.count()

    def stopCapture(self):
        for ctrl in self.__controller:
            ctrl.stopCapture()

    @Slot()
    def deleteController(self, portName):
        for ctrl in self.__controller:
            if ctrl.getPortName() == portName:
                ctrl.destruct()
                self.__controller.remove(ctrl)
                break

    def deleteAll(self):
        for ctrl in self.__controller:
            ctrl.destruct()
        self.__controller = []
