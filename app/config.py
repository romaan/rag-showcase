from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_DB: str = "rag"
    PG_USER: str = "rag"
    PG_PASSWORD: str = "rag"

    EMBEDDINGS_PROVIDER: str = "local"  # local | openai
    LLM_PROVIDER: str = "mock"          # mock | openai
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5

    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "rag-showcase"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
