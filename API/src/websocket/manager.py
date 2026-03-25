from fastapi import WebSocket
from asyncio import Lock
from ..models.ws import wsMessage
import logging

log = logging.getLogger("uvicorn.error")

class ConnectionManager:
    """ Manages WebSocket Connections, indexed on clients provided uid

    Parameters
    ----------
        connections : dict{uid, websocket}
            Where all the connections are stored
        lock : asyncio.Lock()
            Provides locking for editing the connections dictionary
    """
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.lock = Lock()
    
    async def connect(self, ws: WebSocket, uid: str):
        log.info("[WS-MANAGER] Opening Connection for UID:%s", uid)
        await ws.accept()
        ## lock prevents concurrent write and potential race conditions
        async with self.lock:
            self.connections[uid] = ws
    
    async def disconnect(self, ws: WebSocket, uid: str): 
        log.info("[WS-MANAGER] Closing Connection for UID:%s", uid)
        async with self.lock:
            # Only remove if the connection being tracked is the one actually disconnecting
            if self.connections.get(uid) == ws:
                self.connections.pop(uid, None)

    async def send_to_user(self, uid: str, msg: wsMessage):
        log.debug("[WS-MANAGER] sending to UID: %s, MSG:\n%s", uid, msg.model_dump_json(indent=2))
        async with self.lock: 
            ws: WebSocket
            ws=self.connections.get(uid)
            if ws:
                try:
                    await ws.send_text(msg.model_dump_json())
                except Exception as e:
                    log.error("[WS-MANAGER] Failed to send to UID %s: %s", uid, repr(e))
