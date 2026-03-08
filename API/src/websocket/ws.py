from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import ConnectionManager
from .models import wsMessage
from ..redis_db.redis import redis_client as r
import json

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, uid: str):
    await manager.connect(ws, uid)

    try:
        while True:
            data = await ws.receive_json()
            
            message = wsMessage(**data)
            await r.publish(
                "ws_events",
                message.model_dump_json()
            )
    except WebSocketDisconnect:
        await manager.disconnect(uid)
