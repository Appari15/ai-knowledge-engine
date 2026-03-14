"""
ChromaDB vector store manager.
Stores and searches embeddings. FREE.
"""
import chromadb
from typing import List, Dict, Optional
from src.config.settings import get_settings
from src.utils.logger import app_logger as logger


class VectorStore:
    """Manage ChromaDB vector database."""

    def __init__(self):
        settings = get_settings()
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        count = self.collection.count()
        logger.info(f"Vector store connected! Collection has {count} items")

    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Add chunks with embeddings to vector store."""
        if not chunks:
            return

        self.collection.upsert(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["content"] for c in chunks],
            metadatas=[
                {
                    "article_id": str(c["article_id"]),
                    "title": c["title"][:200] if c["title"] else "",
                    "source": c["source"],
                    "chunk_index": c["chunk_index"],
                    "total_chunks": c["total_chunks"],
                }
                for c in chunks
            ],
        )

        logger.info(f"Added {len(chunks)} chunks to vector store")

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> Dict:
        """Search for similar chunks."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def get_count(self) -> int:
        """Get total items in collection."""
        return self.collection.count()

    def reset(self):
        """Delete all items (use carefully!)."""
        self.client.delete_collection("knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Vector store reset!")