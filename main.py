import atexit
import sys
import os
import ctypes

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, QThread, Property
from PySide6.QtGui import QIcon
from core.document_manager import DocumentManager
from core.llm_engine import LLMEngine
from core.ollama_manager import OllamaManager


def resource_path(relative_path):
    """获取资源绝对路径，支持开发模式和 PyInstaller 打包模式"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


class ChatThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    chunk = Signal(str)

    def __init__(self, llm_engine, query, context_docs, conversation_id):
        super().__init__()
        self.llm_engine = llm_engine
        self.query = query
        self.context_docs = context_docs
        self.conversation_id = conversation_id
        self._full_response = ""

    def run(self):
        try:
            self._full_response = ""
            for chunk in self.llm_engine.chat_stream(
                self.query,
                self.context_docs,
                self.conversation_id
            ):
                self._full_response += chunk
                self.chunk.emit(chunk)
            self.finished.emit(self._full_response)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self.terminate()
        self.wait()


class NanoRAGBackend(QObject):
    chatResponseChunk = Signal(str)
    chatResponseFinished = Signal(str)
    chatError = Signal(str)
    documentListChanged = Signal()
    conversationListChanged = Signal()
    conversationLoaded = Signal(list)
    errorOccurred = Signal(str)
    modelChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_manager = DocumentManager()
        self.llm_engine = LLMEngine()
        self.ollama_manager = OllamaManager()
        self._current_conversation_id = None
        self._active_threads = []
        self._current_thread = None
        self._model_list = []

        self._load_documents()
        self._load_conversations()
        self._load_models()

        if self.llm_engine.is_available():
            print(f"LLM 可用 | 模型: {self.llm_engine.model}")
        else:
            print("LLM 不可用，使用降级模式")

    def _load_documents(self):
        self._documents = self.document_manager.get_document_list()

    def _load_conversations(self):
        self._conversations = self.llm_engine.get_all_conversations()

    def _load_models(self):
        self._model_list = self.llm_engine.list_models()

    # ---- Properties ----

    @Property(list, notify=documentListChanged)
    def documents(self):
        return self._documents

    @Property(list, notify=conversationListChanged)
    def conversations(self):
        return self._conversations

    @Property(int, notify=conversationListChanged)
    def currentConversationId(self):
        return self._current_conversation_id if self._current_conversation_id else -1

    @Property(str, notify=modelChanged)
    def currentModel(self):
        return self.llm_engine.model

    @Property(list, notify=modelChanged)
    def modelList(self):
        return self._model_list

    @Property(QObject, constant=True)
    def ollamaManager(self):
        return self.ollama_manager

    # ---- Document slots ----

    @Slot(str, result=bool)
    def uploadDocument(self, file_path):
        try:
            if file_path.startswith("file:///"):
                file_path = file_path[8:]
            self.document_manager.upload_document(file_path)
            self._load_documents()
            self.documentListChanged.emit()
            return True
        except Exception as e:
            msg = f"上传文档失败: {e}"
            print(msg)
            self.errorOccurred.emit(msg)
            return False

    @Slot(int, result=bool)
    def deleteDocument(self, doc_id):
        try:
            success = self.document_manager.delete_document(doc_id)
            if success:
                self._load_documents()
                self.documentListChanged.emit()
            return success
        except Exception as e:
            msg = f"删除文档失败: {e}"
            print(msg)
            self.errorOccurred.emit(msg)
            return False

    # ---- Chat slots ----

    @Slot(str, result=bool)
    def sendMessage(self, message):
        try:
            if self._current_conversation_id is None:
                title = message[:30] + ("..." if len(message) > 30 else "")
                conv_id = self.llm_engine.create_conversation(title=title)
                self._current_conversation_id = conv_id
                self._load_conversations()
                self.conversationListChanged.emit()

            self.llm_engine.db.create_message(
                self._current_conversation_id,
                "user",
                message
            )
            context_docs = self.document_manager.search_documents(message, top_k=5)

            thread = ChatThread(
                self.llm_engine,
                message,
                context_docs,
                self._current_conversation_id
            )
            thread.chunk.connect(self._on_chat_chunk)
            thread.finished.connect(self._on_chat_finished)
            thread.error.connect(self._on_chat_error)
            thread.finished.connect(thread.deleteLater)
            self._active_threads.append(thread)
            self._current_thread = thread
            thread.start()

            return True
        except Exception as e:
            msg = f"发送消息失败: {e}"
            print(msg)
            self.chatError.emit(msg)
            return False

    def _on_chat_chunk(self, chunk):
        self.chatResponseChunk.emit(chunk)

    def _on_chat_finished(self, response):
        if self._current_conversation_id is not None:
            if response:
                self.llm_engine.db.create_message(
                    self._current_conversation_id,
                    "assistant",
                    response
                )
            self._load_conversations()
            self.conversationListChanged.emit()
        self.chatResponseFinished.emit("")

    def _on_chat_error(self, error):
        self.chatError.emit(error)
        self.errorOccurred.emit(f"对话错误: {error}")

    @Slot(result=bool)
    def stopGeneration(self):
        try:
            thread = self._current_thread
            if thread and thread.isRunning():
                partial = getattr(thread, '_full_response', '')
                try:
                    thread.chunk.disconnect(self._on_chat_chunk)
                    thread.finished.disconnect(self._on_chat_finished)
                    thread.error.disconnect(self._on_chat_error)
                except Exception:
                    pass
                thread.stop()
                self._active_threads.remove(thread)
                self._current_thread = None
                if partial and self._current_conversation_id:
                    self.llm_engine.db.create_message(
                        self._current_conversation_id,
                        "assistant",
                        partial
                    )
                    self._load_conversations()
                    self.conversationListChanged.emit()
                self.chatResponseFinished.emit("")
                return True
        except Exception as e:
            print(f"停止生成失败: {e}")
        return False

    # ---- Conversation slots ----

    @Slot(int, result=list)
    def selectConversation(self, conv_id):
        try:
            self._current_conversation_id = conv_id
            messages = self.llm_engine.db.get_messages_by_conversation(conv_id)
            result = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            self.conversationLoaded.emit(result)
            self.conversationListChanged.emit()
            return result
        except Exception as e:
            msg = f"切换对话失败: {e}"
            print(msg)
            self.errorOccurred.emit(msg)
            return []

    @Slot(result=list)
    def newConversation(self):
        try:
            conv_id = self.llm_engine.create_conversation()
            self._current_conversation_id = conv_id
            self._load_conversations()
            self.conversationListChanged.emit()
            self.conversationLoaded.emit([])
            return []
        except Exception as e:
            msg = f"创建对话失败: {e}"
            print(msg)
            self.errorOccurred.emit(msg)
            return []

    @Slot(int, result=bool)
    def deleteConversation(self, conv_id):
        try:
            success = self.llm_engine.delete_conversation(conv_id)
            if success:
                if self._current_conversation_id == conv_id:
                    self._current_conversation_id = None
                self._load_conversations()
                self.conversationListChanged.emit()
                if self._current_conversation_id is None:
                    self.conversationLoaded.emit([])
            return success
        except Exception as e:
            msg = f"删除对话失败: {e}"
            print(msg)
            self.errorOccurred.emit(msg)
            return False

    # ---- Model slots ----

    @Slot(result=list)
    def listModels(self):
        return self.llm_engine.list_models()

    @Slot(str, result=bool)
    def setModel(self, model_name):
        try:
            self.llm_engine.set_model(model_name)
            self.modelChanged.emit()
            self._load_models()
            return self.llm_engine.is_available()
        except Exception as e:
            print(f"切换模型失败: {e}")
            return False

    # ---- Search slot ----

    @Slot(str, result=list)
    def searchDocuments(self, query):
        try:
            return self.document_manager.search_documents(query, top_k=10)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    # ---- Cleanup ----

    def cleanup(self):
        self.ollama_manager.cleanup()
        for thread in self._active_threads:
            if thread.isRunning():
                thread.stop()


def main():
    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hank.NanoRAG.1.0")

    app = QApplication(sys.argv)

    icon_path = resource_path("resources/icons/FC.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    engine = QQmlApplicationEngine()

    backend = NanoRAGBackend()
    engine.rootContext().setContextProperty("nanoRAGBackend", backend)
    atexit.register(backend.cleanup)

    qml_file = resource_path("qml/Main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
