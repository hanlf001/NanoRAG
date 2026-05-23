# NanoRAG 项目开发指南

---

## 一、GitHub 仓库正确流程

**现状说明：**
创建 GitHub 仓库时，系统已自动提交了 README、.gitignore、LICENSE，所以远程仓库已有内容。

**正确操作顺序：**
1. `git clone 仓库地址` 克隆到本地
2. `cd NanoRAG` 进入项目目录
3. 开始本地开发（建目录、写代码等）
4. 有真正修改后再 push

**小步提交原则（重要）：**
- ✅ 每次完成一个小功能就 commit
- ❌ 不要一次写完 100 个功能再提交

示例：
```bash
git commit -m "Add sidebar UI"
git commit -m "Add PDF import"
git commit -m "Implement vector search"
```

---

## 二、项目初始化

**创建虚拟环境：**
```bash
python -m venv venv
```

**激活虚拟环境（Windows）：**
```bash
venv\Scripts\activate
```

**安装依赖：**
```bash
pip install PySide6
```

---

## 三、QML 最小测试版

**目录结构：**
```
NanoRAG/
├── main.py
└── qml/
    └── Main.qml
```

**main.py：**
```python
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

app = QApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.load("qml/Main.qml")

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())
```

**Main.qml：**
```qml
import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 1200
    height: 800
    title: "NanoRAG"

    Rectangle {
        anchors.fill: parent
        color: "#1E1F22"

        Text {
            anchors.centerIn: parent
            text: "NanoRAG"
            color: "white"
            font.pixelSize: 32
            font.bold: true
        }
    }
}
```

**常见错误：**
- `File is empty` → QML 文件存在但没有内容

---

## 四、界面开发顺序

**目标布局：**
```
┌──────────┬──────────────────┐
│ 文档列表 │     聊天区域      │
│          │                  │
│ PDF文件  │    AI回答         │
│          │                  │
├──────────┴──────────────────┤
│         输入框              │
└─────────────────────────────┘
```

**开发顺序（由简到难）：**

| 步骤 | 内容 | 建议 |
|------|------|------|
| 1 | Sidebar（左侧栏） | Logo、导入按钮、文档列表 |
| 2 | 聊天区域 | 用户消息、AI消息、气泡样式 |
| 3 | 输入框 | TextField、发送按钮 |
| 4 | 深色主题统一 | 全局颜色规范化 |

**注意：**
- 先用写死的假数据
- 不要接数据库
- 不要过度设计架构

**示例假数据：**
```qml
model: [
    "FPGA开发文档.pdf",
    "实验数据说明.pdf",
    "Qt教程.pdf"
]
```

---

## 五、推荐颜色主题

| 用途 | 颜色代码 |
|------|----------|
| 背景 | #1E1F22 |
| 侧边栏 | #25262B |
| 卡片 | #2B2D31 |
| 悬停 | #34363C |
| 主蓝色 | #4F8CFF |
| 文字 | #FFFFFF |
| 次要文字 | #B5BAC1 |

---

## 六、下一步建议

**立即执行：**
```bash
git add .
git commit -m "Initialize NanoRAG PySide6 project"
git push
```

**推荐优先做 Sidebar，因为：**
- ✅ 最容易看到成果
- ✅ 最容易提升信心
- ✅ 最容易开始像真正软件

**现在不要做：**
- ❌ 优化架构
- ❌ MVVM
- ❌ 插件化
- ❌ 多线程
- ❌ 复杂信号系统

**核心理念：先把软件"长出来"**
