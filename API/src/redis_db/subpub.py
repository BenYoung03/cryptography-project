from .redis import redis_client as r
from ..websocket.manager import ConnectionManager
from .msg import get_message, get_status
from ..models.redisEvents import RedisEvent, EventType
from ..models.ws import wsMessage
from ..models.msg import Msg, Update
import logging

manager: ConnectionManager = None

log = logging.getLogger("uvicorn.error")
log.setLevel(logging.DEBUG)

def init_manager(m: ConnectionManager):
    global manager
    manager = m

async def redis_listener():
    pubsub = r.pubsub()

    await pubsub.subscribe("ws_events")

    async for data in pubsub.listen():
        try:
            data = RedisEvent(**data)
        except: 
            continue

        log.debug("[REDIS] event posted %s", data.model_dump_json(indent=2))

        if data["type"] == EventType.NEW_MESSAGE.value:
            msg = get_message(data.msg_id)
            if not update: 
                continue
            
            log.debug("[REDIS] Sending msg to UID: %s", msg.recipient_uid)
            await manager.send_to_user(msg.recipient_uid, wsMessage(type=data.type, payload=msg))
            
        elif data["type"] == EventType.STATUS_UPDATE.value:
            update = get_status(data.msg_id)
            if not update: 
                continue


            log.debug("[REDIS] Sending update to UID: %s", msg.recipient_uid)

            await manager.send_to_user(update.sender_uid, wsMessage(type=data.type, payload=update))
            await manager.send_to_user(update.recipient_uid, wsMessage(type=data.type, payload=update))
            
        else:
            continue
