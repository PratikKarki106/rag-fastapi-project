from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    """ Document metadata stored in MongoDB """

    document_id: str
    filename: str
    file_type: str
    file_size: int
    total_chunks: int
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    uploaded_at: datetime
    upload_status: str ="completed"

class ChunkMetadata(BaseModel):
    """ Chunk Metadata stored in MongoDB """
    chunk_id: str
    document_id: str
    chunk_index: int
    chunk_text: str
    chunk_size: int
    vector_id: str #reference to Qdrant vector ID
    created_at: datetime


class BookingRecord(BaseModel):
    """ Booking information stored in MongoDB"""

    booking_id: str
    session_id: str
    name: str
    email: str
    date: str
    time: str
    status: str = "confirmed"
    created_at: datetime
    notes: Optional[str] = None