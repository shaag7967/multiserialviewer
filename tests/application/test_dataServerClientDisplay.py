"""Covers how a connected data server client becomes visible in the GUI.

The chain is: SerialDataServer.signal_clientCountChanged -> Application ->
SerialViewerControllerPool.getController() -> SerialViewerController -> window title.
"""
import pytest

from multiserialviewer.application.serialViewerController import SerialViewerController
from multiserialviewer.application.serialViewerControllerPool import SerialViewerControllerPool
from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.applicationSettings import ApplicationSettings
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings


def createController(qtbot, portName: str) -> SerialViewerController:
    settings = SerialViewerSettings()
    settings.title = portName
    settings.connection.portName = portName
    settings.connection.baudrate = 115200

    view = SerialViewerWindow(settings.title, IconSet('google', '434343'))
    qtbot.addWidget(view)
    return SerialViewerController(settings, ApplicationSettings(), view)


@pytest.fixture
def pool(qtbot) -> SerialViewerControllerPool:
    controllerPool = SerialViewerControllerPool()
    controllerPool.add(createController(qtbot, 'COM3'))
    controllerPool.add(createController(qtbot, 'COM6'))
    yield controllerPool
    controllerPool.deleteAll()


def test_getControllerFindsThePort(pool):
    assert pool.getController('COM6').getPortName() == 'COM6'
    assert pool.getController('COM100') is None


def test_capturedPortsIsEmptyWhileNoPortIsOpen(pool):
    # the ports are not opened in this test, so nothing is captured
    assert pool.getCapturedPorts() == []
    assert pool.getUsedPorts() == ['COM3', 'COM6']


def test_clientCountIsShownInTheWindowTitleOfThatPort(pool):
    pool.getController('COM6').setDataServerClientCount(1)

    assert pool.getController('COM6').view.windowTitle() == 'COM6  [1 client is reading]'
    assert pool.getController('COM3').view.windowTitle() == 'COM3'


def test_windowTitleIsRestoredWhenTheClientIsGone(pool):
    ctrl = pool.getController('COM6')
    ctrl.setDataServerClientCount(1)
    ctrl.setDataServerClientCount(0)

    assert ctrl.view.windowTitle() == 'COM6'
