"""
FastAPI backend for AI Knowledge Engine.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ai_pipeline.rag.rag_engine import RAGEngine
from src.ai_pipeline.embeddings.vector_store import VectorStore
from src.utils.database import DatabaseManager

app = FastAPI(
    title="AI Knowledge Engine",
    description="Ask questions to your AI-powered knowledge base",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize once
rag_engine = None
vector_store = None
db = None


def get_rag():
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine


def get_db():
    global db
    if db is None:
        db = DatabaseManager()
    return db


def get_vs():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store


class QuestionRequest(BaseModel):
    question: str
    num_sources: int = 5


class SourceInfo(BaseModel):
    title: str
    source: str
    relevance: float
    chunk: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceInfo]
    model: str
    tokens_used: dict
    latency_seconds: float
    cost: float


@app.get("/")
def root():
    return {"message": "AI Knowledge Engine API", "status": "running"}


@app.get("/api/stats")
def get_stats():
    database = get_db()
    vs = get_vs()
    return {
        "articles_in_db": database.get_article_count(),
        "vectors_in_chromadb": vs.get_count(),
        "status": "healthy",
        "cost_so_far": 0.00,
    }


@app.post("/api/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        rag = get_rag()
        result = rag.query(
            question=request.question,
            n_results=request.num_sources,
        )

        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            sources=[SourceInfo(**s) for s in result["sources"]],
            model=result["model"],
            tokens_used=result["tokens_used"],
            latency_seconds=result["latency_seconds"],
            cost=result["cost"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))