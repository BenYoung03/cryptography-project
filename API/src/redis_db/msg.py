from .redis import redis_client as r

async def write_msg(msg: str):
    await r.set("msg", msg)

async def read_msg():
    return await r.get("msg")
