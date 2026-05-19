from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB: 
    client: AsyncIOMotorClient = None

    @classmethod
    async def connect_db(cls):
        """Connect MOngoDB"""

        try: 
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(" Connected MongoDB successfully")
        except ConnectionFailure as e:
            logger.error(f"Connection failed: {e}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls):
        """ Get database Instance"""
        return cls.client[settings.MONGODB_DB_NAME]

    @classmethod
    def get_collection(cls, collection_name: str):
        """ Get collection instance"""
        db = cls.get_database()
        return db[collection_name]
    
async def get_documents_collection():
    return MongoDB.get_collection("documents")

async def get_chunks_collection():
    return MongoDB.get_collection("chunks")

async def get_bookings_collection():
    return MongoDB.get_collection("bookings")