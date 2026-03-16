from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio

## Backend Managers and DB
from ..redis_db.redis import redis_client as r
from ..redis_db import msg as msgCRUD
from .manager import ConnectionManager

## Data Models
from ..models.ws import wsMessage, wsError
from ..models.msg import Msg, Update

## utility functions
from ..utils.ulid import generate_id
from ..middleware.auth import get_uid

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, uid: str = Depends(get_uid)):
    await manager.connect(ws, uid) ## add connection to manager

    try:
        while True:
            data = await ws.receive_json()
            
            message = wsMessage(
                type=data["type"],
                payload=data["payload"]
            )

            if message.type == "msg":
                message.payload = Msg(**message.payload)
                message.payload.msg_id = generate_id("m")
                await msgCRUD.store_message(message.payload)

            elif message.type == "update":
                message.payload = Update(**message.payload)
                if msgCRUD.get_msg_recipient(message.payload.msg_id) != uid: 
                    asyncio.create_task(manager.send_to_user(uid, wsMessage("error", wsError("no-access", "message does not belong to client"))))
                    continue
                msgCRUD.update_message_status(message.payload)
            await r.publish(
                "ws_events",
                message.model_dump_json()
            )
    except WebSocketDisconnect:
        await manager.disconnect(uid)
