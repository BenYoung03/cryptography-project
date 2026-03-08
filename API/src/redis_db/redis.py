import redis.asyncio as redis

redis_client = redis.Redis(
    host="redis", ## Docker Container name (docker-network will resolve)
    port=6379, ## Redis port
    decode_responses=True
)
