"""
HackerNews API Connector
Fetches top stories from Hacker News.
FREE API - no key needed.
"""
import requests
from datetime import datetime
from typing import List, Dict, Optional
from src.utils.logger import app_logger as logger


class HackerNewsConnector:
    """Fetch stories from HackerNews API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        logger.info("HackerNews connector initialized")

    def get_top_story_ids(self, limit: int = 30) -> List[int]:
        """Get IDs of top stories."""
        url = f"{self.BASE_URL}/topstories.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ids = response.json()[:limit]
        logger.info(f"Fetched {len(ids)} top story IDs")
        return ids

    def get_story(self, story_id: int) -> Optional[Dict]:
        """Get a single story by ID."""
        url = f"{self.BASE_URL}/item/{story_id}.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data is None or data.get("type") != "story":
                return None

            story = {
                "external_id": str(data.get("id", "")),
                "source": "hackernews",
                "title": data.get("title", ""),
                "url": data.get("url", ""),
                "content": data.get("text", ""),
                "score": data.get("score", 0),
                "author": data.get("by", "unknown"),
                "metadata": {
                    "type": data.get("type"),
                    "descendants": data.get("descendants", 0),
                    "kids_count": len(data.get("kids", [])),
                },
                "created_at": datetime.fromtimestamp(
                    data.get("time", 0)
                ).isoformat(),
                "ingested_at": datetime.utcnow().isoformat(),
            }
            return story

        except Exception as e:
            logger.error(f"Failed to fetch story {story_id}: {e}")
            return None

    def fetch_top_stories(self, limit: int = 30) -> List[Dict]:
        """Fetch multiple top stories."""
        logger.info(f"Fetching top {limit} stories from HackerNews...")

        story_ids = self.get_top_story_ids(limit=limit)
        stories = []
        failed = 0

        for i, story_id in enumerate(story_ids):
            story = self.get_story(story_id)
            if story:
                stories.append(story)
            else:
                failed += 1

            # Progress log every 10 stories
            if (i + 1) % 10 == 0:
                logger.info(f"  Progress: {i + 1}/{len(story_ids)} fetched")

        logger.info(
            f"Fetched {len(stories)} stories "
            f"({failed} failed/skipped)"
        )
        return stories