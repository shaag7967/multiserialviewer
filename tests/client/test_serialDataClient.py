"""Tests the real client against the real server.

The client blocks while the server needs a running Qt event loop, so the client
calls are made in a worker thread while qtbot keeps the event loop alive.
"""
import os
import subprocess
import sys
import pytest
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from PySide6.QtCore import QByteArray

from multiserialviewer.client import SerialDataClient, getPortsOccupiedByMsv
from multiserialviewer.serial_data.serialDataServer import SerialDataServer


TCP_PORT = 45679
UNUSED_TCP_PORT = 45680


@pytest.fixture
def server(qtbot) -> SerialDataServer:
    knownPorts = ['COM3', 'COM6', 'COM9']
    capturedPorts = ['COM3', 'COM6']

    dataServer = SerialDataServer(lambda: knownPorts, lambda: capturedPorts)
    started, msg = dataServer.start(TCP_PORT)
    assert started, msg
    yield dataServer
    dataServer.stop()


@pytest.fixture
def worker() -> ThreadPoolExecutor:
    with ThreadPoolExecutor(max_workers=1) as executor:
        yield executor


def waitFor(qtbot, future: Future, timeout: int = 5000):
    qtbot.waitUntil(future.done, timeout=timeout)
    return future.result()


@pytest.fixture
def openedClient(qtbot, worker, server) -> SerialDataClient:
    client = SerialDataClient('COM6', tcpPort=TCP_PORT)
    waitFor(qtbot, worker.submit(client.open))
    yield client
    client.close()


def test_clientReadsFromMsv(qtbot, worker, server, openedClient):
    assert openedClient.isOpen
    assert openedClient.viaMsv
    assert openedClient.description == 'COM6 (via MultiSerialViewer)'

    server.dispatch('COM6', datetime.now(), QByteArray(b'\x00abc\r\n'))
    assert waitFor(qtbot, worker.submit(openedClient.read)) == b'\x00abc\r\n'


def test_clientUsesThePortNameOfMsv(qtbot, worker, server):
    client = SerialDataClient('com6', tcpPort=TCP_PORT)
    waitFor(qtbot, worker.submit(client.open))

    assert client.portName == 'COM6'
    client.close()


def test_readReturnsNothingWhenMsvReleasesThePort(qtbot, worker, server, openedClient):
    future = worker.submit(openedClient.read)
    server.closeSubscribers('COM6')

    assert waitFor(qtbot, future) == b''


def test_msvSeesTheClient(qtbot, worker, server, openedClient):
    assert server.getSubscriberCount('COM6') == 1


def test_getPortsOccupiedByMsv(qtbot, worker, server):
    future = worker.submit(getPortsOccupiedByMsv, '127.0.0.1', TCP_PORT)
    assert waitFor(qtbot, future) == ['COM3', 'COM6']


def test_getPortsOccupiedByMsvWithoutServer():
    assert getPortsOccupiedByMsv(tcpPort=UNUSED_TCP_PORT) == []


def test_openFailsForNotCapturedPortIfDirectAccessIsForbidden(qtbot, worker, server):
    # COM9 is known by MSV, but not captured -> the port itself would be free
    client = SerialDataClient('COM9', tcpPort=TCP_PORT, allowDirectAccess=False)

    with pytest.raises(ConnectionError):
        waitFor(qtbot, worker.submit(client.open))
    assert not client.isOpen


def test_openFailsForUnknownPortIfDirectAccessIsForbidden(qtbot, worker, server):
    client = SerialDataClient('COM100', tcpPort=TCP_PORT, allowDirectAccess=False)

    with pytest.raises(ConnectionError):
        waitFor(qtbot, worker.submit(client.open))


def test_readBeforeOpenIsRejected():
    client = SerialDataClient('COM6', tcpPort=TCP_PORT)

    assert not client.isOpen
    assert client.description == 'COM6 (not opened)'
    with pytest.raises(RuntimeError):
        client.read()


def test_importingTheClientDoesNotImportQt():
    """A script that reads data shall not be forced to have PySide6 installed."""
    code = ('import sys\n'
            'from multiserialviewer.client import SerialDataClient\n'
            'assert not [name for name in sys.modules if name.startswith("PySide6")]\n')

    environment = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
    result = subprocess.run([sys.executable, '-c', code], env=environment, capture_output=True)
    assert result.returncode == 0, result.stderr.decode()


def test_closeCanBeCalledTwice(qtbot, worker, server, openedClient):
    openedClient.close()
    openedClient.close()
    assert not openedClient.isOpen
