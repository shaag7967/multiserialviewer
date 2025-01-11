import pytest

from multiserialviewer.serial_data.streamingTextExtractor import StreamingTextExtractor


def test_watchFinder_text(qtbot):
    watchExtractor = StreamingTextExtractor('watch1', r'watch:\s*(low|middle|high)')

    with qtbot.waitSignal(watchExtractor.signal_textExtracted, timeout=300) as signal_blocker:
        watchExtractor.processBytesFromStream('aawatch: 222\nwa')
        watchExtractor.processBytesFromStream('tc')
        watchExtractor.processBytesFromStream('h:')
        watchExtractor.processBytesFromStream(' lo')
        watchExtractor.processBytesFromStream('wm')
    assert signal_blocker.args == ['watch1', ['low']]


def test_watchFinder(qtbot):
    watchExtractor = StreamingTextExtractor('watch2', r'watch:\s*(\d+)')

    with qtbot.waitSignal(watchExtractor.signal_textExtracted, timeout=300) as signal_blocker:
        watchExtractor.processBytesFromStream('a: 222\nwa')
        watchExtractor.processBytesFromStream('tc')
        watchExtractor.processBytesFromStream('h:')
        watchExtractor.processBytesFromStream(' 1')
        watchExtractor.processBytesFromStream('2')
        watchExtractor.processBytesFromStream('3')
        watchExtractor.processBytesFromStream('4')
    assert signal_blocker.args == ['watch2', ['1234']]


def test_counterFinder(qtbot):
    counterExtractor = StreamingTextExtractor('counterA', r'counter')

    with qtbot.waitSignal(counterExtractor.signal_textExtracted, timeout=300) as signal_blocker:
        counterExtractor.processBytesFromStream('acounterco')
    assert signal_blocker.args == ['counterA', []]

    with qtbot.waitSignal(counterExtractor.signal_textExtracted, timeout=300) as signal_blocker:
        counterExtractor.processBytesFromStream('u')
        counterExtractor.processBytesFromStream('nte')
        counterExtractor.processBytesFromStream('r')
        counterExtractor.processBytesFromStream('w')
    assert signal_blocker.args == ['counterA', []]
