import redis
import json
from typing import List, Optional
from app.config.settings import settings
from app.models.schemas import ChatMessage
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    _client: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get Redis client (singleton pattern)"""
        if cls._client is None:
            try:
                cls._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                cls._client.ping()
                logger.info("✅ Connected to Redis")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise
        return cls._client
    
    @classmethod
    def close(cls):
        """Close Redis connection"""
        if cls._client:
            cls._client.close()
            logger.info("🔌 Redis connection closed")
    
    @classmethod
    def save_conversation(cls, session_id: str, message: ChatMessage):
        """Save a message to conversation history"""
        client = cls.get_client()
        key = f"conversation:{session_id}"
        
        message_data = {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat() if message.timestamp else None
        }
        
        client.rpush(key, json.dumps(message_data))
        client.expire(key, settings.REDIS_TTL)
    
    @classmethod
    def get_conversation(cls, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get conversation history"""
        client = cls.get_client()
        key = f"conversation:{session_id}"
        
        messages = client.lrange(key, -limit, -1)
        
        chat_history = []
        for msg in messages:
            data = json.loads(msg)
            chat_history.append(ChatMessage(**data))
        
        return chat_history
    
    @classmethod
    def clear_conversation(cls, session_id: str):
        """Clear conversation history"""
        client = cls.get_client()
        key = f"conversation:{session_id}"
        client.delete(key)