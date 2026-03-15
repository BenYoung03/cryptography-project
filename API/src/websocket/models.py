from pydantic import BaseModel

class wsMessage(BaseModel):
    type: str
    payload: dict

class wsError(BaseModel):
    error_type: str
    error_msg: str
    metadata: dict | None = None