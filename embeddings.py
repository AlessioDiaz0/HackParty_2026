"""
Embeddings module: NVIDIA NIM embeddings + ChromaDB vector storage.

Stores classified customer messages as embeddings so similar past messages
can be retrieved for analytics and reference.
"""

import chromadb
from openai import OpenAI

from config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


class EmbeddingStore:
    """Manages NVIDIA NIM embeddings and ChromaDB vector storage."""

    def __init__(self, collection_name: str = "customer_messages"):
        self._client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
        self._chroma = chromadb.Client()
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
        response = self._client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL,
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"},
        )
        return [item.embedding for item in response.data]

    # ------------------------------------------------------------------
    # ChromaDB operations
    # ------------------------------------------------------------------

    def add_message(self, message: str, category: str, confidence: str,
                    urgency: str = "Medium") -> str:
        """Store a classified message with its embedding in ChromaDB."""
        self._counter += 1
        doc_id = f"msg_{self._counter}"

        embedding = self._embed([message])[0]

        self._collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[message],
            metadatas=[{"category": category, "confidence": confidence,
                        "urgency": urgency}],
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
            cat = meta.get("category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {"total_messages": count, "categories": category_counts}
