# NanoRAG

A lightweight local AI knowledge base desktop app with multi-format document support, vector search, and local LLM-powered chat.

> 一个轻量级的本地 AI 知识库桌面应用，支持多种文档格式，提供向量搜索和基于本地 LLM 的对话功能。

## Features / 功能特性

- 📄 **Multi-format support / 多格式支持**：PDF, Word, Excel, PowerPoint, TXT, Markdown
- 🔍 **Smart search / 智能搜索**：FAISS-based fast semantic retrieval
- 🤖 **Local LLM / 本地模型**：Ollama integration for offline AI chat
- 💬 **Contextual Q&A / 上下文问答**：RAG-based document Q&A
- 💾 **Local storage / 本地存储**：All data stored locally, privacy-first
- 🚀 **Fallback mode / 降级模式**：Document search works even without Ollama

## Quick Start / 快速开始

### 1. Requirements / 环境要求

- Python 3.8+
- Ollama (optional / 可选，用于 AI 对话)

### 2. Install dependencies / 安装依赖

```bash
pip install -r requirements.txt
```

### 3. Install Ollama / 安装 Ollama（可选）

1. Download from [Ollama](https://ollama.ai) and install
2. Start the Ollama service
3. Pull a model (e.g., llama3):

```bash
ollama pull llama3
```

> 💡 **Tip / 提示**：The app works without Ollama in fallback mode for document search.
> 没有 Ollama 也能用，应用会自动进入降级模式，提供文档搜索功能。

## Usage / 使用方法

```bash
python main.py
```

1. **Import documents / 导入文档**：Click "导入文档" in the sidebar to upload files
2. **Start chatting / 开始对话**：Type questions in the chat area, AI answers based on imported docs
3. **Manage documents / 管理文档**：View and delete documents in the sidebar list

## Build / 打包

Package as a standalone .exe with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

> Output goes to `dist/` directory. 打包后的文件在 `dist/` 目录中。

## Project Structure / 项目结构

```
NanoRAG/
├── main.py                    # App entry / 应用入口
├── requirements.txt           # Python dependencies
├── core/
│   ├── document_manager.py    # Document manager / 文档管理器
│   ├── llm_engine.py          # LLM engine (with fallback) / LLM 引擎（含降级）
│   ├── pdf_parser.py          # Document parser / 文档解析器
│   └── vector_search.py       # Vector search / 向量搜索
├── database/
│   └── database.py            # Database module / 数据库模块
└── qml/
    ├── Main.qml               # Main UI with chat / 主界面（含聊天区域）
    └── components/
        ├── Sidebar.qml        # Sidebar (import & list) / 侧边栏
        ├── SearchBox.qml      # Search box / 搜索框
        └── TopBar.qml         # Top bar / 顶栏
```

## Tech Stack / 技术栈

- **UI**：PySide6 (Qt Quick/QML)
- **Vector Search / 向量搜索**：FAISS + sentence-transformers
- **Parsing / 文档解析**：PyMuPDF, python-docx, openpyxl, python-pptx
- **Database / 数据库**：SQLite + sqlite-utils
- **LLM**：Ollama

## FAQ / 常见问题

**Q: Can I use it without Ollama? / 没有 Ollama 能用吗？**

A: Yes. The app enters fallback mode — you can still import docs, use search, and view relevant snippets. Only AI summarization is unavailable.

**Q: First run is slow? / 第一次运行很慢？**

A: It downloads models (~80MB) on first run, cached afterward. 第一次运行会下载模型约 80MB，之后会缓存。

**Q: Large .exe size? / 打包的 exe 很大？**

A: Normal — PySide6 and AI libraries result in 100-200MB single-file builds.

## License / 许可证

MIT
