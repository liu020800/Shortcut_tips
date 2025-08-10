#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_exe.py
使用PyInstaller将Python程序打包成独立可执行文件的脚本
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PyInstaller安装失败")
        return False

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 无控制台窗口
        "--name=快捷键提示工具",          # 可执行文件名称
        "--icon=icon.svg",              # 图标文件
        "--add-data=shortcuts.json;.",  # 添加配置文件
        "--add-data=process_mapping.json;.",  # 添加进程映射文件
        "--add-data=icon.svg;.",        # 添加图标文件
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=pynput",
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False

def create_portable_package():
    """创建便携版包"""
    print("创建便携版包...")
    
    # 创建便携版目录
    portable_dir = "快捷键提示工具_便携版"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    os.makedirs(portable_dir)
    
    # 复制可执行文件
    exe_path = os.path.join("dist", "快捷键提示工具.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, portable_dir)
    
    # 复制配置文件
    config_files = ["shortcuts.json", "process_mapping.json", "README.md"]
    for file in config_files:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
    
    # 创建启动批处理文件
    bat_content = '''@echo off
cd /d "%~dp0"
echo 启动快捷键提示工具...
start "" "快捷键提示工具.exe"
'''
    
    with open(os.path.join(portable_dir, "启动工具.bat"), "w", encoding="gbk") as f:
        f.write(bat_content)
    
    print(f"✓ 便携版包已创建: {portable_dir}")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("快捷键提示工具 - 可执行文件构建脚本")
    print("=" * 50)
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("请手动安装PyInstaller: pip install pyinstaller")
            return False
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 创建便携版包
    if not create_portable_package():
        return False
    
    print("\n" + "=" * 50)
    print("构建完成！")
    print("便携版文件夹: 快捷键提示工具_便携版")
    print("用户可以直接运行其中的 快捷键提示工具.exe")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()