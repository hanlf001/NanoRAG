import numpy as np
import faiss
import pickle
import os
import io
from contextlib import redirect_stderr, redirect_stdout
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional


class VectorSearch:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_model_path = os.path.join(project_dir, "models")

        if os.path.exists(local_model_path) and any(
            f.endswith('.safetensors') or f == 'model.safetensors'
            for f in os.listdir(local_model_path)
        ):
            self._model_path = local_model_path
        else:
            self._model_path = model_name

        self.model = None
        self.index = None
        self.documents = []
        self.embedding_dim = None

    def _ensure_model(self):
        if self.model is not None:
            return
        print(f"加载向量模型: {self._model_path}")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.model = SentenceTransformer(self._model_path)

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        self._ensure_model()
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype('float32')

    def build_index(self, documents: List[Dict[str, str]]) -> None:
        self.documents = documents
        texts = [doc['content'] for doc in documents]
        embeddings = self._get_embeddings(texts)
        self.embedding_dim = embeddings.shape[1]

        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.embedding_dim))
        ids = np.array([doc['chunk_id'] for doc in documents], dtype=np.int64)
        self.index.add_with_ids(embeddings, ids)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        if self.index is None or len(self.documents) == 0:
            return []

        query_embedding = self._get_embeddings([query])
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i in range(min(top_k, len(indices[0]))):
            idx = indices[0][i]
            if idx < 0:
                continue
            for doc in self.documents:
                if doc['chunk_id'] == idx:
                    results.append((doc, float(distances[0][i])))
                    break

        return results

    def save_index(self, index_path: str, docs_path: str) -> None:
        if self.index is not None:
            faiss.write_index(self.index, index_path)
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)

    def load_index(self, index_path: str, docs_path: str) -> None:
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        if os.path.exists(docs_path):
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
        if self.index and len(self.documents) > 0:
            self.embedding_dim = self.index.d

    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        if self.index is None:
            self.build_index(documents)
            return

        self.documents.extend(documents)
        texts = [doc['content'] for doc in documents]
        embeddings = self._get_embeddings(texts)
        ids = np.array([doc['chunk_id'] for doc in documents], dtype=np.int64)
        self.index.add_with_ids(embeddings, ids)

    def remove_by_chunk_ids(self, chunk_ids: List[int]) -> None:
        if self.index is None:
            return
        ids_set = set(chunk_ids)
        self.index.remove_ids(np.array(chunk_ids, dtype=np.int64))
        self.documents = [d for d in self.documents if d['chunk_id'] not in ids_set]

    def clear_index(self) -> None:
        self.index = None
        self.documents = []
        self.embedding_dim = None

    @property
    def document_count(self) -> int:
        return len(self.documents)
