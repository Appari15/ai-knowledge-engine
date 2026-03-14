CREATE SCHEMA IF NOT EXISTS raw;
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
