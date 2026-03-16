from .redis import redis_client as r
from ..models.user import PubRSA

async def set_user_rsa(uid: str, key: PubRSA):
    return await r.hset(f"user:{uid}", mapping={
        "type": "RSA",
        "e": key.e,
        "n": key.n
    })

async def get_user_rsa(uid: str):
    data =  await r.hget(f"user:{uid}", "public_key")
    
    if not data:
        return None
    
    return PubRSA(e=data["e"], n=data["n"])
