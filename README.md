# DANGEROUS FILES
## How to use the RAT
### `build_all.py`
A Python file that will build all of the files needed for the RAT. Move the file into its own folder and run it.\
It will ask for the IP and port for the server PC. To find you PC's IP:\
**Windows**: Open the terminal and run `ipconfig`.\
**Mac/Linux**: Open the terminal and run `ifconfig`.\
Look for a section saying something similar to:\
Connection-specific DNS Suffix  . : home.local\
Link-local IPv6 Address . . . . . : xxx::xxx:xxx:xxx:xxx%xx\
IPv4 Address. . . . . . . . . . . : 192.168.1.xxx (Enter this)\
Subnet Mask . . . . . . . . . . . : 255.255.255.0\
Default Gateway . . . . . . . . . : 192.168.1.1 (Make sure there is an IP here)

The Python script will ask for a port. The default `9999` will work, but if you know another service is using it, change it.\
Once the build finishes, look in the `dist` folder for the `control_panel` and `system_helper`.

### Setup
Move the `system_helper` to the target PC and run it. Keep the `control_panel` on your PC and run it.\
In a few seconds, they should connect, and you will be able to run terminal commands to the target PC from your PC.

## Python to executables
These two files will convert any Python file to an executable that can be run on your device.
### Limitations 
If you are using a Windows PC, you will only be able to create Windows executables (`.exe` files).\
If you are on Mac/Linux, you will only be able to make their executable files.

## ZIP bombs
These two ZIP files will completely extract to their labeled size (10 petabytes and 4.5 terabytes) from only 15-20 kilobytes.\
If more sizes are requested, I will add them.
