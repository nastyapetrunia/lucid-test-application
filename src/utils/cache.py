import json
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_cached_posts(user_id: int):
    """Retrieve cached posts from Redis."""
    cached_data = redis_client.get(f"posts_cache_{user_id}")
    return json.loads(cached_data) if cached_data else None

def cache_posts(user_id: int, posts):
    """Cache posts for a user in Redis for 5 minutes."""
    redis_client.setex(f"posts_cache_{user_id}", 300, json.dumps(posts))
