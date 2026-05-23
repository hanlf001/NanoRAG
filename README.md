# NanoRAG

一个轻量级的本地 AI 知识库桌面应用，支持多种文档格式，提供向量搜索和基于本地 LLM 的对话功能。

## ✨ 功能特性

- 📄 **多种文档格式支持**：PDF、Word、Excel、PowerPoint、TXT、Markdown
- 🔍 **智能向量搜索**：基于 FAISS 的快速语义检索
- 🤖 **本地 LLM 集成**：通过 Ollama 使用本地大语言模型
- 💬 **上下文对话**：基于检索文档的智能问答
- 💾 **本地数据存储**：数据全部保存在本地，保护隐私
- 🚀 **降级模式**：没有 Ollama 也能用文档搜索功能

## 📦 快速开始

### 方法一：一键启动（推荐）

Windows 用户直接双击 `启动.bat` 即可！

### 方法二：手动安装

#### 1. 环境要求

- Python 3.8+
- Ollama (可选，用于 AI 对话功能)

#### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

#### 3. （可选）安装和配置 Ollama

1. 从 [Ollama 官网](https://ollama.ai) 下载并安装 Ollama
2. 启动 Ollama 服务
3. 下载一个模型（例如 llama3）：

```bash
ollama pull llama3
```

> 💡 **提示**：没有安装 Ollama 也能用！应用会自动进入降级模式，提供文档搜索功能

## 🚀 使用方法

### 启动应用

```bash
# 方式一：使用启动脚本
启动.bat

# 方式二：手动启动
python main.py
```

### 基本操作

1. **导入文档**：点击左侧栏的「导入文档」按钮，选择要导入的文档
2. **开始对话**：在右侧聊天区域输入问题，AI 会基于已导入的文档回答
3. **管理文档**：可以在文档列表中查看和删除已导入的文档

## 📦 打包成 .exe

如果你想把应用打包给其他用户使用：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包成单文件
python build.py build

# 或创建便携版
python build.py portable
```

打包后的文件在 `dist/` 目录中。

## 📁 项目结构

```
NanoRAG/
├── main.py                    # 应用入口
├── 启动.bat                   # Windows 一键启动脚本
├── build.py                   # 打包脚本
├── requirements.txt           # Python 依赖
├── core/
│   ├── document_manager.py    # 文档管理器
│   ├── llm_engine.py          # LLM 引擎（支持降级模式）
│   ├── pdf_parser.py          # 文档解析器
│   └── vector_search.py       # 向量搜索
├── database/
│   └── database.py            # 数据库模块
└── qml/
    ├── Main.qml               # 主界面
    └── components/            # QML 组件
        ├── Sidebar.qml
        ├── ChatView.qml
        └── ...
```

## 🛠️ 技术栈

- **UI 框架**：PySide6 (Qt Quick/QML)
- **向量搜索**：FAISS + sentence-transformers
- **文档解析**：PyMuPDF, python-docx, openpyxl, python-pptx
- **数据库**：SQLite + sqlite-utils
- **LLM 集成**：Ollama

## 💡 常见问题

### Q: 没有安装 Ollama 可以用吗？

A: 可以！应用会自动进入降级模式，你仍然可以：
- 导入和管理文档
- 使用向量搜索功能
- 查看相关文档片段

只是没有 AI 对话总结功能。

### Q: sentence-transformers 第一次运行很慢？

A: 第一次运行时会下载模型（约 80MB），下载后会缓存，以后就快了。

### Q: 打包后的 .exe 很大？

A: PySide6 和 AI 库比较大，单文件版本可能 100-200MB，这是正常的。

## 📄 许可证

MIT License
