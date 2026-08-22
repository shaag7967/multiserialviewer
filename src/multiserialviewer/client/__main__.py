"""Command line client: writes the data of a serial port to stdout.

    multiserialviewer-client COM6 --baudrate 115200
    multiserialviewer-client --list

The received bytes go to stdout unchanged, everything else to stderr, so the
output can be piped into another program.
"""

import argparse
import sys

from multiserialviewer.client.serialDataClient import SerialDataClient, getPortsOccupiedByMsv
from multiserialviewer.serial_data import serialDataServerProtocol as protocol


def parseArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='multiserialviewer-client',
                                     description='Reads a serial port - through MultiSerialViewer if it '
                                                 'captures the port, otherwise directly.')
    parser.add_argument('portName', nargs='?', help="name of the serial port, e.g. 'COM6'")
    parser.add_argument('-b', '--baudrate', type=int, default=115200,
                        help='only used for direct access (default: %(default)s)')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list the ports currently occupied by MultiSerialViewer and exit')
    parser.add_argument('-n', '--no-direct-access', action='store_true',
                        help='fail instead of opening the serial port ourselves')
    parser.add_argument('--host', default=protocol.DEFAULT_HOST,
                        help='host of the MultiSerialViewer data server (default: %(default)s)')
    parser.add_argument('--tcp-port', type=int, default=protocol.DEFAULT_TCP_PORT,
                        help='TCP port of the MultiSerialViewer data server (default: %(default)s)')

    arguments = parser.parse_args()
    if not arguments.list and arguments.portName is None:
        parser.error('portName is required (or use --list)')
    return arguments


def listPorts(arguments: argparse.Namespace) -> int:
    portNames = getPortsOccupiedByMsv(arguments.host, arguments.tcp_port)
    print(' '.join(portNames) if portNames else 'MultiSerialViewer does not occupy any port')
    return 0


def readPort(arguments: argparse.Namespace) -> int:
    client = SerialDataClient(arguments.portName,
                              arguments.baudrate,
                              host=arguments.host,
                              tcpPort=arguments.tcp_port,
                              allowDirectAccess=not arguments.no_direct_access)
    try:
        client.open()
    except (OSError, ImportError) as e:
        print(f'{e}', file=sys.stderr)
        return 1

    print(f'reading from {client.description}, press Ctrl+C to stop', file=sys.stderr)
    try:
        while True:
            data = client.read()
            if not data:
                print('--- end of stream (the port is free now) ---', file=sys.stderr)
                break
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    except ConnectionError:
        print('--- connection lost, received data is incomplete ---', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

    return 0


def main() -> int:
    arguments = parseArguments()
    return listPorts(arguments) if arguments.list else readPort(arguments)


if __name__ == '__main__':
    sys.exit(main())
