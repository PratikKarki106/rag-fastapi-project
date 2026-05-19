# app/services/document_service.py
import PyPDF2
from typing import Dict, List
import os
from pathlib import Path
import uuid
from datetime import datetime
from app.config.settings import settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.utils.database import get_documents_collection, get_chunks_collection
from app.models.database import DocumentMetadata, ChunkMetadata
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            raise
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type == ".pdf":
            return DocumentService.extract_text_from_pdf(file_path)
        elif file_type == ".txt":
            return DocumentService.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    async def process_document(
        file_path: str,
        filename: str,
        file_size: int,
        chunking_strategy: str = "fixed",
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> Dict:
        """
        Main document processing pipeline:
        1. Extract text
        2. Chunk text
        3. Generate embeddings
        4. Store in vector DB
        5. Save metadata to MongoDB
        """
        document_id = str(uuid.uuid4())
        file_type = Path(filename).suffix.lower()
        
        logger.info(f"Processing document: {filename} (ID: {document_id})")
        
        # Step 1: Extract text
        text = DocumentService.extract_text(file_path, file_type)
        logger.info(f"Extracted {len(text)} characters from {filename}")
        
        # Step 2: Chunk text
        chunks = ChunkingService.chunk_text(
            text,
            strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        logger.info(f"Created {len(chunks)} chunks using {chunking_strategy} strategy")
        
        # Step 3: Generate embeddings for all chunks
        chunk_texts = [chunk['chunk_text'] for chunk in chunks]
        embeddings = EmbeddingService.generate_embeddings_batch(chunk_texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Step 4: Prepare payloads for vector DB
        payloads = []
        for i, chunk in enumerate(chunks):
            payloads.append({
                "document_id": document_id,
                "chunk_index": chunk['chunk_index'],
                "chunk_text": chunk['chunk_text'],
                "filename": filename
            })
        
        # Store in Qdrant
        vector_ids = VectorService.add_vectors(embeddings, payloads)
        logger.info(f"Stored {len(vector_ids)} vectors in Qdrant")
        
        # Step 5: Save metadata to MongoDB
        documents_col = await get_documents_collection()
        chunks_col = await get_chunks_collection()
        
        # Save document metadata
        doc_metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            total_chunks=len(chunks),
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
            uploaded_at=datetime.now()
        )
        await documents_col.insert_one(doc_metadata.model_dump())
        logger.info(f"Saved document metadata to MongoDB")
        
        # Save chunk metadata
        chunk_records = []
        for i, (chunk, vector_id) in enumerate(zip(chunks, vector_ids)):
            chunk_metadata = ChunkMetadata(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_index=chunk['chunk_index'],
                chunk_text=chunk['chunk_text'],
                chunk_size=chunk['chunk_size'],
                vector_id=vector_id,
                created_at=datetime.now()
            )
            chunk_records.append(chunk_metadata.model_dump())
        
        await chunks_col.insert_many(chunk_records)
        logger.info(f"Saved {len(chunk_records)} chunk records to MongoDB")
        
        return {
            "document_id": document_id,
            "filename": filename,
            "total_chunks": len(chunks),
            "chunking_strategy": chunking_strategy,
            "message": "Document processed successfully"
        }