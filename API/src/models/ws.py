from pydantic import BaseModel
from .msg import Msg, Update
from enum import Enum

class wsType(str, Enum):
    MSG = "msg"
    UPDATE = "update"
    ERROR = "error"

class wsError(BaseModel):
    error_type: str
    error_msg: str
    metadata: dict | None = None

class wsMessage(BaseModel):
    type: wsType
    payload: Msg | Update | wsError
