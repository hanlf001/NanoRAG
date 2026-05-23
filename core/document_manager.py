import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from database.database import NanoRAGDatabase
from core.pdf_parser import DocumentParser
from core.vector_search import VectorSearch


class DocumentManager:
    def __init__(self, db_path: str = "nano_rag.db", index_path: str = "nano_rag.index", docs_path: str = "nano_rag.docs"):
        self.db = NanoRAGDatabase(db_path)
        self.parser = DocumentParser()
        self.vector_search = VectorSearch()
        self.index_path = index_path
        self.docs_path = docs_path

        self._load_or_build_index()

    def _load_or_build_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self.vector_search.load_index(self.index_path, self.docs_path)

        db_chunk_count = sum(
            len(self.db.get_chunks_by_document(doc["id"]))
            for doc in self.db.get_all_documents()
        )

        if self.vector_search.document_count != db_chunk_count:
            self._rebuild_index_from_db()
        elif db_chunk_count == 0:
            self.vector_search.clear_index()

    def _rebuild_index_from_db(self):
        all_documents = self.db.get_all_documents()
        vector_docs = []

        for doc in all_documents:
            chunks = self.db.get_chunks_by_document(doc["id"])
            for chunk in chunks:
                vector_docs.append({
                    "content": chunk["content"],
                    "document_id": doc["id"],
                    "document_name": doc["name"],
                    "chunk_id": chunk["id"],
                    "chunk_index": chunk["chunk_index"]
                })

        if vector_docs:
            self.vector_search.build_index(vector_docs)
        else:
            self.vector_search.clear_index()

        self._save_vector_index()

    def _save_vector_index(self):
        self.vector_search.save_index(self.index_path, self.docs_path)

    def upload_document(self, file_path: str) -> Dict[str, Any]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        parsed_result = self.parser.parse_document(str(file_path))

        doc_id = self.db.create_document(
            name=parsed_result["file_name"],
            path=parsed_result["file_path"]
        )

        vector_docs = []
        for idx, chunk in enumerate(parsed_result["chunks"]):
            chunk_id = self.db.create_chunk(
                document_id=doc_id,
                content=chunk,
                chunk_index=idx
            )
            vector_docs.append({
                "content": chunk,
                "document_id": doc_id,
                "document_name": parsed_result["file_name"],
                "chunk_id": chunk_id,
                "chunk_index": idx
            })

        self.vector_search.add_documents(vector_docs)
        self._save_vector_index()

        return {
            "document_id": doc_id,
            "file_name": parsed_result["file_name"],
            "file_path": parsed_result["file_path"],
            "chunk_count": parsed_result["chunk_count"],
            "total_chars": parsed_result["total_chars"]
        }

    def delete_document(self, doc_id: int) -> bool:
        doc = self.db.get_document(doc_id)
        if not doc:
            return False

        chunks = self.db.get_chunks_by_document(doc_id)
        chunk_ids = [chunk["id"] for chunk in chunks]

        self.db.delete_document(doc_id)
        self.vector_search.remove_by_chunk_ids(chunk_ids)
        self._save_vector_index()

        return True

    def get_document_list(self) -> List[Dict[str, Any]]:
        return self.db.get_all_documents()

    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        doc = self.db.get_document(doc_id)
        if doc:
            chunks = self.db.get_chunks_by_document(doc_id)
            doc["chunks"] = chunks
        return doc

    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.vector_search.search(query, top_k)

        search_results = []
        for doc, distance in results:
            search_results.append({
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "chunk_id": doc["chunk_id"],
                "chunk_index": doc["chunk_index"],
                "content": doc["content"],
                "distance": distance
            })

        return search_results

    def clear_all_documents(self) -> None:
        all_docs = self.db.get_all_documents()
        for doc in all_docs:
            self.db.delete_document(doc["id"])
        self.vector_search.clear_index()
        self._save_vector_index()
