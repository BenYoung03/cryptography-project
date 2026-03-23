from .redis import redis_client as r
from ..websocket.manager import ConnectionManager
from .msg import get_message, get_status, get_routing
from ..models.redisEvents import RedisEvent, EventType
from ..models.ws import wsMessage, wsType
from ..models.msg import Msg, Update
import logging
import json
import asyncio

manager: ConnectionManager = None

log = logging.getLogger("uvicorn.error")
log.setLevel(logging.DEBUG)

def init_manager(m: ConnectionManager):
    global manager
    manager = m

async def redis_listener():
    pubsub = r.pubsub()

    await pubsub.subscribe("ws_events")

    log.debug("[REDIS-EVENT] pubsub is listening")

    try:
        async for data in pubsub.listen():
            try:
                event = RedisEvent(**json.loads(data["data"]))
            except Exception as e:
                # Normal for initial subscribe confirmation messages
                continue

            log.debug("[REDIS-EVENT] event posted %s", event.model_dump_json(indent=2))

            if event.type == EventType.NEW_MESSAGE:
                log.debug("[REDIS-EVENT] of type MSG")
                try:
                    msg = await get_message(event.msg_id)
                    if msg: 
                        log.debug("[REDIS-EVENT] Sending msg to UID: %s", msg.recipient_uid)
                        await manager.send_to_user(msg.recipient_uid, wsMessage(type=wsType.MSG, payload=msg))
                except Exception as e:
                    log.error("[REDIS-EVENT] failed to process MSG_ID: %s, error:\n%s", event.msg_id, repr(e))
                    continue
                
            elif event.type == EventType.STATUS_UPDATE:
                log.debug("[REDIS-EVENT] of type UPDATE")
                try:
                    update = await get_status(event.msg_id)
                    routing = await get_routing(event.msg_id)
                    
                    await asyncio.gather(
                        manager.send_to_user(routing[0], wsMessage(type=wsType.UPDATE, payload=update)),
                        manager.send_to_user(routing[1], wsMessage(type=wsType.UPDATE, payload=update))
                    )
                except Exception as e:
                    log.error("[REDIS-EVENT] update processing FAILED.\n[REDIS-EVENT] Error: %s", repr(e))
                    continue
                
            else:
                log.error("[REDIS-EVENT] INVALID TYPE")
                continue
    except Exception as e:
        log.critical("[REDIS-EVENT] FATAL LISTENER CRASH: %s", repr(e))
