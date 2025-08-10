#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
shortcut_manager.py

管理不同应用程序的快捷键配置。
按照开发指南要求，提供JSON schema校验、别名支持、文件监视等功能。
"""

import os
import json
import logging
import jsonschema
from typing import List, Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# JSON Schema 定义
SHORTCUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "default": {
            "type": "array",
            "items": {"$ref": "#/definitions/shortcut"}
        }
    },
    "patternProperties": {
        "^[a-z0-9_.-]+$": {
            "type": "array", 
            "items": {"$ref": "#/definitions/shortcut"}
        }
    },
    "definitions": {
        "shortcut": {
            "type": "object",
            "required": ["key", "desc"],
            "properties": {
                "key": {"type": "string"},
                "desc": {"type": "string"},
                "tags": {
                    "type": "array", 
                    "items": {"type": "string"}
                },
                "when": {
                    "type": "string", 
                    "description": "可选：限定条件"
                },
                "group": {
                    "type": "string",
                    "description": "可选：分组名称"
                }
            },
            "additionalProperties": False
        }
    }
}

class ShortcutFileHandler(FileSystemEventHandler):
    """快捷键文件变更监听器"""
    
    def __init__(self, callback):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            self.callback()

class ShortcutManager:
    DEFAULT_SHORTCUTS = {
        "default": [
            {"key": "Ctrl+C", "desc": "复制"},
            {"key": "Ctrl+V", "desc": "粘贴"},
            {"key": "Ctrl+X", "desc": "剪切"},
            {"key": "Ctrl+Z", "desc": "撤销"},
            {"key": "Ctrl+Y", "desc": "重做"},
            {"key": "Ctrl+S", "desc": "保存"},
            {"key": "Ctrl+A", "desc": "全选"}
        ],
        "explorer.exe": [
            {"key": "Ctrl+C", "desc": "复制"},
            {"key": "Ctrl+V", "desc": "粘贴"},
            {"key": "F2", "desc": "重命名"},
            {"key": "F5", "desc": "刷新"},
            {"key": "Ctrl+Shift+N", "desc": "新建文件夹"}
        ],
        "chrome.exe": [
            {"key": "Ctrl+T", "desc": "新建标签页"},
            {"key": "Ctrl+W", "desc": "关闭标签页"},
            {"key": "Ctrl+Tab", "desc": "下一个标签页"},
            {"key": "Ctrl+L", "desc": "聚焦地址栏"},
            {"key": "Ctrl+R", "desc": "刷新"},
            {"key": "Ctrl+H", "desc": "历史记录"}
        ],
        "code.exe": [
            {"key": "Ctrl+Shift+P", "desc": "命令面板"},
            {"key": "Ctrl+P", "desc": "快速打开文件"},
            {"key": "Ctrl+Shift+F", "desc": "全局搜索"},
            {"key": "Ctrl+B", "desc": "切换侧边栏"},
            {"key": "F12", "desc": "转到定义"}
        ],
        "winword.exe": [
            {"key": "Ctrl+B", "desc": "加粗"},
            {"key": "Ctrl+I", "desc": "斜体"},
            {"key": "Ctrl+U", "desc": "下划线"},
            {"key": "Ctrl+S", "desc": "保存"}
        ],
        "excel.exe": [
            {"key": "F2", "desc": "编辑单元格"},
            {"key": "Ctrl+Arrow", "desc": "跳转到边缘"}
        ],
        "powerpnt.exe": [
            {"key": "F5", "desc": "从头开始放映"},
            {"key": "Shift+F5", "desc": "从当前幻灯片开始放映"}
        ],
        "photoshop.exe": [
            {"key": "Ctrl+T", "desc": "自由变换"},
            {"key": "Ctrl+D", "desc": "取消选择"}
        ],
        "illustrator.exe": [
            {"key": "Ctrl+D", "desc": "复制并偏移"},
            {"key": "Ctrl+G", "desc": "组合"}
        ]
    }

    def __init__(self, json_file_path: Optional[str] = None):
        """初始化快捷键管理器
        
        Args:
            json_file_path: JSON配置文件路径，默认为 shortcuts.json
        """
        self.json_file_path = json_file_path or "shortcuts.json"
        self.shortcuts = {}
        self.observer = None
        self.file_handler = None
        self.load(self.json_file_path)
        
    def load(self, file_path: str) -> bool:
        """加载并校验JSON配置文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            bool: 加载是否成功
        """
        self.json_file_path = file_path
        
        if not os.path.exists(file_path):
            logger.warning(f"快捷键配置文件不存在: {file_path}，使用默认配置")
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Schema 校验
            try:
                jsonschema.validate(data, SHORTCUT_SCHEMA)
                logger.info("JSON schema 校验通过")
            except jsonschema.ValidationError as e:
                logger.error(f"JSON schema 校验失败: {e.message}")
                logger.warning("将使用默认配置")
                self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
                return False
                
            self.shortcuts = data
            logger.info(f"成功加载快捷键配置: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载快捷键配置失败: {e}")
            self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
            return False

    def get_shortcuts_for_process(self, process_name: str) -> List[Dict[str, Any]]:
        """根据进程名获取对应的快捷键列表
        
        支持精确匹配、别名匹配、模糊匹配和默认回退。
        
        Args:
            process_name: 进程名（如 'code.exe'）
            
        Returns:
            list: 快捷键列表
        """
        if not process_name:
            return self.shortcuts.get("default", [])
        
        process_name = process_name.lower()
        
        # 1. 精确匹配
        if process_name in self.shortcuts:
            return self.shortcuts[process_name]
        
        # 2. 别名匹配（检查每个进程配置中的aliases字段）
        for key, shortcuts in self.shortcuts.items():
            if key == "default":
                continue
            # 检查是否有aliases配置
            if isinstance(shortcuts, list) and shortcuts:
                first_item = shortcuts[0]
                if isinstance(first_item, dict) and "aliases" in first_item:
                    aliases = first_item["aliases"]
                    if isinstance(aliases, list) and process_name in [alias.lower() for alias in aliases]:
                        return shortcuts
        
        # 3. 模糊匹配（去掉.exe后缀）
        if process_name.endswith('.exe'):
            base_name = process_name[:-4]
            if base_name in self.shortcuts:
                return self.shortcuts[base_name]
        
        # 4. 返回默认快捷键
        return self.shortcuts.get("default", [])

    def get_all_process_keys(self) -> List[str]:
        """获取所有已配置快捷键的进程名列表
        
        Returns:
            list: 进程名列表
        """
        return list(self.shortcuts.keys())

    def reload(self) -> bool:
        """重新加载快捷键配置
        
        Returns:
            bool: 重载是否成功
        """
        return self.load(self.json_file_path)
        
    def watch_for_changes(self) -> bool:
        """监视文件变更并自动重载
        
        Returns:
            bool: 监视是否启动成功
        """
        try:
            if self.observer:
                self.observer.stop()
                
            self.file_handler = ShortcutFileHandler(self.reload)
            self.observer = Observer()
            
            watch_dir = os.path.dirname(os.path.abspath(self.json_file_path))
            self.observer.schedule(self.file_handler, watch_dir, recursive=False)
            self.observer.start()
            
            logger.info(f"开始监视文件变更: {self.json_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"启动文件监视失败: {e}")
            return False
            
    def stop_watching(self):
        """停止文件监视"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("已停止文件监视")

if __name__ == "__main__":
    manager = ShortcutManager()
    chrome_shortcuts = manager.get_shortcuts_for_process("chrome.exe")
    print(f"Chrome快捷键数量: {len(chrome_shortcuts)}")
    print(f"所有已定义快捷键的进程: {manager.get_all_process_keys()}")