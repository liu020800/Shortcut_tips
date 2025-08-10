#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
start_hidden.py
无窗口启动快捷键提示工具的包装脚本
"""

import sys
import os
import subprocess

def main():
    """
    无窗口启动主程序
    """
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(current_dir, "main.py")
        
        # 检查main.py是否存在
        if not os.path.exists(main_script):
            print(f"错误: 找不到主程序文件 {main_script}")
            return 1
        
        # 使用pythonw启动主程序（无窗口）
        try:
            # 尝试使用pythonw（无控制台窗口）
            subprocess.Popen(["pythonw", main_script], 
                           cwd=current_dir,
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            print("快捷键提示工具已在后台启动")
        except FileNotFoundError:
            # 如果pythonw不可用，使用python但隐藏窗口
            if sys.platform == "win32":
                subprocess.Popen(["python", main_script], 
                               cwd=current_dir,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["python", main_script], 
                               cwd=current_dir)
            print("快捷键提示工具已启动")
        
        return 0
        
    except Exception as e:
        print(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())