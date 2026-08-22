import pytest

from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.icons.iconSet import IconSet


@pytest.fixture
def window(qtbot) -> SerialViewerWindow:
    view = SerialViewerWindow('COM6', IconSet('google', '434343'))
    qtbot.addWidget(view)
    return view


def test_titleIsTheNameWithoutClients(window):
    assert window.windowTitle() == 'COM6'
    assert window.getWindowName() == 'COM6'


def test_titleShowsSingleClient(window):
    window.setDataServerClientCount(1)
    assert window.windowTitle() == 'COM6  [1 client is reading]'


def test_titleShowsMultipleClients(window):
    window.setDataServerClientCount(3)
    assert window.windowTitle() == 'COM6  [3 clients are reading]'


def test_titleIsRestoredWhenLastClientIsGone(window):
    window.setDataServerClientCount(2)
    window.setDataServerClientCount(0)
    assert window.windowTitle() == 'COM6'


def test_renamingKeepsTheClientInformation(window):
    window.setDataServerClientCount(1)
    window.setWindowName('my device')
    assert window.windowTitle() == 'my device  [1 client is reading]'


def test_windowNameIsNotAffectedByClients(window):
    """Application.persistCurrentSettings() stores getWindowName(), so the client
    information must never end up in the settings."""
    window.setDataServerClientCount(2)
    assert window.getWindowName() == 'COM6'

    window.setWindowName('my device')
    assert window.getWindowName() == 'my device'
