from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from .api.routes import router as apiRouter
from .websocket.ws import router as wsRouter, manager as wsManager
from .redis_db.subpub import redis_listener, init_manager
from .middleware.auth import AuthMiddleware

## redis event sub-pub init and connection manager init
init_manager(wsManager)
asyncio.create_task(redis_listener()) ## spin up listener task

## lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    ## startup code
    yield
    for uid, ws in list(wsManager.connections.items()):
        try:
            await ws.close()
        except:
            pass
    wsManager.connections.clear()

## app and router init
app = FastAPI(title="Cyllenian Web Backend", lifespan=lifespan)

app.add_middleware(AuthMiddleware)

app.include_router(apiRouter)
app.include_router(wsRouter)

## test endpoint
@app.get("/")
def hello_world():
    return {"Hello":"World"}
