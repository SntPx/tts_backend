from io import BytesIO
from sqlalchemy.orm import Session
from . import models, schemas
from typing import cast
from pydub import AudioSegment


def get_audio_duration_bytes(data: bytes, ext: str) -> float:
    try:
        audio = AudioSegment.from_file(BytesIO(data), format=ext)
        return len(audio) / 1000.0
    except:
        return None


def create_audio(db: Session, audio: schemas.AudioCreate):
    db_obj = models.Audio(**audio.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_audio(db: Session, audio_hash: str):
    return db.query(models.Audio).filter(cast("ColumnElement[bool]", models.Audio.id == audio_hash)).first()


def list_audios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Audio).offset(skip).limit(limit).all()
