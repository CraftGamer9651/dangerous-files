#!/bin/bash

echo "========================================"
echo "Python to Executable Builder"
echo "========================================"
echo

read -p "Enter the Python file name (example: main.py): " PYFILE

if [ ! -f "$PYFILE" ]; then
    echo
    echo "ERROR: File '$PYFILE' was not found."
    exit 1
fi

echo
echo "Installing/updating PyInstaller..."
python3 -m pip install --upgrade pyinstaller

echo
echo "Building '$PYFILE'..."

python3 -m PyInstaller --onefile "$PYFILE"

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed."
    exit 1
fi

echo
echo "========================================"
echo "Build successful!"
echo "Executable is in the 'dist' folder."
echo "========================================"
