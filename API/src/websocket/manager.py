from fastapi import WebSocket
from asyncio import Lock
from .models import wsMessage

class ConnectionManager:
    def __init__(self):
        self.connections = {}
        self.lock = Lock()
    
    async def connect(self, ws: WebSocket, uid: str):
        await ws.accept()
        ## lock prevents concurrent write and potential race conditions
        async with self.lock:
            self.connections[uid] = ws
    
    async def disconnect(self, ws: WebSocket, uid: str): 
        async with self.lock: self.connections[uid] = ws

    async def send_to_user(self, uid: str, msg: wsMessage):
        async with self.lock: 
            ws: WebSocket
            ws=self.connections.get(uid)

        if ws:
            await ws.send_json(msg)

