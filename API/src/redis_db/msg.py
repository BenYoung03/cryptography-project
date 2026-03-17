from ..models.msg import Msg, Update, Status, CipherText, Key
from .redis import redis_client as r
import time
import logging
import json

log = logging.getLogger("uvicorn.error")

async def get_msg_recipient(msg_id: str):
    return await r.hget(f"msg:{msg_id}", "recipient_uid")

async def update_message_status(update: Update):
    ts = time.time()
    msg: Msg
    msg = await get_message(update.msg_id)

    res = -1
    if msg.status==Status.DELETED: 
        res = await null_message(update.msg_id, ts)
    elif update.status.value<=msg.status.value:
        ##return res 
        pass
        
    else:
        res = await r.hset(
            f"msg:{update.msg_id}", 
            mapping={
                "status": update.status.value, 
                "server_timestamp": ts
            }
        )
    
    await r.zadd(f"user_updates:{msg.recipient_uid}", {update.msg_id: ts})
    await r.zadd(f"user_updates:{msg.sender_uid}", {update.msg_id: ts})

    return res

async def null_message(msg_id, ts = time.time()):
    return await r.hset(
        f"msg:{msg_id}",
        mapping={
            "recipient_uid": "",

            "ciphertext": "",
            "iv": "",
            "tag": "",

            "status": Status.DELETED.value,

            "timestamp": "",
            "ttl": "",
            "server_timestamp": ts
        },
    )

async def store_message(msg: Msg):
    log.debug("[REDIS] storing MSG_ID: %s, from UID: %s, to UID: %s", msg.msg_id, msg.sender_uid, msg.recipient_uid)
    ts = time.time() ## ADD SERVER TIMESTAMP HERE
    
    res = await r.hset(
        f"msg:{msg.msg_id}",
        mapping={
            "msg_id": msg.msg_id,
            "sender_uid": msg.sender_uid or "",
            "recipient_uid": msg.recipient_uid or "",

            "ciphertext": msg.ciphertext.ciphertext or "",
            "IV": msg.ciphertext.IV or "",
            "tag": msg.ciphertext.tag or "",

            "algorithm": msg.key.algorithm or "",
            "encrypted_key": msg.key.encrypted_key or "",

            "status": msg.status.value or 0,

            "timestamp": msg.timestamp or 0,
            "ttl": msg.ttl or 0,
            "server_timestamp": ts
        },
    )

    await r.zadd(f"user_msgs:{msg.sender_uid}", {msg.msg_id: ts})
    await r.zadd(f"user_msgs:{msg.recipient_uid}", {msg.msg_id: ts})

    log.debug("[REDIS] SUCCESS stored MSG_ID: %s", msg.msg_id)
    return res

async def get_message(msg_id: str) -> Msg:
    log.debug("[REDIS] getting MSG_ID: %s", msg_id)
    data = await r.hgetall(f"msg:{msg_id}")

    if not data:
        raise LookupError(f"Could not find MSG_ID: {msg_id}")
    
    msg = Msg(
        msg_id=data["msg_id"],
        sender_uid=data["sender_uid"],
        recipient_uid=data["recipient_uid"],
        ciphertext=CipherText(
            ciphertext=data["ciphertext"], 
            IV=data["IV"], 
            tag=data["tag"]
        ),
        key=Key(
            algorithm=data["algorithm"], 
            encrypted_key=data["encrypted_key"]
        ),
        status=Status(int(data["status"])),
        timestamp=data["status"],
        ttl=int(data["ttl"]),
        server_timestamp=int(float(data["server_timestamp"])) or None
    )
    log.debug("[REDIS] SUCCESS retrieved MSG_ID: %s:\n%s", msg_id, msg.model_dump_json(indent=2))
    return msg

async def get_status(msg_id: str) -> Update:
    log.debug("[REDIS] getting MSG_ID: %s status", msg_id)
    status = await r.hget(f"msg:{msg_id}", "status")

    if not status:
        log.debug("[REDIS] FAIL getting MSG_ID: %s status", msg_id)
        raise LookupError(f"Could not find status for MID: {msg_id}")
    
    log.debug("[REDIS] SUCCESS MSG_ID: %s status, Status: %s", msg_id, status)
    return Update(msg_id=msg_id, status=Status(int(status)))

async def get_routing(msg_id: str): 
    log.debug("[REDIS] getting MSG_ID: %s ROUTING", msg_id)
    routing = await r.hmget(f"msg:{msg_id}", "sender_uid", "recipient_uid")
    if not routing:
        raise LookupError(f"Can't find MID: {msg_id}")
    
    log.debug("[REDIS] SUCCESS got MSG_ID: %s ROUTING: %s", msg_id, json.dumps(routing, indent=None))
    return routing

async def get_messages_since(uid: str, ts: int):
    msg_ids = await r.zrangebyscore(
        f"user_msgs:{uid}",
        ts,
        "+inf"
    )

    messages = []

    for mid in msg_ids:
        try:
            msg = await get_message(mid)
            if msg: 
                messages.append(msg.model_dump_json())
            else:
                await r.zrem(f"user_msgs:{uid}", mid)
        except LookupError:
            await r.zrem(f"user_msgs:{uid}", mid)
        except ValueError:
            await r.zrem(f"user_msgs:{uid}", mid)

    return messages

async def get_updates_since(uid: str, ts: int):
    msg_ids = await r.zrangebyscore(
        f"user_updates:{uid}",
        ts,
        "+inf"
    )

    updates = []
    for mid in msg_ids:
        try:
            status = await get_status(mid)
            if status:
                updates.append(status.model_dump_json())
            else:
                await r.zrem(f"user_msgs:{uid}", mid)
        except:
            await r.zrem(f"user_msgs:{uid}", mid)

    return updates
