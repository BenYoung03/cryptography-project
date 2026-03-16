## event data model
from pydantic import BaseModel
from enum import Enum

class EventType(str, Enum):
    NEW_MESSAGE = "msg"
    STATUS_UPDATE = "update"

class RedisEvent(BaseModel):
    type: EventType
    msg_id: str
