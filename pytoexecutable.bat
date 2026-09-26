@echo off
setlocal enabledelayedexpansion

echo =========================================
echo  PyInstaller Interactive Bundler (Windows)
echo =========================================

:: 1. Ask the user for the filename
set /p SCRIPT_NAME="Enter the Python filename (default: main.py): "

:: Use default if input is empty
if "%SCRIPT_NAME%"=="" set SCRIPT_NAME=main.py

:: Verify the file actually exists before proceeding
if not exist "%SCRIPT_NAME%" (
    echo 0x07
    echo 0x07
    echo 0x07
    echo ❌ Error: File '%SCRIPT_NAME%' not found in this directory!
    goto end
)

:: 2. Check and install PyInstaller if missing
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)

:: 3. Run PyInstaller
echo Compiling %SCRIPT_NAME% into a standalone binary...
pyinstaller --onefile "%SCRIPT_NAME%"

echo =========================================
echo  🎉 Success! Your executable is in the 'dist' folder.
echo =========================================

:end
pause
