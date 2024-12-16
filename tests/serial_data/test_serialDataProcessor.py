import pytest
from queue import Queue
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor


def test_basic_start_process_stop(qtbot):
    # create
    data_queue = Queue()
    processor = SerialDataProcessor(data_queue)
    assert processor._terminateEvent.is_set() is False
    assert processor._thread is None

    # start
    processor.start()
    assert processor._thread is not None
    assert processor._thread.is_alive()

    # process data
    data = bytearray('123'.encode('utf-8'))
    with qtbot.waitSignal(processor.dataAvailable, timeout=100) as signal_blocker:
        data_queue.put(data)  # shall trigger signal dataAvailable, else timeout error
    assert signal_blocker.args == ['123']

    # stop
    processor.stop()
    assert processor._thread is None
