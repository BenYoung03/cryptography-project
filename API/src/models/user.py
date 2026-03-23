from pydantic import BaseModel

class PubRSA(BaseModel):
    public_key: str
