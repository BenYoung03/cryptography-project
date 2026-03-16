from pydantic import BaseModel
from enum import Enum

class Status(Enum):
    SENT =      0
    DELIVERED = 1
    READ =      2
    DELETED =   3


class CipherText(BaseModel):
    ciphertext: str
    IV: str
    tag: str | None = None

class Key(BaseModel):
    algorithm: str
    encrypted_key: str

class Msg(BaseModel):
## Routing Data
    msg_id: str
    sender_uid: str
    recipient_uid: str
    
## Cryptographic Fields
    ciphertext: CipherText
    key: Key

## Metadata
    status: Status
    timestamp: int
    ttl: int
    server_timestamp: int | None = None

class Update(BaseModel):
    msg_id: str
    status: Status
