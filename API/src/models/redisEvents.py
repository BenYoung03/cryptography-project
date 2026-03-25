## event data model
from pydantic import BaseModel
from enum import Enum

## ENUM FOR THE TYPES OF VALID EVENTS
class EventType(str, Enum):
    NEW_MESSAGE = "msg"
    STATUS_UPDATE = "update"

## EVENTTYPE+MSG_ID; KEPT SLIM FOR TRANSPORT
class RedisEvent(BaseModel):
    type: EventType
    msg_id: str
