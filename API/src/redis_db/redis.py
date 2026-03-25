import redis.asyncio as redis

## JUST THE REDIS CONNECTION OBJECT
redis_client = redis.Redis(
    host="redis", ## Docker Container name (docker-network will resolve)
    port=6379, ## Redis port
    decode_responses=True
)
