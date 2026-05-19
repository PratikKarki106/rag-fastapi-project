# test_redis.py
import redis
from dotenv import load_dotenv
import os

load_dotenv()

try:
    # Option 1: Using REDIS_URL (simpler)
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        r = redis.from_url(redis_url, decode_responses=True)
    else:
        # Option 2: Using individual parameters
        r = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True,
            ssl=True
        )
    
    r.ping()
    print("✅ Redis Cloud is connected!")
    
    # Test set/get
    r.set('test_key', 'Hello Redis Cloud!')
    value = r.get('test_key')
    print(f"✅ Redis test value: {value}")
    
    # Clean up
    r.delete('test_key')
    print("✅ Redis is ready for the project!")
    
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    print(f"\nRedis URL: {os.getenv('REDIS_URL')}")