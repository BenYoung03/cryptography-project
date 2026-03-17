from pydantic import BaseModel

class PubRSA(BaseModel):
    e: int
    n: int

