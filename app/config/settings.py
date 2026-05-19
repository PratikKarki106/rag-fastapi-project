# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "RAG FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # LLM Settings (Groq)
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"  # ✅ Fixed with type annotation
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1024
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Chunking Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "rag_db"
    
    # Redis Settings
    REDIS_URL: str
    REDIS_TTL: int = 3600
    
    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "documents"
    QDRANT_USE_MEMORY: bool = True
    
    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt"}
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()