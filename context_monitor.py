#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
context_monitor.py

该模块负责监控系统上下文，获取当前活动窗口的进程信息。
按照开发指南要求，提供快速、可靠的进程名获取功能。
"""

import win32gui
import win32process
import psutil
import logging
import time
import json
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ContextMonitor:
    """获取当前活动窗口的进程信息
    
    提供快速、可靠的当前活动窗口进程信息获取功能，
    支持进程名缓存和错误处理，支持自定义进程映射。
    """

    # 常见IDE和编辑器映射
    IDE_MAPPING = {
        'code.exe', 'pycharm64.exe', 'devenv.exe',
        'atom.exe', 'sublime_text.exe', 'notepad++.exe',
        'webstorm64.exe', 'idea64.exe', 'clion64.exe'
    }
    
    # 进程信息缓存（避免频繁调用系统API）
    _cache = {}
    _cache_timeout = 0.1  # 100ms缓存超时
    
    # 进程映射缓存
    _process_mappings = None
    _mapping_cache_time = 0
    _mapping_cache_timeout = 5.0  # 5秒缓存超时

    @staticmethod
    def _load_process_mappings() -> Dict[str, str]:
        """加载进程映射配置
        
        Returns:
            dict: 进程映射字典，键为实际进程名，值为配置键名
        """
        current_time = time.time()
        
        # 检查缓存
        if (ContextMonitor._process_mappings is not None and 
            current_time - ContextMonitor._mapping_cache_time < ContextMonitor._mapping_cache_timeout):
            return ContextMonitor._process_mappings
        
        try:
            # 先定义内置常用映射（可被用户配置覆盖）
            builtin_mappings = {
                # 浏览器与常用应用
                "chrome.exe": "chrome.exe",
                "firefox.exe": "firefox.exe",
                "msedge.exe": "chrome.exe",
                "code.exe": "code.exe",
                "notepad++.exe": "notepad++.exe",
                "explorer.exe": "explorer.exe",
                
                # CAD 家族常见可执行名 → 统一归并到 acad.exe 配置
                "acad.exe": "acad.exe",
                "acadlt.exe": "acad.exe",
                "map3d.exe": "acad.exe",
                "civil3d.exe": "acad.exe",
                "zwcad.exe": "acad.exe",         # 中望CAD
                "gstarcad.exe": "acad.exe",      # 浩辰CAD
                
                # CASS（如存在独立进程时）
                "cass.exe": "cass.exe",
            }
            
            # 获取映射文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_file = os.path.join(current_dir, "process_mapping.json")
            file_mappings = {}
            
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_mappings = data.get("mappings", {})
            
            # 合并映射：用户配置优先于内置映射
            mappings = {**builtin_mappings, **file_mappings}
            
            # 更新缓存
            ContextMonitor._process_mappings = mappings
            ContextMonitor._mapping_cache_time = current_time
            
            return mappings
            
        except Exception as e:
            logger.warning(f"加载进程映射失败: {e}")
            # 返回内置映射，保证基本可用
            ContextMonitor._process_mappings = {
                "chrome.exe": "chrome.exe",
                "firefox.exe": "firefox.exe",
                "msedge.exe": "chrome.exe",
                "code.exe": "code.exe",
                "notepad++.exe": "notepad++.exe",
                "explorer.exe": "explorer.exe",
                "acad.exe": "acad.exe",
                "acadlt.exe": "acad.exe",
                "map3d.exe": "acad.exe",
                "civil3d.exe": "acad.exe",
                "zwcad.exe": "acad.exe",
                "gstarcad.exe": "acad.exe",
                "cass.exe": "cass.exe",
            }
            ContextMonitor._mapping_cache_time = current_time
            return ContextMonitor._process_mappings
    
    @staticmethod
    def clear_mapping_cache():
        """清除进程映射缓存，强制重新加载配置"""
        ContextMonitor._process_mappings = None
        ContextMonitor._mapping_cache_time = 0
        logger.info("进程映射缓存已清除")
    
    @staticmethod
    def get_current_process_name() -> str:
        """获取当前活动窗口的进程名
        
        返回小写的可执行文件名，如 'code.exe', 'explorer.exe' 等。
        对于无法识别的情况返回 'default'。
        
        Returns:
            str: 进程名（小写），失败时返回 'default'
        """
        current_time = time.time()
        
        # 检查缓存
        if ('process_name' in ContextMonitor._cache and 
            current_time - ContextMonitor._cache.get('timestamp', 0) < ContextMonitor._cache_timeout):
            return ContextMonitor._cache['process_name']
        
        result = "default"
        raw_name = "default"
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid and psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    raw_name = process.name().lower()
        except Exception as e:
            logger.warning(f"获取进程名失败: {e}")
            raw_name = "default"
            
        # 如果无法通过进程直接识别，使用窗口标题进行启发式判断
        if raw_name == "default":
            try:
                title = ContextMonitor.get_current_window_title().lower()
                if title:
                    if ("autocad" in title or "zwcad" in title or "gstarcad" in title or " cad" in title):
                        raw_name = "acad.exe"
                    if "cass" in title:
                        # CASS 作为 AutoCAD 插件较常见，若标题包含 CASS，则优先归类为 cass
                        raw_name = "cass.exe"
            except Exception:
                pass
        
        # 排除工具自身进程和相关Python进程（若误判为自身）
        excluded_processes = {
            "python.exe", "pythonw.exe", "py.exe", "pyw.exe",
            "python", "py", "python3", "python3.exe"
        }
        if raw_name in excluded_processes:
            try:
                import os
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == os.getpid():
                    raw_name = "default"
            except Exception:
                raw_name = "default"
        
        # 应用进程映射
        mappings = ContextMonitor._load_process_mappings()
        mapped_result = mappings.get(raw_name, raw_name)
        
        # 更新缓存
        ContextMonitor._cache = {
            'process_name': mapped_result,
            'timestamp': current_time
        }
        
        logger.debug(f"进程名映射: {raw_name} → {mapped_result}")
        return mapped_result

    @staticmethod
    def get_current_window_title() -> str:
        """获取当前活动窗口的标题
        
        Returns:
            str: 窗口标题，失败时返回空字符串
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return ""
            return win32gui.GetWindowText(hwnd)
        except Exception as e:
            logger.warning(f"获取窗口标题失败: {e}")
            return ""

    @staticmethod
    def get_current_window_info() -> Dict[str, Any]:
        """获取当前活动窗口的详细信息
        
        Returns:
            dict: 包含进程名、窗口标题、PID等信息的字典
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return {
                    "process_name": "default", 
                    "window_title": "桌面",
                    "pid": 0,
                    "hwnd": 0
                }

            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            if not pid or not psutil.pid_exists(pid):
                return {
                    "process_name": "default", 
                    "window_title": window_title,
                    "pid": pid,
                    "hwnd": hwnd
                }

            process = psutil.Process(pid)
            process_name = process.name().lower()

            return {
                "process_name": process_name,
                "window_title": window_title,
                "pid": pid,
                "hwnd": hwnd,
                "exe_path": process.exe() if hasattr(process, 'exe') else ""
            }
        except Exception as e:
            logger.warning(f"获取窗口信息失败: {e}")
            return {
                "process_name": "default",
                "window_title": "未知",
                "pid": 0,
                "hwnd": 0,
                "error": str(e)
            }


# 测试代码
if __name__ == "__main__":
    print(f"当前活动窗口的进程名: {ContextMonitor.get_current_process_name()}")