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
    msg = get_message(update.msg_id)

    res = -1
    if msg.status.value==Status.DELETED.value: 
        res = await null_message(update.msg_id, ts)
    elif update.status.value<=msg.status.value:
        return res
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
            "sender_uid": msg.sender_uid,
            "recipient_uid": msg.recipient_uid,

            "ciphertext": msg.ciphertext.ciphertext,
            "IV": msg.ciphertext.IV,
            "tag": msg.ciphertext.tag or "",

            "algorithm": msg.key.algorithm,
            "encrypted_key": msg.key.encrypted_key,

            "status": msg.status.value,

            "timestamp": msg.timestamp,
            "ttl": msg.ttl,
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
        timestamp=int(data["timestamp"]),
        ttl=int(data["ttl"]),
        server_timestamp=int(float(data["server_timestamp"])) or None
    )
    log.debug("[REDIS] SUCCESS retrieved MSG_ID: %s:\n%s", msg_id, msg.model_dump_json(indent=2))
    return msg

async def get_status(msg_id: str) -> Update | None:
    log.debug("[REDIS] getting MSG_ID: %s status", msg_id)
    status = await r.hget(f"msg:{msg_id}")

    if not status:
        log.debug("[REDIS] FAIL getting MSG_ID: %s status", msg_id)
        return None
    
    log.debug("[REDIS] SUCCESS MSG_ID: %s status", msg_id)
    return Update(msg_id=msg_id, status=status)

async def get_messages_since(uid: str, ts: int):
    msg_ids = await r.zrangebyscore(
        f"user_msgs:{uid}",
        ts,
        "+inf"
    )

    messages = []

    for mid in msg_ids:
        msg = get_message(mid)
        if msg:
            messages.append(msg)

    return messages

async def get_updates_since(uid: str, ts: int):
    msg_ids = await r.zrangebyscore(
        f"user_updates:{uid}",
        ts,
        "+inf"
    )

    updates = []
    for mid in msg_ids:
        status = get_status(mid)
        if status:
            updates.append(status)

    return updates
