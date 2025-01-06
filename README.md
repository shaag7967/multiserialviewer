
# multiserialviewer
Shows multiple serial text streams in a single window with individual highlighting options

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/multiserialviewer.png?raw=true" width="70%" alt="example with two serial connections">


## Motivation for using this tool
Imagine you have several embedded devices / MCUs all printing out debug information over a UART. You don't want to use a terminal program (e.g. HTerm) for every COM port manually. You want to easily open all COM ports at once and clear all received data with a single click. Would be nice, if important text messages could be highlighted with different colors, so you don't have to read everything your devices are telling you.

## Installation
You can install this tool using the package installer for Python ([pypi/multiserialviewer](https://pypi.org/project/multiserialviewer/)).

    pip install multiserialviewer

If already installed, run the following command to install the latest version:

    pip install multiserialviewer --upgrade

## Usage
After installation using pip, you can start it by running 

    multiserialviewer
in a console (or by directly clicking '\Scripts\multiserialviewer.exe' in your python install directory).

### Setting up your serial/COM port connections
Click in the top left corner on "Create Viewer" and enter your connection details. After you created all SerialViewers you need, start receiving your text data by clicking on "Start Capture".

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/create_serial_viewer.png?raw=true" width="70%" alt="create serial viewer connection">

If one of your serial ports can not be opened, you will see an error message in the corresponding SerialView window. In this case all other connections/SerialViewer will be closed again.

### Specifying text patterns for highlighting
If you want to highlight specific text, you can define text patterns using regular expression syntax. If you just want to highlight certain words, enter them as normal text in the highlighter settings dialog (Highlighter).

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/highlighter_settings.png?raw=true" width="60%" alt="highlighter settings">
