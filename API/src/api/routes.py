from fastapi import APIRouter
from ..redis_db import msg, user

router = APIRouter()

"""
@router.get("/msg")
async def get_msg_test(msg: str):
    await write_msg(msg)
    return await read_msg()

@router.get("/msg/read")
async def get_msg_read():
    return await read_msg()
"""

@router.get("/rsa/{uid}")
async def get_rsa_pub():
    return True

@router.post("/rsa/{uid}")
async def post_rsa_pub():
    return True
