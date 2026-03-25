from pydantic import BaseModel

## MAINLY FOR DOCS; WILL AUTO LIST WHATS NEEDED
class PubRSA(BaseModel):
    public_key: str
