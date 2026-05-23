# Changelog

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
