@echo off
echo ========================================
echo 快捷键提示工具启动中...
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境！
    echo 请先安装Python 3.7+，或确保Python已添加到系统PATH
    pause
    exit /b 1
)

REM 检查依赖包
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo 检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
)

echo 正在启动快捷键提示工具...
echo 工具启动后，系统托盘会出现图标
python main.py

if %errorlevel% neq 0 (
    echo 启动失败！请检查日志文件shortcut_tool.log
    pause
) else (
    echo 工具已正常退出
    timeout /t 2 >nul
)