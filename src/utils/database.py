"""
Database manager for PostgreSQL operations.
"""
from sqlalchemy import create_engine, text
from typing import List, Dict, Any, Optional
import json
from src.config.settings import get_settings
from src.utils.logger import app_logger as logger


class DatabaseManager:
    """Handles all database operations."""

    def __init__(self):
        settings = get_settings()
        self.engine = create_engine(settings.database_url)
        logger.info("Database manager initialized")

    def execute(self, query: str, params: Optional[Dict] = None):
        """Execute a query."""
        with self.engine.connect() as conn:
            conn.execute(text(query), params or {})
            conn.commit()

    def fetch_all(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch all rows as list of dicts."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def fetch_scalar(self, query: str, params: Optional[Dict] = None) -> Any:
        """Fetch single value."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.scalar()

    def insert_article(self, article: Dict) -> bool:
        """Insert one article into raw.articles."""
        query = """
            INSERT INTO raw.articles 
                (external_id, source, title, url, content, score, author, metadata, created_at, ingested_at)
            VALUES 
                (:external_id, :source, :title, :url, :content, :score, :author, CAST(:metadata AS jsonb), CAST(:created_at AS timestamp), CAST(:ingested_at AS timestamp))
            ON CONFLICT (external_id, source) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                score = EXCLUDED.score,
                ingested_at = EXCLUDED.ingested_at
        """
        try:
            params = {
                "external_id": article["external_id"],
                "source": article["source"],
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "content": article.get("content", ""),
                "score": article.get("score", 0),
                "author": article.get("author", "unknown"),
                "metadata": json.dumps(article.get("metadata", {})),
                "created_at": article.get("created_at"),
                "ingested_at": article.get("ingested_at"),
            }
            self.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to insert article {article.get('external_id')}: {e}")
            return False

    def insert_articles(self, articles: List[Dict]) -> int:
        """Insert multiple articles. Returns count of successful inserts."""
        success = 0
        for article in articles:
            if self.insert_article(article):
                success += 1
        logger.info(f"Inserted {success}/{len(articles)} articles into database")
        return success

    def get_article_count(self) -> int:
        """Get total articles in raw.articles."""
        return self.fetch_scalar("SELECT COUNT(*) FROM raw.articles")

    def get_articles_without_content(self) -> List[Dict]:
        """Get articles that have a URL but no scraped content."""
        return self.fetch_all("""
            SELECT id, external_id, url, title 
            FROM raw.articles 
            WHERE url IS NOT NULL 
              AND url != '' 
              AND (content IS NULL OR content = '')
            LIMIT 50
        """)