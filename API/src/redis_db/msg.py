from ..models.msg import Msg, Update
from .redis import redis_client as r
import uuid
import time


async def write_msg(msg: str):
    await r.set("msg", msg)

async def read_msg():
    return await r.get("msg")

async def get_msg_recipients(msg_id: str):
    return True

async def update_message_status(update: Update):
    ts = time.time()
    if update.status == "read" or update.status == "deleted":
        await r.hset()
    else: 
        await r.hset(f"msg:{update.msg_id}", "status", update.status, "server_timestamp", ts)

async def store_message(msg: Msg):
    ts = time.time() ## ADD SERVER TIMESTAMP HERE
    
    await r.hset(
        f"msg:{msg.msg_id}",
        mapping={
            "sender_uid": msg.sender_uid,
            "recipient_uid": msg.recipient_uid,

            "ciphertext": msg.ciphertext.ciphertext,
            "iv": msg.ciphertext.IV,
            "tag": msg.ciphertext.tag or "",

            "hmac": msg.hmac.string,

            "status": msg.status.value,

            "timestamp": msg.timestamp,
            "ttl": msg.ttl,
            "server_timestamp": ts
        },
    )

    await r.zadd(f"user_msgs:{msg.sender_id}", {msg.msg_id: ts})
    await r.zadd(f"user_msgs:{msg.receiver_id}", {msg.msg_id: ts})

    return msg.msg_id
