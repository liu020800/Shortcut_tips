@echo off
echo Starting Shortcut Tool...
echo Starting application...
"快捷键提示工具.exe"
if errorlevel 1 (
    echo Error: Failed to start the application
    pause
)