import pytest
from PySide6.QtCore import QByteArray
from PySide6.QtNetwork import QTcpSocket, QHostAddress
from datetime import datetime
from functools import partial

from multiserialviewer.serial_data import serialDataServerProtocol as protocol
from multiserialviewer.serial_data.serialDataServer import SerialDataServer
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings


TCP_PORT = 45678


@pytest.fixture
def capturedPorts() -> list[str]:
    return ['COM3', 'COM6']


@pytest.fixture
def knownPorts() -> list[str]:
    return ['COM3', 'COM6', 'COM9']


@pytest.fixture
def server(qtbot, knownPorts, capturedPorts) -> SerialDataServer:
    dataServer = SerialDataServer(lambda: knownPorts, lambda: capturedPorts)
    started, msg = dataServer.start(TCP_PORT)
    assert started, msg
    yield dataServer
    dataServer.stop()


def sendCommand(qtbot, command: str) -> tuple[QTcpSocket, str]:
    client = QTcpSocket()
    client.connectToHost(QHostAddress(QHostAddress.SpecialAddress.LocalHost), TCP_PORT)
    qtbot.waitUntil(lambda: client.state() == QTcpSocket.SocketState.ConnectedState)

    client.write(f'{command}\n'.encode())
    qtbot.waitUntil(client.canReadLine)
    return client, bytes(client.readLine().data()).decode().strip()


def test_subscribeToCapturedPortReturnsOk(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'
    assert server.getSubscriberCount('COM6') == 1


def test_subscribeIsCaseInsensitive(qtbot, server):
    client, response = sendCommand(qtbot, 'sub com6')
    assert response == 'OK COM6'


def test_subscribeToNotCapturedPortReturnsErrClosed(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM9')
    assert response == 'ERR CLOSED'


def test_subscribeToUnknownPortReturnsErrNoPort(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM100')
    assert response == 'ERR NOPORT'


def test_invalidCommandReturnsErrUnknown(qtbot, server):
    client, response = sendCommand(qtbot, 'GIVE ME EVERYTHING')
    assert response == 'ERR UNKNOWN'


def test_listReturnsCapturedPorts(qtbot, server):
    client, response = sendCommand(qtbot, 'LIST')
    assert response == 'PORTS COM3 COM6'


def test_subscriberReceivesRawData(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    server.dispatch('COM6', datetime.now(), QByteArray(b'\x00abc\r\n'))
    qtbot.waitUntil(lambda: client.bytesAvailable() >= 6)
    assert bytes(client.readAll().data()) == b'\x00abc\r\n'


def test_subscriberDoesNotReceiveDataOfOtherPort(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    server.dispatch('COM3', datetime.now(), QByteArray(b'not for you'))
    server.dispatch('COM6', datetime.now(), QByteArray(b'for you'))
    qtbot.waitUntil(lambda: client.bytesAvailable() >= 7)
    assert bytes(client.readAll().data()) == b'for you'


def test_receiverSignalReachesSubscriber(qtbot, server):
    """Verifies the connection that is used in Application.createSerialViewer()."""
    receiver = SerialDataReceiver(SerialConnectionSettings('COM6'))
    receiver.signal_rawDataAvailable.connect(partial(server.dispatch, 'COM6'))

    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    receiver.signal_rawDataAvailable.emit(datetime.now(), QByteArray(b'from receiver'))
    qtbot.waitUntil(lambda: client.bytesAvailable() >= 13)
    assert bytes(client.readAll().data()) == b'from receiver'


def test_clientCountIsReportedOnSubscribe(qtbot, server):
    with qtbot.waitSignal(server.signal_clientCountChanged, timeout=1000) as blocker:
        client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'
    assert blocker.args == ['COM6', 1]

    with qtbot.waitSignal(server.signal_clientCountChanged, timeout=1000) as blocker:
        secondClient, response = sendCommand(qtbot, 'SUB COM6')
    assert blocker.args == ['COM6', 2]


def test_clientCountIsReportedOnDisconnect(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    with qtbot.waitSignal(server.signal_clientCountChanged, timeout=1000) as blocker:
        client.disconnectFromHost()
    assert blocker.args == ['COM6', 0]


def test_clientCountIsReportedWhenSubscribersAreClosed(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    with qtbot.waitSignal(server.signal_clientCountChanged, timeout=1000) as blocker:
        server.closeSubscribers('COM6')
    assert blocker.args == ['COM6', 0]


def test_noClientCountReportedForPortWithoutSubscribers(qtbot, server):
    with qtbot.assertNotEmitted(server.signal_clientCountChanged):
        server.closeSubscribers('COM3')


def test_closeSubscribersDisconnectsClient(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    server.closeSubscribers('COM6')
    qtbot.waitUntil(lambda: client.state() == QTcpSocket.SocketState.UnconnectedState)
    assert server.getSubscriberCount('COM6') == 0


def test_disconnectedClientIsRemoved(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    client.disconnectFromHost()
    qtbot.waitUntil(lambda: server.getSubscriberCount('COM6') == 0)

    # data for a port without subscribers must not cause any trouble
    server.dispatch('COM6', datetime.now(), QByteArray(b'nobody is listening'))


def test_repeatedConnectAndDisconnect(qtbot, server):
    """A disconnected client is handed over to Qt for deletion (deleteLater).
    That must not disturb the connections that follow."""
    for _ in range(5):
        client, response = sendCommand(qtbot, 'SUB COM6')
        assert response == 'OK COM6'

        client.disconnectFromHost()
        qtbot.waitUntil(lambda: server.getSubscriberCount('COM6') == 0)


def test_oversizedCommandIsRejected(qtbot, server):
    client = QTcpSocket()
    client.connectToHost(QHostAddress(QHostAddress.SpecialAddress.LocalHost), TCP_PORT)
    qtbot.waitUntil(lambda: client.state() == QTcpSocket.SocketState.ConnectedState)

    client.write(b'S' * (protocol.MAX_COMMAND_SIZE + 1))
    qtbot.waitUntil(lambda: client.state() == QTcpSocket.SocketState.UnconnectedState)


def test_restartOnSamePortIsNoOperation(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    assert server.start(TCP_PORT) == (True, '')
    assert server.getSubscriberCount('COM6') == 1


def test_stopClosesServerAndSubscribers(qtbot, server):
    client, response = sendCommand(qtbot, 'SUB COM6')
    assert response == 'OK COM6'

    server.stop()
    qtbot.waitUntil(lambda: client.state() == QTcpSocket.SocketState.UnconnectedState)
    assert not server.isListening()
