from PySide6.QtCore import Qt, QObject, Slot, QPoint
from PySide6.QtWidgets import QCheckBox, QAbstractSlider

from multiserialviewer.gui_viewer.serialViewerTextEdit import SerialViewerTextEdit


class AutoscrollHandler(QObject):
    def __init__(self, textEdit: SerialViewerTextEdit, autoscrollActive: QCheckBox, autoReactivate: QCheckBox):
        super(AutoscrollHandler, self).__init__()

        self.__textEdit: SerialViewerTextEdit = textEdit
        self.__autoscrollActive: QCheckBox = autoscrollActive
        self.__autoReactivate: QCheckBox = autoReactivate

        self.__autoscrollActive.checkStateChanged.connect(self.autoscrollStateChanged)
        self.__textEdit.signal_mousePressed.connect(self.handleMousePress)
        self.__textEdit.signal_wheelEvent.connect(self.handleWheelEvent)
        self.__textEdit.verticalScrollBar().sliderPressed.connect(self.handleSliderPress)
        self.__textEdit.verticalScrollBar().sliderReleased.connect(self.handleSliderRelease)
        self.__textEdit.verticalScrollBar().actionTriggered.connect(self.handleSliderAction)

    def activateAutoscroll(self):
        self.__autoscrollActive.setCheckState(Qt.CheckState.Checked)

    @Slot()
    def deactivateAutoscroll(self):
        self.__autoscrollActive.setCheckState(Qt.CheckState.Unchecked)

    def autoscrollIsActive(self) -> bool:
        return self.__autoscrollActive.isChecked()

    def autoReactivateIsActive(self) -> bool:
        return self.__autoReactivate.isChecked()

    @Slot(QPoint)
    def handleMousePress(self, position: QPoint):
        self.deactivateAutoscroll()

    @Slot()
    def handleSliderPress(self):
        self.deactivateAutoscroll()

    @Slot()
    def handleSliderRelease(self):
        if self.__textEdit.verticalScrollBar().value() < self.__textEdit.verticalScrollBar().maximum():
            self.deactivateAutoscroll()

    @Slot()
    def handleSliderAction(self, action: QAbstractSlider.SliderAction):
        if action in [QAbstractSlider.SliderAction.SliderPageStepAdd.value,
                      QAbstractSlider.SliderAction.SliderSingleStepAdd.value]:
            if self.__textEdit.verticalScrollBar().value() < self.__textEdit.verticalScrollBar().maximum():
                # note: clicking down arrow will cause checkIfScrolledToBottom to enable autoscroll at some
                #       point. If you then click again the down arrow (while you are already at the bottom),
                #       autoscroll will be deactivated again. This is not what you expect. Therefore, we only
                #       deactivate autoscroll while not at the bottom (when using down arrow).
                self.deactivateAutoscroll()
        elif action in [QAbstractSlider.SliderAction.SliderPageStepSub.value,
                        QAbstractSlider.SliderAction.SliderSingleStepSub.value]:
            self.deactivateAutoscroll()

    @Slot()
    def handleWheelEvent(self, angleDelta: QPoint):
        scrollingDownwards = angleDelta.y() < 0
        bottomOfScrollBarReached = self.__textEdit.verticalScrollBar().value() == self.__textEdit.verticalScrollBar().maximum()

        if scrollingDownwards and bottomOfScrollBarReached:
            if self.autoReactivateIsActive():
                self.activateAutoscroll()
        else:
            self.deactivateAutoscroll()

    @Slot()
    def checkIfScrolledToBottom(self, value: int):
        if value == self.__textEdit.verticalScrollBar().maximum():
            if self.autoReactivateIsActive():
                self.activateAutoscroll()

    @Slot()
    def autoscrollStateChanged(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self.__textEdit.verticalScrollBar().valueChanged.disconnect(self.checkIfScrolledToBottom)
        elif state == Qt.CheckState.Unchecked:
            self.__textEdit.verticalScrollBar().valueChanged.connect(self.checkIfScrolledToBottom)
