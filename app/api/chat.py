# app/api/chat.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage, BookingResponse
from app.utils.redis_client import RedisClient
from app.utils.database import get_bookings_collection
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.models.database import BookingRecord
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/chat", tags=["Conversational RAG"])

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    try:
        # 1. Fetch chat memory records from Redis
        chat_history = RedisClient.get_conversation(session_id=request.session_id, limit=6)
        
        # 2. Vector Search: Convert query into vectors and locate snippets from Qdrant
        query_vector = EmbeddingService.generate_embedding(request.query)
        search_results = VectorService.search_similar(query_vector, top_k=request.top_k)
        
        # Extract plain text chunks for the context engine
        context_chunks = [match['payload']['chunk_text'] for match in search_results]
        
        # 3. Generate answers safely passing down history lists and text components
        llm_answer = LLMService.generate_rag_response(
            query=request.query, 
            context_chunks=context_chunks, 
            chat_history=chat_history
        )
        
        # 4. Save this specific conversation turn into Redis (User query + Assistant response)
        user_msg = ChatMessage(role="user", content=request.query, timestamp=datetime.now())
        assistant_msg = ChatMessage(role="assistant", content=llm_answer, timestamp=datetime.now())
        RedisClient.save_conversation(request.session_id, user_msg)
        RedisClient.save_conversation(request.session_id, assistant_msg)
        
        # Extract data payload snippets for client references
        retrieved_metadata = [
            {"filename": m['payload'].get('filename'), "score": m['score'], "text": m['payload'].get('chunk_text')[:200]}
            for m in search_results
        ]
        
        return ChatResponse(
            session_id=request.session_id,
            query=request.query,
            response=llm_answer,
            retrieved_chunks=retrieved_metadata,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/book", response_model=BookingResponse)
async def check_and_book_interview(session_id: str, last_message: str):
    """
    Explicitly checks if a message contains booking data.
    If full details are found, compiles them directly into MongoDB.
    """
    try:
        booking_info = LLMService.check_and_extract_booking(last_message)
        
        if not booking_info:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract complete booking information. Ensure Name, Email, Date, and Time are provided."
            )
            
        bookings_col = await get_bookings_collection()
        booking_id = str(uuid.uuid4())
        
        record = BookingRecord(
            booking_id=booking_id,
            session_id=session_id,
            name=booking_info.name,
            email=booking_info.email,
            date=booking_info.date,
            time=booking_info.time,
            created_at=datetime.now()
        )
        
        await bookings_col.insert_one(record.model_dump())
        
        return BookingResponse(
            booking_id=booking_id,
            message="Interview booking successfully captured and verified!",
            booking_details=booking_info,
            created_at=datetime.now()
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")