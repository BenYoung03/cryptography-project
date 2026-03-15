from pydantic import BaseModel
from enum import Enum

class Status(Enum):
    SENT = "sent"
    READ = "read"
    DELETED = "deleted"


class CipherText(BaseModel):
    ciphertext: str
    IV: str
    tag: str | None = None

class Key(BaseModel):
    algorithm: str
    encrypted_key: str

class HMAC(BaseModel):
    string: str

class Msg(BaseModel):
## Routing Data
    msg_id: str
    sender_uid: str
    recipient_uid: str
    
## Cryptographic Fields
    ciphertext: CipherText
    hmac: HMAC

## Metadata
    status: Status
    timestamp: int
    server_timestamp: int

class Update(BaseModel):
    msg_id: str
    status: Status
