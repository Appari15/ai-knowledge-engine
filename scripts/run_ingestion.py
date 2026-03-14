"""
Main ingestion pipeline.
Fetches articles from HackerNews → Scrapes content → Saves to PostgreSQL.

Usage: python scripts/run_ingestion.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.ingestion.connectors.hackernews import HackerNewsConnector
from src.ingestion.scrapers.article_scraper import ArticleScraper
from src.utils.database import DatabaseManager
from src.utils.logger import app_logger as logger

console = Console()


def run_ingestion():
    console.print(Panel(
        "[bold green]DATA INGESTION PIPELINE[/bold green]\n"
        "HackerNews API → Scraper → PostgreSQL",
        style="green",
    ))

    start_time = time.time()

    # Step 1: Fetch from HackerNews
    console.print("\n[bold]Step 1: Fetching from HackerNews API...[/bold]")
    hn = HackerNewsConnector()
    stories = hn.fetch_top_stories(limit=20)
    console.print(f"   Fetched [green]{len(stories)}[/green] stories")

    # Step 2: Scrape article content
    console.print("\n[bold]Step 2: Scraping article content...[/bold]")
    scraper = ArticleScraper()
    enriched = 0

    for story in stories:
        url = story.get("url", "")
        if url and url.startswith("http"):
            result = scraper.scrape(url)
            if result and result.get("content"):
                story["content"] = result["content"]
                enriched += 1
                console.print(f"   [green]✓[/green] {story['title'][:60]}...")
            else:
                console.print(f"   [yellow]⊘[/yellow] {story['title'][:60]}... (no content)")
        else:
            console.print(f"   [yellow]⊘[/yellow] {story['title'][:60]}... (no URL)")

    console.print(f"   Scraped content for [green]{enriched}[/green] articles")

    # Step 3: Save to database
    console.print("\n[bold]Step 3: Saving to PostgreSQL...[/bold]")
    db = DatabaseManager()
    saved = db.insert_articles(stories)
    total = db.get_article_count()

    # Summary
    elapsed = round(time.time() - start_time, 1)

    console.print("\n")
    table = Table(title="Ingestion Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Stories fetched", str(len(stories)))
    table.add_row("Content scraped", str(enriched))
    table.add_row("Saved to DB", str(saved))
    table.add_row("Total in DB", str(total))
    table.add_row("Time taken", f"{elapsed}s")
    table.add_row("Cost", "$0.00")
    console.print(table)

    console.print(Panel(
        f"[bold green]INGESTION COMPLETE![/bold green]\n"
        f"{total} articles in database ready for AI processing",
        style="green",
    ))


if __name__ == "__main__":
    run_ingestion()