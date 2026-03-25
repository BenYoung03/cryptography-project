from pydantic import BaseModel
from enum import Enum

## STORED AS NUMBERS FOR COMPARISON
class Status(Enum):
    SENT =      0
    DELIVERED = 1
    READ =      2
    DELETED =   3

## SIG AND CIPHERTEXT
class CipherText(BaseModel):
    ciphertext: str
    IV: str
    signature: str | None = None

## AES KEY WITH WHAT IT WAS ENCRYPTED WITH
class Key(BaseModel):
    algorithm: str
    encrypted_key: str | None = None

## MESSAGE DATA
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

## UPDATE DATA
class Update(BaseModel):
    msg_id: str
    status: Status
