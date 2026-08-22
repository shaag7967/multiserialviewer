"""Reads serial data - either through MultiSerialViewer or directly from the port.

A serial port can only be opened by one application at a time. If MultiSerialViewer
(MSV) is running and captures the port, it hands out the received data via a local
TCP socket ("Serial data server" in the MSV settings). Otherwise the port is free
and can be opened directly.

    from multiserialviewer.client import SerialDataClient

    with SerialDataClient('COM6', 115200) as client:
        print(f'reading from {client.description}')
        while True:
            data = client.read()
            if not data:
                break            # port was released by MSV / stream ended
            ...

SerialDataClient figures out which of the two ways works, so a script does not have
to know whether MSV is running.

Only the standard library is needed for reading through MSV. Direct access to the
serial port needs pyserial ('pip install multiserialviewer[direct]').
"""

import socket
import time

from multiserialviewer.serial_data import serialDataServerProtocol as protocol

_HANDSHAKE_TIMEOUT_S: float = 1.0
# read() waits in slices instead of blocking forever. Only that way the interpreter
# gets the chance to run signal handlers, i.e. Ctrl+C works without waiting for the
# next received character (a blocking read is not interrupted by a signal on Windows).
_READ_TIMEOUT_S: float = 0.5


class SerialDataClient:
    """Reads the data of one serial port, via MultiSerialViewer or directly.

    The connection is established by open() or by using the client as a context
    manager. viaMsv and description are meaningful only while the client is open.
    """

    def __init__(self, portName: str,
                 baudrate: int = 115200,
                 *,
                 host: str = protocol.DEFAULT_HOST,
                 tcpPort: int = protocol.DEFAULT_TCP_PORT,
                 allowDirectAccess: bool = True,
                 retries: int = 3,
                 retryDelay: float = 0.2,
                 **serialPortKwargs):
        """
        :param portName: name of the serial port, e.g. 'COM6'
        :param baudrate: only used for direct access, MSV uses its own settings
        :param host: host the MSV data server runs on
        :param tcpPort: TCP port of the MSV data server
        :param allowDirectAccess: if False, the serial port is never opened by us.
               Use it if the port must not be occupied under any circumstances.
        :param retries: attempts to survive MSV opening the port just in between
        :param serialPortKwargs: further arguments for serial.Serial()
        """
        self.portName: str = portName
        self.__baudrate: int = baudrate
        self.__host: str = host
        self.__tcpPort: int = tcpPort
        self.__allowDirectAccess: bool = allowDirectAccess
        self.__retries: int = max(1, retries)
        self.__retryDelay: float = retryDelay
        self.__serialPortKwargs: dict = serialPortKwargs

        self.__stream: _MsvStream | _SerialPortStream | None = None

    @property
    def isOpen(self) -> bool:
        return self.__stream is not None

    @property
    def viaMsv(self) -> bool:
        """True if the data is provided by MultiSerialViewer."""
        return isinstance(self.__stream, _MsvStream)

    @property
    def description(self) -> str:
        if self.__stream is None:
            return f'{self.portName} (not opened)'
        return f'{self.portName} (via MultiSerialViewer)' if self.viaMsv else f'{self.portName} (direct)'

    def open(self):
        """Connects to MSV or - if it does not hold the port - to the port itself.

        Raises ConnectionError if MSV does not provide the port and direct access
        is not allowed, otherwise the error of the failed serial port access.
        """
        if self.isOpen:
            return

        lastError = None
        for _ in range(self.__retries):
            stream = _MsvStream.connect(self.portName, self.__host, self.__tcpPort)
            if stream is not None:
                self.__stream = stream
                self.portName = stream.portName  # as MSV spells it
                return

            if not self.__allowDirectAccess:
                raise ConnectionError(f'{self.portName} is not provided by MultiSerialViewer '
                                      f'and direct access is not allowed')
            try:
                self.__stream = _SerialPortStream(self.portName, self.__baudrate, **self.__serialPortKwargs)
                return
            except OSError as e:
                # MSV might have opened the port in the meantime -> ask it again
                lastError = e
                time.sleep(self.__retryDelay)

        raise lastError

    def read(self, size: int = 4096) -> bytes:
        """Waits until data is received and returns it.

        Returns b'' if the stream ended in an orderly way. Reading through MSV that
        happens when the capture is stopped, the serial viewer is removed or MSV is
        closed - in all these cases the serial port is free afterwards.

        Raises ConnectionError if MSV had to drop us because we did not read fast
        enough. Data is missing then, the stream must not be used any further.
        """
        if self.__stream is None:
            raise RuntimeError(f'{self.portName} is not opened')
        return self.__stream.read(size)

    def close(self):
        if self.__stream is not None:
            self.__stream.close()
            self.__stream = None

    def __enter__(self) -> 'SerialDataClient':
        self.open()
        return self

    def __exit__(self, *args):
        self.close()


