#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
main.py
智能悬浮快捷键列表工具的主入口文件。
"""

import sys, os, logging, json
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QDialog,
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSlider, QColorDialog, QComboBox,
                             QSpinBox, QMessageBox, QFileDialog, QGroupBox, QFormLayout,
                             QListWidget, QInputDialog, QTabWidget, QWidget)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QAction, QColor

from shortcut_manager import ShortcutManager
from context_monitor import ContextMonitor
from hotkey_listener import HotkeyListener
from shortcut_window import ShortcutWindow

# 统一日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shortcut_tool.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """简洁设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(500, 600)
        self.settings = QSettings("ShortcutTool", "Settings")
        self.process_mappings = {}
        self._load_process_mappings()
        self._build_ui()
        self._load()

    def _load_process_mappings(self):
        """加载进程映射配置"""
        try:
            mapping_file = os.path.join(os.path.dirname(__file__), "process_mapping.json")
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.process_mappings = data.get("mappings", {})
            else:
                # 默认映射
                self.process_mappings = {
                    "chrome.exe": "chrome.exe",
                    "firefox.exe": "firefox.exe",
                    "msedge.exe": "chrome.exe",
                    "code.exe": "code.exe",
                    "notepad++.exe": "notepad++.exe",
                    "explorer.exe": "explorer.exe"
                }
        except Exception as e:
            logger.error(f"加载进程映射失败: {e}")
            self.process_mappings = {}

    def _save_process_mappings(self):
        """保存进程映射配置"""
        try:
            mapping_file = os.path.join(os.path.dirname(__file__), "process_mapping.json")
            data = {
                "mappings": self.process_mappings,
                "description": "进程名映射配置文件，左侧为实际进程名，右侧为shortcuts.json中对应的配置键名"
            }
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("进程映射配置已保存")
        except Exception as e:
            logger.error(f"保存进程映射失败: {e}")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 基本设置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # 热键
        hotkey_box = QGroupBox("热键")
        hotkey_layout = QHBoxLayout(hotkey_box)
        self.ctrl_cb = QComboBox(); self.ctrl_cb.addItems(["Ctrl","无"])
        self.shift_cb = QComboBox(); self.shift_cb.addItems(["Shift","无"])
        self.alt_cb = QComboBox(); self.alt_cb.addItems(["Alt","无"])
        self.key_cb = QComboBox()
        # 添加所有支持的按键选项
        key_options = (
            # 功能键
            [f"F{i}" for i in range(1, 13)] +
            # 数字键
            [str(i) for i in range(10)] +
            # 字母键
            [chr(i) for i in range(ord('A'), ord('Z') + 1)] +
            # 小键盘
            [f"Num{i}" for i in range(10)] +
            # 方向键
            ["Up", "Down", "Left", "Right"] +
            # 特殊键
            ["Space", "Tab", "Enter", "Esc", "Backspace", "Delete", 
             "Home", "End", "PageUp", "PageDown", "Insert"] +
            # 标点符号
            [";", "=", ",", "-", ".", "/", "`", "[", "\\", "]", "'"]
        )
        self.key_cb.addItems(key_options)
        for w in (QLabel("全局热键:"), self.ctrl_cb, self.shift_cb, self.alt_cb, self.key_cb):
            hotkey_layout.addWidget(w)
        basic_layout.addWidget(hotkey_box)

        # 窗口
        win_box = QGroupBox("窗口")
        win_layout = QVBoxLayout(win_box)
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50,100)
        self.opacity_lbl = QLabel("90%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_lbl.setText(f"{v}%"))
        for w in (QLabel("透明度:"), self.opacity_slider, self.opacity_lbl):
            opacity_layout.addWidget(w)
        win_layout.addLayout(opacity_layout)

        color_layout = QHBoxLayout()
        self.bg_btn = QPushButton(); self.bg_btn.setFixedWidth(80); self.bg_btn.clicked.connect(lambda: self._pick_color(self.bg_btn))
        color_layout.addWidget(QLabel("背景色:")); color_layout.addWidget(self.bg_btn)
        win_layout.addLayout(color_layout)
        basic_layout.addWidget(win_box)

        # 字体
        font_box = QGroupBox("字体")
        font_layout = QFormLayout(font_box)
        self.font_cb = QComboBox(); self.font_cb.addItems(["Microsoft YaHei","Arial","SimSun"])
        self.size_spin = QSpinBox(); self.size_spin.setRange(8,20)
        font_layout.addRow("字体:", self.font_cb)
        font_layout.addRow("大小:", self.size_spin)
        self.font_color_btn = QPushButton(); self.font_color_btn.setFixedWidth(80); self.font_color_btn.clicked.connect(lambda: self._pick_color(self.font_color_btn))
        font_layout.addRow("文字色:", self.font_color_btn)
        basic_layout.addWidget(font_box)

        # 数据文件
        data_box = QGroupBox("数据文件")
        data_layout = QHBoxLayout(data_box)
        self.data_edit = QLineEdit(); self.data_edit.setReadOnly(True)
        browse_btn = QPushButton("浏览..."); browse_btn.clicked.connect(self._browse)
        data_layout.addWidget(self.data_edit); data_layout.addWidget(browse_btn)
        basic_layout.addWidget(data_box)
        
        # 添加基本设置选项卡
        tab_widget.addTab(basic_tab, "基本设置")
        
        # 进程映射选项卡
        process_tab = QWidget()
        process_layout = QVBoxLayout(process_tab)
        
        # 进程映射说明
        info_label = QLabel("配置进程名映射，将实际运行的进程名映射到shortcuts.json中的配置键名：")
        info_label.setWordWrap(True)
        process_layout.addWidget(info_label)
        
        # 进程映射列表
        mapping_box = QGroupBox("进程映射")
        mapping_layout = QVBoxLayout(mapping_box)
        
        self.mapping_list = QListWidget()
        self._update_mapping_list()
        mapping_layout.addWidget(self.mapping_list)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加映射")
        add_btn.clicked.connect(self._add_mapping)
        edit_btn = QPushButton("编辑映射")
        edit_btn.clicked.connect(self._edit_mapping)
        del_btn = QPushButton("删除映射")
        del_btn.clicked.connect(self._delete_mapping)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        mapping_layout.addLayout(btn_layout)
        
        process_layout.addWidget(mapping_box)
        
        # 添加进程映射选项卡
        tab_widget.addTab(process_tab, "进程映射")
        
        # 将选项卡添加到主布局
        layout.addWidget(tab_widget)

        # 按钮
        main_btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存"); save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消"); cancel_btn.clicked.connect(self.reject)
        main_btn_layout.addStretch(); main_btn_layout.addWidget(save_btn); main_btn_layout.addWidget(cancel_btn)
        layout.addLayout(main_btn_layout)

    def _update_mapping_list(self):
        """更新进程映射列表显示"""
        self.mapping_list.clear()
        for process_name, config_key in self.process_mappings.items():
            item_text = f"{process_name} → {config_key}"
            self.mapping_list.addItem(item_text)
    
    def _add_mapping(self):
        """添加新的进程映射"""
        process_name, ok1 = QInputDialog.getText(self, "添加进程映射", "请输入进程名称（如：chrome.exe）:")
        if ok1 and process_name.strip():
            process_name = process_name.strip().lower()
            config_key, ok2 = QInputDialog.getText(self, "添加进程映射", "请输入对应的配置键名（如：chrome.exe）:")
            if ok2 and config_key.strip():
                config_key = config_key.strip()
                self.process_mappings[process_name] = config_key
                self._update_mapping_list()
                logger.info(f"添加进程映射: {process_name} → {config_key}")
    
    def _edit_mapping(self):
        """编辑选中的进程映射"""
        current_item = self.mapping_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要编辑的映射项")
            return
        
        item_text = current_item.text()
        try:
            process_name, config_key = item_text.split(" → ")
            
            new_process_name, ok1 = QInputDialog.getText(self, "编辑进程映射", "进程名称:", text=process_name)
            if ok1 and new_process_name.strip():
                new_process_name = new_process_name.strip().lower()
                new_config_key, ok2 = QInputDialog.getText(self, "编辑进程映射", "配置键名:", text=config_key)
                if ok2 and new_config_key.strip():
                    new_config_key = new_config_key.strip()
                    
                    # 删除旧映射
                    if process_name in self.process_mappings:
                        del self.process_mappings[process_name]
                    
                    # 添加新映射
                    self.process_mappings[new_process_name] = new_config_key
                    self._update_mapping_list()
                    logger.info(f"编辑进程映射: {process_name} → {config_key} 改为 {new_process_name} → {new_config_key}")
        except ValueError:
            QMessageBox.warning(self, "错误", "无法解析选中的映射项")
    
    def _delete_mapping(self):
        """删除选中的进程映射"""
        current_item = self.mapping_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的映射项")
            return
        
        item_text = current_item.text()
        try:
            process_name, config_key = item_text.split(" → ")
            
            reply = QMessageBox.question(self, "确认删除", f"确定要删除映射 '{process_name} → {config_key}' 吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if process_name in self.process_mappings:
                    del self.process_mappings[process_name]
                    self._update_mapping_list()
                    logger.info(f"删除进程映射: {process_name} → {config_key}")
        except ValueError:
            QMessageBox.warning(self, "错误", "无法解析选中的映射项")

    def _pick_color(self, btn):
        c = QColorDialog.getColor(QColor(btn.text()), self)
        if c.isValid():
            btn.setText(c.name()); btn.setStyleSheet(f"background:{c.name()}")

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择快捷键数据文件", "", "JSON (*.json)")
        if path: self.data_edit.setText(path)

    def _load(self):
        def set_combo(cb, val, default=True):
            cb.setCurrentIndex(0 if val else 1)
        set_combo(self.ctrl_cb, self.settings.value("hotkey/ctrl", True, bool))
        set_combo(self.shift_cb, self.settings.value("hotkey/shift", True, bool))
        set_combo(self.alt_cb, self.settings.value("hotkey/alt", False, bool))
        key = self.settings.value("hotkey/key", "F1")
        self.key_cb.setCurrentText(key)

        self.opacity_slider.setValue(int(float(self.settings.value("window/opacity", 0.9))*100))
        bg = self.settings.value("window/bg_color", "#2E2E2E")
        self.bg_btn.setText(bg); self.bg_btn.setStyleSheet(f"background:{bg}")

        font = self.settings.value("font/family", "Microsoft YaHei")
        self.font_cb.setCurrentText(font)
        self.size_spin.setValue(self.settings.value("font/size", 10, int))
        fc = self.settings.value("font/color", "#FFFFFF")
        self.font_color_btn.setText(fc); self.font_color_btn.setStyleSheet(f"background:{fc}")

        data = self.settings.value("data/file_path", "")
        if not data:
            data = os.path.join(os.path.dirname(__file__), "shortcuts.json")
        self.data_edit.setText(data)

    def accept(self):
        self.settings.setValue("hotkey/ctrl", self.ctrl_cb.currentText()=="Ctrl")
        self.settings.setValue("hotkey/shift", self.shift_cb.currentText()=="Shift")
        self.settings.setValue("hotkey/alt", self.alt_cb.currentText()=="Alt")
        self.settings.setValue("hotkey/key", self.key_cb.currentText())
        self.settings.setValue("window/opacity", self.opacity_slider.value()/100)
        self.settings.setValue("window/bg_color", self.bg_btn.text())
        self.settings.setValue("font/family", self.font_cb.currentText())
        self.settings.setValue("font/size", self.size_spin.value())
        self.settings.setValue("font/color", self.font_color_btn.text())
        self.settings.setValue("data/file_path", self.data_edit.text())
        
        # 保存进程映射配置
        self._save_process_mappings()
        
        super().accept()



class ShortcutTool:
    """
    快捷键工具主类，协调各个模块的工作
    """
    
    def __init__(self):
        """
        初始化快捷键工具
        """
        # 创建应用
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 加载设置
        self.settings = QSettings("ShortcutTool", "Settings")
        
        # 初始化模块
        self.init_modules()
        
        # 创建系统托盘图标
        self.create_tray_icon()
    
    def init_modules(self):
        """
        初始化各个模块
        """
        try:
            # 获取数据文件路径
            data_file = self.settings.value("data/file_path", "")
            if not data_file:
                # 使用默认路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                data_file = os.path.join(current_dir, "shortcuts.json")
            
            # 创建快捷键管理器
            self.shortcut_manager = ShortcutManager(data_file)
            
            # 启用文件监视（自动重载）
            self.shortcut_manager.watch_for_changes()
            
            # 初始化上下文监控器
            self.context_monitor = ContextMonitor()
            
            # 创建快捷键窗口
            self.shortcut_window = ShortcutWindow(self.shortcut_manager)
            
            # 更新窗口设置
            window_settings = {
                "opacity": self.settings.value("window/opacity", 0.9),
                "bg_color": self.settings.value("window/bg_color", "#2E2E2E"),
                "font_family": self.settings.value("font/family", "Microsoft YaHei"),
                "font_size": self.settings.value("font/size", 10),
                "font_color": self.settings.value("font/color", "#FFFFFF")
            }
            self.shortcut_window.update_settings(window_settings)
            
            # 创建热键监听器
            hotkey_config = {
                "ctrl": self.settings.value("hotkey/ctrl", True, type=bool),
                "shift": self.settings.value("hotkey/shift", True, type=bool),
                "alt": self.settings.value("hotkey/alt", False, type=bool),
                "key": self.settings.value("hotkey/key", "F1").lower()
            }
            
            self.hotkey_listener = HotkeyListener(hotkey_config)
            # 连接新的按下/松开信号
            self.hotkey_listener.hotkey_pressed.connect(self.on_hotkey_pressed)
            self.hotkey_listener.hotkey_released.connect(self.on_hotkey_released)
            
            logger.info("所有模块初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"模块初始化失败: {e}")
            return False
    
    def create_tray_icon(self):
        """
        创建系统托盘图标
        """
        # 检查系统是否支持托盘图标
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.error("系统不支持托盘图标")
            QMessageBox.critical(None, "错误", "系统不支持托盘图标，程序无法正常运行。")
            sys.exit(1)
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.svg")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
            logger.info(f"已加载图标文件: {icon_path}")
        else:
            logger.warning(f"找不到图标文件: {icon_path}，使用默认图标")
            # 使用默认图标
            self.tray_icon.setIcon(self.app.style().standardIcon(self.app.style().StandardPixmap.SP_ComputerIcon))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 添加菜单项
        # 显示快捷键列表
        show_action = QAction("显示快捷键", self.app)
        show_action.triggered.connect(self.test_show_shortcuts)
        tray_menu.addAction(show_action)
        
        settings_action = QAction("设置", self.app)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        reload_action = QAction("重新加载数据", self.app)
        reload_action.triggered.connect(self.reload_data)
        tray_menu.addAction(reload_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("退出", self.app)
        exit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(exit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 设置提示文本
        self.tray_icon.setToolTip("快捷键提示工具")
        
        # 显示托盘图标
        self.tray_icon.show()
        logger.info("系统托盘图标已创建并显示")
    
    def on_hotkey_pressed(self):
        """
        热键按下时的回调函数
        """
        try:
            logger.info("热键按下，正在获取当前活动窗口进程名")
            # 获取当前活动窗口的进程名
            process_name = self.context_monitor.get_current_process_name()
            logger.info(f"当前活动窗口进程名: {process_name}")
            
            # 显示对应的快捷键列表
            logger.info("正在显示快捷键列表")
            self.shortcut_window.show_shortcuts(process_name)
            logger.info(f"快捷键窗口显示状态: {self.shortcut_window.isVisible()}")
            
            # 检查窗口是否可见，如果不可见则尝试强制显示
            if not self.shortcut_window.isVisible():
                logger.warning("窗口不可见，尝试强制显示")
                # 尝试多种方法强制显示窗口
                self.shortcut_window.setWindowState(self.shortcut_window.windowState() & ~self.shortcut_window.WindowState.WindowMinimized)
                self.shortcut_window.show()
                self.shortcut_window.setVisible(True)
                self.shortcut_window.activateWindow()
                self.shortcut_window.raise_()
                logger.info(f"强制显示后窗口可见状态: {self.shortcut_window.isVisible()}")
        except Exception as e:
            logger.error(f"处理热键按下时出错: {str(e)}", exc_info=True)
    
    def on_hotkey_released(self):
        """
        热键松开时的回调函数
        """
        try:
            logger.info("热键松开，隐藏快捷键窗口")
            self.shortcut_window.hide()
        except Exception as e:
            logger.error(f"处理热键松开时出错: {str(e)}", exc_info=True)
    
    def test_show_shortcuts(self):
        """
        测试显示快捷键窗口的功能
        """
        try:
            logger.info("手动测试显示快捷键窗口")
            # 获取当前活动窗口的进程名
            process_name = self.context_monitor.get_current_process_name()
            logger.info(f"当前活动窗口进程名: {process_name}")
            
            # 显示对应的快捷键列表
            self.shortcut_window.show_shortcuts(process_name)
            logger.info(f"快捷键窗口显示状态: {self.shortcut_window.isVisible()}")
            
        except Exception as e:
            logger.error(f"测试显示快捷键窗口时出错: {str(e)}", exc_info=True)
    
    def show_settings(self):
        """
        显示设置对话框
        """
        dialog = SettingsDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 清除进程映射缓存
            from context_monitor import ContextMonitor
            ContextMonitor.clear_mapping_cache()
            
            # 重新初始化模块
            self.init_modules()
            
            # 显示提示
            self.tray_icon.showMessage("设置已更新", "快捷键、窗口设置和进程映射已更新", QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def reload_data(self):
        """
        重新加载快捷键数据
        """
        if self.shortcut_manager.reload():
            self.tray_icon.showMessage("数据已重新加载", "快捷键数据已成功重新加载", QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            self.tray_icon.showMessage("加载失败", "无法加载快捷键数据，请检查数据文件", QSystemTrayIcon.MessageIcon.Warning, 2000)
    
    def run(self):
        """
        运行应用
        """
        # 启动热键监听
        self.hotkey_listener.start()
        
        # 显示欢迎消息
        self.tray_icon.showMessage(
            "快捷键提示工具已启动",
            f"按下 {self.get_hotkey_text()} 显示当前应用的快捷键列表",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )
        
        # 运行应用
        return self.app.exec()
    
    def get_hotkey_text(self):
        """
        获取当前热键的文本表示
        
        Returns:
            str: 热键文本，例如 "Ctrl+F1"
        """
        parts = []
        
        if self.settings.value("hotkey/ctrl", True, type=bool):
            parts.append("Ctrl")
        
        if self.settings.value("hotkey/shift", True, type=bool):
            parts.append("Shift")
        
        if self.settings.value("hotkey/alt", False, type=bool):
            parts.append("Alt")
        
        parts.append(self.settings.value("hotkey/key", "F1"))
        
        return "+".join(parts)


# 程序入口
if __name__ == "__main__":
    try:
        sys.exit(ShortcutTool().run())
    except Exception as e:
        logging.error(f"程序崩溃: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "致命错误", f"程序异常终止:\n{str(e)}")