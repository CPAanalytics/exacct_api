from pydantic import BaseModel


class BatchIn(BaseModel):
    platform: str
    request_batch: list[dict]


class BatchOut(BaseModel):
    response_batch: list[dict]
