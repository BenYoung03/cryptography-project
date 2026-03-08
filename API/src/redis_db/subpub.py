from .redis import redis_client as r
from ..websocket.manager import ConnectionManager
import json

manager: ConnectionManager = None

def init_manager(m: ConnectionManager):
    global manager
    manager = m

async def redis_listener():
    pubsub = r.pubsub()

    await pubsub.subscribe("ws_events")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        data = json.loads(message["data"])
        uid = data["recipient_uid"]

        await manager.send_to_user(uid, data)
