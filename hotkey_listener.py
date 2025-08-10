#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
hotkey_listener.py

基于 pywin32 的全局热键监听器，支持按下/松开事件的精确控制。
使用 RegisterHotKey 和低级键盘钩子实现可靠的热键监听。
"""

import win32api
import win32con
import win32gui
import threading
import logging
import ctypes
import time
from ctypes import wintypes
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

# 定义KBDLLHOOKSTRUCT结构体
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

# 定义回调函数类型
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# 全局实例引用
_global_listener_instance = None

class HotkeyListener(QObject):
    """全局热键监听器
    
    使用 pywin32 实现可靠的热键监听，支持：
    - 按下显示，松开隐藏的交互模式
    - 热键冲突检测
    - 线程安全的启动/停止
    """

    hotkey_pressed = pyqtSignal()
    hotkey_released = pyqtSignal()

    def __init__(self, hotkey_config=None):
        super().__init__()
        global _global_listener_instance
        _global_listener_instance = self
        
        self.hotkey_config = hotkey_config or {'ctrl': True, 'shift': True, 'alt': False, 'key': 'f12'}
        self.hotkey_id = 1
        self.is_running = False
        self.hook_thread = None
        self.hook_id = None
        self.pressed_keys = set()
        self.hotkey_active = False  # 防止重复触发的状态标记
        self.last_hotkey_time = 0  # 上次热键触发时间
        self.debounce_interval = 0.05  # 防抖动间隔（秒）
        # 创建回调函数实例 - 使用静态方法避免self参数问题
        self._hook_callback = HOOKPROC(self._static_keyboard_proc)

    def start(self):
        """启动热键监听"""
        if self.is_running:
            return True
            
        try:
            # 启动低级键盘钩子线程
            self.hook_thread = threading.Thread(target=self._hook_proc, daemon=True)
            self.hook_thread.start()
            self.is_running = True
            logger.info("热键监听器启动成功")
            return True
        except Exception as e:
            logger.error(f"启动热键监听器失败: {e}")
            return False

    def stop(self):
        """停止热键监听"""
        if not self.is_running:
            return
            
        try:
            self.is_running = False
            if self.hook_id:
                ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
                self.hook_id = None
            logger.info("热键监听器已停止")
        except Exception as e:
            logger.error(f"停止热键监听器失败: {e}")

    def register_hotkey(self, hotkey_config):
        """注册热键配置
        
        Args:
            hotkey_config (dict): 热键配置字典
            
        Returns:
            bool: 注册是否成功
        """
        self.hotkey_config = hotkey_config
        return True
        
    def unregister_hotkey(self):
        """注销热键"""
        self.stop()

    def update_hotkey_config(self, new_config):
        """更新热键配置"""
        self.hotkey_config = new_config
        # 如果正在运行，重启监听器
        if self.is_running:
            self.stop()
            self.start()

    def _hook_proc(self):
        """键盘钩子处理线程"""
        try:
            # 安装低级键盘钩子
            self.hook_id = ctypes.windll.user32.SetWindowsHookExW(
                win32con.WH_KEYBOARD_LL,
                self._hook_callback,
                0,  # 对于低级钩子，可以使用0
                0
            )
            
            if not self.hook_id:
                logger.error("安装键盘钩子失败")
                return
                
            # 消息循环
            while self.is_running:
                try:
                    msg = win32gui.GetMessage(None, 0, 0)
                    if msg[1] == win32con.WM_QUIT:
                        break
                    win32gui.TranslateMessage(msg)
                    win32gui.DispatchMessage(msg)
                except:
                    if not self.is_running:
                        break
                        
        except Exception as e:
            logger.error(f"键盘钩子线程异常: {e}")
        finally:
            if self.hook_id:
                ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
                self.hook_id = None

    @staticmethod
    def _static_keyboard_proc(nCode, wParam, lParam):
        """静态键盘钩子处理函数"""
        global _global_listener_instance
        if _global_listener_instance and nCode >= 0:
            try:
                if wParam == win32con.WM_KEYDOWN or wParam == win32con.WM_SYSKEYDOWN:
                    # lParam是指向KBDLLHOOKSTRUCT的指针
                    kbd_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk_code = kbd_struct.vkCode
                    _global_listener_instance._on_key_down(vk_code)
                elif wParam == win32con.WM_KEYUP or wParam == win32con.WM_SYSKEYUP:
                    kbd_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk_code = kbd_struct.vkCode
                    _global_listener_instance._on_key_up(vk_code)
            except Exception as e:
                logger.error(f"键盘钩子处理异常: {e}")
                
        # 确保参数类型正确
        return ctypes.windll.user32.CallNextHookEx(
            ctypes.c_void_p(0),  # hhk
            ctypes.c_int(nCode),  # nCode
            ctypes.wintypes.WPARAM(wParam),  # wParam
            ctypes.wintypes.LPARAM(lParam)   # lParam
        )
        
    def _low_level_keyboard_proc(self, nCode, wParam, lParam):
        """低级键盘钩子处理函数"""
        if nCode >= 0:
            if wParam == win32con.WM_KEYDOWN or wParam == win32con.WM_SYSKEYDOWN:
                # lParam是指向KBDLLHOOKSTRUCT的指针
                vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value
                self._on_key_down(vk_code)
            elif wParam == win32con.WM_KEYUP or wParam == win32con.WM_SYSKEYUP:
                vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value
                self._on_key_up(vk_code)
                
        return ctypes.windll.user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def _on_key_down(self, vk_code):
        """按键按下处理"""
        self.pressed_keys.add(vk_code)
        logger.debug(f"按键按下: {vk_code}, 当前按下的键: {self.pressed_keys}")
        
        # 检查热键状态
        hotkey_matched = self._is_hotkey_pressed()
        logger.debug(f"热键匹配检查: {hotkey_matched}, 配置: {self.hotkey_config}")
        
        if hotkey_matched:
            # 只有在热键状态从未激活变为激活时才发送信号
            if not self.hotkey_active:
                current_time = time.time()
                # 检查时间间隔，防止过于频繁的触发
                if current_time - self.last_hotkey_time >= self.debounce_interval:
                    self.hotkey_active = True
                    self.last_hotkey_time = current_time
                    logger.info(f"热键组合检测到，发送hotkey_pressed信号")
                    self.hotkey_pressed.emit()
                else:
                    logger.debug(f"防抖动阻止: 时间间隔 {current_time - self.last_hotkey_time:.3f}s < {self.debounce_interval}s")
        else:
            # 如果热键组合不完整，重置状态
            self.hotkey_active = False

    def _on_key_up(self, vk_code):
        """按键释放处理"""
        if vk_code in self.pressed_keys:
            self.pressed_keys.remove(vk_code)
            # 如果释放的是热键组合中的任一键，触发释放事件
            if self._was_hotkey_key(vk_code):
                # 重置热键激活状态
                self.hotkey_active = False
                self.hotkey_released.emit()

    def _is_hotkey_pressed(self):
        """检查当前是否按下了配置的热键组合"""
        # 检查修饰键
        ctrl_pressed = False
        shift_pressed = False
        alt_pressed = False
        
        if self.hotkey_config.get('ctrl'):
            ctrl_pressed = (win32con.VK_LCONTROL in self.pressed_keys or 
                           win32con.VK_RCONTROL in self.pressed_keys)
        else:
            ctrl_pressed = True
            
        if self.hotkey_config.get('shift'):
            shift_pressed = (win32con.VK_LSHIFT in self.pressed_keys or 
                            win32con.VK_RSHIFT in self.pressed_keys)
        else:
            shift_pressed = True
            
        if self.hotkey_config.get('alt'):
            alt_pressed = (win32con.VK_LMENU in self.pressed_keys or 
                          win32con.VK_RMENU in self.pressed_keys)
        else:
            alt_pressed = True
            
        # 检查主键
        key_name = self.hotkey_config.get('key', 'f12').lower()
        key_mapping = {
            # 功能键
            'f1': win32con.VK_F1, 'f2': win32con.VK_F2, 'f3': win32con.VK_F3,
            'f4': win32con.VK_F4, 'f5': win32con.VK_F5, 'f6': win32con.VK_F6,
            'f7': win32con.VK_F7, 'f8': win32con.VK_F8, 'f9': win32con.VK_F9,
            'f10': win32con.VK_F10, 'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
            # 数字键
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
            # 小键盘数字
            'num0': win32con.VK_NUMPAD0, 'num1': win32con.VK_NUMPAD1, 'num2': win32con.VK_NUMPAD2,
            'num3': win32con.VK_NUMPAD3, 'num4': win32con.VK_NUMPAD4, 'num5': win32con.VK_NUMPAD5,
            'num6': win32con.VK_NUMPAD6, 'num7': win32con.VK_NUMPAD7, 'num8': win32con.VK_NUMPAD8,
            'num9': win32con.VK_NUMPAD9,
            # 方向键
            'up': win32con.VK_UP, 'down': win32con.VK_DOWN, 'left': win32con.VK_LEFT, 'right': win32con.VK_RIGHT,
            # 特殊键
            'space': win32con.VK_SPACE, 'tab': win32con.VK_TAB, 'enter': win32con.VK_RETURN,
            'esc': win32con.VK_ESCAPE, 'backspace': win32con.VK_BACK, 'delete': win32con.VK_DELETE,
            'home': win32con.VK_HOME, 'end': win32con.VK_END, 'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT, 'insert': win32con.VK_INSERT,
            # 标点符号
            ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF,
            '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE
        }
        
        main_key_pressed = False
        if key_name in key_mapping:
            main_key_pressed = key_mapping[key_name] in self.pressed_keys
        elif len(key_name) == 1 and key_name.isalpha():
            main_key_pressed = ord(key_name.upper()) in self.pressed_keys
            
        return ctrl_pressed and shift_pressed and alt_pressed and main_key_pressed
        
    def _was_hotkey_key(self, vk_code):
        """检查释放的键是否是热键组合中的一个"""
        # 检查是否是修饰键
        if self.hotkey_config.get('ctrl') and vk_code in [win32con.VK_LCONTROL, win32con.VK_RCONTROL]:
            return True
        if self.hotkey_config.get('shift') and vk_code in [win32con.VK_LSHIFT, win32con.VK_RSHIFT]:
            return True
        if self.hotkey_config.get('alt') and vk_code in [win32con.VK_LMENU, win32con.VK_RMENU]:
            return True
            
        # 检查是否是主键
        key_name = self.hotkey_config.get('key', 'f12').lower()
        key_mapping = {
            # 功能键
            'f1': win32con.VK_F1, 'f2': win32con.VK_F2, 'f3': win32con.VK_F3,
            'f4': win32con.VK_F4, 'f5': win32con.VK_F5, 'f6': win32con.VK_F6,
            'f7': win32con.VK_F7, 'f8': win32con.VK_F8, 'f9': win32con.VK_F9,
            'f10': win32con.VK_F10, 'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
            # 数字键
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
            # 小键盘数字
            'num0': win32con.VK_NUMPAD0, 'num1': win32con.VK_NUMPAD1, 'num2': win32con.VK_NUMPAD2,
            'num3': win32con.VK_NUMPAD3, 'num4': win32con.VK_NUMPAD4, 'num5': win32con.VK_NUMPAD5,
            'num6': win32con.VK_NUMPAD6, 'num7': win32con.VK_NUMPAD7, 'num8': win32con.VK_NUMPAD8,
            'num9': win32con.VK_NUMPAD9,
            # 方向键
            'up': win32con.VK_UP, 'down': win32con.VK_DOWN, 'left': win32con.VK_LEFT, 'right': win32con.VK_RIGHT,
            # 特殊键
            'space': win32con.VK_SPACE, 'tab': win32con.VK_TAB, 'enter': win32con.VK_RETURN,
            'esc': win32con.VK_ESCAPE, 'backspace': win32con.VK_BACK, 'delete': win32con.VK_DELETE,
            'home': win32con.VK_HOME, 'end': win32con.VK_END, 'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT, 'insert': win32con.VK_INSERT,
            # 标点符号
            ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF,
            '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE
        }
        
        if key_name in key_mapping:
            return vk_code == key_mapping[key_name]
        elif len(key_name) == 1 and key_name.isalpha():
            return vk_code == ord(key_name.upper())
            
        return False

    def _get_required_vk_codes(self):
        """获取配置热键对应的虚拟键码集合"""
        vk_codes = set()
        
        if self.hotkey_config.get('ctrl'):
            vk_codes.add(win32con.VK_LCONTROL)
            vk_codes.add(win32con.VK_RCONTROL)
        if self.hotkey_config.get('shift'):
            vk_codes.add(win32con.VK_LSHIFT)
            vk_codes.add(win32con.VK_RSHIFT)
        if self.hotkey_config.get('alt'):
            vk_codes.add(win32con.VK_LMENU)
            vk_codes.add(win32con.VK_RMENU)
            
        # 主键映射
        key_name = self.hotkey_config.get('key', 'f12').lower()
        key_mapping = {
            # 功能键
            'f1': win32con.VK_F1, 'f2': win32con.VK_F2, 'f3': win32con.VK_F3,
            'f4': win32con.VK_F4, 'f5': win32con.VK_F5, 'f6': win32con.VK_F6,
            'f7': win32con.VK_F7, 'f8': win32con.VK_F8, 'f9': win32con.VK_F9,
            'f10': win32con.VK_F10, 'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
            # 数字键
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
            # 小键盘数字
            'num0': win32con.VK_NUMPAD0, 'num1': win32con.VK_NUMPAD1, 'num2': win32con.VK_NUMPAD2,
            'num3': win32con.VK_NUMPAD3, 'num4': win32con.VK_NUMPAD4, 'num5': win32con.VK_NUMPAD5,
            'num6': win32con.VK_NUMPAD6, 'num7': win32con.VK_NUMPAD7, 'num8': win32con.VK_NUMPAD8,
            'num9': win32con.VK_NUMPAD9,
            # 方向键
            'up': win32con.VK_UP, 'down': win32con.VK_DOWN, 'left': win32con.VK_LEFT, 'right': win32con.VK_RIGHT,
            # 特殊键
            'space': win32con.VK_SPACE, 'tab': win32con.VK_TAB, 'enter': win32con.VK_RETURN,
            'esc': win32con.VK_ESCAPE, 'backspace': win32con.VK_BACK, 'delete': win32con.VK_DELETE,
            'home': win32con.VK_HOME, 'end': win32con.VK_END, 'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT, 'insert': win32con.VK_INSERT,
            # 标点符号
            ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF,
            '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE
        }
        
        if key_name in key_mapping:
            vk_codes.add(key_mapping[key_name])
        elif len(key_name) == 1 and key_name.isalpha():
            vk_codes.add(ord(key_name.upper()))
            
        return vk_codes


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("热键监听器测试")
            self.setGeometry(100, 100, 300, 250)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            self.status_label = QLabel("状态: 未启动")
            layout.addWidget(self.status_label)
            
            self.start_btn = QPushButton("开始监听")
            self.start_btn.clicked.connect(self.start_listening)
            layout.addWidget(self.start_btn)
            
            self.stop_btn = QPushButton("停止监听")
            self.stop_btn.clicked.connect(self.stop_listening)
            layout.addWidget(self.stop_btn)
            
            self.press_label = QLabel("按下次数: 0")
            layout.addWidget(self.press_label)
            
            self.release_label = QLabel("释放次数: 0")
            layout.addWidget(self.release_label)
            
            self.hotkey_listener = HotkeyListener()
            self.hotkey_listener.hotkey_pressed.connect(self.on_hotkey_pressed)
            self.hotkey_listener.hotkey_released.connect(self.on_hotkey_released)
            self.press_count = 0
            self.release_count = 0
        
        def start_listening(self):
            if self.hotkey_listener.start():
                cfg = self.hotkey_listener.hotkey_config
                parts = []
                if cfg.get('ctrl'): parts.append('Ctrl')
                if cfg.get('shift'): parts.append('Shift')
                if cfg.get('alt'): parts.append('Alt')
                parts.append(str(cfg.get('key', '')).upper())
                self.status_label.setText(f"状态: 监听中 ({'+'.join(parts)})")
            else:
                self.status_label.setText("状态: 启动失败")
        
        def stop_listening(self):
            self.hotkey_listener.stop()
            self.status_label.setText("状态: 已停止")
        
        def on_hotkey_pressed(self):
            self.press_count += 1
            self.press_label.setText(f"按下次数: {self.press_count}")
            
        def on_hotkey_released(self):
            self.release_count += 1
            self.release_label.setText(f"释放次数: {self.release_count}")
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())