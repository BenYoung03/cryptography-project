## event data model
from pydantic import BaseModel
from enum import Enum

class EventType(str, Enum):
    NEW_MESSAGE = "new_message"
    STATUS_UPDATE = "status_update"

class RedisEvent(BaseModel):
    type: EventType
    msg_id: str
    recipient_id: str
