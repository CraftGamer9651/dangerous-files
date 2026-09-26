## How to Use

### RAT Python scripts
#### `build_rat.py` (Automatic installation)
Run this on the server PC, it will create four executable files.
Windows: `dist/system_helper.exe` and `dist/control_panel.exe`
Mac/Linux: `dist/system_helper` and `dist/control_panel`

Run these on their corresponding system.

#### `install_client.py`/`system_helper.py` (Manual installation)
`install_client.py`:
Installs the client Python file, asks for the target server IP address, and copies the run command to clipboard.

`system_helper.py`:
Runs the target end of the RAT. Receives commands and sends back an output.

#### `install_server.py`/`control_panel.py` (Manual installation)
`install_server.py`:
Installs the server Python file, asks for the port to use, and copies the run command to clipboard.

`control_panel.py`:
Runs the attacker end of the RAT. Sends commands and receives the output.

### Python to executable scripts
Both `pytoexecutable.bat` and `pytoexecutable.sh` convert the target Python file to a Windows EXE and Mac/Linux executable.
`pytoexecutable.bat` runs on Windows and `pytoexecutable.sh` runs on Mac/Linux.

###ZIP bombs
`zipbomb_10pb.zip` is a 19kb zip file that unzips to 10pb.
`zipbomb_4.5tb.zip` is a 15kb zip file that unzips to 4.5tb.
