from pydantic import BaseModel

class PublicKey(BaseModel):
    uid: str

class PubRSA(PublicKey):
    e: int
    n: int

