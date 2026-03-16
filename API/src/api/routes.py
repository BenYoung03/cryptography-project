from fastapi import APIRouter, Depends, Request, Header, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..redis_db import user
from ..redis_db import msg
from ..models.user import PubRSA
from ..middleware.auth import get_uid
import time

router = APIRouter()

class RSAResponse(BaseModel):
    uid: str
    key: PubRSA

async def required_headers(x_uid: str = Header(...), x_jwt: str = Header(...)):
    # This dependency is just for docs
    return {"uid": x_uid, "jwt": x_jwt}

@router.get("/{uid}/rsa", dependencies=[Depends(required_headers)])
async def get_rsa_pub(uid: str) -> Response:
    res = await user.get_user_rsa(uid)
    if res == None:
        return JSONResponse(status_code=404, content={"error": "uid does not have associated public key"})
    return JSONResponse(status_code=200, content=RSAResponse(uid=uid, key=res).model_dump())

@router.post("/{uid}/rsa", dependencies=[Depends(required_headers)])
async def post_rsa_pub(uid: str, rsa: PubRSA, x_uid: str = Header(...)) -> Response: ## fastAPI rejects if body doesnt match this!! very handy
    if uid != x_uid:
        return JSONResponse(status_code=401, content={"unauthorized": "Can only post keys for authourized user"})
    
    res = await user.set_user_rsa(x_uid, rsa)
    if res<0:
        return JSONResponse(status_code=500, content={"error": "redis update/write failed, contact backend dev; bad!!"})
    
    return JSONResponse(status_code=201, content={"success": f"New RSA pub key written for {x_uid}"})

@router.get("/history")
async def get_history(ts: int = time.time(), uid: str = Depends(get_uid)):
    messages = msg.get_messages_since(uid, ts)
    updates = msg.get_updates_since(uid, ts)
    return JSONResponse(status_code=200, content={"messages": messages, "updates": updates, "since": ts})
