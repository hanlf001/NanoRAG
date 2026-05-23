import atexit
import sys
import os

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, QThread, Property
from core.document_manager import DocumentManager
from core.llm_engine import LLMEngine


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
    messageAdded = Signal()
    chatResponseChunk = Signal(str)
    chatResponseFinished = Signal(str)
    chatError = Signal(str)
    documentListChanged = Signal()
    conversationListChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document_manager = DocumentManager()
        self.llm_engine = LLMEngine()
        self._current_conversation_id = None
        self._active_threads = []

        self._load_documents()
        self._load_conversations()

        if self.llm_engine.is_available():
            print(f"LLM 可用 | 模型: {self.llm_engine.model}")
        else:
            print("LLM 不可用，使用降级模式")
    
    def _load_documents(self):
        self._documents = self.document_manager.get_document_list()
    
    def _load_conversations(self):
        self._conversations = self.llm_engine.get_all_conversations()
    
    @Property(list, notify=documentListChanged)
    def documents(self):
        return self._documents
    
    @Property(list, notify=conversationListChanged)
    def conversations(self):
        return self._conversations
    
    @Property(int, notify=conversationListChanged)
    def currentConversationId(self):
        return self._current_conversation_id if self._current_conversation_id else -1
    
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
            print(f"上传文档失败: {e}")
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
            print(f"删除文档失败: {e}")
            return False
    
    @Slot(str, result=bool)
    def sendMessage(self, message):
        try:
            if self._current_conversation_id is None:
                conv_id = self.llm_engine.create_conversation(title=message[:50])
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
            thread.start()
            
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            self.chatError.emit(str(e))
            return False
    
    def _on_chat_chunk(self, chunk):
        self.chatResponseChunk.emit(chunk)
    
    def _on_chat_finished(self, response):
        if response and self._current_conversation_id is not None:
            self.llm_engine.db.create_message(
                self._current_conversation_id,
                "assistant",
                response
            )
        self.chatResponseFinished.emit("")
        self.messageAdded.emit()
    
    def _on_chat_error(self, error):
        self.chatError.emit(error)
    
    @Slot(int, result=bool)
    def selectConversation(self, conv_id):
        try:
            self._current_conversation_id = conv_id
            self.conversationListChanged.emit()
            self.messageAdded.emit()
            return True
        except Exception as e:
            print(f"选择对话失败: {e}")
            return False
    
    @Slot(result=bool)
    def newConversation(self):
        try:
            conv_id = self.llm_engine.create_conversation()
            self._current_conversation_id = conv_id
            self._load_conversations()
            self.conversationListChanged.emit()
            self.messageAdded.emit()
            return True
        except Exception as e:
            print(f"创建对话失败: {e}")
            return False
    
    @Slot(int, result=bool)
    def deleteConversation(self, conv_id):
        try:
            success = self.llm_engine.delete_conversation(conv_id)
            if success:
                if self._current_conversation_id == conv_id:
                    self._current_conversation_id = None
                self._load_conversations()
                self.conversationListChanged.emit()
                self.messageAdded.emit()
            return success
        except Exception as e:
            print(f"删除对话失败: {e}")
            return False
    
    @Slot(int, result=list)
    def getConversationMessages(self, conv_id):
        try:
            messages = self.llm_engine.db.get_messages_by_conversation(conv_id)
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
        except Exception as e:
            print(f"获取消息失败: {e}")
            return []
    
    @Slot(str, result=list)
    def searchDocuments(self, query):
        try:
            results = self.document_manager.search_documents(query, top_k=10)
            return results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def cleanup(self):
        for thread in self._active_threads:
            if thread.isRunning():
                thread.stop()


def main():
    app = QApplication(sys.argv)

    engine = QQmlApplicationEngine()

    backend = NanoRAGBackend()
    engine.rootContext().setContextProperty("nanoRAGBackend", backend)
    atexit.register(backend.cleanup)

    qml_file = os.path.join(os.path.dirname(__file__), "qml", "Main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
