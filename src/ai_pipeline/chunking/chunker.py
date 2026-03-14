"""
Smart document chunker.
Splits articles into smaller pieces for embedding.
"""
import hashlib
from typing import List, Dict
from src.utils.logger import app_logger as logger


class SmartChunker:
    """Split documents into chunks with overlap."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Chunker initialized: size={chunk_size}, overlap={chunk_overlap}")

    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text or len(text) < 50:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If not at the end, try to break at a sentence
            if end < len(text):
                # Look for sentence break near the end
                for sep in ["\n\n", "\n", ". ", "! ", "? ", ", ", " "]:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > self.chunk_size * 0.5:
                        end = start + last_sep + len(sep)
                        break

            chunk = text[start:end].strip()

            if len(chunk) > 50:  # Skip tiny chunks
                chunks.append(chunk)

            # Move forward with overlap
            start = end - self.chunk_overlap

            # Prevent infinite loop
            if start >= len(text) - 50:
                break

        return chunks

    def chunk_article(self, article: Dict) -> List[Dict]:
        """Split one article into chunks with metadata."""
        content = article.get("content", "")
        title = article.get("title", "")

        # Add title to content for context
        full_text = f"{title}\n\n{content}" if title else content

        text_chunks = self._split_text(full_text)

        if not text_chunks:
            return []

        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Create unique chunk ID
            chunk_id = hashlib.md5(
                f"{article['id']}_{i}".encode()
            ).hexdigest()

            chunks.append({
                "chunk_id": chunk_id,
                "article_id": article["id"],
                "content": chunk_text,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "source": article.get("source", "unknown"),
                "title": title,
            })

        return chunks

    def chunk_articles(self, articles: List[Dict]) -> List[Dict]:
        """Chunk multiple articles."""
        all_chunks = []

        for article in articles:
            chunks = self.chunk_article(article)
            all_chunks.extend(chunks)

        logger.info(
            f"Chunked {len(articles)} articles into {len(all_chunks)} chunks"
        )
        return all_chunks