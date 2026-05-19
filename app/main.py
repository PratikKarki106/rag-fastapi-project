# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.utils.database import MongoDB
from app.utils.redis_client import RedisClient
from app.api import ingestion, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions on Startup
    await MongoDB.connect_db()
    # Initialize Redis verification
    RedisClient.get_client()
    yield
    # Actions on Shutdown
    await MongoDB.close_db()
    RedisClient.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Attach API endpoints
app.include_router(ingestion.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the FastAPI Production RAG Ecosystem",
        "docs_url": "/docs"
    }