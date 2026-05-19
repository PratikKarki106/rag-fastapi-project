# app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model: SentenceTransformer = None
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Load embedding model (singleton pattern)"""
        if cls._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("✅ Embedding model loaded")
        return cls._model
    
    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate embedding for a single text"""
        model = cls.get_model()
        embedding = model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)"""
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        return [emb.tolist() for emb in embeddings]
    
    @classmethod
    def get_embedding_dimension(cls) -> int:
        """Get the dimension of embeddings"""
        return settings.EMBEDDING_DIMENSION