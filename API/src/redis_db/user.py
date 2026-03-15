from .redis import redis_client as r

async def set_user_public_key(uid: str, key: str):
    await r.hset(f"user:{uid}", "public_key", key)

async def get_user_public_key(uid: str):
    return await r.hget(f"user:{uid}", "public_key")
