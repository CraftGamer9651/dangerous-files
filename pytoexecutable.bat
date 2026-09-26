@echo off
setlocal

echo ========================================
echo Python to Executable Builder
echo ========================================
echo.

set /p PYFILE=Enter the Python file name (example: main.py): 

if not exist "%PYFILE%" (
    echo.
    echo ERROR: File "%PYFILE%" was not found.
    pause
    exit /b 1
)

echo.
echo Installing/updating PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Building "%PYFILE%"...
python -m PyInstaller --onefile "%PYFILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo Executable is in the "dist" folder.
echo ========================================
pause
