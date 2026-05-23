# Changelog

## v0.2.0 (2026-05-23)

### Added / 新增

- **Ollama 安装向导**：启动时检测 Ollama，未安装则弹出引导对话框，支持一键下载安装
- **模型推荐**：根据电脑硬件配置（内存/CPU/GPU）推荐合适的模型
- **模型下载管理**：支持多模型同时下载，带进度条和速度显示
- **国内镜像源配置**：默认勾选阿里云镜像，加速模型下载
- **模型选择器**：TopBar 下拉框切换 Ollama 模型
- **对话列表**：侧边栏新增对话管理区域，支持新建/切换/删除对话
- **停止生成按钮**：AI 回复过程中可随时停止
- **错误提示 Toast**：页面顶部红色提示条，操作失败时自动弹出
- **关于对话框**：显示版本号、公司信息和联系方式
- **应用图标**：窗口左上角和任务栏图标
- **对话标题自动生成**：新建对话时自动取第一条消息前 30 字作为标题
- **网络检测**：下载前检查网络连通性

### Changed / 变更

- TopBar 集成模型选择器和关于入口
- Sidebar 重构为对话列表 + 文档搜索 + 文档列表三区布局
- 消息气泡宽度从 360px 加宽到 520px
- 向量模型改为懒加载，启动时不加载

### Fixed / 修复

- 消息重复存储到数据库（chat_stream 和 sendMessage 各存一份）
- 对话切换不加载历史消息
- 启动时向量索引重复构建
- 删除文档时全量重建 FAISS 索引，改用 IndexIDMap + remove_ids 高效删除
- 删除按钮点击无效（MouseArea 层级冲突）
- 模型选择器不显示当前模型
- 发送消息后不自动滚动到底部
- 停止生成后无法继续对话（旧线程信号未断开）

---

## v0.1.0 (2026-05-23)

### Added / 新增

- Multi-format document import (PDF, Word, Excel, PowerPoint, TXT, Markdown)
- FAISS-based vector search for semantic retrieval
- Ollama integration for local LLM chat
- RAG-based contextual Q&A
- Fallback mode when Ollama is unavailable
- Conversation management (create, switch, delete)

### Changed / 变更

- Chat UI refactored from ListView+delegate to Flickable+Repeater for reliable rendering
- Message display now inline in Main.qml instead of separate ChatView/MessageBubble components

### Fixed / 修复

- Messages not rendering in chat area
- QThread cleanup on app exit
- Foreign keys enforcement in SQLite database
- QML binding loop in MessageBubble component

### Removed / 移除

- ChatView.qml and MessageBubble.qml (merged into Main.qml)
