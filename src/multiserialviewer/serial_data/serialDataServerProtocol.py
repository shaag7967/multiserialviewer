"""Protocol spoken by the serial data server of MultiSerialViewer.

Used by both sides - the server (serialDataServer.py) and the client
(multiserialviewer.client.serialDataClient) - so that the wire format exists
exactly once.

IMPORTANT: this module must stay free of Qt and of any other dependency. A client
imports it and shall not be forced to install PySide6 because of that.

A client connects, sends a single command line and receives a single response line.
In case of a subscription the raw data of the serial port follows:

    SUB COM6\\n  ->  'OK COM6\\n' + raw data stream
                     'ERR CLOSED\\n' if the port is currently not captured
                     'ERR NOPORT\\n' if no serial viewer exists for that port
    LIST\\n      ->  'PORTS COM3 COM6\\n' (ports currently occupied by the server)
"""

DEFAULT_HOST: str = '127.0.0.1'
DEFAULT_TCP_PORT: int = 45600

LINE_END: str = '\n'
# a command line is short, everything above this is not one of our clients
MAX_COMMAND_SIZE: int = 100

COMMAND_SUBSCRIBE: str = 'SUB'
COMMAND_LIST: str = 'LIST'

RESPONSE_OK: str = 'OK'          # followed by the port name and the raw data stream
RESPONSE_PORTS: str = 'PORTS'    # followed by the port names
RESPONSE_ERROR_CLOSED: str = 'ERR CLOSED'    # port is known, but not captured
RESPONSE_ERROR_NO_PORT: str = 'ERR NOPORT'   # no serial viewer for that port
RESPONSE_ERROR_UNKNOWN: str = 'ERR UNKNOWN'  # command not understood


def encodeLine(line: str) -> bytes:
    """Turns a command or response into the bytes that go over the socket."""
    return f'{line}{LINE_END}'.encode()


def buildSubscribeCommand(portName: str) -> str:
    return f'{COMMAND_SUBSCRIBE} {portName}'


def buildListCommand() -> str:
    return COMMAND_LIST


def parseCommand(line: str) -> tuple[str, list[str]]:
    """Splits a command line into its name (upper case) and its arguments."""
    parts = line.split()
    return (parts[0].upper(), parts[1:]) if parts else ('', [])


def buildOkResponse(portName: str) -> str:
    return f'{RESPONSE_OK} {portName}'


def buildPortsResponse(portNames: list[str]) -> str:
    return ' '.join([RESPONSE_PORTS] + list(portNames))


def parseOkResponse(line: str) -> str | None:
    """Returns the port name of an OK response, None if it is not one."""
    parts = line.split()
    return parts[1] if len(parts) == 2 and parts[0] == RESPONSE_OK else None


def parsePortsResponse(line: str) -> list[str]:
    """Returns the port names of a PORTS response, empty if it is not one."""
    parts = line.split()
    return parts[1:] if parts and parts[0] == RESPONSE_PORTS else []
