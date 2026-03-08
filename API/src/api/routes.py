from fastapi import APIRouter
from ..redis_db.msg import read_msg, write_msg

router = APIRouter()

@router.get("/msg")
async def get_msg_test(msg: str):
    await write_msg(msg)
    return await read_msg()

@router.get("/msg/read")
async def get_msg_read():
    return await read_msg()

