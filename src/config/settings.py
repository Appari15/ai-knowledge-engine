from pydantic_settings import BaseSettings
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
