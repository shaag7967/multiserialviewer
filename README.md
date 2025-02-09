
# multiserialviewer

See multiple serial text streams in a single window

## What you can do with it

- evaluate the output of one or more serial ports
- automatically highlight text, e.g. in color, according to user-defined patterns
- open and close all serial ports with a single click
- search the output of a serial port and navigate between the findings
- watch key-value pairs and display the last value
- count text while the data is being received
- get insights into your serial port bandwidth utilization
- keep all your settings and window sizes until next time 

## Screenshots

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/multiserialviewer.png?raw=true" width="70%" alt="example with two serial connections">


## Installation

You can install this tool using the package installer for Python ([pypi/multiserialviewer](https://pypi.org/project/multiserialviewer/)).

    pip install multiserialviewer

If already installed, run the following command to install the latest version:

    pip install multiserialviewer --upgrade

## Start

After installation using pip, you can start it by running 

    multiserialviewer

in a console.

### Start it using a Windows batch file

Create a batch file, e.g. multiserialviewer.bat, with the following content (*enter your python path accordingly*):

    start /B pythonw "C:\myPythonInstallDir\Python311\Scripts\multiserialviewer.exe"

With this, you will not get a console window in the background.

## Usage

### Set up your serial port connections

Click the button "Create Viewer" and enter your connection details. You can give 
the window a name and set your autoscroll preferences. The latter may be changed 
at any time later (but not the connection details).

It is not possible to create a viewer for the same port multiple times.

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/create_serial_viewer.png?raw=true" width="70%" alt="create serial viewer connection">

### Open your serial ports and receive data

After you created all SerialViewers you need, start receiving your data by clicking 
"Start Capture".

You can close all serial ports by clicking "Stop Capture".

If one of your serial ports can not be opened, you will see an error message in the corresponding 
SerialView window. In this case all other connections will be closed again automatically.

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/open_error.png?raw=true" width="70%">

#### What data is displayed?

You will only see printable characters in the output window, meaning every character with 
a value between (including) 32 and 126. LineFeed and CarriageReturn will cause a line break/new line.

If you want to see non-printable characters (in hex), you can enable this in the settings 
dialog. E.g. '\0' will then be printed as [00].

### Work with the data you received (while you receive it)

#### Specify text patterns to highlight information

If you want to highlight specific text, you can define text patterns using regular expression syntax. 
If you just want to highlight certain words, just enter them as normal text.

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/highlighter_settings.png?raw=true" width="60%">

#### Search for a word and jump to the next/previous occurrence

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/navigate.png?raw=true" width="60%">

#### Watch values of key-value pairs

If you receive a lot of data and want to keep track of single values, e.g. `temperature=88`, you 
can create a watch and display these values in a separate table. In this table, the last received 
value will be displayed.

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/create_watch_menu.png?raw=true" width="60%">

#### Count the occurrence of text patterns

If you are just interested in the number of occurrences of a word (or text pattern), you can 
create counter.

<img src="https://github.com/shaag7967/multiserialviewer/blob/main/doc/img/create_counter_menu.png?raw=true" width="60%">

#### Get an idea of how much data you received and bandwidth is left

In the statistics tab you find basic information about the received data.


