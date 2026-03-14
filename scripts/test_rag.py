"""
Test the RAG engine with real questions.
Usage: python scripts/test_rag.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.ai_pipeline.rag.rag_engine import RAGEngine

console = Console()

console.print(Panel(
    "[bold green]RAG ENGINE TEST[/bold green]\n"
    "Ask questions to your AI knowledge base!",
    style="green",
))

# Initialize
console.print("\n[bold]Initializing RAG Engine...[/bold]")
rag = RAGEngine()

# Test questions
questions = [
    "What programming languages or tools are mentioned?",
    "What are the latest technology trends discussed?",
    "Tell me about any open source projects mentioned",
]

for i, question in enumerate(questions):
    console.print(f"\n{'='*60}")
    console.print(f"[bold cyan]Question {i+1}: {question}[/bold cyan]")
    console.print(f"{'='*60}")

    result = rag.query(question)

    # Show answer
    console.print(f"\n[bold green]Answer:[/bold green]")
    console.print(result["answer"])

    # Show sources
    console.print(f"\n[bold yellow]Sources:[/bold yellow]")
    for j, source in enumerate(result["sources"]):
        console.print(
            f"   {j+1}. [{source['relevance']}] {source['title'][:60]}"
        )

    # Show stats
    console.print(
        f"\n   ⏱️  {result['latency_seconds']}s | "
        f"🔤 {result['tokens_used']['total']} tokens | "
        f"💰 $0.00"
    )

# Interactive mode
console.print(f"\n{'='*60}")
console.print("[bold green]Interactive Mode - Ask your own questions![/bold green]")
console.print("Type 'quit' to exit\n")

while True:
    question = input("You: ").strip()
    if question.lower() in ("quit", "exit", "q"):
        break
    if not question:
        continue

    result = rag.query(question)

    console.print(f"\n[green]AI:[/green] {result['answer']}")
    console.print(f"[dim]({result['latency_seconds']}s | {len(result['sources'])} sources | $0.00)[/dim]\n")

console.print("[green]Goodbye![/green]")