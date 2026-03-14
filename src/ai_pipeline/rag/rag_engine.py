"""
RAG Engine - Retrieval Augmented Generation.
Searches knowledge base and generates AI answers.
"""
import time
from typing import Dict, Optional, List
from src.ai_pipeline.embeddings.embedding_service import EmbeddingService
from src.ai_pipeline.embeddings.vector_store import VectorStore
from src.ai_pipeline.rag.llm_service import LLMService
from src.utils.logger import app_logger as logger


class RAGEngine:
    """
    The brain of the system.
    1. Takes a question
    2. Finds relevant chunks from ChromaDB
    3. Sends them to LLM with the question
    4. Returns answer with sources
    """

    def __init__(self):
        logger.info("Initializing RAG Engine...")
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm = LLMService()
        logger.info("RAG Engine ready!")

    def _build_context(self, query: str, n_results: int = 5) -> tuple:
        """Search vector DB and build context string."""

        # Generate query embedding
        query_embedding = self.embedding_service.generate_single(query)

        # Search ChromaDB
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
        )

        # Build context from results
        context_parts = []
        sources = []

        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            similarity = round(1 - distance, 3)

            context_parts.append(
                f"[Source {i+1}] (Relevance: {similarity})\n"
                f"Title: {metadata.get('title', 'Unknown')}\n"
                f"Content: {doc}\n"
            )

            sources.append({
                "title": metadata.get("title", "Unknown"),
                "source": metadata.get("source", "unknown"),
                "relevance": similarity,
                "chunk": f"{metadata.get('chunk_index', 0)+1}/{metadata.get('total_chunks', 1)}",
            })

        context = "\n---\n".join(context_parts)
        return context, sources

    def query(
        self,
        question: str,
        n_results: int = 5,
    ) -> Dict:
        """
        Full RAG pipeline:
        Question → Search → Context → LLM → Answer
        """
        start = time.time()

        # Step 1: Find relevant context
        context, sources = self._build_context(question, n_results)

        # Step 2: Build prompt
        system_prompt = """You are a helpful knowledge assistant. 
Answer questions based ONLY on the provided context below.
If the context doesn't contain enough information to answer, say "I don't have enough information about that in my knowledge base."
Always reference your sources using [Source N] notation.
Be concise but thorough."""

        user_prompt = f"""Context from knowledge base:
{context}

Question: {question}

Answer based on the context above. Cite sources using [Source N]."""

        # Step 3: Get LLM response
        llm_result = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        total_time = round(time.time() - start, 2)

        result = {
            "question": question,
            "answer": llm_result["content"],
            "sources": sources,
            "model": llm_result["model"],
            "tokens_used": llm_result["tokens_used"],
            "latency_seconds": total_time,
            "cost": 0.00,
        }

        logger.info(f"RAG query completed in {total_time}s")
        return result