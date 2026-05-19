import sys
print(f"Python version: {sys.version}")

try:
    import fastapi
    print("✅ FastAPI installed")
except:
    print("❌ FastAPI not installed")

try:
    import groq
    print("✅ Groq installed")
except:
    print("❌ Groq not installed")

try:
    import pymongo
    print("✅ PyMongo installed")
except:
    print("❌ PyMongo not installed")

try:
    import redis
    print("✅ Redis installed")
except:
    print("❌ Redis not installed")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ Sentence Transformers installed")
except Exception as e:
    print("❌ Sentence Transformers error:")
    print(e)

try:
    from qdrant_client import QdrantClient
    print("✅ Qdrant Client installed")
except:
    print("❌ Qdrant Client not installed")

print("\n🎉 Setup verification complete!")