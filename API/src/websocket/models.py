from pydantic import BaseModel

class wsMessage(BaseModel):
    type: str
    sender_uid: str
    recipient_uid: str
    room_id: str
    msg: str
    