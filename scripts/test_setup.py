import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel

console = Console()
console.print(Panel("AI Knowledge Engine - Setup Test", style="bold green"))
results = {}
settings = None

# Test 1: Config
console.print("\n[bold]1. Testing Config...[/bold]")
try:
    from src.config.settings import get_settings
    settings = get_settings()
    console.print(f"   [green]PASS[/green] Model: {settings.openrouter_model}")
    key_preview = settings.openrouter_api_key[:20]
    console.print(f"   [green]PASS[/green] API Key: {key_preview}...")
    results["Config"] = True
except Exception as e:
    console.print(f"   [red]FAIL: {e}[/red]")
    results["Config"] = False

# Test 2: OpenRouter FREE LLM
console.print("\n[bold]2. Testing OpenRouter FREE LLM...[/bold]")
if settings is None:
    console.print("   [red]SKIP - Config failed[/red]")
    results["OpenRouter LLM"] = False
else:
    try:
        import requests
        import time
        start = time.time()
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [{"role": "user", "content": "Say hello in 5 words"}],
                "max_tokens": 30,
            },
            timeout=30,
        )
        latency = time.time() - start
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            console.print(f"   [green]PASS[/green] Response: {answer}")
            console.print(f"   [green]PASS[/green] Latency: {latency:.1f}s | Cost: $0.00")
            results["OpenRouter LLM"] = True
        else:
            console.print(f"   [red]FAIL: {response.status_code} - {response.text[:200]}[/red]")
            results["OpenRouter LLM"] = False
    except Exception as e:
        console.print(f"   [red]FAIL: {e}[/red]")
        results["OpenRouter LLM"] = False

# Test 3: FREE Embeddings
console.print("\n[bold]3. Testing FREE Embeddings...[/bold]")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode(["test sentence"])
    console.print(f"   [green]PASS[/green] Dimension: {len(emb[0])} | Cost: $0.00")
    results["Embeddings"] = True
except Exception as e:
    console.print(f"   [red]FAIL: {e}[/red]")
    results["Embeddings"] = False

# Test 4: PostgreSQL
console.print("\n[bold]4. Testing PostgreSQL...[/bold]")
if settings is None:
    console.print("   [red]SKIP - Config failed[/red]")
    results["PostgreSQL"] = False
else:
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).scalar()
            sql = "SELECT table_schema || '.' || table_name FROM information_schema.tables WHERE table_schema IN ('raw','ai','monitoring')"
            tables = conn.execute(text(sql)).fetchall()
        console.print(f"   [green]PASS[/green] Connected!")
        console.print(f"   [green]PASS[/green] Tables: {[t[0] for t in tables]}")
        results["PostgreSQL"] = True
    except Exception as e:
        console.print(f"   [red]FAIL: {e}[/red]")
        results["PostgreSQL"] = False

# Test 5: ChromaDB
console.print("\n[bold]5. Testing ChromaDB...[/bold]")
try:
    import chromadb
    client = chromadb.HttpClient(host="localhost", port=8000)
    client.heartbeat()
    console.print(f"   [green]PASS[/green] Connected!")
    results["ChromaDB"] = True
except Exception as e:
    console.print(f"   [red]FAIL: {e}[/red]")
    results["ChromaDB"] = False

# Summary
console.print("\n" + "=" * 50)
passed = sum(1 for v in results.values() if v)
total = len(results)
for name, status in results.items():
    icon = "[green]PASS[/green]" if status else "[red]FAIL[/red]"
    console.print(f"   {icon}  {name}")
console.print(f"\n   Result: {passed}/{total} passed")
console.print(f"   Total cost: [bold green]$0.00[/bold green]")
if passed == total:
    console.print(Panel("[bold green]ALL TESTS PASSED! Ready for Step 1![/bold green]", style="green"))
else:
    console.print(Panel("[bold red]Some tests failed. Fix errors above.[/bold red]", style="red"))
