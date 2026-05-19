# 🤖 Custom Conversational RAG Backend with Automated Interview Booking

A production-grade, asynchronous **Retrieval-Augmented Generation (RAG)** system built from scratch using **FastAPI**. This backend implements custom document ingestion, dual chunking strategies, multi-turn conversational memory, vector-based semantic search, and intelligent interview booking extraction—**without relying on pre-built RAG frameworks** like LangChain or LlamaIndex.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

This system demonstrates enterprise-level RAG architecture with:
- ✅ **Custom RAG Pipeline**: No `RetrievalQAChain` or similar abstractions
- ✅ **Dual Chunking Strategies**: Fixed-size and semantic sentence-aware chunking
- ✅ **Multi-turn Conversations**: Redis-backed chat memory for context-aware responses
- ✅ **Intelligent Intent Detection**: LLM-powered interview booking extraction with structured data validation
- ✅ **Industry-Standard Code**: Full type annotations, async/await patterns, and modular service architecture

Built as a technical assessment for **Palm Mind AI**.

---

## 🏗️ System Architecture

**Document Ingestion Pipeline**                    
PDF/TXT Upload & Validation                   
  ├─Text Extraction (PyPDF2)                      
  ├─ Dual Chunking (Fixed-Size / Semantic)         
  ├─ Embedding Generation (SentenceTransformers)   
  └─ Vector Storage (Qdrant) + Metadata (MongoDB)  
                                                   
**Conversational RAG Engine**                      
  ├─ Query Vectorization                           
  ├─ Semantic Search (Cosine Similarity - Qdrant)  
  ├─ Context Retrieval & Ranking                   
  ├─ LLM Response Generation (Groq API)            
  └─ Session Management (Redis Cloud)              
                                                                 
**Interview Booking System**                                     
  ├─ Intent Detection (LLM-based)                                
  ├─ Structured Data Extraction                                  
  ├─ Pydantic Validation                                         
  └─ Booking Record Persistence (MongoDB)                        

↓&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;↓&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;↓<br>
🗄️ Qdrant    &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;      💾 MongoDB     &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp; &ensp;     🔴 Redis <br>
(Vector Search) &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;     (Metadata)    &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;     (Session Cache)
---

## 🚀 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | Async REST API with automatic OpenAPI documentation |
| **LLM** | Groq API (`llama-3.3-70b-versatile`) | Response generation & intent extraction |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) | Local 384-dimensional vector generation |
| **Vector DB** | Qdrant (In-Memory) | Semantic search with cosine similarity |
| **Database** | MongoDB (Motor async driver) | Document & booking metadata storage |
| **Cache** | Redis Cloud | Multi-turn conversation memory (1-hour TTL) |
| **Validation** | Pydantic v2 | Type-safe request/response schemas |
| **PDF Processing** | PyPDF2 | Text extraction from PDF documents |
| **HTTP Server** | Uvicorn | ASGI server for FastAPI |

---

## ✨ Key Features

### 1. 📄 Document Ingestion API
**Endpoint:** `POST /api/v1/ingest/upload`

- Accepts PDF and TXT files (up to 10MB)
- **Two chunking strategies:**
  - **Fixed-size**: Character-based chunks with configurable overlap
  - **Semantic**: Sentence-aware chunking for better context preservation
- Generates embeddings using local SentenceTransformers model
- Stores vectors in Qdrant with metadata in MongoDB
- Returns processing status with unique document ID

---

### 2. 💬 Conversational RAG API
**Endpoint:** `POST /api/v1/chat/query`

- Custom RAG implementation (no pre-built chains)
- Multi-turn conversation support with Redis memory
- Top-K semantic retrieval from vector database
- Context-aware responses using retrieved document chunks
- Returns source references with similarity scores

---

### 3. 📅 Interview Booking System
**Endpoint:** `POST /api/v1/chat/book`

- LLM-powered intent detection and extraction
- Structured data parsing (name, email, date, time)
- Automatic Pydantic validation
- Persistent storage in MongoDB

