# app/models/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# Document Ingestion Schemas
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    total_chunks: int
    chunking_strategy: str
    message: str
    uploaded_at: datetime

class ChunkingStrategy(BaseModel):
    strategy: Literal["fixed", "semantic"] = Field(
        default="fixed",
        description="Chunking strategy: 'fixed' (by character count) or 'semantic' (by meaning)"
    )
    chunk_size: Optional[int] = Field(default=500, description="Size of each chunk")
    chunk_overlap: Optional[int] = Field(default=50, description="Overlap between chunks")

# Chat Schemas
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID for conversation")
    query: str = Field(..., description="User query")
    top_k: Optional[int] = Field(default=3, description="Number of relevant chunks to retrieve")

class ChatResponse(BaseModel):
    session_id: str
    query: str
    response: str
    retrieved_chunks: List[dict]
    timestamp: datetime
    
# Booking Schemas
class BookingInfo(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    date: str = Field(..., description="Interview date (YYYY-MM-DD)")
    time: str = Field(..., description="Interview time (HH:MM)")

class BookingResponse(BaseModel):
    booking_id: str
    message: str
    booking_details: BookingInfo
    created_at: datetime