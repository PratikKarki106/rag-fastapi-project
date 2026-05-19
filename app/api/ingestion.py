# app/api/ingestion.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import DocumentUploadResponse, ChunkingStrategy
from app.services.document_service import DocumentService
from app.utils.file_utils import validate_file, save_upload_file
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ingest", tags=["Document Ingestion"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF or TXT file to upload"),
    chunking_strategy: str = Form("fixed", description="Chunking strategy: 'fixed' or 'semantic'"),
    chunk_size: int = Form(500, description="Size of each chunk (characters)"),
    chunk_overlap: int = Form(50, description="Overlap between chunks (characters)")
):
    """
    Upload and process a document (PDF or TXT)
    
    - **file**: The document file to upload
    - **chunking_strategy**: Choose 'fixed' or 'semantic' chunking
    - **chunk_size**: Number of characters per chunk
    - **chunk_overlap**: Number of overlapping characters between chunks
    
    Returns document metadata and processing status
    """
    try:
        # Validate file type
        validate_file(file)
        
        # Save file
        file_path, file_size = await save_upload_file(file)
        logger.info(f"Saved file: {file.filename} ({file_size} bytes)")
        
        # Process document
        result = await DocumentService.process_document(
            file_path=file_path,
            filename=file.filename,
            file_size=file_size,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return DocumentUploadResponse(
            document_id=result['document_id'],
            filename=result['filename'],
            total_chunks=result['total_chunks'],
            chunking_strategy=result['chunking_strategy'],
            message=result['message'],
            uploaded_at=datetime.now()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        from app.utils.database import get_documents_collection
        documents_col = await get_documents_collection()
        
        documents = await documents_col.find().sort("uploaded_at", -1).to_list(length=100)
        
        # Convert ObjectId to string
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        
        return {
            "total": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(document_id: str):
    """Get details of a specific document"""
    try:
        from app.utils.database import get_documents_collection, get_chunks_collection
        
        documents_col = await get_documents_collection()
        chunks_col = await get_chunks_collection()
        
        # Get document
        document = await documents_col.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks
        chunks = await chunks_col.find({"document_id": document_id}).to_list(length=1000)
        
        document['_id'] = str(document['_id'])
        for chunk in chunks:
            chunk['_id'] = str(chunk['_id'])
        
        return {
            "document": document,
            "chunks": chunks
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))