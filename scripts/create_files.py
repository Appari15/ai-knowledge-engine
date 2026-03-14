"""Run this to create all project files correctly."""
import os

# ============================================
# FILE 1: src/config/settings.py
# ============================================
settings_code = '''from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="google/gemma-2-9b-it:free", env="OPENROUTER_MODEL")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="knowledge_engine", env="DB_NAME")
    db_user: str = Field(default="dataeng", env="DB_USER")
    db_password: str = Field(default="localdev123", env="DB_PASSWORD")
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    chunk_size: int = 1000
    chunk_overlap: int = 200
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1000

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
'''

with open("src/config/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)
print("1/4 Created: src/config/settings.py")


# ============================================
# FILE 2: src/utils/logger.py
# ============================================
logger_code = '''import sys
import os
from loguru import logger

os.makedirs("logs", exist_ok=True)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)
logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="DEBUG")
app_logger = logger
'''

with open("src/utils/logger.py", "w", encoding="utf-8") as f:
    f.write(logger_code)
print("2/4 Created: src/utils/logger.py")


# ============================================
# FILE 3: scripts/test_setup.py
# ============================================
test_code = r'''import sys
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
'''

with open("scripts/test_setup.py", "w", encoding="utf-8") as f:
    f.write(test_code)
print("3/4 Created: scripts/test_setup.py")


# ============================================
# FILE 4: scripts/init_db.sql
# ============================================
sql_code = '''CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS monitoring;

CREATE TABLE IF NOT EXISTS raw.articles (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,
    title TEXT,
    url TEXT,
    content TEXT,
    score INTEGER,
    author VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(external_id, source)
);

CREATE TABLE IF NOT EXISTS ai.chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(64) NOT NULL UNIQUE,
    article_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    source VARCHAR(50),
    title TEXT,
    embedded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring.llm_queries (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    model VARCHAR(100),
    tokens_used INTEGER,
    latency_seconds FLOAT,
    cost FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

with open("scripts/init_db.sql", "w", encoding="utf-8") as f:
    f.write(sql_code)
print("4/4 Created: scripts/init_db.sql")


print("\n" + "=" * 50)
print("ALL FILES CREATED SUCCESSFULLY!")
print("=" * 50)
print("\nNext steps:")
print("1. Open .env and paste your OpenRouter API key")
print("2. Run: docker-compose down -v")
print("3. Run: docker-compose up -d")
print("4. Wait 10 seconds")
print("5. Run: python scripts/test_setup.py")