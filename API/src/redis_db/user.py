from .redis import redis_client as r
from ..models.user import PubRSA
import logging
import json

log = logging.getLogger("uvicorn.error")

async def set_user_rsa(uid: str, key: PubRSA):
    log.debug("[REDIS] Writing RSA for UID: %s: %s", uid, key.model_dump_json(indent=None))
    return await r.hset(f"user:{uid}", mapping={
        "type": "RSA",
        "public_key": key.public_key
    })

async def get_user_rsa(uid: str):
    log.debug("[REDIS] Getting RSA for UID: %s", uid)
    data =  await r.hgetall(f"user:{uid}")
    log.debug("[REDIS] Got RSA for UID: %s: %s", uid, json.dumps(data, indent=None))
    
    if not data:
        return None
    
    return PubRSA(public_key=data["public_key"])
