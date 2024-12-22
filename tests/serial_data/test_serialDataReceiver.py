import pytest

from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings

from serial import SerialException

def test_serial(mocker):
    settings = SerialConnectionSettings('MyPortName')
    receiver = SerialDataReceiver(settings)
    assert receiver._terminateEvent.is_set() is False
    assert receiver._thread is None
    assert receiver._serialPort is None

    mocker.patch('serial.Serial.open', side_effect=SerialException)
    assert receiver.open_port() == False
    assert receiver._serialPort is not None

    mocker.patch('serial.Serial.open')
    assert receiver.open_port() == True
    assert receiver._serialPort.port == 'MyPortName'



