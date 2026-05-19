# app/services/vector_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import uuid
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VectorService:
    _client: QdrantClient = None
    
    @classmethod
    def get_client(cls) -> QdrantClient:
        """Initialize Qdrant client (singleton pattern)"""
        if cls._client is None:
            if settings.QDRANT_USE_MEMORY:
                # In-memory mode (no server needed)
                cls._client = QdrantClient(":memory:")
                logger.info("✅ Qdrant initialized (in-memory mode)")
            else:
                # Server mode
                cls._client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT
                )
                logger.info(f"✅ Qdrant connected to {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            
            # Create collection if it doesn't exist
            cls._ensure_collection()
        
        return cls._client
    
    @classmethod
    def _ensure_collection(cls):
        """Create collection if it doesn't exist"""
        client = cls._client
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        collections = client.get_collections().collections
        collection_exists = any(col.name == collection_name for col in collections)
        
        if not collection_exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created Qdrant collection: {collection_name}")
        else:
            logger.info(f"✅ Qdrant collection exists: {collection_name}")
    
    @classmethod
    def add_vectors(
        cls, 
        vectors: List[List[float]], 
        payloads: List[Dict]
    ) -> List[str]:
        """
        Add vectors to Qdrant with metadata
        Returns list of vector IDs
        """
        client = cls.get_client()
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        points = []
        vector_ids = []
        
        for vector, payload in zip(vectors, payloads):
            vector_id = str(uuid.uuid4())
            vector_ids.append(vector_id)
            
            point = PointStruct(
                id=vector_id,
                vector=vector,
                payload=payload
            )
            points.append(point)
        
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        logger.info(f"✅ Added {len(points)} vectors to Qdrant")
        return vector_ids
    
    @classmethod
    def search_similar(
        cls, 
        query_vector: List[float], 
        top_k: int = 3,
        filter_dict: Dict = None
    ) -> List[Dict]:
        """
        Search for similar vectors
        Returns list of matches with scores and payloads
        """
        client = cls.get_client()
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter_dict
        )
        
        matches = []
        for result in results:
            matches.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })
        
        logger.info(f"✅ Found {len(matches)} similar vectors")
        return matches
    
    @classmethod
    def delete_by_document_id(cls, document_id: str):
        """Delete all vectors for a specific document"""
        client = cls.get_client()
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        client.delete(
            collection_name=collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        )
        
        logger.info(f"✅ Deleted vectors for document: {document_id}")