from fastapi import FastAPI
import asyncio

from .api.routes import router as apiRouter
from .websocket.ws import router as wsRouter, manager as wsManager
from .redis_db.subpub import redis_listener, init_manager

## redis event sub-pub init and connection manager init
init_manager(wsManager)
asyncio.create_task(redis_listener()) ## spin up listener task

## app and router init
app = FastAPI(title="Cyllenian Web Backend")

app.include_router(apiRouter)
app.include_router(wsRouter)

## test endpoint
@app.get("/")
def hello_world():
    return {"Hello":"World"}
