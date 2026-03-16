from fastapi import APIRouter, Depends, Request, Header
from fastapi.responses import JSONResponse
from ..redis_db import user
from ..redis_db import msg
from ..models.user import PubRSA
from ..middleware.auth import get_uid
import time

router = APIRouter()

async def required_headers(x_uid: str = Header(...), x_jwt: str = Header(...)):
    # This dependency is just for docs
    return {"uid": x_uid, "jwt": x_jwt}

@router.get("/rsa", dependencies=[Depends(get_uid), Depends(required_headers)])
async def get_rsa_pub(request: Request):
    uid = request.state.uid
    res = await user.get_user_rsa(uid)
    if res == None:
        return JSONResponse(status_code=404, content={"error": "uid does not have associated public key"})
    return JSONResponse(status_code=200, content={uid: res})

@router.post("/rsa")
async def post_rsa_pub(rsa: PubRSA, uid: str = Depends(get_uid)): ## fastAPI rejects if body doesnt match this!! very handy
    res = await user.set_user_rsa(uid, rsa)
    if res<0:
        return JSONResponse(status_code=500, content={"error": "redis update/write failed, contact backend dev"})
    return JSONResponse(status_code=201, content={"success": f"New RSA pub key written for {uid}"})

@router.get("/history")
async def get_history(ts: int = time.time(), uid: str = Depends(get_uid)):
    messages = msg.get_messages_since(uid, ts)
    updates = msg.get_updates_since(uid, ts)
    return JSONResponse(status_code=200, content={"messages": messages, "updates": updates, "since": ts})
