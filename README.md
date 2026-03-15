\# AI Knowledge Engine

An AI-powered knowledge base that ingests articles, generates embeddings, and answers questions using RAG (Retrieval-Augmented Generation). Built on a 100% FREE tech stack.


\## Resources Used

\- OpenRouter API: For FREE LLM chat completions

\- Sentence-Transformers: For FREE local text embeddings

\- ChromaDB: For vector similarity search

\- PostgreSQL: For storing ingested articles

\- FastAPI: For the REST API backend

\- Streamlit: For the interactive chat UI

\- HackerNews API: For fetching tech articles

\- BeautifulSoup: For scraping article content

\- Docker: For running PostgreSQL and ChromaDB



\## How To Use

1\. Get FREE API key at openrouter.ai (no credit card needed)

2\. Install Python 3.10+ and Docker Desktop

3\. Clone the repository

4\. Open Terminal/PowerShell at the project folder

5\. Run 'python -m venv venv'

6\. Run 'venv\\Scripts\\Activate.ps1' (Windows) or 'source venv/bin/activate' (Mac/Linux)

7\. Run 'pip install -r requirements.txt'

8\. Copy .env.example to .env and add your OpenRouter API key

9\. Run 'docker-compose up -d'

10\. Run 'python scripts/run\_ingestion.py'

11\. Run 'python scripts/run\_embeddings.py'

12\. Run 'uvicorn src.api.main:app --port 8001' (Terminal 1)

13\. Run 'streamlit run frontend/app.py --server.port 8501' (Terminal 2)

14\. Open http://localhost:8501 in your browser

