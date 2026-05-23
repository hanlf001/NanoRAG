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
- 🧙 **Setup wizard / 安装向导**：Auto-detect Ollama, one-click install with mirror acceleration
- 🎯 **Model recommendation / 模型推荐**：Hardware-based model suggestions
- 🔄 **Model switching / 模型切换**：Switch between any installed Ollama model

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
3. Pull a model (e.g., qwen3):

```bash
ollama pull qwen3:4b
```

> 💡 **Tip / 提示**：The app includes a setup wizard that can auto-detect and install Ollama for you. 应用内置安装向导，可自动检测并引导安装 Ollama。

## Usage / 使用方法

```bash
python main.py
```

1. **Setup / 安装**：First launch will guide you through Ollama installation and model download
2. **Import documents / 导入文档**：Click "导入文档" in the sidebar to upload files
3. **Start chatting / 开始对话**：Type questions in the chat area, AI answers based on imported docs
4. **Manage conversations / 管理对话**：Create, switch, and delete conversations in the sidebar
5. **Switch models / 切换模型**：Choose any installed Ollama model from the top bar

## Build / 打包

Package as a standalone .exe with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=resources/icons/FC.ico --name NanoRAG --add-data "qml;qml" --add-data "resources;resources" main.py
```

> Output goes to `dist/` directory (~420MB, includes all dependencies).
> 打包后的文件在 `dist/` 目录中（约 420MB，包含所有依赖）。

## Project Structure / 项目结构

```
NanoRAG/
├── main.py                    # App entry / 应用入口
├── requirements.txt           # Python dependencies
├── core/
│   ├── document_manager.py    # Document manager / 文档管理器
│   ├── llm_engine.py          # LLM engine (with fallback) / LLM 引擎（含降级）
│   ├── ollama_manager.py      # Ollama setup & model management / Ollama 安装与模型管理
│   ├── pdf_parser.py          # Document parser / 文档解析器
│   └── vector_search.py       # Vector search / 向量搜索
├── database/
│   └── database.py            # Database module / 数据库模块
├── resources/
│   └── icons/
│       ├── FC.ico             # Application icon / 应用图标
│       └── FC.png             # Application icon (PNG) / 应用图标 (PNG)
└── qml/
    ├── Main.qml               # Main UI with chat / 主界面（含聊天区域）
    └── components/
        ├── AboutDialog.qml    # About dialog / 关于对话框
        ├── OllamaSetupDialog.qml # Ollama setup wizard / Ollama 安装向导
        ├── SearchBox.qml      # Search box / 搜索框
        ├── Sidebar.qml        # Sidebar (docs & conversations) / 侧边栏
        └── TopBar.qml         # Top bar (model selector & about) / 顶栏
```

## Tech Stack / 技术栈

- **UI**：PySide6 (Qt Quick/QML)
- **Vector Search / 向量搜索**：FAISS + sentence-transformers
- **Parsing / 文档解析**：PyMuPDF, python-docx, openpyxl, python-pptx
- **Database / 数据库**：SQLite + sqlite-utils
- **LLM**：Ollama
- **Hardware Detection / 硬件检测**：psutil

## FAQ / 常见问题

**Q: Can I use it without Ollama? / 没有 Ollama 能用吗？**

A: Yes. The app enters fallback mode — you can still import docs and use keyword search. Only AI summarization is unavailable.

**Q: First run is slow? / 第一次运行很慢？**

A: The app lazily loads the embedding model (~80MB) on first search, cached afterward. 第一次搜索时会加载模型约 80MB，之后会缓存。

**Q: Can't download Ollama models in China? / 国内下载不了模型？**

A: The setup wizard auto-configures Alibaba Cloud mirror for model downloads. 安装向导会自动配置阿里云镜像加速。

**Q: Large .exe size? / 打包的 exe 很大？**

A: Normal — PySide6 and AI libraries result in 100-200MB single-file builds.

## License / 许可证

MIT

---

© 2026 北京凡策科技有限公司 韩丽峰
