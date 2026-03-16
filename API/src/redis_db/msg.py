from ..models.msg import Msg, Update, Status, CipherText, Key
from .redis import redis_client as r
import time

async def get_msg_recipient(msg_id: str):
    return await r.hget(f"msg:{msg_id}", "recipient_uid")

async def update_message_status(update: Update):
    ts = time.time()
    msg = r.hgetall(f"msg:{update.msg_id}")
    cur_status = msg["status"]
    sender = msg["sender_id"]

    res = -1
    if cur_status==Status.DELETED.value: 
        res = await null_message(update.msg_id, ts)
    elif update.status.value<=int(cur_status):
        return res
    else:
        res = await r.hset(
            f"msg:{update.msg_id}", 
            mapping={
                "status": update.status.value, 
                "server_timestamp": ts
            }
        )
    await r.zadd(f"user_msgs:{sender}", {update.msg_id: ts})

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
    ts = time.time() ## ADD SERVER TIMESTAMP HERE
    
    res = await r.hset(
        f"msg:{msg.msg_id}",
        mapping={
            "sender_uid": msg.sender_uid,
            "recipient_uid": msg.recipient_uid,

            "ciphertext": msg.ciphertext.ciphertext,
            "iv": msg.ciphertext.IV,
            "tag": msg.ciphertext.tag or "",

            "algorithm": msg.key.algorithm,
            "encrypted_key": msg.key.encrypted_key,

            "status": msg.status.value,

            "timestamp": msg.timestamp,
            "ttl": msg.ttl,
            "server_timestamp": ts
        },
    )

    await r.zadd(f"user_msgs:{msg.sender_id}", {msg.msg_id: ts})
    await r.zadd(f"user_msgs:{msg.receiver_id}", {msg.msg_id: ts})

    return res

async def get_message(msg_id: str) -> Msg | None:
    data = await r.hgetall(f"msg:{msg_id}")

    if not data:
        return None
    
    return Msg(
        msg_id=data["msg_id"],
        sender_uid=data["sender_uid"],
        recipient_uid=data["recipient_uid"],
        ciphertext=CipherText(
            ciphertext=data["ciphertext"],
            IV=data["iv"],
            tag=data["tag"] or None
        ),
        key=Key(
            algorithm=data["algorithm"],
            encrypted_key=data["key"]
        ),
        status=Status(data["status"]),
        timestamp=int(data["timestamp"]),
        ttl=data["ttl"],
        server_timestamp=int(data["server_timestamp"])
    )

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
