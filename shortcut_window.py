#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
shortcut_window.py

简洁的快捷键悬浮窗口实现。
"""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QGridLayout, QSizePolicy, QGraphicsDropShadowEffect, QLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QFont, QColor, QMouseEvent

logger = logging.getLogger(__name__)

class ShortcutWindow(QWidget):
    def __init__(self, shortcut_manager):
        super().__init__()
        self.shortcut_manager = shortcut_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 启用毛玻璃效果（Windows 10/11）
        try:
            from PyQt6.QtWinExtras import QtWin
            if QtWin.isCompositionEnabled():
                QtWin.enableBlurBehindWindow(self)
        except ImportError:
            pass  # 如果没有QtWinExtras，跳过毛玻璃效果
        # 仅为顶层窗口设置样式作用域
        self.setObjectName("ShortcutWindow")

        self.settings = QSettings("ShortcutTool", "ShortcutWindow")
        self.load_settings()
        self.init_ui()

        self.dragging = False
        self.drag_position = QPoint()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title_label = QLabel("快捷键列表")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setFont(QFont(self.font_family, self.font_size + 2, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {self.font_color};")
        layout.addWidget(self.title_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

        # 设置窗口样式（改善可读性）
        self.setStyleSheet(f"""
            #ShortcutWindow {{
                background: rgba(20, 20, 20, 0.95);
                color: #ffffff;
                font-family: {self.font_family};
                border-radius: 15px;
                border: 2px solid rgba(100, 149, 237, 0.6);
            }}
            QLabel {{
                color: #ffffff;
                background: transparent;
            }}
            #titleLabel {{
                background: rgba(100, 149, 237, 0.8);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(100, 149, 237, 1.0);
                font-weight: bold;
                color: #ffffff;
            }}
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ border: none; background: rgba(100, 149, 237, 0.2); width: 10px; margin: 0; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: rgba(100, 149, 237, 0.7); min-height: 20px; border-radius: 5px; }}
            QScrollBar::handle:vertical:hover {{ background: rgba(100, 149, 237, 0.9); }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)
    

    
    def load_settings(self):
        pos = self.settings.value("pos", QPoint(100, 100))
        size = self.settings.value("size", (400, 500))
        # 兼容不同返回类型
        try:
            if hasattr(pos, 'x') and hasattr(pos, 'y'):
                self.move(pos)
            elif isinstance(pos, (tuple, list)) and len(pos) == 2:
                self.move(int(pos[0]), int(pos[1]))
            else:
                self.move(100, 100)
        except Exception:
            self.move(100, 100)
        
        try:
            if hasattr(size, 'width') and hasattr(size, 'height'):
                self.resize(size)
            elif isinstance(size, (tuple, list)) and len(size) == 2:
                self.resize(int(size[0]), int(size[1]))
            else:
                self.resize(400, 500)
        except Exception:
            self.resize(400, 500)

        self.opacity = float(self.settings.value("opacity", 0.9))
        self.bg_color = QColor(self.settings.value("bg_color", "#2E2E2E"))
        self.font_family = self.settings.value("font_family", "Microsoft YaHei")
        self.font_size = int(self.settings.value("font_size", 10))
        self.font_color = self.settings.value("font_color", "#FFFFFF")
    
    def save_settings(self):
        """
        保存窗口设置到QSettings
        """
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        self.settings.setValue("opacity", self.opacity)
        self.settings.setValue("bg_color", self.bg_color.name())
        self.settings.setValue("font_family", self.font_family)
        self.settings.setValue("font_size", self.font_size)
        self.settings.setValue("font_color", self.font_color)
        
        logger.info("窗口设置已保存")
    
    def update_settings(self, settings_dict):
        """
        更新窗口设置
        
        Args:
            settings_dict (dict): 包含设置的字典
        """
        # 更新透明度
        if "opacity" in settings_dict:
            self.opacity = float(settings_dict["opacity"])
        
        # 更新背景色
        if "bg_color" in settings_dict:
            self.bg_color = QColor(settings_dict["bg_color"])
        
        # 更新字体设置
        if "font_family" in settings_dict:
            self.font_family = settings_dict["font_family"]
        
        if "font_size" in settings_dict:
            self.font_size = int(settings_dict["font_size"])
        
        if "font_color" in settings_dict:
            self.font_color = settings_dict["font_color"]
        
        # 应用新样式
        alpha = int(self.opacity * 255)
        self.setStyleSheet(f"""
            #ShortcutWindow {{
                background-color: rgba({self.bg_color.red()}, {self.bg_color.green()}, {self.bg_color.blue()}, {alpha});
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.font_color};
            }}
        """)
        
        # 更新标题栏样式
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.font_color};
                }}
            """)
        
        logger.info("窗口样式已更新")
    
    def get_clean_process_name(self, process_name):
        """
        获取干净的进程名称用于显示
        
        Args:
            process_name (str): 原始进程名称
            
        Returns:
            str: 清理后的进程名称
        """
        if not process_name:
            return "未知应用"
        
        # 移除 .exe 后缀
        if process_name.lower().endswith('.exe'):
            clean_name = process_name[:-4]
        else:
            clean_name = process_name
        
        # 特殊应用名称映射
        name_mapping = {
            'chrome': 'Google Chrome',
            'firefox': 'Mozilla Firefox',
            'msedge': 'Microsoft Edge',
            'notepad': '记事本',
            'notepad++': 'Notepad++',
            'code': 'Visual Studio Code',
            'explorer': '文件资源管理器',
            'winword': 'Microsoft Word',
            'excel': 'Microsoft Excel',
            'powerpnt': 'Microsoft PowerPoint',
            'acad': 'AutoCAD',
            'cass': 'CASS'
        }
        
        return name_mapping.get(clean_name.lower(), clean_name)
    
    def show_shortcuts(self, process_name=""):
        """
        显示指定进程的快捷键
        
        Args:
            process_name (str): 进程名称
        """
        self.clear_content()
        
        shortcuts = self.shortcut_manager.get_shortcuts_for_process(process_name)
        
        if not shortcuts:
            no_shortcuts_label = QLabel("暂无快捷键配置")
            no_shortcuts_label.setFont(QFont(self.font_family, self.font_size))
            no_shortcuts_label.setStyleSheet(f"color: {self.font_color}; padding: 20px;")
            no_shortcuts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_shortcuts_label)
            logger.info(f"进程 {process_name} 暂无快捷键配置")
        else:
            self.create_card_layout(shortcuts)
            logger.info(f"已显示进程 {process_name} 的 {len(shortcuts)} 个快捷键")
        
        # 更新窗口标题
        clean_name = self.get_clean_process_name(process_name)
        if process_name == "explorer.exe":
            self.title_label.setText("文件资源管理器 - 快捷键")
        elif process_name == "default" or not process_name:
            self.title_label.setText("通用快捷键")
        else:
            # 检查是否使用了默认配置
            # 由于get_shortcuts_for_process方法总是会返回默认配置作为回退，
            # 我们需要通过其他方式检查是否有专门的配置
            has_specific_config = process_name.lower() in self.shortcut_manager.shortcuts
            if not has_specific_config and shortcuts:
                self.title_label.setText(f"{clean_name} - 快捷键 [通用配置]")
            else:
                self.title_label.setText(f"{clean_name} - 快捷键")
        
        # 调整窗口大小和位置
        self.adjust_window_size()
        self.center_on_screen()
        
        self.show()
        self.raise_()
        self.activateWindow()
    
    def create_card_layout(self, shortcuts):
        """
        创建卡片布局
        
        Args:
            shortcuts (list): 快捷键列表
        """
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # 创建容器widget
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        # 创建网格布局
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # 计算每行显示的卡片数量（响应式布局）
        cards_per_row = self.calculate_cards_per_row(len(shortcuts))
        
        for i, shortcut in enumerate(shortcuts):
            card = self.create_shortcut_card(shortcut)
            row = i // cards_per_row
            col = i % cards_per_row
            grid_layout.addWidget(card, row, col)
        
        # 设置列的拉伸因子，使卡片均匀分布
        for col in range(cards_per_row):
            grid_layout.setColumnStretch(col, 1)
        
        scroll_area.setWidget(container)
        self.content_layout.addWidget(scroll_area)
    
    def calculate_cards_per_row(self, total_cards):
        """
        根据窗口大小和卡片数量计算每行显示的卡片数量
        
        Args:
            total_cards (int): 总卡片数量
            
        Returns:
            int: 每行卡片数量
        """
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        
        # 根据屏幕宽度确定每行卡片数量
        if screen_width >= 1920:  # 大屏幕
            max_per_row = 5
        elif screen_width >= 1366:  # 中等屏幕
            max_per_row = 4
        else:  # 小屏幕
            max_per_row = 3
        
        # 根据卡片总数调整
        if total_cards <= 6:
            return min(3, total_cards)
        elif total_cards <= 12:
            return min(4, max_per_row)
        else:
            return max_per_row
    
    def adjust_window_size(self):
        """
        根据内容调整窗口大小
        """
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 计算窗口大小（占屏幕的80%，但不超过最大尺寸）
        max_width = min(1200, int(screen_width * 0.8))
        max_height = min(800, int(screen_height * 0.8))
        
        # 设置最小尺寸
        min_width = 600
        min_height = 400
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        self.resize(max_width, max_height)
    
    def center_on_screen(self):
        """
        将窗口居中显示在屏幕上
        """
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    

    


    def create_shortcut_card(self, shortcut, max_width=None, compact_mode=False, max_height=None):
        from PyQt6.QtWidgets import QSizePolicy
        
        card = QWidget()
        # 设置卡片尺寸
        if max_width:
            card.setMinimumWidth(max_width)
            card.setMaximumWidth(max_width + 100)
        else:
            card.setMinimumWidth(180)
        
        # 设置最小高度，但允许自适应扩展
        card.setMinimumHeight(100)
        
        if max_height:
            card.setMaximumHeight(max_height + 40)
        else:
            # 为多快捷键情况设置更大的最大高度
            card.setMaximumHeight(160)
        
        # 设置大小策略为可扩展
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 设置高对比度卡片样式
        card.setStyleSheet(f"""
            QWidget {{
                background: rgba(40, 40, 40, 0.9);
                border: 2px solid rgba(100, 149, 237, 0.5);
                border-radius: 12px;
            }}
            QWidget:hover {{
                background: rgba(50, 50, 50, 0.95);
                border: 2px solid rgba(100, 149, 237, 0.8);
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        # 使用适中的字体
        key_font_size = self.font_size + 1
        desc_font_size = self.font_size - 1
        key_padding = "4px 8px"
        
        # 智能处理多个快捷键的显示
        key_text = shortcut["key"]
        
        # 检测是否包含多个快捷键（常见分隔符：/ 、 " / " 或 "或"）
        if " / " in key_text or " 或 " in key_text or ("/" in key_text and " / " not in key_text):
            # 分割多个快捷键
            if " / " in key_text:
                keys = key_text.split(" / ")
            elif " 或 " in key_text:
                keys = key_text.split(" 或 ")
            elif "/" in key_text:
                keys = key_text.split("/")
            
            # 创建垂直布局来显示多个快捷键
            key_container = QWidget()
            key_layout = QVBoxLayout(key_container)
            key_layout.setContentsMargins(0, 0, 0, 0)
            key_layout.setSpacing(3)  # 增加间距避免挤在一起
            
            # 根据快捷键数量调整字体大小
            multi_key_font_size = max(8, key_font_size - 2) if len(keys) > 2 else max(9, key_font_size - 1)
            
            for i, single_key in enumerate(keys):
                key_label = QLabel(single_key.strip())
                key_label.setFont(QFont(self.font_family, multi_key_font_size, QFont.Weight.Bold))
                key_label.setStyleSheet("""
                    color: #ffffff;
                    font-weight: bold;
                    background: rgba(100, 149, 237, 0.8);
                    border-radius: 4px;
                    padding: 3px 6px;
                    border: 1px solid rgba(100, 149, 237, 1.0);
                    margin: 1px;
                """)
                key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                key_label.setWordWrap(True)
                key_layout.addWidget(key_label)
            
            layout.addWidget(key_container)
        else:
            # 单个快捷键的正常显示
            key_label = QLabel(key_text)
            key_label.setFont(QFont(self.font_family, key_font_size, QFont.Weight.Bold))
            key_label.setStyleSheet(f"""
                color: #ffffff;
                font-weight: bold;
                background: rgba(100, 149, 237, 0.8);
                border-radius: 6px;
                padding: 6px 10px;
                border: 1px solid rgba(100, 149, 237, 1.0);
            """)
            key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            key_label.setWordWrap(True)
            layout.addWidget(key_label)

        desc = QLabel(shortcut["desc"]) 
        desc.setFont(QFont(self.font_family, desc_font_size))
        desc.setStyleSheet("""
            color: #ffffff;
            background: transparent;
            padding: 4px;
            font-weight: normal;
        """)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置描述标签的大小策略
        desc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(desc)

        return card
    
    def clear_content(self):
        """
        清空内容区域
        """
        # 清除所有子部件
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        logger.info("内容区域已清空")
    
    def mousePressEvent(self, event: QMouseEvent):
        """
        鼠标按下事件处理
        
        Args:
            event (QMouseEvent): 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.position().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        鼠标移动事件处理
        
        Args:
            event (QMouseEvent): 鼠标事件
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.position().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        鼠标释放事件处理
        
        Args:
            event (QMouseEvent): 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    def keyPressEvent(self, event):
        """
        按键事件处理，ESC键隐藏窗口
        
        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            logger.info("用户按ESC键隐藏窗口")
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建一个示例快捷键管理器
    class DummyShortcutManager:
        def get_shortcuts_for_process(self, process_name, allow_default=True):
            return [
                {"key": "Ctrl+C", "desc": "复制"},
                {"key": "Ctrl+V", "desc": "粘贴"},
                {"key": "Ctrl+Z", "desc": "撤销"},
                {"key": "Ctrl+Y", "desc": "重做"},
                {"key": "Ctrl+A", "desc": "全选"},
                {"key": "Ctrl+S", "desc": "保存"},
                {"key": "Ctrl+O", "desc": "打开"},
                {"key": "Ctrl+N", "desc": "新建"},
                {"key": "Ctrl+F", "desc": "查找"},
                {"key": "Ctrl+H", "desc": "替换"},
            ]
    
    shortcut_manager = DummyShortcutManager()
    window = ShortcutWindow(shortcut_manager)
    window.show_shortcuts("chrome.exe")
    
    sys.exit(app.exec())

class FlowLayout(QLayout):
    """一个简单的流式布局，支持按行居中对齐，自动换行。"""
    def __init__(self, parent=None, margin=0, hspacing=10, vspacing=10, center_lines=True):
        super().__init__(parent)
        self._item_list = []
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._center_lines = center_lines
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        line_items = []
        line_width = 0
        total_height = 0

        def place_line(start_y):
            nonlocal total_height
            if not line_items:
                return 0
            # 计算行内总宽度
            total_w = sum(i.sizeHint().width() for i in line_items)
            total_w += self._hspacing * (len(line_items) - 1) if len(line_items) > 1 else 0
            # 计算起始x以实现居中
            if self._center_lines:
                start_x = effective_rect.x() + max(0, (effective_rect.width() - total_w) // 2)
            else:
                start_x = effective_rect.x()
            # 布局行内元素
            cx = start_x
            max_h = 0
            for it in line_items:
                w = it.sizeHint().width()
                h = it.sizeHint().height()
                if not test_only:
                    it.setGeometry(QRect(cx, start_y, w, h))
                cx += w + self._hspacing
                max_h = max(max_h, h)
            total_height += max_h + self._vspacing
            return max_h

        for item in self._item_list:
            hint = item.sizeHint()
            next_x = x + hint.width()
            if line_items and (next_x - effective_rect.x() > effective_rect.width()):
                # 换行并布局上一行
                y += place_line(y) + 0
                line_items = []
                x = effective_rect.x()
                line_width = 0
                line_height = 0
            line_items.append(item)
            x += hint.width() + self._hspacing
            line_width += hint.width() + self._hspacing
            line_height = max(line_height, hint.height())
        # 最后一行
        if line_items:
            place_line(y)
        # 返回总高度
        return total_height + bottom + top
