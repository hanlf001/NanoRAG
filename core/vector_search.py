import numpy as np
import faiss
import pickle
import os
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
            print(f"使用本地模型: {local_model_path}")
            self.model = SentenceTransformer(local_model_path)
        else:
            print(f"使用默认模型: {model_name}")
            self.model = SentenceTransformer(model_name)
        
        self.index = None
        self.documents = []
        self.embedding_dim = None

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype('float32')

    def build_index(self, documents: List[Dict[str, str]]) -> None:
        self.documents = documents
        texts = [doc['content'] for doc in documents]
        embeddings = self._get_embeddings(texts)
        self.embedding_dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        if self.index is None or len(self.documents) == 0:
            return []

        query_embedding = self._get_embeddings([query])
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i in range(min(top_k, len(indices[0]))):
            idx = indices[0][i]
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distances[0][i])))

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
        self.index.add(embeddings)

    def clear_index(self) -> None:
        self.index = None
        self.documents = []
        self.embedding_dim = None
