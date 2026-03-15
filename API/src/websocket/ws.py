from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from .manager import ConnectionManager
from .models import wsMessage, wsError
from ..models.msg import Msg, Update
from ..redis_db.redis import redis_client as r
from ..redis_db import msg as msgCRUD

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, uid: str):
    await manager.connect(ws, uid)

    try:
        while True:
            data = await ws.receive_json()
            
            message = wsMessage(**data)
            if message.type == "msg":
                message.payload = Msg(**message.payload)
            if message.type == "update":
                message.payload = Update(**message.payload)
                if msgCRUD.get_msg_recipient(message.payload.msg_id) != uid: 
                    asyncio.create_task(manager.send_to_user(uid, wsMessage("error", wsError("no-access", "message to update does not belong to client"))))
                    continue
            await r.publish(
                "ws_events",
                message
            )
    except WebSocketDisconnect:
        await manager.disconnect(uid)
