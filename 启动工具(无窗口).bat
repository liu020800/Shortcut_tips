@echo off
REM Silent startup for shortcut tool
REM Use pythonw.exe to completely hide console window

REM Switch to script directory
cd /d "%~dp0"

REM Check if pythonw.exe is available
pythonw --version >nul 2>&1
if %errorlevel% neq 0 (
    REM If pythonw is not available, try python
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python environment not detected!
        echo Please install Python 3.7+ or ensure Python is added to system PATH
        pause
        exit /b 1
    )
    REM Use python to start (will have brief console window)
    start /min python start_hidden.py
) else (
    REM Use pythonw to start (completely windowless)
    pythonw start_hidden.py
)

REM Exit immediately without waiting
exit /b 0