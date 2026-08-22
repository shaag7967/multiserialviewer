from PySide6.QtCore import Signal, Slot, QObject, QByteArray
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from datetime import datetime
from typing import Callable

from multiserialviewer.serial_data import serialDataServerProtocol as protocol


class SerialDataServer(QObject):
    """Gives other applications read access to the serial data received by us.

    A serial port can only be opened by a single application. Instead of closing
    a port so that another application can use it, we forward the received raw
    data via a local TCP socket. See serialDataServerProtocol for the commands.

    'OK' is sent only if we really hold the port at that moment. Therefore a
    client that does not get a data stream (connection refused, ERR CLOSED,
    ERR NOPORT) can safely open the serial port on its own.

    multiserialviewer.client.SerialDataClient is the counterpart of this class.
    """

    # if a client does not read its data, we drop it instead of buffering forever
    MAX_BUFFERED_BYTES: int = 4 * 1024 * 1024

    # portName, number of clients that currently read the data of that port
    signal_clientCountChanged: Signal = Signal(str, int)

    def __init__(self, knownPorts: Callable[[], list[str]], capturedPorts: Callable[[], list[str]]):
        super(SerialDataServer, self).__init__()

        self.__knownPorts = knownPorts
        self.__capturedPorts = capturedPorts

        self.__server: QTcpServer = QTcpServer(self)
        self.__server.newConnection.connect(self.__handleNewConnections)

        # clients that did not send a complete command line yet
        self.__commandBuffer: dict[QTcpSocket, bytearray] = {}
        # clients that receive the data of a serial port
        self.__subscribers: dict[str, list[QTcpSocket]] = {}

    def start(self, tcpPort: int) -> tuple[bool, str]:
        if self.__server.isListening():
            if self.__server.serverPort() == tcpPort:
                return True, ''
            self.stop()

        # local only, we do not want to expose the serial data to the network
        if self.__server.listen(QHostAddress(QHostAddress.SpecialAddress.LocalHost), tcpPort):
            return True, ''
        else:
            return False, self.__server.errorString()

    def stop(self):
        self.__server.close()
        self.closeAllSubscribers()
        for client in list(self.__commandBuffer.keys()):
            client.disconnectFromHost()

    def isListening(self) -> bool:
        return self.__server.isListening()

    def getSubscriberCount(self, portName: str) -> int:
        return len(self.__subscribers.get(portName, []))

    def dispatch(self, portName: str, rxTime: datetime, rawData: QByteArray):
        """Sends the received data to all subscribers of portName.

        Only the raw data is forwarded, rxTime is not part of the stream (a
        client can take its own timestamp when it reads from the socket).
        """
        for client in list(self.__subscribers.get(portName, [])):
            if client.bytesToWrite() > SerialDataServer.MAX_BUFFERED_BYTES:
                # skipping data would silently corrupt the stream of the client,
                # so we drop the client instead. It notices the broken connection
                # and can decide on its own what to do.
                self.__removeClient(client, abort=True)
            else:
                client.write(rawData)

    @Slot(str)
    def closeSubscribers(self, portName: str):
        clients = self.__subscribers.pop(portName, [])
        for client in clients:
            client.disconnectFromHost()
        if clients:
            self.signal_clientCountChanged.emit(portName, 0)

    def closeAllSubscribers(self):
        for portName in list(self.__subscribers.keys()):
            self.closeSubscribers(portName)

    @Slot()
    def __handleNewConnections(self):
        while self.__server.hasPendingConnections():
            client: QTcpSocket = self.__server.nextPendingConnection()
            self.__commandBuffer[client] = bytearray()
            client.readyRead.connect(self.__handleReadyRead)
            client.disconnected.connect(self.__handleDisconnected)

    @Slot()
    def __handleReadyRead(self):
        client: QTcpSocket = self.sender()

        if client not in self.__commandBuffer:
            client.readAll()  # subscribers are not supposed to send anything
            return

        buffer: bytearray = self.__commandBuffer[client]
        buffer.extend(client.readAll().data())

        endOfCommand = buffer.find(protocol.LINE_END.encode())
        if endOfCommand < 0:
            if len(buffer) > protocol.MAX_COMMAND_SIZE:
                self.__removeClient(client, abort=True)
            return

        command = bytes(buffer[:endOfCommand]).decode(errors='replace').strip()
        del self.__commandBuffer[client]  # handshake is done
        self.__handleCommand(client, command)

    def __handleCommand(self, client: QTcpSocket, command: str):
        name, arguments = protocol.parseCommand(command)

        if name == protocol.COMMAND_SUBSCRIBE and len(arguments) == 1:
            self.__handleSubscription(client, arguments[0])
        elif name == protocol.COMMAND_LIST and len(arguments) == 0:
            self.__respondAndClose(client, protocol.buildPortsResponse(self.__capturedPorts()))
        else:
            self.__respondAndClose(client, protocol.RESPONSE_ERROR_UNKNOWN)

    def __handleSubscription(self, client: QTcpSocket, requestedPort: str):
        portName = SerialDataServer.__findPort(requestedPort, self.__capturedPorts())
        if portName is not None:
            clients = self.__subscribers.setdefault(portName, [])
            clients.append(client)
            client.write(protocol.encodeLine(protocol.buildOkResponse(portName)))
            self.signal_clientCountChanged.emit(portName, len(clients))
        elif SerialDataServer.__findPort(requestedPort, self.__knownPorts()) is not None:
            # port is known, but capture is stopped -> the port itself is free
            self.__respondAndClose(client, protocol.RESPONSE_ERROR_CLOSED)
        else:
            self.__respondAndClose(client, protocol.RESPONSE_ERROR_NO_PORT)

    @staticmethod
    def __findPort(requestedPort: str, portNames: list[str]) -> str | None:
        return next((name for name in portNames if name.upper() == requestedPort.upper()), None)

    @staticmethod
    def __respondAndClose(client: QTcpSocket, response: str):
        client.write(protocol.encodeLine(response))
        client.disconnectFromHost()  # written data is still sent

    def __removeClient(self, client: QTcpSocket, abort: bool = False):
        self.__commandBuffer.pop(client, None)
        for portName, clients in self.__subscribers.items():
            if client in clients:
                clients.remove(client)
                self.signal_clientCountChanged.emit(portName, len(clients))

        if abort:
            client.abort()

    @Slot()
    def __handleDisconnected(self):
        client: QTcpSocket = self.sender()
        self.__removeClient(client)
        client.deleteLater()
