from pydantic import BaseModel

class CipherText(BaseModel):
    ciphertext: str
    IV: str
    tag: str | None = None

class Key(BaseModel):
    algorithm: str
    encrypted_key: str

class HMAC(BaseModel):
    string: str

class msg(BaseModel):
## Routing Data
    msg_id: str
    sender_uid: str
    recipient_uid: str
    
## Cryptographic Fields
    ciphertext: CipherText
    hmac: HMAC

## Metadata
    status: str
    timestamp: int
    server_timestamp: int
