import redis
import os

# Redis connection configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# In-memory fallback for development without Redis
memory_blacklist = set()

try:
    if os.getenv("USE_REDIS", "False").lower() == "true":
        redis_client = redis.StrictRedis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=REDIS_DB, 
            decode_responses=True,
            socket_connect_timeout=1
        )
        # Test connection immediately
        redis_client.ping()
        print("[SYSTEM] Connected to Redis Blacklist.")
    else:
        redis_client = None
except Exception:
    print("[WARNING] Redis connection failed or not configured. Falling back to in-memory blacklist.")
    redis_client = None

def blacklist_jti(jti, expiration=3600):
    """Adds a JTI to the blacklist."""
    if redis_client:
        try:
            redis_client.setex(f"blacklist:{jti}", expiration, "true")
            return True
        except Exception:
            pass
    
    memory_blacklist.add(jti)
    return True

def is_jti_blacklisted(jti):

    """Checks if a JTI is present in the blacklist."""

    if redis_client:

        try:

            if redis_client.exists(f"blacklist:{jti}"):

                return True

        except Exception as e:

            print(f"[WARNING] Redis check failed: {e}. Falling back to memory check.")

            

    return jti in memory_blacklist
