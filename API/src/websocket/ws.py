from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from .manager import ConnectionManager
from ..models.ws import wsMessage, wsError
from ..models.msg import Msg, Update
from ..redis_db.redis import redis_client as r
from ..redis_db import msg as msgCRUD
from ..utils.ulid import generate_id

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
                message.payload = Msg(msg_id=generate_id('m'), **message.payload)
                msgCRUD.store_message(message.payload)
            elif message.type == "update":
                message.payload = Update(**message.payload)
                if msgCRUD.get_msg_recipient(message.payload.msg_id) != uid: 
                    asyncio.create_task(manager.send_to_user(uid, wsMessage("error", wsError("no-access", "message to update does not belong to client"))))
                    continue
                msgCRUD.update_message_status(**message.payload)
            await r.publish(
                "ws_events",
                message.model_dump_json()
            )
    except WebSocketDisconnect:
        await manager.disconnect(uid)
