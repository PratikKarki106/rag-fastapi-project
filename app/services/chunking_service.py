# app/services/chunking_service.py
from typing import List, Dict
import re
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ChunkingService:
    
    @staticmethod
    def fixed_size_chunking(
        text: str, 
        chunk_size: int = None, 
        chunk_overlap: int = None
    ) -> List[Dict[str, any]]:
        """
        Strategy 1: Fixed-size chunking with overlap
        Splits text into chunks of fixed character length
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0
        
        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Don't create empty chunks
            if chunk_text.strip():
                chunks.append({
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text.strip(),
                    "start_char": start,
                    "end_char": end,
                    "chunk_size": len(chunk_text)
                })
                chunk_index += 1
            
            start = end - chunk_overlap
        
        logger.info(f"Fixed chunking: Created {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def semantic_chunking(
        text: str, 
        chunk_size: int = None, 
        chunk_overlap: int = None
    ) -> List[Dict[str, any]]:
        """
        Strategy 2: Semantic chunking (sentence-aware)
        Splits text at sentence boundaries, respecting meaning
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_size + sentence_len > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text.strip(),
                    "sentence_count": len(current_chunk),
                    "chunk_size": len(chunk_text)
                })
                chunk_index += 1
                
                # Keep last few sentences for overlap (semantic continuity)
                overlap_sentences = []
                overlap_size = 0
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_len
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "chunk_index": chunk_index,
                "chunk_text": chunk_text.strip(),
                "sentence_count": len(current_chunk),
                "chunk_size": len(chunk_text)
            })
        
        logger.info(f"Semantic chunking: Created {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def chunk_text(text: str, strategy: str = "fixed", **kwargs) -> List[Dict[str, any]]:
        """
        Main chunking method - routes to appropriate strategy
        """
        if strategy == "fixed":
            return ChunkingService.fixed_size_chunking(text, **kwargs)
        elif strategy == "semantic":
            return ChunkingService.semantic_chunking(text, **kwargs)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")