import asyncio
from app.utils.database import MongoDB
from app.utils.redis_client import RedisClient
from app.models.schemas import ChatMessage
from datetime import datetime

async def test_connections():
    print("Testing database connections...\n")
    
    # Test MongoDB
    try:
        await MongoDB.connect_db()
        db = MongoDB.get_database()
        collections = await db.list_collection_names()
        print(f"✅ MongoDB connected! Collections: {collections}")
    except Exception as e:
        print(f"❌ MongoDB failed: {e}")
    
    # Test Redis
    try:
        redis_client = RedisClient.get_client()
        
        # Test save/retrieve conversation
        test_msg = ChatMessage(
            role="user",
            content="Hello!",
            timestamp=datetime.now()
        )
        RedisClient.save_conversation("test_session", test_msg)
        history = RedisClient.get_conversation("test_session")
        print(f"✅ Redis connected! Test message saved and retrieved: {len(history)} messages")
        
        # Cleanup
        RedisClient.clear_conversation("test_session")
    except Exception as e:
        print(f"❌ Redis failed: {e}")
    
    # Cleanup
    await MongoDB.close_db()
    RedisClient.close()
    print("\n🎉 Database connection tests complete!")

if __name__ == "__main__":
    asyncio.run(test_connections())