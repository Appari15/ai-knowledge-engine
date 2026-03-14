"""
Embedding pipeline.
Reads articles from DB → Chunks → Embeds → Stores in ChromaDB.

Usage: python scripts/run_embeddings.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.ai_pipeline.chunking.chunker import SmartChunker
from src.ai_pipeline.embeddings.embedding_service import EmbeddingService
from src.ai_pipeline.embeddings.vector_store import VectorStore
from src.utils.database import DatabaseManager
from src.utils.logger import app_logger as logger

console = Console()


def run_embedding_pipeline():
    console.print(Panel(
        "[bold green]AI EMBEDDING PIPELINE[/bold green]\n"
        "PostgreSQL → Chunking → Embeddings → ChromaDB",
        style="green",
    ))

    start_time = time.time()

    # Step 1: Get articles from database
    console.print("\n[bold]Step 1: Loading articles from PostgreSQL...[/bold]")
    db = DatabaseManager()
    articles = db.fetch_all("""
        SELECT id, external_id, source, title, url, content, score, author
        FROM raw.articles 
        WHERE content IS NOT NULL AND content != ''
        ORDER BY id
    """)
    console.print(f"   Loaded [green]{len(articles)}[/green] articles with content")

    if not articles:
        console.print("[red]No articles found! Run ingestion first.[/red]")
        return

    # Step 2: Chunk articles
    console.print("\n[bold]Step 2: Chunking articles...[/bold]")
    chunker = SmartChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_articles(articles)
    console.print(f"   Created [green]{len(chunks)}[/green] chunks from {len(articles)} articles")

    # Show some examples
    for chunk in chunks[:3]:
        preview = chunk["content"][:80].replace("\n", " ")
        console.print(f"   📄 [{chunk['chunk_index']+1}/{chunk['total_chunks']}] {preview}...")

    if not chunks:
        console.print("[red]No chunks created![/red]")
        return

    # Step 3: Generate embeddings
    console.print("\n[bold]Step 3: Generating embeddings (FREE)...[/bold]")
    embedding_service = EmbeddingService()
    texts = [c["content"] for c in chunks]
    embeddings = embedding_service.generate(texts)
    console.print(f"   Generated [green]{len(embeddings)}[/green] embeddings")
    console.print(f"   Dimension: {len(embeddings[0])}")
    console.print(f"   Cost: [green]$0.00[/green]")

    # Step 4: Store in ChromaDB
    console.print("\n[bold]Step 4: Storing in ChromaDB...[/bold]")
    vector_store = VectorStore()
    vector_store.add_chunks(chunks, embeddings)
    total = vector_store.get_count()
    console.print(f"   Total vectors in ChromaDB: [green]{total}[/green]")

    # Step 5: Quick search test
    console.print("\n[bold]Step 5: Testing search...[/bold]")
    test_query = "data engineering and programming"
    query_embedding = embedding_service.generate_single(test_query)
    results = vector_store.search(query_embedding, n_results=3)

    console.print(f"   Query: [cyan]'{test_query}'[/cyan]")
    console.print(f"   Top results:")
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        similarity = round(1 - dist, 3)
        preview = doc[:100].replace("\n", " ")
        console.print(f"   {i+1}. [{similarity}] {meta['title'][:50]}")
        console.print(f"      {preview}...")

    # Summary
    elapsed = round(time.time() - start_time, 1)

    console.print("\n")
    table = Table(title="Embedding Pipeline Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Articles processed", str(len(articles)))
    table.add_row("Chunks created", str(len(chunks)))
    table.add_row("Embeddings generated", str(len(embeddings)))
    table.add_row("Vectors in ChromaDB", str(total))
    table.add_row("Time taken", f"{elapsed}s")
    table.add_row("Cost", "$0.00")
    console.print(table)

    console.print(Panel(
        f"[bold green]EMBEDDING PIPELINE COMPLETE![/bold green]\n"
        f"{total} vectors ready for AI search!",
        style="green",
    ))


if __name__ == "__main__":
    run_embedding_pipeline()