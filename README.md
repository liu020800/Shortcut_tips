# 智能快捷键提示工具 🚀

一个强大的Windows桌面辅助工具，能够智能识别当前应用程序并显示相关快捷键提示。通过全局热键快速获取当前程序的快捷键列表，极大提升工作效率。

![版本](https://img.shields.io/badge/版本-v2.1.0-blue.svg)
![平台](https://img.shields.io/badge/平台-Windows-green.svg)
![Python](https://img.shields.io/badge/Python-3.7+-orange.svg)
![许可证](https://img.shields.io/badge/许可证-MIT-red.svg)

## ✨ 功能特点

### 🎯 核心功能
- **智能上下文感知** - 自动识别当前活动窗口应用程序
- **全局热键监听** - 默认`Ctrl+Shift+F1`快速唤起快捷键面板
- **进程映射系统** - 灵活映射复杂进程名到简洁配置键
- **可视化设置界面** - 无需手动编辑配置文件的图形化设置
- **实时配置更新** - 设置修改后立即生效，无需重启

### 🎨 界面定制
- **透明度调节** - 支持0.1-1.0自由调节窗口透明度
- **主题定制** - 自定义背景色、字体颜色、字体族和大小
- **位置记忆** - 智能窗口定位，支持居中、鼠标位置等多种模式
- **响应式布局** - 自动适应不同屏幕尺寸和DPI设置
- **显示模式** - 为屏幕的正中显示，根据快捷键的多少，向四周扩散显示
- **显示卡片** - 每个快捷键占用一个卡片，卡片的大小根据快捷键的内容自适应，显示的字体大小一样
- **悬浮窗毛玻璃效果** - 窗口背景模糊，不遮挡其他应用程序

### 📊 数据管理
- **JSON配置** - 结构化的快捷键数据存储
- **Schema验证** - 确保配置文件格式正确
- **文件监控** - 自动检测配置文件变化并重载
- **默认配置** - 内置常用应用程序快捷键

## 🖥️ 系统要求

| 组件 | 要求 | 推荐 |
|------|------|------|
| **操作系统** | Windows 7/8/10/11 | Windows 10/11 |
| **Python版本** | Python 3.7+ | Python 3.9+ |
| **内存** | 64MB | 128MB |
| **磁盘空间** | 30MB | 50MB |

## 🚀 快速开始

### 安装方式

#### 方法一：双击启动（推荐新手）
1. **下载项目**
   ```bash
   git clone https://github.com/your-repo/快捷键提示工具.git
   ```

2. **双击启动**
   - 双击 `启动快捷键工具.bat` 文件即可启动
   - 或者双击 `启动工具(无窗口).bat` 无窗口启动

#### 方法二：命令行运行
1. **下载项目**
   ```bash
   git clone https://github.com/your-repo/快捷键提示工具.git
   cd 快捷键提示工具
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动程序**
   - **无窗口模式**（推荐）：双击 `启动工具(无窗口).bat`
   - **调试模式**：双击 `run.bat` 或运行 `python main.py`

#### 方法二：虚拟环境（推荐开发者）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 首次使用
1. 程序启动后会在**系统托盘**显示图标
2. 按下默认热键 **`Ctrl+Shift+F1`** 测试功能
3. 右键托盘图标进入**设置界面**进行个性化配置

## 📖 使用指南

### 基本操作
- **显示快捷键**: 按下热键（默认`Ctrl+Shift+F1`）
- **隐藏快捷键**: 再次按下热键或点击其他区域
- **移动窗口**: 拖拽快捷键窗口标题栏
- **打开设置**: 右键托盘图标 → "设置"

### 进程映射配置
进程映射允许您将复杂的可执行文件名映射到简洁的配置键：

1. **打开设置界面** → "进程映射"标签页
2. **添加新映射**：
   - 进程名：`chrome.exe`
   - 配置键：`chrome`
3. **保存设置**并重新加载配置

### 快捷键配置
编辑 `shortcuts.json` 文件添加或修改快捷键：

```json
{
  "chrome": [
    {
      "key": "Ctrl+T",
      "desc": "新建标签页",
      "group": "标签管理",
      "tags": ["标签", "新建"]
    },
    {
      "key": "Ctrl+W",
      "desc": "关闭当前标签页",
      "group": "标签管理"
    }
  ],
  "vscode": [
    {
      "key": "Ctrl+Shift+P",
      "desc": "命令面板",
      "group": "导航"
    }
  ]
}
```

### 热键自定义
在设置界面可以自定义：
- **修饰键**: Ctrl、Shift、Alt的组合
- **功能键**: F1-F12或字母数字键
- **示例**: `Ctrl+Alt+H`、`F2`、`Ctrl+Shift+Space`

## 📁 项目结构

```
快捷键提示工具/
├── 📄 main.py                     # 主程序入口和设置界面
├── 📄 shortcut_manager.py         # 快捷键数据管理模块
├── 📄 shortcut_window.py          # 快捷键显示窗口模块
├── 📄 hotkey_listener.py          # 全局热键监听模块
├── 📄 context_monitor.py          # 上下文监控模块
├── 📄 requirements.txt            # Python依赖列表
├── 📄 shortcuts.json              # 快捷键配置文件
├── 📄 process_mapping.json        # 进程映射配置文件
├── 📄 config.json                 # 程序设置文件（自动生成）
├── 📄 run.bat                     # 启动脚本（显示控制台）
├── 📄 启动工具(无窗口).bat        # 启动脚本（无控制台）
├── 🖼️ icon.svg                    # 程序图标文件
└── 📄 README.md                   # 项目说明文档
```

## ⚙️ 配置文件详解

### shortcuts.json - 快捷键配置
支持丰富的字段来组织快捷键信息：

```json
{
  "应用配置键": [
    {
      "key": "快捷键组合",          // 必填：快捷键
      "desc": "功能描述",           // 必填：描述
      "group": "分组名称",          // 可选：用于分组显示
      "tags": ["标签1", "标签2"],   // 可选：标签系统
      "when": "特定条件"           // 可选：使用条件
    }
  ]
}
```

### process_mapping.json - 进程映射
```json
{
  "_description": "进程名映射配置文件",
  "chrome.exe": "chrome",
  "firefox.exe": "firefox", 
  "code.exe": "vscode",
  "notepad++.exe": "notepad",
  "explorer.exe": "explorer"
}
```

### config.json - 程序设置（自动生成）
```json
{
  "hotkey": {
    "ctrl": true,
    "shift": true,
    "alt": false,
    "key": "f1"
  },
  "window": {
    "opacity": 0.9,
    "background_color": "#2b2b2b",
    "font_color": "#ffffff",
    "font_family": "Microsoft YaHei",
    "font_size": 12,
    "position": "center",
    "auto_hide": true,
    "auto_hide_delay": 3000
  },
  "data_files": {
    "shortcuts_file": "shortcuts.json",
    "process_mapping_file": "process_mapping.json"
  }
}
```

## 🔧 开发者指南

### 核心模块说明

#### main.py - 主程序模块
- **ShortcutHintApp**: 主应用程序类，管理系统托盘和程序生命周期
- **SettingsDialog**: 设置界面，提供可视化配置功能
- **核心功能**: 热键处理、托盘管理、设置保存

#### shortcut_manager.py - 数据管理模块
- **ShortcutManager**: 快捷键数据管理器
- **功能特性**: 
  - JSON Schema验证
  - 文件变化监控
  - 多级匹配策略（精确→别名→模糊→默认）
  - 缓存机制

#### shortcut_window.py - 显示窗口模块
- **ShortcutWindow**: 快捷键显示窗口
- **功能特性**:
  - 自适应布局算法
  - 样式自定义引擎
  - 屏幕边界检测
  - 动画效果支持

#### hotkey_listener.py - 热键监听模块
- **HotkeyListener**: 全局热键监听器
- **技术实现**:
  - Windows Hook API
  - 线程安全设计
  - 热键冲突检测
  - 多修饰键支持

#### context_monitor.py - 上下文监控模块
- **ContextMonitor**: 上下文监控器
- **功能特性**:
  - 活动窗口检测
  - 进程映射应用
  - 性能缓存机制
  - 跨平台兼容性

### 扩展开发

#### 添加新应用支持
1. 获取应用进程名：
   ```python
   from context_monitor import ContextMonitor
   monitor = ContextMonitor()
   print(monitor.get_current_process_name())
   ```

2. 添加进程映射（设置界面或手动编辑）
3. 在 `shortcuts.json` 中配置快捷键

#### 自定义显示样式
修改 `shortcut_window.py` 中的样式模板：
```python
def get_card_style(self):
    return f"""
        QWidget {{
            background-color: {self.bg_color};
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }}
    """
```

#### 添加新热键类型
在 `hotkey_listener.py` 的 `key_mapping` 字典中添加：
```python
key_mapping = {
    'new_key': win32con.VK_NEWKEY,
    # ... 其他映射
}
```

## ❗ 常见问题解决

### 问题诊断

#### Q: 程序无法启动？
**解决方案**：
1. 检查Python版本：`python --version`
2. 验证依赖安装：`pip list | findstr PyQt6`
3. 以管理员权限运行
4. 查看错误日志：`shortcut_tool.log`

#### Q: 热键不响应？
**可能原因及解决**：
- **热键冲突**: 检查其他程序是否占用相同热键
- **权限不足**: 以管理员权限运行程序
- **系统兼容**: 确保Windows版本支持
- **防火墙拦截**: 添加程序到防火墙白名单

#### Q: 快捷键显示为空或默认？
**检查步骤**：
1. 验证 `shortcuts.json` 格式：使用JSON验证器
2. 确认进程映射正确：查看 `process_mapping.json`
3. 检查当前进程名：在设置界面查看"当前进程"
4. 查看控制台输出或日志文件

#### Q: 界面显示异常？
**解决方法**：
1. 重置配置：删除 `config.json` 文件
2. 检查显示器设置：缩放比例、分辨率
3. 更新显卡驱动
4. 尝试不同的字体设置

### 性能优化

#### 内存使用优化
- 程序正常运行内存占用: 50-80MB
- 如占用过高，检查是否存在内存泄漏
- 重启程序可释放累积的缓存

#### 响应速度优化
- 热键响应时间: < 100ms
- 如响应慢，检查是否有资源密集型程序干扰
- 优化快捷键配置文件大小

## 📝 更新日志

### v2.1.0 (当前版本) - 2024年新版
- ✨ **新增**: 完全重写的可视化设置界面
- ✨ **新增**: 智能进程映射系统
- ✨ **新增**: 多快捷键组合显示支持
- ✨ **新增**: 实时配置重载功能
- 🔧 **改进**: 优化热键监听性能
- 🔧 **改进**: 增强界面响应式设计
- 🐛 **修复**: 修复重复启动问题
- 🐛 **修复**: 修复界面布局bug
- 💄 **优化**: 全新的现代化UI设计

### v2.0.0 - 功能增强版
- ✨ 新增进程映射功能
- ✨ 新增设置界面
- 🔧 优化窗口显示逻辑
- 🐛 修复多显示器兼容性问题

### v1.0.0 - 初始版本
- 🎉 首次发布
- ✨ 基础热键监听功能
- ✨ 快捷键显示窗口
- ✨ JSON配置支持

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献方式
- 🐛 **报告Bug**: 通过Issues页面报告问题
- 💡 **功能建议**: 提出新功能想法
- 📝 **文档改进**: 完善文档和示例
- 💻 **代码贡献**: 提交Pull Request

### 开发流程
1. **Fork** 本项目
2. **创建特性分支**: `git checkout -b feature/AmazingFeature`
3. **提交更改**: `git commit -m 'Add some AmazingFeature'`
4. **推送分支**: `git push origin feature/AmazingFeature`
5. **创建Pull Request**

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加适当的注释和文档字符串
- 确保新功能有对应的测试用例
- 提交前运行代码格式化工具

## 📄 许可证

本项目采用 **MIT许可证** 开源。这意味着您可以自由地：
- ✅ 商业使用
- ✅ 修改源码
- ✅ 分发软件
- ✅ 私人使用

详细许可证条款请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下开源项目和技术：

- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - 强大的GUI框架
- **[psutil](https://github.com/giampaolo/psutil)** - 系统和进程监控库
- **[pywin32](https://github.com/mhammond/pywin32)** - Windows API访问
- **[jsonschema](https://github.com/python-jsonschema/jsonschema)** - JSON数据验证
- **[watchdog](https://github.com/gorakhargosh/watchdog)** - 文件系统监控

## 📞 联系与支持

- 📧 **邮箱**: [your-email@example.com](mailto:your-email@example.com)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📖 **项目主页**: [GitHub Repository](https://github.com/your-repo)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！⭐**

Made with ❤️ by [Your Name]

</div>