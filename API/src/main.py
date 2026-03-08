from fastapi import FastAPI

from .redis_db import redis
from .api.routes import router as apiRouter

app = FastAPI(title="C4476 Project API")

app.include_router(apiRouter)

@app.get("/")
def hello_world():
    return {"Hello":"World"}