def getPortsOccupiedByMsv(host: str = protocol.DEFAULT_HOST,
                          tcpPort: int = protocol.DEFAULT_TCP_PORT) -> list[str]:
    """Returns the ports MSV is capturing at the moment.

    The list is empty if MSV is not running, its data server is disabled or it
    does not capture anything. All these ports can be read with a SerialDataClient.
    """
    result = _sendCommand(protocol.buildListCommand(), host, tcpPort)
    if result is None:
        return []

    sock, response = result
    sock.close()
    return protocol.parsePortsResponse(response)


def _readLine(sock: socket.socket) -> str:
    # read byte by byte on purpose: everything behind the line end already belongs
    # to the data stream and must not end up in a buffer we throw away
    line = bytearray()
    lineEnd = protocol.LINE_END.encode()
    while not line.endswith(lineEnd):
        b = sock.recv(1)
        if not b:
            return ''
        line += b
    return line.decode(errors='replace').strip()


def _sendCommand(command: str, host: str, tcpPort: int) -> tuple[socket.socket, str] | None:
    """Sends a single command to MSV. Returns the socket and the response line."""
    try:
        sock = socket.create_connection((host, tcpPort), timeout=_HANDSHAKE_TIMEOUT_S)
    except OSError:
        return None  # MSV is not running or its data server is disabled

    try:
        sock.sendall(protocol.encodeLine(command))
        response = _readLine(sock)
    except OSError:
        sock.close()
        return None

    return sock, response


class _MsvStream:
    """Receives the data of a serial port from MultiSerialViewer."""

    def __init__(self, sock: socket.socket, portName: str):
        sock.settimeout(_READ_TIMEOUT_S)
        self.__socket = sock
        self.portName: str = portName

    @staticmethod
    def connect(portName: str, host: str, tcpPort: int) -> '_MsvStream | None':
        """Returns a stream if MSV currently occupies portName, otherwise None."""
        result = _sendCommand(protocol.buildSubscribeCommand(portName), host, tcpPort)
        if result is None:
            return None

        sock, response = result
        acceptedPortName = protocol.parseOkResponse(response)
        if acceptedPortName is not None:
            return _MsvStream(sock, acceptedPortName)

        # ERR CLOSED (capture stopped) or ERR NOPORT (unknown port):
        # in both cases the serial port itself is free
        sock.close()
        return None

    def read(self, size: int) -> bytes:
        while True:
            try:
                return self.__socket.recv(size)
            except TimeoutError:
                pass  # nothing received yet, see _READ_TIMEOUT_S

    def close(self):
        self.__socket.close()


class _SerialPortStream:
    """Receives the data directly from the serial port."""

    def __init__(self, portName: str, baudrate: int, **kwargs):
        try:
            import serial  # only needed for direct access
        except ImportError as e:
            raise ImportError(f'{portName} is not provided by MultiSerialViewer and direct '
                              f'access needs pyserial (pip install multiserialviewer[direct])') from e

        kwargs.setdefault('timeout', _READ_TIMEOUT_S)
        self.__port = serial.Serial(portName, baudrate, **kwargs)

    def read(self, size: int) -> bytes:
        while True:
            # read() would wait for exactly 'size' bytes, so we limit it to what is there
            data = self.__port.read(max(1, min(size, self.__port.in_waiting)))
            if data:
                return data  # otherwise nothing was received, see _READ_TIMEOUT_S

    def close(self):
        self.__port.close()