---

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.10+**
- **MongoDB** (local or cloud)
- **Redis** (local or cloud)
- **Groq API Key** (free tier available at [console.groq.com](https://console.groq.com/))

---

### Step 5: Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Base:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`
- **Alternative Docs:** `http://localhost:8000/redoc`

---

## 📊 API Documentation

### Document Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest/upload` | Upload and process PDF/TXT documents |
| `GET` | `/api/v1/ingest/documents` | List all uploaded documents |
| `GET` | `/api/v1/ingest/documents/{document_id}` | Get document details and chunks |

### Conversational RAG Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/query` | Ask questions about uploaded documents |
| `POST` | `/api/v1/chat/book` | Extract and book interview details |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status and health check |

---

## 🎯 Design Decisions

### Why No LangChain/LlamaIndex?

- **Deep Understanding**: Building from scratch demonstrates comprehensive knowledge of RAG principles
- **Full Control**: Complete control over chunking, retrieval, and generation strategies
- **Performance**: Optimized for specific use case without framework overhead
- **Transparency**: Clear separation of concerns and explicit data flow
- **Learning**: Better understanding of underlying mechanisms

### Why These Technologies?

**FastAPI**
- Best-in-class async performance
- Automatic OpenAPI documentation
- Native Pydantic integration
- Type safety and validation

**Qdrant**
- Efficient vector similarity search
- Flexible filtering capabilities
- Easy to deploy (in-memory or server mode)
- Good documentation

**MongoDB**
- Schema flexibility for metadata
- Excellent async driver (Motor)
- Easy to scale
- Document-oriented storage matches our needs

**Redis**
- Ultra-fast in-memory storage
- Perfect for session management
- Simple key-value operations
- TTL support for auto-expiring sessions

**Groq**
- Free tier available
- Fast inference
- Good model quality
- Simple API

---

## 📈 Performance Characteristics

- **Embedding Generation**: ~100ms for batch of 10 chunks (local)
- **Vector Search**: <50ms for top-K retrieval (in-memory Qdrant)
- **LLM Response**: 1-3 seconds (Groq API dependent)
- **End-to-End Query**: 2-4 seconds (including retrieval + generation)
- **Document Processing**: ~2-5 seconds per PDF (depends on size)

---

## 🔒 Security Features

- ✅ File type validation (PDF, TXT only)
- ✅ File size limits (10MB max)
- ✅ Input validation using Pydantic models
- ✅ API key management via environment variables
- ✅ Async operations prevent blocking attacks
- ✅ No SQL injection (MongoDB parameterized queries)
- ✅ Email validation for booking system

---

## 🧩 Core Components Explained

### Chunking Strategies

**1. Fixed-Size Chunking:**
- Splits text by character count
- Configurable overlap for context preservation
- Fast and predictable
- Best for: Uniform documents

**2. Semantic Chunking:**
- Splits at sentence boundaries
- Preserves semantic meaning
- Better context preservation
- Best for: Narrative documents

### RAG Pipeline
User Query<br>
↓<br>
Generate query embedding (SentenceTransformers)<br>
↓<br>
Search similar vectors (Qdrant - Cosine Similarity)<br>
↓<br>
Retrieve top-K chunks with metadata<br>
↓<br>
Fetch conversation history (Redis)<br>
↓<br>
Build context + history prompt<br>
↓<br>
Generate response (Groq LLM)<br>
↓<br>
Save conversation turn (Redis)<br>
↓<br>
Response to User<br>

### Session Management

- Each conversation has a unique `session_id`
- Chat history stored in Redis with 1-hour TTL
- Last 10 messages retrieved for context
- Automatic cleanup after expiry

---

## 🚧 Future Enhancements

### High Priority
- Add user authentication & authorization (JWT)
- Implement rate limiting (per user/IP)
- Add comprehensive logging (structlog)
- Unit & integration tests (pytest)

### Medium Priority
- Support more file types (DOCX, CSV, JSON)
- Document versioning system
- Hybrid search (keyword + semantic)
- Advanced chunking strategies (recursive, custom)

### Low Priority
- Monitoring & observability (Prometheus/Grafana)
- Docker containerization
- Kubernetes deployment manifests
- CI/CD pipeline (GitHub Actions)
- Admin dashboard UI

---

## 🐛 Limitations

- In-memory Qdrant loses data on restart (use persistent mode for production)
- Redis TTL means old conversations expire (increase if needed)
- Single LLM provider (Groq) - no fallback
- No built-in authentication
- Limited to 10MB file uploads

---

## 📚 Learning Resources

If you want to understand the concepts better:

- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Vector Databases](https://www.pinecone.io/learn/vector-database/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Sentence Transformers](https://www.sbert.net/)

---

## 🤝 Contributing

This project is a technical assessment and not open for contributions. However, feedback is welcome!

---

## 👤 Author

**Pratik Karki**

- 📧 Email: karkipratik063@gmail.com
- 💼 LinkedIn: [[LinkedIn](https://www.linkedin.com/in/pratik-karki-a90801362/)]
- 🐙 GitHub: [[GitHub](https://github.com/PratikKarki106)]

---

## 📝 License

This project is created as part of a technical assessment for **Palm Mind AI**.

---

## 🙏 Acknowledgments

- Built as a technical assessment for **Palm Mind AI**
- Demonstrates production-ready RAG system architecture
- Implements industry best practices for async Python backends
- Special thanks to the FastAPI, Qdrant, and Groq teams for excellent documentation

---

For questions or issues, please contact: karkipratik063@gmail.com