"""
Embeddings module: NVIDIA NIM embeddings + ChromaDB vector storage.

Stores classified customer messages as embeddings so similar past messages
can be retrieved for analytics and reference.
"""

import chromadb
import requests

from config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


class EmbeddingStore:
    """Manages NVIDIA NIM embeddings and ChromaDB vector storage."""

    def __init__(self, collection_name: str = "customer_messages"):
        self._chroma = chromadb.PersistentClient(path="./chroma_db")
        self._collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._counter = self._collection.count()

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings from NVIDIA NIM for a list of texts."""
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": texts,
            "model": EMBEDDING_MODEL,
            "encoding_format": "float",
            "input_type": "query",
            "truncate": "NONE"
        }
        
        response = requests.post(f"{NVIDIA_BASE_URL}/embeddings", headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return [item['embedding'] for item in data['data']]

    # ------------------------------------------------------------------
    # ChromaDB operations
    # ------------------------------------------------------------------

    def add_message(self, message: str, category: str, confidence: str) -> str:
        """Store a classified message with its embedding in ChromaDB."""
        self._counter += 1
        doc_id = f"msg_{self._counter}"

        embedding = self._embed([message])[0]

        self._collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[message],
            metadatas=[{"category": category, "confidence": confidence}],
        )
        return doc_id

    def query_similar(self, message: str, n_results: int = 5) -> dict:
        """Find similar past messages using vector similarity."""
        embedding = self._embed([message])[0]

        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        return results

    def get_stats(self) -> dict:
        """Return basic stats about the stored messages."""
        count = self._collection.count()
        if count == 0:
            return {"total_messages": 0, "categories": {}}

        all_data = self._collection.get(include=["metadatas"])
        category_counts: dict[str, int] = {}
        for meta in all_data["metadatas"]:
            cat = str(meta.get("category", "Unknown"))
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {"total_messages": count, "categories": category_counts}
