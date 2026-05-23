import sqlite_utils
import os
import threading
from datetime import datetime
from typing import List, Dict, Optional, Any


class NanoRAGDatabase:
    def __init__(self, db_path: str = "nano_rag.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_tables()

    @property
    def db(self):
        if not hasattr(self._local, 'db'):
            self._local.db = sqlite_utils.Database(self.db_path)
            self._local.db.execute("PRAGMA foreign_keys = ON")
        return self._local.db

    def _init_tables(self):
        db = sqlite_utils.Database(self.db_path)
        db.execute("PRAGMA foreign_keys = ON")

        if "documents" not in db.table_names():
            db["documents"].create({
                "id": int,
                "name": str,
                "path": str,
                "created_at": str,
                "updated_at": str
            }, pk="id")

        if "chunks" not in db.table_names():
            db["chunks"].create({
                "id": int,
                "document_id": int,
                "content": str,
                "chunk_index": int,
                "created_at": str
            }, pk="id", foreign_keys=[("document_id", "documents", "id")])

        if "conversations" not in db.table_names():
            db["conversations"].create({
                "id": int,
                "title": str,
                "created_at": str,
                "updated_at": str
            }, pk="id")

        if "messages" not in db.table_names():
            db["messages"].create({
                "id": int,
                "conversation_id": int,
                "role": str,
                "content": str,
                "created_at": str
            }, pk="id", foreign_keys=[("conversation_id", "conversations", "id")])

    def _get_current_time(self) -> str:
        return datetime.now().isoformat()

    def create_document(self, name: str, path: str) -> int:
        now = self._get_current_time()
        result = self.db["documents"].insert({
            "name": name,
            "path": path,
            "created_at": now,
            "updated_at": now
        })
        if hasattr(result, 'id'):
            return result.id
        return int(result.last_rowid) if hasattr(result, 'last_rowid') else 1

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        doc = self.db["documents"].get(doc_id)
        return dict(doc) if doc else None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return [dict(doc) for doc in self.db["documents"].rows]

    def update_document(self, doc_id: int, name: Optional[str] = None, path: Optional[str] = None) -> bool:
        doc = self.get_document(doc_id)
        if not doc:
            return False
        
        updates = {"updated_at": self._get_current_time()}
        if name is not None:
            updates["name"] = name
        if path is not None:
            updates["path"] = path
        
        self.db["documents"].update(doc_id, updates)
        return True

    def delete_document(self, doc_id: int) -> bool:
        if self.get_document(doc_id) is None:
            return False
        
        self.db["chunks"].delete_where("document_id = ?", [doc_id])
        self.db["documents"].delete(doc_id)
        return True

    def create_chunk(self, document_id: int, content: str, chunk_index: int) -> int:
        result = self.db["chunks"].insert({
            "document_id": document_id,
            "content": content,
            "chunk_index": chunk_index,
            "created_at": self._get_current_time()
        })
        if hasattr(result, 'id'):
            return result.id
        return int(result.last_rowid) if hasattr(result, 'last_rowid') else 1

    def get_chunk(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        chunk = self.db["chunks"].get(chunk_id)
        return dict(chunk) if chunk else None

    def get_chunks_by_document(self, document_id: int) -> List[Dict[str, Any]]:
        chunks = self.db["chunks"].rows_where("document_id = ?", [document_id], order_by="chunk_index")
        return [dict(chunk) for chunk in chunks]

    def delete_chunk(self, chunk_id: int) -> bool:
        if self.get_chunk(chunk_id) is None:
            return False
        self.db["chunks"].delete(chunk_id)
        return True

    def delete_chunks_by_document(self, document_id: int) -> int:
        return self.db["chunks"].delete_where("document_id = ?", [document_id])

    def create_conversation(self, title: str) -> int:
        now = self._get_current_time()
        result = self.db["conversations"].insert({
            "title": title,
            "created_at": now,
            "updated_at": now
        })
        if hasattr(result, 'id'):
            return result.id
        return int(result.last_rowid) if hasattr(result, 'last_rowid') else 1

    def get_conversation(self, conv_id: int) -> Optional[Dict[str, Any]]:
        conv = self.db["conversations"].get(conv_id)
        return dict(conv) if conv else None

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        return [dict(conv) for conv in self.db["conversations"].rows]

    def update_conversation(self, conv_id: int, title: Optional[str] = None) -> bool:
        conv = self.get_conversation(conv_id)
        if not conv:
            return False
        
        updates = {"updated_at": self._get_current_time()}
        if title is not None:
            updates["title"] = title
        
        self.db["conversations"].update(conv_id, updates)
        return True

    def delete_conversation(self, conv_id: int) -> bool:
        if self.get_conversation(conv_id) is None:
            return False
        
        self.db["messages"].delete_where("conversation_id = ?", [conv_id])
        self.db["conversations"].delete(conv_id)
        return True

    def create_message(self, conversation_id: int, role: str, content: str) -> int:
        result = self.db["messages"].insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": self._get_current_time()
        })
        
        self.update_conversation(conversation_id)
        if hasattr(result, 'id'):
            return result.id
        return int(result.last_rowid) if hasattr(result, 'last_rowid') else 1

    def get_message(self, msg_id: int) -> Optional[Dict[str, Any]]:
        msg = self.db["messages"].get(msg_id)
        return dict(msg) if msg else None

    def get_messages_by_conversation(self, conversation_id: int) -> List[Dict[str, Any]]:
        messages = self.db["messages"].rows_where("conversation_id = ?", [conversation_id], order_by="id")
        return [dict(msg) for msg in messages]

    def delete_message(self, msg_id: int) -> bool:
        if self.get_message(msg_id) is None:
            return False
        self.db["messages"].delete(msg_id)
        return True

    def delete_messages_by_conversation(self, conversation_id: int) -> int:
        return self.db["messages"].delete_where("conversation_id = ?", [conversation_id])
