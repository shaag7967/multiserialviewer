# Release Notes

## 26.8.0

### New: Serial Data Server & Client

A serial port can normally only be opened by one application at a time. The new **serial data server**
shares the raw data of all captured ports with other programs, so you no longer have to stop capturing.

- Enable it in the settings dialog; TCP port configurable (default 45600), settings are persisted
- Read-only server with a minimal text protocol: `SUB <port>` subscribes to the data stream,
  `LIST` returns the ports currently held by multiserialviewer
- Viewer window titles show active readers, e.g. `COM6  [1 client is reading]`

**Python client** (`multiserialviewer.client.SerialDataClient`):

- Reads through multiserialviewer if it holds the port, otherwise opens the port directly - your script
  does not need to know which applies (`allowDirectAccess=False` disables the direct path)
- Importing it does not pull in PySide6; only direct port access needs pyserial
  (`pip install multiserialviewer[direct]`)
- Also provides `getPortsOccupiedByMsv()`, `DEFAULT_HOST` and `DEFAULT_TCP_PORT`

**Command line:**

```console
multiserialviewer-client COM6 --baudrate 115200   # raw data to stdout, can be piped
multiserialviewer-client --list                   # ports currently occupied
```

Documented in the README, with a full example in
[examples/readSerialData.py](examples/readSerialData.py) and tests for server, protocol, client
and window title.

### Improvements

- **Text highlighter:** an invalid regular expression no longer raises - the offending pattern is skipped
- **Watch handler:** consistency checks now raise descriptive `ValueError`s instead of `assert`
  (so they stay active under `python -O`)
- **StreamingTextExtractor:** `alreadyProcessed` is now initialized, fixing a possible attribute error
  in the timeout handler

### Other

- Version bumped to **26.8.0**
