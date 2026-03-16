from pydantic import BaseModel, ConfigDict
from .msg import Msg, Update
from enum import Enum

class wsType(str, Enum):
    MSG = "msg"
    UPDATE = "update"
    ERROR = "error"
    RESPONSE = "response"

class wsError(BaseModel):
    error_type: str
    error_msg: str
    metadata: dict | None = None

class wsResponse(BaseModel):
    msg_id: str
    response_status: str
    response_body: str | dict

class wsMessage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: wsType
    payload: Msg | Update | wsError | wsResponse | None
