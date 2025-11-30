from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.minio_client import get_public_url

Base = declarative_base()


class Audio(Base):
    __tablename__ = "audio"
    id = Column(String(40), primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    minio_key = Column(String)
    country = Column(String(2))
    filename = Column(String)
    content_type = Column(String)
    duration = Column(Float, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    owner = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def public_url(self):
        return get_public_url(self.minio_key)
