#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
autostart_manager.py
开机自启动管理模块
"""

import os
import sys
import winreg
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AutostartManager:
    """
    Windows开机自启动管理器
    通过注册表管理程序的开机自启动
    """
    
    def __init__(self):
        # 注册表路径
        self.reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        # 应用名称（注册表键名）
        self.app_name = "ShortcutTool"
        # 获取当前执行文件的路径
        self.exe_path = self._get_exe_path()
        
    def _get_exe_path(self):
        """
        获取当前执行文件的完整路径
        
        Returns:
            str: 执行文件路径
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            return sys.executable
        else:
            # 如果是Python脚本，返回Python解释器和脚本路径
            script_path = os.path.abspath(__file__).replace('autostart_manager.py', 'main.py')
            return f'"{sys.executable}" "{script_path}"'
    
    def is_autostart_enabled(self):
        """
        检查是否已启用开机自启动
        
        Returns:
            bool: True表示已启用，False表示未启用
        """
        try:
            # 打开注册表键
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_READ) as key:
                try:
                    # 尝试读取值
                    value, _ = winreg.QueryValueEx(key, self.app_name)
                    # 检查路径是否匹配当前程序路径
                    current_path = self.exe_path.strip('"')
                    stored_path = value.strip('"')
                    
                    # 如果是exe文件，直接比较路径
                    if getattr(sys, 'frozen', False):
                        return os.path.normpath(stored_path) == os.path.normpath(current_path)
                    else:
                        # 如果是Python脚本，检查是否包含正确的脚本路径
                        return current_path in stored_path
                        
                except FileNotFoundError:
                    return False
        except Exception as e:
            logger.error(f"检查自启动状态失败: {e}")
            return False
    
    def enable_autostart(self):
        """
        启用开机自启动
        
        Returns:
            bool: True表示成功，False表示失败
        """
        try:
            # 打开注册表键（如果不存在则创建）
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE) as key:
                # 设置值
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.exe_path)
                logger.info(f"已启用开机自启动: {self.exe_path}")
                return True
        except Exception as e:
            logger.error(f"启用自启动失败: {e}")
            return False
    
    def disable_autostart(self):
        """
        禁用开机自启动
        
        Returns:
            bool: True表示成功，False表示失败
        """
        try:
            # 打开注册表键
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE) as key:
                try:
                    # 删除值
                    winreg.DeleteValue(key, self.app_name)
                    logger.info("已禁用开机自启动")
                    return True
                except FileNotFoundError:
                    # 如果值不存在，也算成功
                    logger.info("自启动项不存在，无需禁用")
                    return True
        except Exception as e:
            logger.error(f"禁用自启动失败: {e}")
            return False
    
    def toggle_autostart(self):
        """
        切换自启动状态
        
        Returns:
            bool: 切换后的状态（True表示已启用，False表示已禁用）
        """
        if self.is_autostart_enabled():
            self.disable_autostart()
            return False
        else:
            self.enable_autostart()
            return True
    
    def get_autostart_info(self):
        """
        获取自启动相关信息
        
        Returns:
            dict: 包含自启动状态和路径信息的字典
        """
        return {
            'enabled': self.is_autostart_enabled(),
            'exe_path': self.exe_path,
            'app_name': self.app_name,
            'reg_path': self.reg_path
        }

# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建自启动管理器
    manager = AutostartManager()
    
    # 显示当前状态
    info = manager.get_autostart_info()
    print(f"自启动状态: {'已启用' if info['enabled'] else '已禁用'}")
    print(f"程序路径: {info['exe_path']}")
    print(f"注册表项: {info['app_name']}")
    
    # 测试切换功能
    print("\n切换自启动状态...")
    new_status = manager.toggle_autostart()
    print(f"新状态: {'已启用' if new_status else '已禁用'}")