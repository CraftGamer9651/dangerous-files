#!/bin/bash
set -e

echo "========================================="
echo " PyInstaller Interactive Bundler (Unix) "
echo "========================================="

# 1. Ask the user for the filename
read -p "Enter the Python filename (default: main.py): " SCRIPT_NAME

# Use default if input is empty
SCRIPT_NAME="${SCRIPT_NAME:-main.py}"

# Verify the file actually exists before proceeding
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "❌ Error: File '$SCRIPT_NAME' not found in this directory!"
    exit 1
fi

# 2. Check and install PyInstaller if missing
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
else
    echo "PyInstaller is already installed."
fi

# 3. Run PyInstaller
echo "Compiling $SCRIPT_NAME into a standalone binary..."
pyinstaller --onefile "$SCRIPT_NAME"

echo "========================================="
echo " 🎉 Success! Your executable is in the 'dist' folder."
echo "========================================="
