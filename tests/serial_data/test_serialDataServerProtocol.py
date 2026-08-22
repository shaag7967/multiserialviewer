import pytest

from multiserialviewer.serial_data import serialDataServerProtocol as protocol


def test_encodeLineAppendsTheLineEnd():
    assert protocol.encodeLine('SUB COM6') == b'SUB COM6\n'


def test_subscribeCommandRoundTrip():
    name, arguments = protocol.parseCommand(protocol.buildSubscribeCommand('COM6'))
    assert name == protocol.COMMAND_SUBSCRIBE
    assert arguments == ['COM6']


def test_listCommandRoundTrip():
    name, arguments = protocol.parseCommand(protocol.buildListCommand())
    assert name == protocol.COMMAND_LIST
    assert arguments == []


def test_commandNameIsUpperCased():
    assert protocol.parseCommand('sub com6') == (protocol.COMMAND_SUBSCRIBE, ['com6'])


def test_emptyCommand():
    assert protocol.parseCommand('   ') == ('', [])


def test_okResponseRoundTrip():
    assert protocol.parseOkResponse(protocol.buildOkResponse('COM6')) == 'COM6'


@pytest.mark.parametrize('response', [protocol.RESPONSE_ERROR_CLOSED,
                                      protocol.RESPONSE_ERROR_NO_PORT,
                                      protocol.RESPONSE_ERROR_UNKNOWN,
                                      'OK',
                                      'OK COM6 COM7',
                                      ''])
def test_parseOkResponseRejectsEverythingElse(response):
    assert protocol.parseOkResponse(response) is None


def test_portsResponseRoundTrip():
    assert protocol.parsePortsResponse(protocol.buildPortsResponse(['COM3', 'COM6'])) == ['COM3', 'COM6']


def test_portsResponseWithoutPorts():
    assert protocol.parsePortsResponse(protocol.buildPortsResponse([])) == []


def test_parsePortsResponseRejectsOtherResponses():
    assert protocol.parsePortsResponse(protocol.RESPONSE_ERROR_UNKNOWN) == []
