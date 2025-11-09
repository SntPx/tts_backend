from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AudioCreate(BaseModel):
    key: str
    filename: str
    content_type: Optional[str]
    duration: Optional[float]
    size_bytes: Optional[int]
    owner: Optional[str]


class AudioOut(BaseModel):
    id: str
    key: str
    minio_key: str
    filename: str
    country: str
    content_type: Optional[str]
    duration: Optional[float]
    size_bytes: Optional[int]
    owner: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class AudioResponse(BaseModel):
    id: str
    country: str
    filename: str
    duration: float | None
    size_bytes: int | None
    public_url: str

    class Config:
        from_attributes = True
