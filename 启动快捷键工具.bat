@echo off
cd /d "%~dp0"
echo ========================================
echo Shortcut Tool Starting...
echo ========================================
echo Starting shortcut tool...
echo System tray icon will appear after startup
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Startup failed, please check Python environment
    echo Press any key to exit...
    pause >nul
)