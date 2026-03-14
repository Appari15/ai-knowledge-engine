"""
Article Scraper
Extracts article text content from URLs.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict
from src.utils.logger import app_logger as logger


class ArticleScraper:
    """Scrape article content from URLs."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def scrape(self, url: str) -> Optional[Dict]:
        """Scrape article content from a URL."""
        if not url or not url.startswith("http"):
            return None

        try:
            response = requests.get(
                url,
                headers=self.HEADERS,
                timeout=15,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Get title
            title = ""
            if soup.title:
                title = soup.title.string or ""

            # Get main content
            # Try common article containers
            content = ""
            for selector in ["article", "main", ".post-content", ".article-body", "#content"]:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator="\n", strip=True)
                    break

            # Fallback: get body text
            if not content or len(content) < 100:
                body = soup.find("body")
                if body:
                    content = body.get_text(separator="\n", strip=True)

            # Clean up content
            lines = content.split("\n")
            cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 20]
            content = "\n".join(cleaned_lines)

            # Skip if too short
            if len(content) < 100:
                logger.warning(f"Content too short for {url}")
                return None

            # Limit content length
            if len(content) > 10000:
                content = content[:10000]

            result = {
                "url": url,
                "title": title.strip(),
                "content": content,
                "word_count": len(content.split()),
                "scraped_at": datetime.utcnow().isoformat(),
            }

            logger.debug(f"Scraped {url}: {result['word_count']} words")
            return result

        except requests.Timeout:
            logger.warning(f"Timeout scraping {url}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return None