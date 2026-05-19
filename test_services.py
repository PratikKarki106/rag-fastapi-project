# test_services.py
import asyncio
from app.services.embedding_service import EmbeddingService
from app.services.chunking_service import ChunkingService
from app.services.vector_service import VectorService

def test_embedding_service():
    print("\n=== Testing Embedding Service ===")
    
    # Test single embedding
    text = "This is a test sentence."
    embedding = EmbeddingService.generate_embedding(text)
    print(f"✅ Generated embedding of dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test batch embeddings
    texts = ["First sentence.", "Second sentence.", "Third sentence."]
    embeddings = EmbeddingService.generate_embeddings_batch(texts)
    print(f"✅ Generated {len(embeddings)} embeddings in batch")

def test_chunking_service():
    print("\n=== Testing Chunking Service ===")
    
    sample_text = """
    Natural language processing (NLP) is a subfield of linguistics, computer science, 
    and artificial intelligence concerned with the interactions between computers and human language.
    It focuses on how to program computers to process and analyze large amounts of natural language data.
    The goal is a computer capable of understanding the contents of documents, including the contextual 
    nuances of the language within them.
    """
    
    # Test fixed chunking
    fixed_chunks = ChunkingService.fixed_size_chunking(sample_text, chunk_size=100, chunk_overlap=20)
    print(f"✅ Fixed chunking: {len(fixed_chunks)} chunks")
    print(f"   First chunk: {fixed_chunks[0]['chunk_text'][:50]}...")
    
    # Test semantic chunking
    semantic_chunks = ChunkingService.semantic_chunking(sample_text, chunk_size=150, chunk_overlap=30)
    print(f"✅ Semantic chunking: {len(semantic_chunks)} chunks")
    print(f"   First chunk: {semantic_chunks[0]['chunk_text'][:50]}...")

def test_vector_service():
    print("\n=== Testing Vector Service ===")
    
    # Initialize
    client = VectorService.get_client()
    print("✅ Vector service initialized")
    
    # Create test vectors
    texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Python is a popular programming language for data science."
    ]
    
    embeddings = EmbeddingService.generate_embeddings_batch(texts)
    
    # Add to vector DB
    payloads = [
        {"text": texts[0], "document_id": "test_doc_1", "chunk_index": 0},
        {"text": texts[1], "document_id": "test_doc_1", "chunk_index": 1},
        {"text": texts[2], "document_id": "test_doc_2", "chunk_index": 0},
    ]
    
    vector_ids = VectorService.add_vectors(embeddings, payloads)
    print(f"✅ Added {len(vector_ids)} vectors to Qdrant")
    
    # Search similar
    query = "What is AI and machine learning?"
    query_embedding = EmbeddingService.generate_embedding(query)
    results = VectorService.search_similar(query_embedding, top_k=2)
    
    print(f"✅ Search results for: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['score']:.4f} - {result['payload']['text'][:60]}...")

def main():
    print("🚀 Testing AI Services...\n")
    
    test_embedding_service()
    test_chunking_service()
    test_vector_service()
    
    print("\n🎉 All service tests complete!")

if __name__ == "__main__":
    main()