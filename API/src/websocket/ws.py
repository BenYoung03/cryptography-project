from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging

## Backend Managers and DB
from ..redis_db.redis import redis_client as r
from ..redis_db import msg as msgCRUD
from .manager import ConnectionManager

## Data Models
from ..models.ws import wsMessage, wsError
from ..models.msg import Msg, Update, Status
from ..models.redisEvents import RedisEvent

## utility functions
from ..utils.ulid import generate_id
from ..middleware.auth import get_uid

router = APIRouter()
manager = ConnectionManager()

log = logging.getLogger("uvicorn.error")
log.setLevel(logging.DEBUG)

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    uid = ws.state.uid
    await manager.connect(ws, uid) ## add connection to manager

    try:
        while True:
            try:
                data = await ws.receive_json()
                
                message = wsMessage(
                    type=data["type"],
                    payload=data["payload"]
                )
            except:
                await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                    error_type="invalid-format", 
                    error_msg="wsMessage has an invalid format"
                )))
                continue

            log.debug("[WS] ws payload: %s", message.payload.model_dump_json(indent=2))


            if message.type == "msg":
                message.payload.msg_id = generate_id("m")
                message.payload.status = Status.READ
                """try:
                    message.payload = Msg(**message.payload)
                except Exception as e:
                    log.debug("[WS] error parsing %s", repr(e))
                    await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                        error_type="invalid-format", 
                        error_msg="message payload has an invalid format"
                    )))
                    continue"""

                await msgCRUD.store_message(message.payload)

            elif message.type == "update":
                """try:
                    message.payload = Update(**message.payload)
                except:
                    await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                        error_type="invalid-format", 
                        error_msg="message payload has an invalid format"
                    )))
                    continue"""

                if await msgCRUD.get_msg_recipient(message.payload.msg_id) != uid: 
                    await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                        error_type="no-access", 
                        error_msg="message does not belong to client"
                    )))
                    continue

                if await msgCRUD.update_message_status(message.payload) == -1:
                    await manager.send_to_user(uid, wsMessage("error", payload=wsError(
                        error_type="invalid-update", 
                        error_msg="Attempted update not valid for message state"
                    )))
                    continue

            await r.publish(
                "ws_events",
                RedisEvent(type=message.type, msg_id=message.payload.msg_id).model_dump_json()
            )
        
    finally:
        await manager.disconnect(uid)
