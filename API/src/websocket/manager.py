from fastapi import WebSocket
from asyncio import Lock
from ..models.ws import wsMessage
import weakref
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
        self.connections = weakref.WeakValueDictionary()
        self.lock = Lock()
    
    async def connect(self, ws: WebSocket, uid: str):
        await ws.accept()
        ## lock prevents concurrent write and potential race conditions
        async with self.lock:
            self.connections[uid] = ws
    
    async def disconnect(self, uid: str): 
        async with self.lock:
            ws = self.connections.pop(uid, None)

    async def send_to_user(self, uid: str, msg: wsMessage):
        log.debug("[WS-MANAGER] sending to UID: %s, MSG:\n%s", uid, msg.model_dump_json(indent=2))
        async with self.lock: 
            ws: WebSocket
            ws=self.connections.get(uid)
            if ws:
                await ws.send_json(msg.model_dump_json())


