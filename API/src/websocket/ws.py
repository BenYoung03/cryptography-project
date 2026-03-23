from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
import json

## Backend Managers and DB
from ..redis_db.redis import redis_client as r
from ..redis_db import msg as msgCRUD
from .manager import ConnectionManager

## Data Models
from ..models.ws import wsMessage, wsError, wsType, wsResponse
from ..models.msg import Msg, Update, Status
from ..models.redisEvents import RedisEvent

## utility functions
from ..utils.ulid import generate_id
from ..uauth.middleware import get_uid

router = APIRouter()
manager = ConnectionManager()

log = logging.getLogger("uvicorn.error")

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    uid = ws.state.uid
    await manager.connect(ws, uid) ## add connection to manager

    try:
        while True:
            try:
                data = await ws.receive_json()
                log.debug("[WS] recieved raw-data:\n%s", json.dumps(data, indent=2))
                
                message = wsMessage(
                    type=data["type"],
                    payload=None
                )

                if message.type == wsType.MSG:
                    message.payload = Msg(**data["payload"])
                elif message.type == wsType.UPDATE:
                    message.payload = Update(**data["payload"])
                else:
                    await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                        error_type="invalid-type",
                        error_msg=f"Server does not accept {message.type.value}"
                    )))
                    continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                await manager.send_to_user(uid, wsMessage(type="error", payload=wsError(
                    error_type="invalid-format", 
                    error_msg="wsMessage has an invalid format",
                    metadata={**e.__dict__, "error-string": repr(e)}
                )))
                continue

            log.debug("[WS] ws payload: %s", message.payload.model_dump_json(indent=2))


            if message.type == wsType.MSG:
                message.payload.msg_id = generate_id("m")
                message.payload.status = Status.SENT

                await msgCRUD.store_message(message.payload)
                await manager.send_to_user(uid, wsMessage(type=wsType.RESPONSE, payload=wsResponse(
                    msg_id=message.payload.msg_id, 
                    response_status="success", 
                    response_body="sent to recipient"
                )))

            elif message.type == wsType.UPDATE:
                if await msgCRUD.get_msg_recipient(message.payload.msg_id) != uid: 
                    await manager.send_to_user(uid, wsMessage(type=wsType.ERROR, payload=wsError(
                        error_type="no-access", 
                        error_msg="message does not belong to client"
                    )))
                    continue

                elif await msgCRUD.update_message_status(message.payload) == -1:
                    await manager.send_to_user(uid, wsMessage(type=wsType.ERROR, payload=wsError(
                        error_type="invalid-update", 
                        error_msg="Attempted update not valid for message status"
                    )))
                    continue
                
                else:
                    await manager.send_to_user(uid, wsMessage(type=wsType.UPDATE, payload=wsResponse(
                        msg_id=message.payload.msg_id,
                        response_status="success",
                        response_body="Posted Update"
                    )))

                
            log.debug("[WS] Sending REDIS event of type: %s", message.type)
            await r.publish(
                "ws_events",
                RedisEvent(type=message.type, msg_id=message.payload.msg_id).model_dump_json()
            )
        
    finally:
        await manager.disconnect(ws, uid)
