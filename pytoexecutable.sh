#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define your script name here
SCRIPT_NAME="your_script.py"

echo "========================================="
echo " Starting PyInstaller Bundle Process (Unix) "
echo "========================================="

# 1. Check if PyInstaller is installed, install if missing
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
else
    echo "PyInstaller is already installed."
fi

# 2. Run PyInstaller to create a single executable
echo "Compiling $SCRIPT_NAME into a standalone binary..."
pyinstaller --onefile "$SCRIPT_NAME"

echo "========================================="
echo " Success! Your executable is in the 'dist' folder."
echo "========================================="
