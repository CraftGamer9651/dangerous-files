@echo off
setlocal enabledelayedexpansion

:: Define your script name here
set SCRIPT_NAME=your_script.py

echo =========================================
echo  Starting PyInstaller Bundle Process (Windows)
echo =========================================

:: 1. Check if PyInstaller is installed
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)

:: 2. Run PyInstaller to create a single executable
echo Compiling %SCRIPT_NAME% into a standalone binary...
pyinstaller --onefile "%SCRIPT_NAME%"

echo =========================================
echo  Success! Your executable is in the 'dist' folder.
echo =========================================
pause
